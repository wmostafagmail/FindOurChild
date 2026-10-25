"""Real PostgreSQL/RLS and API projection tests with explicit identity-boundary doubles.
Actual Keycloak/BFF tests remain separately mandatory; these doubles do not count as MFA validation.
"""

from uuid import uuid4

import psycopg
import pytest
from foc_api import reporting, worker
from foc_api.identity import digest, mutation_guard
from jsonschema import Draft202012Validator, FormatChecker

from .helpers import MODERATOR, ORG, admin, cid, create_report, headers, make_client, upload, verify_reporter


@pytest.fixture
def case_context(monkeypatch):
    client = make_client()
    from .helpers import report_body

    proposed = report_body()
    proposed["reporter"]["relationship"] = "parent"
    receipt, body = create_report(client, body=proposed)
    case = cid(receipt)
    verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])

    def authenticated(request, mutation=False):
        if mutation:
            mutation_guard(request, digest("synthetic-staff-csrf"))
        return MODERATOR, "synthetic-unit-boundary-session"

    monkeypatch.setattr(reporting, "authenticate", authenticated)
    client.cookies.set("__Host-foc-csrf", "synthetic-staff-csrf", domain="127.0.0.1", path="/")
    yield client, case, receipt
    client.close()


def command(client, case, action, body, revision=1, key=None):
    h = headers(client, True)
    h["If-Match"] = '"' + str(revision) + '"'
    if key:
        h["Idempotency-Key"] = str(key)
    return client.post(f"/v1/staff/cases/{case}/{action}?organization_id={ORG}", json=body, headers=h)


def detail(client, case, org=ORG):
    return client.get(f"/v1/staff/cases/{case}?organization_id={org}")


def test_case_projection_is_closed_and_has_no_custody_or_contacts(case_context):
    client, case, _ = case_context
    response = detail(client, case)
    assert response.status_code == 200
    assert response.headers["etag"] == '"1"'
    assert not any(
        v in response.text
        for v in [
            "@synthetic.invalid",
            "receipt_hash",
            "contact_ciphertext",
            "restricted_custody",
            "wrapped_key",
        ]
    )
    spec = reporting.json.loads(reporting.CONTRACT.read_text())
    schema = {"$ref": "#/components/schemas/Case", "components": spec["components"]}
    assert not list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(response.json()))
    page = client.get("/v1/staff/cases?organization_id=" + ORG + "&limit=1")
    assert page.status_code == 200
    assert len(page.json()["items"]) <= 1
    assert "total" not in page.json()


@pytest.mark.parametrize(
    "attack",
    [
        "other_org",
        "unknown_case",
        "org_admin_without_grant",
        "revoked_grant",
        "expired_grant",
        "principal_disabled",
        "membership_expired",
        "wrong_purpose",
    ],
)
def test_staff_case_scope_denies_existence_and_cross_organization_exposure(case_context, monkeypatch, attack):
    client, case, _ = case_context
    if attack == "other_org":
        assert detail(client, case, "10000000-0000-4000-8000-000000000002").status_code == 404
        return
    if attack == "unknown_case":
        assert detail(client, uuid4()).status_code == 404
        return
    if attack == "org_admin_without_grant":
        monkeypatch.setattr(
            reporting, "authenticate", lambda *a, **kw: ("20000000-0000-4000-8000-000000000003", None)
        )
        assert detail(client, case).status_code == 404
        return
    with admin() as conn:
        if attack in ["revoked_grant", "expired_grant", "wrong_purpose"]:
            field = {
                "revoked_grant": "revoked_at=now()",
                "expired_grant": "expires_at=now()-interval '1 minute'",
                "wrong_purpose": "purpose='investigation'",
            }[attack]
            conn.execute(
                "UPDATE app.case_grants SET " + field + " WHERE case_id=%s AND permission='case.read'",
                (case,),
            )
        if attack == "principal_disabled":
            conn.execute("UPDATE app.staff_principals SET disabled_at=now() WHERE id=%s", (MODERATOR,))
        if attack == "membership_expired":
            conn.execute(
                "UPDATE app.memberships SET expires_at=now()-interval '1 second',starts_at=now()-interval '1 day' WHERE organization_id=%s AND principal_id=%s",
                (ORG, MODERATOR),
            )
        try:
            assert detail(client, case).status_code == 404
        finally:
            if attack == "principal_disabled":
                conn.execute("UPDATE app.staff_principals SET disabled_at=NULL WHERE id=%s", (MODERATOR,))
            if attack == "membership_expired":
                conn.execute(
                    "UPDATE app.memberships SET expires_at=now()+interval '30 days' WHERE organization_id=%s AND principal_id=%s",
                    (ORG, MODERATOR),
                )


def test_moderation_notes_revision_and_idempotency(case_context):
    client, case, _ = case_context
    key = uuid4()
    body = {"decision": "review", "reason": "synthetic intake reviewed", "evidence_refs": []}
    first = command(client, case, "moderation", body, key=key)
    assert first.status_code == 200
    assert first.json()["revision"] == 2
    replay = command(client, case, "moderation", body, key=key)
    assert replay.json() == first.json()
    assert command(client, case, "moderation", {**body, "reason": "changed"}, key=key).status_code == 409
    assert command(client, case, "notes", {"text": "synthetic note", "evidence_refs": []}).status_code == 412
    assert (
        command(
            client, case, "notes", {"text": "<script>SYNTHETIC</script>", "evidence_refs": []}, revision=2
        ).status_code
        == 200
    )
    result = detail(client, case).json()
    assert result["notes"][0]["text"] == "<script>SYNTHETIC</script>"
    assert result["summary"]["revision"] == 3
    with admin() as conn:
        assert (
            conn.execute(
                "SELECT count(*) FROM app.audit_events WHERE target_ref=%s AND action='case.moderation'",
                (case,),
            ).fetchone()[0]
            == 1
        )
        assert (
            conn.execute(
                "SELECT count(*) FROM app.outbox_events WHERE case_id=%s AND type='notification.requested'",
                (case,),
            ).fetchone()[0]
            == 2
        )


def test_fraudulent_parent_claim_pauses_contact_without_establishing_identity(case_context):
    client, case, _ = case_context
    assert (
        command(
            client,
            case,
            "moderation",
            {"decision": "fraud", "reason": "contradictory synthetic claim", "evidence_refs": []},
        ).status_code
        == 200
    )
    assert client.get("/v1/reporter/submission").status_code == 401
    result = detail(client, case).json()
    assert result["contact_paused"]
    assert result["summary"]["verification_status"] == "unverified"
    assert result["summary"]["lifecycle"] == "held"


def test_verification_or_scanning_incomplete_blocks_active_transition(case_context):
    client, case, _ = case_context
    assert (
        command(
            client,
            case,
            "transitions",
            {"target": "active", "reason": "unsafe shortcut", "evidence_refs": []},
        ).status_code
        == 409
    )
    assert (
        command(
            client, case, "transitions", {"target": "review", "reason": "intake", "evidence_refs": []}
        ).status_code
        == 200
    )
    client.post(
        "/v1/reporter/upload-intents",
        json={"mime": "image/png", "bytes": 10, "sha256": "0" * 64},
        headers=headers(client),
    )
    assert (
        command(
            client,
            case,
            "transitions",
            {"target": "active", "reason": "scan unavailable", "evidence_refs": []},
            2,
        ).status_code
        == 409
    )
    with admin() as conn:
        conn.execute(
            "UPDATE platform.report_submissions SET contact_verified=false WHERE case_id=%s", (case,)
        )
        conn.execute("UPDATE app.upload_intents SET state='expired' WHERE case_id=%s", (case,))
    assert (
        command(
            client,
            case,
            "transitions",
            {"target": "active", "reason": "contact unverified", "evidence_refs": []},
            2,
        ).status_code
        == 409
    )


def test_close_revokes_reporter_and_reopen_requires_supervisor(case_context):
    client, case, _ = case_context
    assert (
        command(
            client,
            case,
            "transitions",
            {"target": "closed", "reason": "synthetic withdrawn", "evidence_refs": []},
        ).status_code
        == 200
    )
    assert client.get("/v1/reporter/submission").status_code == 401
    assert (
        command(
            client, case, "transitions", {"target": "active", "reason": "bypass", "evidence_refs": []}, 2
        ).status_code
        == 409
    )
    assert (
        command(
            client,
            case,
            "transitions",
            {"target": "review", "reason": "supervisor reopening", "evidence_refs": []},
            2,
        ).status_code
        == 200
    )
    assert client.get("/v1/reporter/submission").status_code == 401


@pytest.mark.parametrize(
    "attack",
    [
        "custody_target",
        "identity_target",
        "reunited_target",
        "missing_evidence",
        "self_approval",
        "forged_csrf",
    ],
)
def test_sensitive_workflow_bypasses_have_no_effect(case_context, attack):
    client, case, _ = case_context
    if attack == "self_approval":
        response = client.post(
            "/v1/staff/reunification-plans/" + str(uuid4()) + "/approvals",
            json={"override": True},
            headers=headers(client, True),
        )
        assert response.status_code == 503
        return
    if attack == "forged_csrf":
        h = headers(client, True)
        h["X-CSRF-Token"] = "forged"
        h["If-Match"] = '"1"'
        response = client.post(
            f"/v1/staff/cases/{case}/moderation?organization_id={ORG}",
            json={"decision": "review", "reason": "bad", "evidence_refs": []},
            headers=h,
        )
        assert response.status_code == 403
        return
    if attack == "missing_evidence":
        response = command(
            client, case, "notes", {"text": "forged evidence", "evidence_refs": [str(uuid4())]}
        )
    else:
        response = command(
            client,
            case,
            "transitions",
            {
                "target": {
                    "custody_target": "custody_authorized",
                    "identity_target": "identity_confirmed",
                    "reunited_target": "reunited",
                }[attack],
                "reason": "unsafe",
                "evidence_refs": [],
            },
        )
    assert response.status_code == 422
    assert detail(client, case).json()["summary"]["revision"] == 1


def test_evidence_assertions_require_same_case_clean_object_and_supervisor(case_context):
    client, case, _ = case_context
    source = detail(client, case).json()["claims"][0]["source_id"]
    body = {
        "field": "description",
        "value": "synthetic verified statement",
        "source_id": source,
        "precision": "reported",
        "state": "verified",
        "evidence_refs": [],
    }
    assert command(client, case, "assertions", body).status_code == 404
    _iid, _ = upload(client)
    assert worker.once()
    with admin() as conn:
        evidence = conn.execute("SELECT id FROM app.evidence_documents WHERE case_id=%s", (case,)).fetchone()[
            0
        ]
    body["evidence_refs"] = [str(evidence)]
    assert command(client, case, "assertions", body).status_code == 200
    assert detail(client, case).json()["verified_assertions"][0]["verified_by"] == MODERATOR


def test_assignment_bounded_to_active_same_org_staff(case_context):
    client, case, _ = case_context
    from datetime import UTC, datetime, timedelta

    expires = (datetime.now(UTC) + timedelta(minutes=30)).isoformat()
    assert (
        command(
            client,
            case,
            "assignments",
            {
                "principal_id": "20000000-0000-4000-8000-000000000002",
                "purpose": "case_management",
                "grant_expires_at": expires,
            },
        ).status_code
        == 404
    )
    assert (
        command(
            client,
            case,
            "assignments",
            {"principal_id": MODERATOR, "purpose": "custody", "grant_expires_at": expires},
        ).status_code
        == 404
    )
    assert (
        command(
            client,
            case,
            "assignments",
            {"principal_id": MODERATOR, "purpose": "case_management", "grant_expires_at": expires},
        ).status_code
        == 200
    )


def test_media_gateway_reauthorizes_and_never_serves_original(case_context):
    client, case, _ = case_context
    _iid, _ = upload(client)
    assert worker.once()
    result = detail(client, case).json()
    mid = result["photographs"][0]["media_id"]
    evidence = result["evidence_refs"][0]
    response = client.get(f"/v1/staff/media/{mid}/content?organization_id={ORG}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.headers["cache-control"] == "no-store"
    assert client.get(f"/v1/staff/media/{evidence}/content?organization_id={ORG}").status_code == 404
    with admin() as conn:
        conn.execute(
            "UPDATE app.case_grants SET revoked_at=now() WHERE case_id=%s AND permission='media.read'",
            (case,),
        )
    assert client.get(f"/v1/staff/media/{mid}/content?organization_id={ORG}").status_code == 404


def test_runtime_cannot_mutate_claims_sessions_or_worker_results():
    import os

    with psycopg.connect(os.environ["FOC_DATABASE_URL"], autocommit=True) as conn:
        for statement in [
            "SELECT * FROM platform.report_submissions",
            "SELECT * FROM platform.report_sessions",
            "SELECT * FROM platform.safeguarding_inbox",
            "SELECT platform.media_lease()",
            "SELECT platform.reporting_audit(NULL,NULL,NULL,NULL)",
            "UPDATE app.notes SET revision=2",
            "UPDATE app.objects SET scan_status='clean'",
        ]:
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                conn.execute(statement)
        assert (
            conn.execute(
                "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='platform' AND c.relname IN ('report_submissions','report_versions','report_codes','report_sessions','reporting_commands','upload_metadata','safeguarding_inbox') AND c.relrowsecurity AND c.relforcerowsecurity"
            ).fetchone()[0]
            == 7
        )


def test_concurrent_case_writes_allow_one_revision_and_one_audit(case_context):
    import os
    from concurrent.futures import ThreadPoolExecutor

    from psycopg.types.json import Jsonb

    client, case, _ = case_context

    def write(i):
        try:
            with psycopg.connect(os.environ["FOC_DATABASE_URL"]) as conn:
                for key, value in [
                    ("principal", MODERATOR),
                    ("organization", ORG),
                    ("purpose", "case_management"),
                ]:
                    conn.execute("SELECT set_config(%s,%s,true)", ("foc." + key, value))
                body = {"text": "synthetic concurrent note " + str(i), "evidence_refs": []}
                conn.execute(
                    "SELECT platform.staff_command(%s,%s,'note',%s,%s,1,%s,%s)",
                    (ORG, case, Jsonb(body), reporting.seal(body), uuid4(), reporting.body_hash(body)),
                )
            return "passed"
        except psycopg.Error as exc:
            return exc.sqlstate

    with ThreadPoolExecutor(2) as executor:
        results = list(executor.map(write, [1, 2]))
    assert sorted(results) == ["P0412", "passed"]
    assert len(detail(client, case).json()["notes"]) == 1


def test_audit_failure_rolls_back_case_note_revision_and_outbox(case_context):
    client, case, _ = case_context
    with admin() as conn:
        before = conn.execute("SELECT count(*) FROM app.outbox_events WHERE case_id=%s", (case,)).fetchone()[
            0
        ]
        conn.execute(
            "CREATE FUNCTION platform.synthetic_reject_reporting_audit() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.action='case.note' THEN RAISE EXCEPTION 'synthetic audit failure' USING ERRCODE='23514'; END IF; RETURN NEW; END $$"
        )
        conn.execute(
            "CREATE TRIGGER synthetic_reporting_audit BEFORE INSERT ON app.audit_events FOR EACH ROW EXECUTE FUNCTION platform.synthetic_reject_reporting_audit()"
        )
        try:
            assert (
                command(client, case, "notes", {"text": "must roll back", "evidence_refs": []}).status_code
                == 503
            )
        finally:
            conn.execute("DROP TRIGGER synthetic_reporting_audit ON app.audit_events")
            conn.execute("DROP FUNCTION platform.synthetic_reject_reporting_audit()")
        assert conn.execute("SELECT revision FROM app.cases WHERE id=%s", (case,)).fetchone()[0] == 1
        assert conn.execute("SELECT count(*) FROM app.notes WHERE case_id=%s", (case,)).fetchone()[0] == 0
        assert (
            conn.execute("SELECT count(*) FROM app.outbox_events WHERE case_id=%s", (case,)).fetchone()[0]
            == before
        )
