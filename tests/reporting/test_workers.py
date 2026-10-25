from pathlib import Path

import pytest
from botocore.exceptions import ClientError
from foc_api import media, worker

from .helpers import MODERATOR, admin, cid, create_report, headers, make_client, png, verify_reporter


def test_neutral_notification_sink_deduplicates_and_has_no_child_payload():
    with make_client() as client:
        receipt, _ = create_report(client)
        case = cid(receipt)
        with admin() as conn:
            event = conn.execute(
                "SELECT id FROM app.outbox_events WHERE case_id=%s AND type='report.submitted'", (case,)
            ).fetchone()[0]
            conn.execute("UPDATE app.outbox_events SET occurred_at='2000-01-01' WHERE id=%s", (event,))
        worker.maintain()
        path = Path("/notifications") / (str(event) + "-" + MODERATOR + ".json")
        data = path.read_bytes()
        assert b"case_id" not in data and str(case).encode() not in data and receipt.encode() not in data
        assert b"neutral-task-v1" in data
        with admin() as conn:
            conn.execute(
                "UPDATE app.outbox_events SET state='pending',next_attempt_at=now() WHERE id=%s", (event,)
            )
        worker.maintain()
        assert path.read_bytes() == data


def test_revoked_notification_recipient_is_excluded_at_send_time():
    with make_client() as client:
        receipt, _ = create_report(client)
        case = cid(receipt)
        with admin() as conn:
            event = conn.execute("SELECT id FROM app.outbox_events WHERE case_id=%s", (case,)).fetchone()[0]
            conn.execute("UPDATE app.outbox_events SET occurred_at='1999-01-01' WHERE id=%s", (event,))
        with worker.connection() as conn:
            leased = conn.execute("SELECT platform.outbox_next()").fetchone()[0]
        assert leased["event_id"] == str(event)
        with admin() as conn:
            conn.execute(
                "UPDATE app.case_grants SET revoked_at=now() WHERE case_id=%s AND permission='case.read'",
                (case,),
            )
        with worker.connection() as conn:
            assert (
                conn.execute(
                    "SELECT platform.outbox_recipient_current(%s,%s,%s)",
                    (event, MODERATOR, leased["attempt"]),
                ).fetchone()[0]
                is False
            )
        assert not (Path("/notifications") / (str(event) + "-" + MODERATOR + ".json")).exists()


def test_expired_orphan_version_is_erased_before_acknowledgment():
    import hashlib

    with make_client() as client:
        receipt, body = create_report(client)
        verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])
        data = png()
        response = client.post(
            "/v1/reporter/upload-intents",
            json={"mime": "image/png", "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()},
            headers=headers(client),
        )
        assert response.status_code == 201
        iid = response.json()["id"]
        bound = client.put(
            "/v1/reporter/upload-intents/" + iid + "/content",
            content=data,
            headers={**headers(client), "Content-Type": "image/png"},
        )
        assert bound.status_code == 200
        with admin() as conn:
            key = conn.execute(
                "SELECT quarantine_key FROM platform.upload_metadata WHERE intent_id=%s", (iid,)
            ).fetchone()[0]
            conn.execute(
                "UPDATE app.upload_intents SET expires_at=now()-interval '25 hours' WHERE id=%s", (iid,)
            )
        # Other ready images can precede this orphan; all candidates are bounded synthetic fixture objects.
        for _ in range(100):
            worker.maintain()
            with admin() as conn:
                if (
                    conn.execute("SELECT state FROM app.upload_intents WHERE id=%s", (iid,)).fetchone()[0]
                    == "expired"
                ):
                    break
        with admin() as conn:
            assert (
                conn.execute("SELECT state FROM app.upload_intents WHERE id=%s", (iid,)).fetchone()[0]
                == "expired"
            )
        with pytest.raises(ClientError):
            media.s3("ADMIN").get_object(
                Bucket="foc-quarantine", Key=str(key), VersionId=bound.json()["object_version"]
            )


def test_exhausted_worker_leases_dead_letter_without_unsafe_publication():
    from .helpers import upload

    with make_client() as client:
        receipt, body = create_report(client)
        verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])
        iid, _ = upload(client)
        with admin() as conn:
            conn.execute(
                "UPDATE app.jobs SET state='leased',attempts=5,lease_until=now()-interval '1 second' WHERE aggregate_id=%s",
                (iid,),
            )
        with worker.connection() as conn:
            conn.execute("SELECT platform.reporting_reconcile()")
        with admin() as conn:
            assert (
                conn.execute("SELECT state FROM app.jobs WHERE aggregate_id=%s", (iid,)).fetchone()[0]
                == "dead"
            )
            assert (
                conn.execute("SELECT state FROM app.upload_intents WHERE id=%s", (iid,)).fetchone()[0]
                == "rejected"
            )


def test_unbound_storage_write_is_erased_before_orphan_acknowledgment():
    import hashlib
    from types import SimpleNamespace

    from foc_api.config import Settings
    from foc_api.identity import connection, digest

    with make_client() as client:
        receipt, body = create_report(client)
        verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])
        data = png()
        response = client.post(
            "/v1/reporter/upload-intents",
            json={"mime": "image/png", "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()},
            headers=headers(client),
        )
        assert response.status_code == 201
        iid = response.json()["id"]
        request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(settings=Settings.load())))
        with connection(request) as conn:
            intent = conn.execute(
                "SELECT platform.upload_get(%s,%s)", (digest(client.cookies.get("__Host-foc-reporter")), iid)
            ).fetchone()[0]
        version = media.put("API", "foc-quarantine", intent["quarantine_key"], data, intent["wrapped_key"])
        with admin() as conn:
            conn.execute(
                "UPDATE app.upload_intents SET expires_at=now()-interval '26 hours' WHERE id=%s", (iid,)
            )
        worker.maintain()
        with admin() as conn:
            assert conn.execute(
                "SELECT quarantine_purged FROM platform.upload_metadata WHERE intent_id=%s", (iid,)
            ).fetchone()[0]
        with pytest.raises(ClientError):
            media.s3("ADMIN").get_object(
                Bucket="foc-quarantine", Key=intent["quarantine_key"], VersionId=version
            )
