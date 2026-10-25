import hashlib
import json
from uuid import uuid4

import pytest
from fastapi import HTTPException
from foc_api.reporting import validate

from .helpers import (
    ORG,
    ORIGIN,
    admin,
    cid,
    create_report,
    headers,
    make_client,
    public,
    report_body,
    verify_reporter,
)


@pytest.mark.parametrize("registry", ["missing", "found"])
def test_unknown_attributes_without_photo_create_independent_quarantined_reports(registry):
    with make_client() as client:
        receipt, body = create_report(client, registry)
        with admin() as conn:
            row = conn.execute(
                "SELECT registry,lifecycle,verification_status FROM app.cases WHERE id=%s", (cid(receipt),)
            ).fetchone()
            assert row == (registry, "quarantined", "unverified")
            assert (
                conn.execute(
                    "SELECT count(*) FROM app.outbox_events WHERE case_id=%s AND type='report.submitted'",
                    (cid(receipt),),
                ).fetchone()[0]
                == 1
            )
            assert (
                conn.execute(
                    "SELECT count(*) FROM app.audit_events WHERE target_ref=%s", (cid(receipt),)
                ).fetchone()[0]
                == 1
            )
        assert client.get("/v1/reporter/submission").status_code == 401
        verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])
        response = client.get("/v1/reporter/submission")
        assert response.status_code == 200
        assert response.json()["id"] == str(cid(receipt))
        assert not any(
            word in response.text
            for word in ["custody", "capability_hash", "ciphertext", "contact_hash", "scan_signature"]
        )


def test_idempotency_exact_replay_and_conflict():
    with make_client() as client:
        body = report_body()
        key = uuid4()
        first = public(client, "reports/missing", body, key)
        second = public(client, "reports/missing", body, key)
        assert first.status_code == second.status_code == 202
        assert first.json()["receipt"] == second.json()["receipt"]
        body["description"] = "changed synthetic statement"
        assert public(client, "reports/missing", body, key).status_code == 409
        with admin() as conn:
            assert (
                conn.execute(
                    "SELECT count(*) FROM platform.report_versions WHERE case_id=%s",
                    (cid(first.json()["receipt"]),),
                ).fetchone()[0]
                == 1
            )


@pytest.mark.parametrize(
    "mutation",
    [
        "unknown_field",
        "invalid_range",
        "fabricated_unknown",
        "bad_timezone",
        "production_contact",
        "unapproved_notice",
        "missing_purpose",
        "unknown_registry",
    ],
)
def test_intake_rejects_invalid_or_unapproved_payload(mutation):
    body = report_body()
    registry = "missing"
    if mutation == "unknown_field":
        body["shelter_lookup"] = "SYNTHETIC_SECRET_CANARY"
    if mutation == "invalid_range":
        body["estimated_age"].update(min_months=24, max_months=12)
    if mutation == "fabricated_unknown":
        body["birth_date"]["lower"] = "2020-01-01"
        body["birth_date"]["upper"] = "2020-01-01"
    if mutation == "bad_timezone":
        body["missing_at"]["timezone"] = "unknown/not-a-zone"
    if mutation == "production_contact":
        body["reporter"]["encrypted_transport_contact"] = "not-allowed@example.com"
    if mutation == "unapproved_notice":
        body["notice_version"] = "not-approved"
    if mutation == "missing_purpose":
        body["processing_purposes"] = []
    if mutation == "unknown_registry":
        registry = "other"
    with make_client() as client:
        response = public(client, "reports/" + registry, body)
        assert response.status_code in {404, 422}
        assert "CANARY" not in response.text


@pytest.mark.parametrize(
    "attack", ["missing_challenge", "other_browser", "expired", "wrong_origin", "cross_site", "oversized"]
)
def test_challenge_and_transport_boundaries(attack):
    with make_client() as client:
        body = report_body()
        response = client.post("/v1/public/intake-challenges", json={}, headers={"Origin": ORIGIN})
        token = response.json()["challenge"]
        h = {"Origin": ORIGIN, "Idempotency-Key": str(uuid4()), "X-Intake-Challenge": token}
        if attack == "missing_challenge":
            h.pop("X-Intake-Challenge")
        if attack == "other_browser":
            client.cookies.clear()
        if attack == "expired":
            with admin() as conn:
                conn.execute(
                    "UPDATE platform.intake_challenges SET expires_at=now()-interval '1 minute' WHERE hash=%s",
                    (hashlib.sha256(token.encode()).digest(),),
                )
        if attack == "wrong_origin":
            h["Origin"] = "https://attacker.invalid"
        if attack == "cross_site":
            h["Sec-Fetch-Site"] = "cross-site"
        if attack == "oversized":
            body["description"] = "X" * 65537
        assert client.post("/v1/public/reports/missing", json=body, headers=h).status_code in {401, 403, 413}


def test_neutral_access_request_for_unknown_and_wrong_contact():
    with make_client() as client:
        receipt, _body = create_report(client)
        responses = [
            public(client, "access-requests", {"receipt": r, "contact": "wrong@synthetic.invalid"})
            for r in [receipt, "guessed-receipt"]
        ]
        assert all(r.status_code == 202 for r in responses)
        assert all(set(r.json()) == {"request_id", "message_key"} for r in responses)
        assert responses[0].json()["message_key"] == responses[1].json()["message_key"]
        assert client.get("/v1/reporter/submission").status_code == 401


def test_code_one_use_contact_possession_not_guardianship():
    with make_client() as client:
        receipt, body = create_report(client)
        code = verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])
        response = public(client, "access-exchanges", {"receipt": receipt, "code": code})
        assert response.status_code == 401
        with admin() as conn:
            assert (
                conn.execute(
                    "SELECT verification_status FROM app.cases WHERE id=%s", (cid(receipt),)
                ).fetchone()[0]
                == "unverified"
            )
        cookie = client.cookies.get("__Host-foc-reporter")
        with admin() as conn:
            assert (
                conn.execute(
                    "SELECT hash FROM platform.report_sessions WHERE case_id=%s", (cid(receipt),)
                ).fetchone()[0]
                == hashlib.sha256(cookie.encode()).digest()
            )


@pytest.mark.parametrize(
    "attack",
    [
        "five_attempts",
        "expired_code",
        "expired_session",
        "revoked_access",
        "revoked_session",
        "paused_claimant",
        "org_suspended",
        "case_deleted",
    ],
)
def test_reporter_expiry_revocation_and_verification_fail_safely(attack):
    with make_client() as client:
        receipt, body = create_report(client)
        case = cid(receipt)
        if attack in ["five_attempts", "expired_code"]:
            public(
                client,
                "access-requests",
                {"receipt": receipt, "contact": body["reporter"]["encrypted_transport_contact"]},
            )
            if attack == "expired_code":
                with admin() as conn:
                    conn.execute(
                        "UPDATE platform.report_codes SET expires_at=now()-interval '1 minute' WHERE receipt_hash=%s",
                        (hashlib.sha256(receipt.encode()).digest(),),
                    )
            for _ in range(5):
                assert (
                    public(client, "access-exchanges", {"receipt": receipt, "code": "wrong-code"}).status_code
                    == 401
                )
            with admin() as conn:
                assert conn.execute(
                    "SELECT attempts<=5 FROM platform.report_codes WHERE receipt_hash=%s",
                    (hashlib.sha256(receipt.encode()).digest(),),
                ).fetchone()[0]
            return
        verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])
        with admin() as conn:
            if attack == "expired_session":
                conn.execute(
                    "UPDATE platform.report_sessions SET expires_at=now()-interval '1 minute' WHERE case_id=%s",
                    (case,),
                )
            if attack == "revoked_access":
                conn.execute("UPDATE app.report_access SET revoked_at=now() WHERE case_id=%s", (case,))
            if attack == "revoked_session":
                conn.execute("UPDATE platform.report_sessions SET revoked_at=now() WHERE case_id=%s", (case,))
            if attack == "paused_claimant":
                conn.execute(
                    "UPDATE platform.report_submissions SET contact_paused=true WHERE case_id=%s", (case,)
                )
            if attack == "case_deleted":
                conn.execute("UPDATE app.cases SET deleted_at=now() WHERE id=%s", (case,))
            if attack == "org_suspended":
                conn.execute(
                    "UPDATE app.organizations SET suspended_at=now() WHERE id=(SELECT organization_id FROM app.cases WHERE id=%s)",
                    (case,),
                )
            try:
                assert client.get("/v1/reporter/submission").status_code == 401
            finally:
                if attack == "org_suspended":
                    conn.execute(
                        "UPDATE app.organizations SET suspended_at=NULL WHERE id=(SELECT organization_id FROM app.cases WHERE id=%s)",
                        (case,),
                    )


def test_supplement_immutable_original_and_replay():
    with make_client() as client:
        receipt, body = create_report(client)
        verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])
        original = client.get("/v1/reporter/submission").json()["submitted_claims"]
        h = headers(client)
        supplement = {
            "claims": [
                {
                    "field": "description",
                    "value": "<script>SYNTHETIC_SECRET_CANARY</script>",
                    "source_id": original[0]["source_id"],
                }
            ],
            "evidence_refs": [],
        }
        assert client.post("/v1/reporter/supplements", json=supplement, headers=h).status_code == 202
        assert client.post("/v1/reporter/supplements", json=supplement, headers=h).status_code == 202
        result = client.get("/v1/reporter/submission").json()["submitted_claims"]
        assert result[:-1] == original
        with admin() as conn:
            assert (
                conn.execute(
                    "SELECT count(*) FROM platform.report_versions WHERE case_id=%s AND kind='supplement'",
                    (cid(receipt),),
                ).fetchone()[0]
                == 1
            )


def test_reporter_csrf_and_arbitrary_evidence_denied():
    with make_client() as client:
        receipt, body = create_report(client)
        verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])
        assert (
            client.post(
                "/v1/reporter/contact",
                json={"message": "synthetic"},
                headers={"Origin": ORIGIN, "Idempotency-Key": str(uuid4()), "X-CSRF-Token": "forged"},
            ).status_code
            == 403
        )
        assert (
            client.post(
                "/v1/reporter/supplements",
                json={"claims": [], "evidence_refs": [str(uuid4())]},
                headers=headers(client),
            ).status_code
            == 422
        )
        assert (
            client.post(
                "/v1/reporter/contact", json={"message": "synthetic"}, headers=headers(client)
            ).status_code
            == 202
        )


def test_restricted_custody_never_in_receipt_submission_or_staff_projection():
    with make_client() as client:
        body = report_body("found")
        body["restricted_custody"] = {
            "location": "SYNTHETIC_SECRET_CANARY",
            "authority_reference": "UNVERIFIED",
        }
        receipt, body = create_report(client, "found", body)
        verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])
        assert "CANARY" not in client.get("/v1/reporter/submission").text
        with admin() as conn:
            encrypted = conn.execute(
                "SELECT body_ciphertext FROM platform.intake_restricted WHERE case_id=%s", (cid(receipt),)
            ).fetchone()[0]
            assert "CANARY" not in encrypted


def test_abuse_report_does_not_lookup_receipt():
    with make_client() as client:
        response = public(
            client,
            "abuse-reports",
            {"concern": "synthetic confidential concern", "report_reference": "nonexistent"},
        )
        assert response.status_code == 202
        assert set(response.json()) == {"request_id", "message_key"}


@pytest.mark.parametrize("locale", ["ar", "en"])
def test_bilingual_safety_has_no_unapproved_emergency_numbers(locale):
    with make_client() as client:
        r = client.get("/v1/public/safety?locale=" + locale)
        assert r.status_code == 200
        assert r.json()["locale"] == locale
        assert not any(c.isdigit() for c in r.json()["text"])


def test_interval_validation_rejects_half_unknown():
    body = report_body()
    body["birth_date"]["lower"] = "2020-01-01"
    with pytest.raises(HTTPException):
        validate("MissingReport", body)


def test_private_server_draft_scope_revision_expiry_and_removal():
    with make_client() as client, make_client() as other:
        body = {
            "registry": "found",
            "revision": 0,
            "fields": {"name": "synthetic name", "contact": "draft@synthetic.invalid"},
        }
        key = uuid4()
        first = public(client, "drafts", body, key)
        assert first.status_code == 200
        assert first.json()["revision"] == 1
        assert public(client, "drafts", body, key).json() == first.json()
        assert other.get("/v1/public/drafts").json() == {"draft": None, "revision": 0}
        assert client.get("/v1/public/drafts").json()["draft"]["fields"] == body["fields"]
        assert public(client, "drafts", body).status_code == 412
        token = client.cookies.get("__Host-foc-draft")
        with admin() as conn:
            encrypted = conn.execute(
                "SELECT body_ciphertext FROM platform.report_drafts WHERE hash=%s",
                (hashlib.sha256(token.encode()).digest(),),
            ).fetchone()[0]
            assert "synthetic name" not in encrypted
        create_report(client)
        assert client.get("/v1/public/drafts").json()["draft"] is None


def test_expired_private_draft_is_not_recovered():
    with make_client() as client:
        assert (
            public(client, "drafts", {"registry": "missing", "revision": 0, "fields": {}}).status_code == 200
        )
        token = client.cookies.get("__Host-foc-draft")
        with admin() as conn:
            conn.execute(
                "UPDATE platform.report_drafts SET expires_at=now()-interval '1 second' WHERE hash=%s",
                (hashlib.sha256(token.encode()).digest(),),
            )
        assert client.get("/v1/public/drafts").json()["draft"] is None


def test_public_command_replay_cannot_change_contact_or_duplicate_concern():
    with make_client() as client:
        body = report_body()
        key = uuid4()
        assert public(client, "reports/missing", body, key).status_code == 202
        body["reporter"]["encrypted_transport_contact"] = "changed@synthetic.invalid"
        assert public(client, "reports/missing", body, key).status_code == 409
        concern = {"concern": "unique synthetic concern " + str(uuid4())}
        key = uuid4()
        with admin() as conn:
            before = conn.execute("SELECT count(*) FROM platform.safeguarding_inbox").fetchone()[0]
        assert public(client, "abuse-reports", concern, key).status_code == 202
        assert public(client, "abuse-reports", concern, key).status_code == 202
        with admin() as conn:
            assert (
                conn.execute("SELECT count(*) FROM platform.safeguarding_inbox").fetchone()[0] == before + 1
            )


def test_access_request_replay_keeps_original_verification_code():
    from pathlib import Path

    with make_client() as client:
        receipt, body = create_report(client)
        key = uuid4()
        request = {"receipt": receipt, "contact": body["reporter"]["encrypted_transport_contact"]}
        assert public(client, "access-requests", request, key).status_code == 202
        path = Path("/delivery") / (hashlib.sha256(receipt.encode()).hexdigest() + ".json")
        first = path.read_bytes()
        assert public(client, "access-requests", request, key).status_code == 202
        assert path.read_bytes() == first
        assert (
            public(
                client, "access-requests", {**request, "contact": "other@synthetic.invalid"}, key
            ).status_code
            == 409
        )


def test_local_event_dates_preserve_original_timezone_and_calendar_interval():
    with make_client() as client:
        body = report_body()
        body["missing_at"].update(
            precision="day", local_date_lower="2026-10-24", local_date_upper="2026-10-25"
        )
        receipt, body = create_report(client, body=body)
        verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])
        claims = client.get("/v1/reporter/submission").json()["submitted_claims"]
        event = json.loads(next(c["value"] for c in claims if c["field"] == "missing_at"))
        assert event["timezone"] == "Africa/Cairo"
        assert event["local_date_lower"] == "2026-10-24"
        assert event["lower"].endswith("+00:00")
        assert event["precision"] == "day"


def test_reporter_logout_revokes_replayed_session():
    with make_client() as client:
        receipt, body = create_report(client)
        verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])
        token = client.cookies.get("__Host-foc-reporter")
        assert client.post("/v1/reporter/logout", json={}, headers=headers(client)).status_code == 200
        client.cookies.set("__Host-foc-reporter", token, domain="127.0.0.1", path="/")
        assert client.get("/v1/reporter/submission").status_code == 401


@pytest.mark.parametrize("relationship", ["parent", "guardian"])
def test_contact_verified_claimants_never_gain_staff_or_custody_authority(relationship):
    with make_client() as client:
        body = report_body()
        body["reporter"]["relationship"] = relationship
        receipt, body = create_report(client, body=body)
        verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])
        assert (
            client.get("/v1/staff/cases?organization_id=10000000-0000-4000-8000-000000000001").status_code
            == 401
        )
        assert (
            client.get(
                "/v1/staff/media/"
                + str(uuid4())
                + "/content?organization_id=10000000-0000-4000-8000-000000000001"
            ).status_code
            == 401
        )
        with admin() as conn:
            assert (
                conn.execute(
                    "SELECT verification_status FROM app.cases WHERE id=%s", (cid(receipt),)
                ).fetchone()[0]
                == "unverified"
            )


def test_journal_quota_rejects_growth_without_destroying_original_claims():
    from foc_api.reporting import seal

    with make_client() as client:
        receipt, body = create_report(client)
        verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])
        case = cid(receipt)
        with admin() as conn:
            conn.execute(
                "INSERT INTO platform.report_versions(organization_id,case_id,kind,body_ciphertext) SELECT organization_id,case_id,'supplement',%s FROM platform.report_submissions CROSS JOIN generate_series(1,199) WHERE case_id=%s",
                (seal({"claims": [], "evidence_refs": []}), case),
            )
        response = client.post(
            "/v1/reporter/supplements", json={"claims": [], "evidence_refs": []}, headers=headers(client)
        )
        assert response.status_code == 422
        with admin() as conn:
            assert (
                conn.execute(
                    "SELECT count(*) FROM platform.report_versions WHERE case_id=%s", (case,)
                ).fetchone()[0]
                == 200
            )
            assert (
                conn.execute(
                    "SELECT count(*) FROM platform.report_versions WHERE case_id=%s AND kind='original'",
                    (case,),
                ).fetchone()[0]
                == 1
            )


@pytest.mark.parametrize(
    "invalid", ["known_without_date", "unknown_precision_with_date", "reversed_actual_instants"]
)
def test_temporal_uncertainty_and_offset_ordering_are_not_fabricated(invalid):
    body = report_body()
    if invalid == "known_without_date":
        body["birth_date"].update(knowledge="known", precision="day")
    if invalid == "unknown_precision_with_date":
        body["missing_at"].update(lower="2026-10-25T12:00:00Z", upper="2026-10-25T13:00:00Z")
    if invalid == "reversed_actual_instants":
        body["missing_at"].update(
            precision="interval", lower="2026-10-25T12:00:00+02:00", upper="2026-10-25T12:30:00+03:00"
        )
    with pytest.raises(HTTPException):
        validate("MissingReport", body)


def test_long_literal_and_structured_claims_match_closed_response_contracts():
    from foc_api.reporting import CONTRACT
    from jsonschema import Draft202012Validator, FormatChecker

    with make_client() as client:
        body = report_body()
        body["description"] = '"quoted synthetic description" ' * 100
        body["distinguishing_marks"] = ["synthetic mark " + str(i) + " X" * 900 for i in range(20)]
        body["general_location"]["description"] = "synthetic region " * 200
        receipt, body = create_report(client, body=body)
        verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])
        result = client.get("/v1/reporter/submission")
        assert result.status_code == 200
        spec = json.loads(CONTRACT.read_text())
        validator = Draft202012Validator(
            {"$ref": "#/components/schemas/Submission", "components": spec["components"]},
            format_checker=FormatChecker(),
        )
        assert not list(validator.iter_errors(result.json()))
        description = next(c for c in result.json()["submitted_claims"] if c["field"] == "description")
        assert description["encoding"] == "text"
        assert description["value"] == body["description"]
        assert (
            len([c for c in result.json()["submitted_claims"] if c["field"] == "distinguishing_marks"]) == 20
        )


def test_untrusted_supplement_keys_and_values_remain_literal_unverified_claims():
    with make_client() as client:
        receipt, body = create_report(client)
        verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])
        source = client.get("/v1/reporter/submission").json()["submitted_claims"][0]["source_id"]
        claims = [
            {"field": key, "value": "prototype-" + key, "source_id": source}
            for key in ["__proto__", "constructor", "toString"]
        ]
        assert (
            client.post(
                "/v1/reporter/supplements",
                json={"claims": claims, "evidence_refs": []},
                headers=headers(client),
            ).status_code
            == 202
        )
        result = client.get("/v1/reporter/submission").json()["submitted_claims"]
        for claim in claims:
            projected = next(c for c in result if c["field"] == claim["field"])
            assert projected["value"] == claim["value"]
            assert projected["encoding"] == "text"
        with admin() as conn:
            assert (
                conn.execute(
                    "SELECT verification_status FROM app.cases WHERE id=%s", (cid(receipt),)
                ).fetchone()[0]
                == "unverified"
            )


def test_signed_anonymous_browser_limits_isolate_reporters_and_bound_peer_admission():
    import hmac
    import os
    from uuid import uuid4

    from fastapi.testclient import TestClient
    from foc_api.reporting import BROWSER, anonymous_browser

    peer = str(uuid4())
    from foc_api.config import Settings
    from foc_api.main import create_app

    app = create_app(Settings.load())
    first = TestClient(app, base_url=ORIGIN, client=(peer, 50000))
    second = TestClient(app, base_url=ORIGIN, client=(peer, 50001))
    third = TestClient(app, base_url=ORIGIN, client=(peer, 50002))
    admission = hmac.digest(os.environ["FOC_CONTACT_KEY"].encode(), ("new-browser:" + peer).encode(), "sha256")
    try:
        with admin() as conn:
            conn.execute("INSERT INTO platform.intake_limits VALUES(%s,now(),98)", (admission,))
        assert first.post("/v1/public/intake-challenges", json={}, headers={"Origin": ORIGIN}).status_code == 201
        token = first.cookies[BROWSER]
        assert anonymous_browser(token)
        assert not anonymous_browser("A" * 43)
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        alias = token[:-1] + alphabet[alphabet.index(token[-1]) ^ 1]
        assert not anonymous_browser(alias)
        from datetime import UTC, datetime, timedelta
        from unittest.mock import patch

        with patch("foc_api.reporting.datetime") as clock:
            clock.now.return_value = datetime.now(UTC) + timedelta(seconds=1801)
            assert not anonymous_browser(token)
        browser_limit = hmac.digest(os.environ["FOC_CONTACT_KEY"].encode(), ("challenge:" + token).encode(), "sha256")
        with admin() as conn:
            conn.execute("INSERT INTO platform.intake_limits VALUES(%s,now(),100)", (browser_limit,))
        denied = first.post("/v1/public/intake-challenges", json={}, headers={"Origin": ORIGIN})
        assert denied.status_code == 429 and denied.headers["Retry-After"] == "600"
        assert second.post("/v1/public/intake-challenges", json={}, headers={"Origin": ORIGIN}).status_code == 201
        assert second.cookies[BROWSER] != token
        third.cookies.set(BROWSER, "A" * 43, domain="127.0.0.1", path="/")
        denied = third.post("/v1/public/intake-challenges", json={}, headers={"Origin": ORIGIN, "X-Forwarded-For": str(uuid4())})
        assert denied.status_code == 429
        assert second.get("/v1/reporter/submission").status_code == 401
        assert second.get("/v1/staff/cases?organization_id=" + ORG).status_code == 401
        receipt, body = create_report(second)
        verify_reporter(second, receipt, body["reporter"]["encrypted_transport_contact"])
        second.cookies.set(BROWSER, "A" * 43, domain="127.0.0.1", path="/")
        # Anonymous-cookie rotation/expiry cannot revoke a separately valid reporter session.
        assert second.post("/v1/reporter/contact", json={"message": "synthetic"}, headers=headers(second)).status_code == 202
    finally:
        first.close()
        second.close()
        third.close()
