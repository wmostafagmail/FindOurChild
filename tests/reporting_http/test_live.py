"""Actual TLS Next BFF/API/Keycloak/PostgreSQL/storage/scanner/worker flows. No route mocks."""

import io
import json
import ssl
import time
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from PIL import Image

from scripts.reporting_code import read_code
from tests.identity.helpers import real_login
from tests.reporting.helpers import ORG, ORIGIN, report_body

ROOT = Path(__file__).resolve().parents[2]


def public(client, path, body):
    challenge = client.post(ORIGIN + "/v1/public/intake-challenges", json={}, headers={"Origin": ORIGIN})
    assert challenge.status_code == 201
    return client.post(
        ORIGIN + "/v1/public/" + path,
        json=body,
        headers={
            "Origin": ORIGIN,
            "X-Intake-Challenge": challenge.json()["challenge"],
            "Idempotency-Key": str(uuid4()),
        },
    )


@pytest.fixture(scope="module")
def flow():
    reporter = httpx.Client(
        verify=ssl.create_default_context(cafile=str(ROOT / ".runtime/tls/cert.pem")),
        trust_env=False,
        timeout=20,
    )
    staff, staff_headers = real_login("synthetic-intake-moderator")
    body = report_body()
    response = public(reporter, "reports/missing", body)
    assert response.status_code == 202
    receipt = response.json()["receipt"]
    response = public(
        reporter,
        "access-requests",
        {"receipt": receipt, "contact": body["reporter"]["encrypted_transport_contact"]},
    )
    assert response.status_code == 202
    private = ROOT / ".runtime/e2e-receipt.json"
    private.write_text(json.dumps({"receipt": receipt}))
    private.chmod(0o600)
    try:
        code = read_code()
    finally:
        private.unlink(missing_ok=True)
    response = public(reporter, "access-exchanges", {"receipt": receipt, "code": code})
    assert response.status_code == 200
    submission = reporter.get(ORIGIN + "/v1/reporter/submission")
    assert submission.status_code == 200
    yield {
        "reporter": reporter,
        "staff": staff,
        "staff_headers": staff_headers,
        "case": submission.json()["id"],
        "receipt": receipt,
        "code": code,
    }
    staff.close()
    reporter.close()


def staff_detail(flow):
    response = flow["staff"].get(
        f"{ORIGIN}/v1/staff/cases/{flow['case']}?organization_id={ORG}", headers=flow["staff_headers"]
    )
    assert response.status_code == 200
    return response


def reporter_headers(flow):
    return {
        "Origin": ORIGIN,
        "X-CSRF-Token": flow["reporter"].cookies["__Host-foc-reporter-csrf"],
        "Idempotency-Key": str(uuid4()),
    }


def staff_command(flow, action, body, revision):
    return flow["staff"].post(
        f"{ORIGIN}/v1/staff/cases/{flow['case']}/{action}?organization_id={ORG}",
        headers={**flow["staff_headers"], "Idempotency-Key": str(uuid4()), "If-Match": f'"{revision}"'},
        json=body,
    )


def test_real_bff_verified_reporter_has_only_own_submission_and_one_time_code(flow):
    submission = flow["reporter"].get(ORIGIN + "/v1/reporter/submission")
    assert submission.status_code == 200
    assert set(submission.json()) == {"id", "intake_status", "submitted_claims", "upload_statuses"}
    assert flow["reporter"].get(ORIGIN + "/v1/staff/cases?organization_id=" + ORG).status_code == 401
    assert (
        public(
            flow["reporter"], "access-exchanges", {"receipt": flow["receipt"], "code": flow["code"]}
        ).status_code
        == 401
    )
    cookie = next(c for c in flow["reporter"].cookies.jar if c.name == "__Host-foc-reporter")
    assert cookie.secure
    assert cookie.has_nonstandard_attr("HttpOnly")


def test_real_mfa_case_projection_and_tenant_denials(flow):
    detail = staff_detail(flow)
    assert detail.json()["summary"]["verification_status"] == "unverified"
    assert "@synthetic.invalid" not in detail.text
    assert "ciphertext" not in detail.text
    assert (
        flow["staff"]
        .get(
            f"{ORIGIN}/v1/staff/cases/{flow['case']}?organization_id=10000000-0000-4000-8000-000000000002",
            headers=flow["staff_headers"],
        )
        .status_code
        == 404
    )
    response = flow["staff"].post(
        f"{ORIGIN}/v1/staff/cases/{flow['case']}/notes?organization_id={ORG}",
        json={"text": "synthetic", "evidence_refs": []},
        headers={
            **flow["staff_headers"],
            "X-CSRF-Token": "forged",
            "If-Match": '"1"',
            "Idempotency-Key": str(uuid4()),
        },
    )
    assert response.status_code == 403


def test_real_two_photo_uploads_complete_through_background_worker(flow):
    import hashlib

    for color in ["green", "blue"]:
        image = io.BytesIO()
        Image.new("RGB", (16, 16), color).save(image, format="PNG")
        data = image.getvalue()
        sha = hashlib.sha256(data).hexdigest()
        response = flow["reporter"].post(
            ORIGIN + "/v1/reporter/upload-intents",
            json={"mime": "image/png", "bytes": len(data), "sha256": sha},
            headers=reporter_headers(flow),
        )
        assert response.status_code == 201
        iid = response.json()["id"]
        bound = flow["reporter"].put(
            ORIGIN + f"/v1/reporter/upload-intents/{iid}/content",
            content=data,
            headers={**reporter_headers(flow), "Content-Type": "image/png"},
        )
        assert bound.status_code == 200
        assert (
            flow["reporter"]
            .post(
                ORIGIN + f"/v1/reporter/upload-intents/{iid}/complete",
                json=bound.json(),
                headers=reporter_headers(flow),
            )
            .status_code
            == 202
        )
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        photos = staff_detail(flow).json()["photographs"]
        if len(photos) == 2 and all(p["state"] == "ready" for p in photos):
            break
        time.sleep(0.25)
    assert len(photos) == 2 and all(p["state"] == "ready" for p in photos)
    for photo in photos:
        assert photo["scan_engine"] == "ClamAV 1.5.4"
        assert photo["scan_signature"].startswith("ClamAV 1.5.4/")


def test_real_media_gateway_serves_derivative_and_denies_original(flow):
    detail = staff_detail(flow).json()
    assert len(detail["evidence_refs"]) == 2
    for original in detail["evidence_refs"]:
        assert (
            flow["staff"]
            .get(
                f"{ORIGIN}/v1/staff/media/{original}/content?organization_id={ORG}",
                headers=flow["staff_headers"],
            )
            .status_code
            == 404
        )
    mid = detail["photographs"][0]["media_id"]
    response = flow["staff"].get(
        f"{ORIGIN}/v1/staff/media/{mid}/content?organization_id={ORG}", headers=flow["staff_headers"]
    )
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["referrer-policy"] == "no-referrer"
    with Image.open(io.BytesIO(response.content)) as image:
        assert image.info == {}
        assert not image.getexif()


def test_real_moderation_notes_and_stale_revision_are_atomic(flow):
    revision = staff_detail(flow).json()["summary"]["revision"]
    assert (
        staff_command(
            flow,
            "moderation",
            {"decision": "review", "reason": "synthetic contact and intake reviewed", "evidence_refs": []},
            revision,
        ).status_code
        == 200
    )
    assert (
        staff_command(
            flow, "notes", {"text": "stale synthetic note", "evidence_refs": []}, revision
        ).status_code
        == 412
    )
    assert (
        staff_command(
            flow, "notes", {"text": "synthetic investigation note", "evidence_refs": []}, revision + 1
        ).status_code
        == 200
    )
    assert staff_detail(flow).json()["notes"][-1]["text"] == "synthetic investigation note"


def test_real_suspicious_claim_pause_revokes_reporter_without_identity_or_release(flow):
    revision = staff_detail(flow).json()["summary"]["revision"]
    assert (
        staff_command(
            flow,
            "moderation",
            {"decision": "fraud", "reason": "contradictory synthetic claimant evidence", "evidence_refs": []},
            revision,
        ).status_code
        == 200
    )
    assert flow["reporter"].get(ORIGIN + "/v1/reporter/submission").status_code == 401
    detail = staff_detail(flow).json()
    assert detail["contact_paused"]
    assert detail["summary"]["verification_status"] == "unverified"
    assert detail["summary"]["lifecycle"] == "held"
    assert (
        flow["staff"]
        .post(
            ORIGIN + "/v1/staff/reunification-plans/00000000-0000-4000-8000-000000000001/handover",
            headers=flow["staff_headers"],
            json={"override": True},
        )
        .status_code
        == 404
    )
