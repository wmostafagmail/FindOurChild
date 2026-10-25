import hashlib
import io
from uuid import uuid4

import psycopg
import pytest
from botocore.exceptions import ClientError
from foc_api import media, worker
from PIL import Image

from .helpers import admin, cid, create_report, headers, make_client, png, upload, verify_reporter


def authenticated():
    client = make_client()
    receipt, body = create_report(client)
    verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])
    return client, receipt


@pytest.mark.parametrize("mime,fmt", [("image/png", "PNG"), ("image/jpeg", "JPEG"), ("image/webp", "WEBP")])
def test_real_clamav_versioned_storage_and_sanitized_derivative(mime, fmt):
    client, receipt = authenticated()
    try:
        output = io.BytesIO()
        Image.new("RGB", (16, 16), "green").save(output, format=fmt)
        data = output.getvalue()
        iid, _ = upload(client, data, mime)
        assert worker.once()
        with admin() as conn:
            assert (
                conn.execute("SELECT state FROM app.upload_intents WHERE id=%s", (iid,)).fetchone()[0]
                == "ready"
            )
            row = conn.execute(
                "SELECT scan_engine,scan_signature FROM platform.upload_metadata WHERE intent_id=%s", (iid,)
            ).fetchone()
            assert row[0] == "ClamAV 1.5.4"
            assert row[1].startswith("ClamAV 1.5.4/")
            assert (
                conn.execute(
                    "SELECT count(*) FROM app.photographs WHERE case_id=%s AND synthetic", (cid(receipt),)
                ).fetchone()[0]
                == 1
            )
            assert (
                conn.execute(
                    "SELECT count(*) FROM app.photo_derivatives WHERE case_id=%s AND exif_removed",
                    (cid(receipt),),
                ).fetchone()[0]
                == 1
            )
    finally:
        client.close()


def test_multiple_photos_keep_individual_intents_and_no_automatic_identity():
    client, receipt = authenticated()
    try:
        ids = [upload(client, png())[0] for _ in range(2)]
        assert len(set(ids)) == 2
        assert worker.once()
        assert worker.once()
        with admin() as conn:
            assert (
                conn.execute(
                    "SELECT count(*) FROM app.photographs WHERE case_id=%s", (cid(receipt),)
                ).fetchone()[0]
                == 2
            )
            assert (
                conn.execute(
                    "SELECT verification_status FROM app.cases WHERE id=%s", (cid(receipt),)
                ).fetchone()[0]
                == "unverified"
            )
            assert (
                conn.execute(
                    "SELECT count(*) FROM app.embeddings WHERE case_id=%s", (cid(receipt),)
                ).fetchone()[0]
                == 0
            )
    finally:
        client.close()


def test_clamav_detects_controlled_eicar_test_signature_without_serving():
    # Standard inert antivirus test string, never an executable malware sample.
    eicar = b"X5O!P%@AP[4" + b"\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    assert media.scan(eicar)[0] == "infected"
    client, receipt = authenticated()
    try:
        iid, _ = upload(client, eicar)
        assert worker.once()
        with admin() as conn:
            assert (
                conn.execute("SELECT state FROM app.upload_intents WHERE id=%s", (iid,)).fetchone()[0]
                == "rejected"
            )
            assert (
                conn.execute("SELECT count(*) FROM app.objects WHERE case_id=%s", (cid(receipt),)).fetchone()[
                    0
                ]
                == 0
            )
    finally:
        client.close()


@pytest.mark.parametrize("attack", ["invalid_bytes", "mime_mismatch", "animation", "decompression_bomb"])
def test_bad_media_never_becomes_ready(attack):
    if attack == "invalid_bytes":
        data = b"not an image <script>SYNTHETIC_SECRET_CANARY</script>"
    elif attack == "mime_mismatch":
        out = io.BytesIO()
        Image.new("RGB", (8, 8)).save(out, format="JPEG")
        data = out.getvalue()
    elif attack == "animation":
        out = io.BytesIO()
        Image.new("RGB", (8, 8), "red").save(
            out, format="PNG", save_all=True, append_images=[Image.new("RGB", (8, 8), "green")], duration=10
        )
        data = out.getvalue()
    else:
        out = io.BytesIO()
        Image.new("1", (4000, 4000)).save(out, format="PNG")
        data = out.getvalue()
    client, receipt = authenticated()
    try:
        iid, _ = upload(client, data)
        assert worker.once()
        with admin() as conn:
            assert (
                conn.execute("SELECT state FROM app.upload_intents WHERE id=%s", (iid,)).fetchone()[0]
                == "rejected"
            )
            assert (
                conn.execute(
                    "SELECT count(*) FROM app.photo_derivatives WHERE case_id=%s", (cid(receipt),)
                ).fetchone()[0]
                == 0
            )
    finally:
        client.close()


def test_metadata_removed_at_byte_level_and_envelope_authentication():
    data = png(True)
    clean = media.sanitize(data, "image/png")
    assert b"CANARY" in data
    assert b"CANARY" not in clean
    with Image.open(io.BytesIO(clean)) as image:
        assert image.info == {}
        assert not image.getexif()
    wrapped = media.new_key()
    key = uuid4()
    encrypted = media.encrypt(data, wrapped, key)
    assert data not in encrypted
    assert media.decrypt(encrypted, wrapped, key) == data
    from cryptography.exceptions import InvalidTag

    with pytest.raises(InvalidTag):
        media.decrypt(encrypted, wrapped, uuid4())
    with pytest.raises(InvalidTag):
        media.decrypt(encrypted[:-1] + bytes([encrypted[-1] ^ 1]), wrapped, key)


@pytest.mark.parametrize(
    "attack",
    [
        "checksum",
        "size",
        "mime",
        "foreign_intent",
        "expired_intent",
        "complete_version",
        "complete_hash",
        "overwrite",
    ],
)
def test_upload_binding_rejects_tampering_and_replay(attack):
    client, _receipt = authenticated()
    try:
        data = png()
        body = {"mime": "image/png", "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        result = client.post("/v1/reporter/upload-intents", json=body, headers=headers(client))
        assert result.status_code == 201
        iid = result.json()["id"]
        if attack == "foreign_intent":
            iid = str(uuid4())
        if attack == "expired_intent":
            with admin() as conn:
                conn.execute(
                    "UPDATE app.upload_intents SET expires_at=now()-interval '1 minute' WHERE id=%s", (iid,)
                )
        sent = data + b"extra" if attack == "size" else data[:-1] + b"X" if attack == "checksum" else data
        response = client.put(
            "/v1/reporter/upload-intents/" + iid + "/content",
            content=sent,
            headers={**headers(client), "Content-Type": "text/html" if attack == "mime" else "image/png"},
        )
        if attack in ["checksum", "size", "mime", "foreign_intent", "expired_intent"]:
            assert response.status_code in {404, 413, 415, 422}
            return
        assert response.status_code == 200
        bound = response.json()
        if attack == "overwrite":
            replay = client.put(
                "/v1/reporter/upload-intents/" + iid + "/content",
                content=data,
                headers={**headers(client), "Content-Type": "image/png"},
            )
            assert replay.status_code == 200 and replay.json() == bound
            changed = client.put(
                "/v1/reporter/upload-intents/" + iid + "/content",
                content=data[:-1] + b"X",
                headers={**headers(client), "Content-Type": "image/png"},
            )
            assert changed.status_code == 422
            return
        if attack == "complete_version":
            bound["object_version"] = "forged-version"
        if attack == "complete_hash":
            bound["sha256"] = "0" * 64
        assert (
            client.post(
                "/v1/reporter/upload-intents/" + iid + "/complete", json=bound, headers=headers(client)
            ).status_code
            == 409
        )
        with admin() as conn:
            assert (
                conn.execute("SELECT count(*) FROM app.jobs WHERE aggregate_id=%s", (iid,)).fetchone()[0] == 0
            )
    finally:
        client.close()


def test_duplicate_completion_creates_only_one_scan_job():
    client, _receipt = authenticated()
    try:
        iid, bound = upload(client)
        assert (
            client.post(
                "/v1/reporter/upload-intents/" + iid + "/complete", json=bound, headers=headers(client)
            ).status_code
            == 202
        )
        with admin() as conn:
            assert (
                conn.execute("SELECT count(*) FROM app.jobs WHERE aggregate_id=%s", (iid,)).fetchone()[0] == 1
            )
        assert worker.once()
    finally:
        client.close()


def test_upload_quota_and_oversize_rejected_before_storage():
    client, _ = authenticated()
    try:
        body = {"mime": "image/png", "bytes": 5242881, "sha256": "0" * 64}
        assert (
            client.post("/v1/reporter/upload-intents", json=body, headers=headers(client)).status_code == 422
        )
        body["bytes"] = 10
        for _ in range(10):
            assert (
                client.post("/v1/reporter/upload-intents", json=body, headers=headers(client)).status_code
                == 201
            )
        assert (
            client.post("/v1/reporter/upload-intents", json=body, headers=headers(client)).status_code == 422
        )
    finally:
        client.close()


def test_storage_role_permissions_and_no_anonymous_access():
    import boto3
    from botocore import UNSIGNED
    from botocore.config import Config

    unsigned = boto3.client(
        "s3",
        endpoint_url="http://storage:8333",
        config=Config(signature_version=UNSIGNED, connect_timeout=3, read_timeout=3),
    )
    with pytest.raises(ClientError):
        unsigned.list_buckets()
    with pytest.raises(ClientError):
        media.s3("API").get_object(Bucket="foc-original", Key=str(uuid4()))
    with pytest.raises(ClientError):
        media.s3("GATEWAY").put_object(Bucket="foc-derivative", Key=str(uuid4()), Body=b"forged")
    with pytest.raises(ClientError):
        media.s3("GATEWAY").get_object(Bucket="foc-quarantine", Key=str(uuid4()))
    for bucket in ["foc-quarantine", "foc-original", "foc-derivative"]:
        assert media.s3("ADMIN").get_bucket_versioning(Bucket=bucket)["Status"] == "Enabled"


@pytest.mark.parametrize("revocation", ["report_access", "case_deleted", "org_suspended", "generation"])
def test_worker_publish_rechecks_current_authority_and_deletion_generation(revocation):
    client, receipt = authenticated()
    try:
        iid, _ = upload(client)
        case = cid(receipt)
        with admin() as conn:
            if revocation == "report_access":
                conn.execute("UPDATE app.report_access SET revoked_at=now() WHERE case_id=%s", (case,))
            if revocation == "case_deleted":
                conn.execute("UPDATE app.cases SET deleted_at=now() WHERE id=%s", (case,))
            if revocation == "org_suspended":
                conn.execute(
                    "UPDATE app.organizations SET suspended_at=now() WHERE id=(SELECT organization_id FROM app.cases WHERE id=%s)",
                    (case,),
                )
            if revocation == "generation":
                conn.execute(
                    "UPDATE app.cases SET deletion_generation=deletion_generation+1 WHERE id=%s", (case,)
                )
            try:
                assert worker.once()
                assert (
                    conn.execute("SELECT state FROM app.jobs WHERE aggregate_id=%s", (iid,)).fetchone()[0]
                    == "cancelled"
                )
                assert (
                    conn.execute(
                        "SELECT count(*) FROM app.photo_derivatives WHERE case_id=%s", (case,)
                    ).fetchone()[0]
                    == 0
                )
            finally:
                if revocation == "org_suspended":
                    conn.execute(
                        "UPDATE app.organizations SET suspended_at=NULL WHERE id=(SELECT organization_id FROM app.cases WHERE id=%s)",
                        (case,),
                    )
    finally:
        client.close()


def test_lease_fencing_and_worker_database_least_privilege():
    client, _ = authenticated()
    try:
        iid, _ = upload(client)
        with worker.connection() as conn:
            job = conn.execute("SELECT platform.media_lease()").fetchone()[0]
        assert job["intent_id"] == iid
        with worker.connection() as conn:
            assert (
                conn.execute(
                    "SELECT platform.media_finish(%s,%s,'error',NULL,NULL,NULL,NULL,NULL,NULL,NULL)",
                    (job["job_id"], uuid4()),
                ).fetchone()[0]
                is False
            )
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                conn.execute("SELECT * FROM app.cases")
        with admin() as conn:
            conn.execute(
                "UPDATE app.jobs SET lease_until=now()-interval '1 second' WHERE id=%s", (job["job_id"],)
            )
        assert worker.once()
        with worker.connection() as conn:
            assert (
                conn.execute(
                    "SELECT platform.media_finish(%s,%s,'error',NULL,NULL,NULL,NULL,NULL,NULL,NULL)",
                    (job["job_id"], job["lease_token"]),
                ).fetchone()[0]
                is False
            )
    finally:
        client.close()


@pytest.mark.parametrize("crash_at", ["before_scan", "after_original", "after_derivative"])
def test_actual_worker_process_crash_recovers_lease_without_duplicate_publication(crash_at):
    import subprocess
    import sys

    client, receipt = authenticated()
    try:
        iid, _ = upload(client)
        with admin() as conn:
            conn.execute("UPDATE app.jobs SET next_attempt_at='1980-01-01' WHERE aggregate_id=%s", (iid,))
        if crash_at == "before_scan":
            program = (
                "import os;from foc_api import worker,media;media.scan=lambda data:os._exit(73);worker.once()"
            )
        else:
            bucket = "foc-original" if crash_at == "after_original" else "foc-derivative"
            program = (
                "import os;from foc_api import worker,media;original=media.put_once\ndef interrupted(bucket,*args):\n result=original(bucket,*args)\n if bucket=="
                + repr(bucket)
                + ":os._exit(73)\n return result\nmedia.put_once=interrupted\nworker.once()"
            )
        process = subprocess.run(
            [sys.executable, "-c", program], capture_output=True, timeout=20, check=False
        )
        assert process.returncode == 73
        with admin() as conn:
            assert conn.execute(
                "SELECT state,attempts FROM app.jobs WHERE aggregate_id=%s", (iid,)
            ).fetchone() == ("leased", 1)
            conn.execute(
                "UPDATE app.jobs SET lease_until=now()-interval '1 second',next_attempt_at='1980-01-01' WHERE aggregate_id=%s",
                (iid,),
            )
        assert worker.once()
        with admin() as conn:
            assert conn.execute(
                "SELECT state,attempts FROM app.jobs WHERE aggregate_id=%s", (iid,)
            ).fetchone() == ("completed", 2)
            assert (
                conn.execute(
                    "SELECT count(*) FROM app.photographs WHERE case_id=%s", (cid(receipt),)
                ).fetchone()[0]
                == 1
            )
    finally:
        client.close()


def test_stale_worker_cannot_erase_versions_adopted_by_newer_lease():
    import subprocess
    import sys
    import tempfile
    import time
    from pathlib import Path

    client, receipt = authenticated()
    try:
        iid, _ = upload(client)
        with admin() as conn:
            conn.execute("UPDATE app.jobs SET next_attempt_at='1970-01-01' WHERE aggregate_id=%s", (iid,))
        with tempfile.TemporaryDirectory() as directory:
            ready = Path(directory) / "ready"
            release = Path(directory) / "release"
            program = (
                "import time;from pathlib import Path;from foc_api import worker,media;original=media.scan\ndef paused(data):\n result=original(data)\n Path("
                + repr(str(ready))
                + ").touch()\n while not Path("
                + repr(str(release))
                + ").exists():time.sleep(.05)\n return result\nmedia.scan=paused\nworker.once()"
            )
            process = subprocess.Popen(
                [sys.executable, "-c", program], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            try:
                deadline = time.monotonic() + 15
                while not ready.exists() and time.monotonic() < deadline:
                    time.sleep(0.05)
                assert ready.exists()
                with admin() as conn:
                    conn.execute(
                        "UPDATE app.jobs SET lease_until=now()-interval '1 second' WHERE aggregate_id=%s",
                        (iid,),
                    )
                assert worker.once()
                release.touch()
                assert process.wait(timeout=15) == 0
                with admin() as conn:
                    objects = conn.execute(
                        "SELECT bucket_class,opaque_key,object_version FROM app.objects WHERE case_id=%s",
                        (cid(receipt),),
                    ).fetchall()
                assert len(objects) == 2
                for bucket, key, version in objects:
                    response = media.s3("ADMIN").get_object(
                        Bucket="foc-" + bucket, Key=str(key), VersionId=version
                    )
                    try:
                        assert len(response["Body"].read()) > 28
                    finally:
                        response["Body"].close()
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=5)
    finally:
        client.close()
