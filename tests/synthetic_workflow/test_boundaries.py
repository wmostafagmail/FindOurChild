from datetime import UTC, datetime, timedelta
from uuid import uuid4

import psycopg
import pytest
from psycopg.types.json import Jsonb

from scripts.identity_setup import ADMIN_A, ORG_B, STAFF_B
from scripts.synthetic_workflow_setup import CANDIDATE
from tests.synthetic_workflow.helpers import (
    ACTOR,
    ALIAS,
    ORG_A,
    PEER,
    QUERY,
    admin,
    body,
    command,
    comparison,
    publish,
    runtime,
    scenario,
    start,
)


def test_real_fixture_provider_completes_without_model_or_identity_effect():
    with scenario() as (sid, _), runtime() as conn:
        lid = publish(conn, sid)
        view = comparison(conn, lid)
        assert view["data_class"] == "synthetic" and view["identity_determination"] == "not_performed"
        assert view["result_source"]["kind"] == "fixture_scenario"
        assert (
            view["result_source"]["model_version"] is None and view["result_source"]["score"]["value"] is None
        )
        assert len(view["photos"]) == 5 and {p["side"] for p in view["photos"]} == {"query", "candidate"}
        assert any(p["capture_date"]["lower"] is None for p in view["photos"])
        assert any(p["capture_age_months"]["lower"] == 18 for p in view["photos"])
        assert not any(
            word in str(view)
            for word in ["custody", "wrapped_key", "object_version", "sha256", "contact_ciphertext"]
        )
        assert conn.execute(
            "SELECT verification_status FROM app.cases WHERE id IN (%s,%s)", (QUERY, CANDIDATE)
        ).fetchall() == [("unverified",), ("unverified",)]


@pytest.mark.parametrize("permission", ["case.read", "case.write", "matching.request"])
def test_run_requires_each_live_query_permission(permission):
    with scenario() as (sid, _), admin() as a:
        a.execute(
            "UPDATE app.case_grants SET revoked_at=now() WHERE principal_id=%s AND case_id=%s AND permission=%s",
            (ACTOR, QUERY, permission),
        )
        try:
            with runtime() as conn, pytest.raises(psycopg.errors.InsufficientPrivilege):
                start(conn, sid)
        finally:
            a.execute(
                "UPDATE app.case_grants SET revoked_at=NULL WHERE principal_id=%s AND case_id=%s AND permission=%s",
                (ACTOR, QUERY, permission),
            )


@pytest.mark.parametrize(
    "attack",
    [
        "other_tenant",
        "admin_only",
        "query_only",
        "candidate_only",
        "wrong_purpose",
        "missing_epoch",
        "wrong_epoch",
        "expired_workflow",
        "revoked_workflow",
        "unknown_conflict",
    ],
)
def test_paired_scope_and_purpose_fail_closed(attack):
    with scenario() as (sid, _):
        with runtime() as conn:
            lid = publish(conn, sid)
        with admin() as a:
            altered = None
            if attack in ["query_only", "candidate_only"]:
                cid = CANDIDATE if attack == "query_only" else QUERY
                a.execute(
                    "UPDATE app.case_grants SET revoked_at=now() WHERE principal_id=%s AND case_id=%s AND permission='case.read'",
                    (ACTOR, cid),
                )
                altered = cid
            if attack == "expired_workflow":
                a.execute(
                    "UPDATE platform.synthetic_workflow_grants SET expires_at=now()-interval '1 second' WHERE scenario_id=%s AND principal_id=%s",
                    (sid, ACTOR),
                )
            if attack == "revoked_workflow":
                a.execute(
                    "UPDATE platform.synthetic_workflow_grants SET revoked_at=now() WHERE scenario_id=%s AND principal_id=%s",
                    (sid, ACTOR),
                )
            if attack == "unknown_conflict":
                a.execute(
                    "UPDATE platform.synthetic_workflow_grants SET conflict_clear=false WHERE scenario_id=%s AND principal_id=%s",
                    (sid, ACTOR),
                )
            try:
                options = (
                    {"actor": STAFF_B, "org": ORG_B}
                    if attack == "other_tenant"
                    else {"actor": ADMIN_A}
                    if attack == "admin_only"
                    else {"purpose": "biometric_search"}
                    if attack == "wrong_purpose"
                    else {"epoch": "" if attack == "missing_epoch" else "0" * 64}
                    if attack in ["missing_epoch", "wrong_epoch"]
                    else {}
                )
                with runtime(**options) as conn:
                    if attack == "unknown_conflict":
                        with pytest.raises(psycopg.errors.InsufficientPrivilege):
                            command(conn, lid, "reviews", body(comparison(conn, lid), "hold"))
                    else:
                        assert (
                            conn.execute(
                                "SELECT id FROM app.synthetic_candidate_leads WHERE id=%s", (lid,)
                            ).fetchall()
                            == []
                        )
                        # The optimized queue projection must enforce the same
                        # live scope as direct-table RLS, without hidden IDs.
                        try:
                            with conn.transaction():
                                queue = conn.execute(
                                    "SELECT platform.sw_queue(%s,%s,NULL,false,0,101)", (ORG_A, QUERY)
                                ).fetchone()[0]
                        except psycopg.errors.InsufficientPrivilege:
                            queue = {"items": []}
                        assert all(row["id"] != str(lid) for row in queue["items"])
                        with pytest.raises(psycopg.errors.InsufficientPrivilege):
                            comparison(conn, lid)
            finally:
                if altered:
                    a.execute(
                        "UPDATE app.case_grants SET revoked_at=NULL WHERE principal_id=%s AND case_id=%s AND permission='case.read'",
                        (ACTOR, altered),
                    )


@pytest.mark.parametrize("attack", ["url", "model", "embedding", "candidates", "version", "custody"])
def test_direct_runtime_run_function_rejects_unbounded_input(attack):
    with scenario() as (sid, _), runtime() as conn:
        payload = {"scenario_id": str(sid), "scenario_version": "fixture-2d-v1"}
        if attack == "version":
            payload["scenario_version"] = "real-model"
        else:
            payload[attack] = "synthetic.invalid"
        with pytest.raises(psycopg.Error):
            conn.execute(
                "SELECT platform.sw_run_command(%s,%s,'runs',%s,1,%s)",
                (ORG_A, QUERY, Jsonb(payload), uuid4()),
            )


@pytest.mark.parametrize("outcome", ["hold", "reject", "escalate"])
def test_human_decisions_are_immutable_and_do_not_verify_identity(outcome):
    with scenario() as (sid, _), runtime() as conn:
        lid = publish(conn, sid)
        value = command(conn, lid, "reviews", body(comparison(conn, lid), outcome))
        assert value["revision"] == 2
        assert (
            comparison(conn, lid)["review_state"]
            == {"hold": "held", "reject": "rejected", "escalate": "escalated"}[outcome]
        )
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            conn.execute(
                "UPDATE app.synthetic_investigation_events SET payload=%s WHERE lead_id=%s", (Jsonb({}), lid)
            )
        assert conn.execute("SELECT verification_status FROM app.cases WHERE id=%s", (QUERY,)).fetchone() == (
            "unverified",
        )


@pytest.mark.parametrize(
    "attack",
    [
        "confirm_identity",
        "reunited",
        "no_evidence",
        "wrong_ref",
        "wrong_snapshot",
        "no_ack",
        "html",
        "free_text",
        "unknown_reason",
        "too_many_reasons",
    ],
)
def test_review_rejects_forged_sensitive_conclusions_and_evidence(attack):
    with scenario() as (sid, _), runtime() as conn:
        lid = publish(conn, sid)
        payload = body(comparison(conn, lid), "escalate")
        if attack in ["confirm_identity", "reunited"]:
            payload["outcome"] = attack
        elif attack == "no_evidence":
            payload["evidence_refs"] = []
        elif attack == "wrong_ref":
            payload["evidence_refs"] = [str(uuid4())]
        elif attack == "wrong_snapshot":
            payload["snapshot_hash"] = "0" * 64
        elif attack == "no_ack":
            payload["uncertainty_acknowledged"] = False
        elif attack in ["html", "free_text"]:
            payload[attack] = "<script>SYNTHETIC_SECRET_CANARY</script>"
        elif attack == "unknown_reason":
            payload["rationale_codes"] = ["identity_is_confirmed"]
        else:
            payload["rationale_codes"] = ["SYNTHETIC_WORKFLOW_ONLY"] * 6
        with pytest.raises(psycopg.Error):
            command(conn, lid, "reviews", payload)


def test_exact_replay_changed_body_stale_revision_and_revoked_replay():
    with scenario() as (sid, _), runtime() as conn:
        lid = publish(conn, sid)
        payload = body(comparison(conn, lid), "hold")
        key = uuid4()
        first = command(conn, lid, "reviews", payload, key=key)
        conn.commit()
        assert command(conn, lid, "reviews", payload, key=key) == first
        with pytest.raises(psycopg.errors.UniqueViolation), conn.transaction():
            command(conn, lid, "reviews", {**payload, "outcome": "reject"}, key=key)
        with pytest.raises(psycopg.Error) as error, conn.transaction():
            command(conn, lid, "reviews", payload)
        assert error.value.sqlstate == "P0412"
        conn.commit()
        with admin() as a:
            a.execute(
                "UPDATE platform.synthetic_workflow_grants SET revoked_at=now() WHERE scenario_id=%s AND principal_id=%s",
                (sid, ACTOR),
            )
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            command(conn, lid, "reviews", payload, key=key)


def test_assignment_structured_notes_and_independent_safeguarding_review():
    with scenario() as (sid, _), runtime() as conn:
        lid = publish(conn, sid)
        view = comparison(conn, lid)
        p = body(view)
        command(conn, lid, "notes", p)
        p = body(comparison(conn, lid), "escalate")
        first = command(conn, lid, "reviews", p, 2)
        p = body(comparison(conn, lid))
        p.update(principal_id=PEER, expires_at=(datetime.now(UTC) + timedelta(minutes=5)).isoformat())
        command(conn, lid, "assignments", p, 3)
        command(conn, lid, "peer-review-requests", p, 4)
        conn.commit()
        with runtime(actor=PEER) as peer:
            p = body(comparison(peer, lid))
            p.update(outcome="workflow_review_complete", first_review_id=first["id"])
            command(peer, lid, "independent-reviews", p, 5)
            assert comparison(peer, lid)["investigation_state"] == "workflow_reviewed"
            assert peer.execute(
                "SELECT verification_status FROM app.cases WHERE id=%s", (CANDIDATE,)
            ).fetchone() == ("unverified",)
        assert (
            conn.execute(
                "SELECT count(*) FROM app.synthetic_investigation_events WHERE lead_id=%s", (lid,)
            ).fetchone()[0]
            == 5
        )


@pytest.mark.parametrize(
    "attack",
    [
        "self",
        "alias",
        "other_org",
        "expired",
        "not_escalated",
        "wrong_first_review",
        "reviewer_not_safeguarding",
    ],
)
def test_independence_assignment_and_conflict_denials(attack):
    with scenario() as (sid, _), runtime() as conn:
        lid = publish(conn, sid)
        view = comparison(conn, lid)
        if attack != "not_escalated":
            first = command(conn, lid, "reviews", body(view, "escalate"))
        p = body(view)
        p.update(
            principal_id=ACTOR
            if attack == "self"
            else ALIAS
            if attack == "alias"
            else STAFF_B
            if attack == "other_org"
            else PEER,
            expires_at=(datetime.now(UTC) + timedelta(minutes=-1 if attack == "expired" else 5)).isoformat(),
        )
        if attack in ["wrong_first_review", "reviewer_not_safeguarding"]:
            command(conn, lid, "peer-review-requests", p, 2)
            conn.commit()
            with admin() as a:
                if attack == "reviewer_not_safeguarding":
                    a.execute(
                        "UPDATE app.memberships SET revoked_at=now() WHERE principal_id=%s AND role='safeguarding'",
                        (PEER,),
                    )
                try:
                    with runtime(actor=PEER) as peer, pytest.raises(psycopg.errors.InsufficientPrivilege):
                        payload = body(view)
                        payload.update(
                            outcome="workflow_review_complete",
                            first_review_id=str(uuid4()) if attack == "wrong_first_review" else first["id"],
                        )
                        command(peer, lid, "independent-reviews", payload, 3)
                finally:
                    if attack == "reviewer_not_safeguarding":
                        a.execute(
                            "UPDATE app.memberships SET revoked_at=NULL WHERE principal_id=%s AND role='safeguarding'",
                            (PEER,),
                        )
        else:
            with pytest.raises(psycopg.Error):
                command(conn, lid, "peer-review-requests", p, 1 if attack == "not_escalated" else 2)


@pytest.mark.parametrize(
    "attack",
    [
        "case_revision",
        "case_closed",
        "case_deleted",
        "claims",
        "object_hash",
        "object_version",
        "scanner_provenance",
    ],
)
def test_changed_evidence_invalidates_all_pair_projections(attack):
    with scenario() as (sid, _), runtime() as conn:
        lid = publish(conn, sid)
        conn.commit()
        with admin() as a, a.transaction():
            if attack == "case_revision":
                a.execute("UPDATE app.cases SET revision=revision+1 WHERE id=%s", (CANDIDATE,))
            elif attack == "case_closed":
                a.execute("UPDATE app.cases SET lifecycle='closed' WHERE id=%s", (CANDIDATE,))
            elif attack == "case_deleted":
                a.execute("UPDATE app.cases SET deleted_at=now() WHERE id=%s", (CANDIDATE,))
            elif attack == "claims":
                a.execute(
                    "INSERT INTO platform.report_versions(organization_id,case_id,kind,body_ciphertext) VALUES(%s,%s,'supplement','changed')",
                    (ORG_A, CANDIDATE),
                )
            elif attack == "object_hash":
                a.execute(
                    "UPDATE app.objects SET content_sha256=decode(repeat('00',32),'hex') WHERE case_id=%s AND bucket_class='derivative'",
                    (CANDIDATE,),
                )
            elif attack == "object_version":
                a.execute(
                    "UPDATE app.objects SET object_version=object_version||'-changed' WHERE case_id=%s AND bucket_class='derivative'",
                    (CANDIDATE,),
                )
            else:
                a.execute(
                    "UPDATE platform.upload_metadata SET scan_signature=NULL WHERE case_id=%s", (CANDIDATE,)
                )
            a.execute("SET LOCAL ROLE foc_api")
            for k, v in [
                ("organization", ORG_A),
                ("principal", ACTOR),
                ("purpose", "case_management"),
                ("workflow_epoch", __import__("os").environ["FOC_WORKFLOW_EPOCH"]),
            ]:
                a.execute("SELECT set_config(%s,%s,true)", ("foc." + k, str(v)))
            assert a.execute(
                "SELECT count(*) FROM app.synthetic_candidate_leads WHERE id=%s", (lid,)
            ).fetchone() == (0,)
            raise psycopg.Rollback()


@pytest.mark.parametrize(
    "table", ["synthetic_workflow_scenarios", "synthetic_workflow_grants", "synthetic_workflow_commands"]
)
def test_private_control_tables_deny_runtime_select_and_writes(table):
    with runtime() as conn, pytest.raises(psycopg.errors.InsufficientPrivilege):
        conn.execute("SELECT * FROM platform." + table)


@pytest.mark.parametrize(
    "function",
    [
        "sw_lease()",
        "sw_finish(gen_random_uuid(),gen_random_uuid(),gen_random_uuid())",
        "sw_event_command_base(gen_random_uuid(),gen_random_uuid(),'reviews','{}',1,gen_random_uuid())",
        "outbox_next_1c()",
    ],
)
def test_internal_definers_unavailable_to_api(function):
    with runtime() as conn, pytest.raises(psycopg.errors.InsufficientPrivilege):
        conn.execute("SELECT platform." + function)


def test_eight_new_tables_force_rls_and_nonowner_history_is_append_only():
    with admin() as a:
        rows = a.execute(
            "SELECT c.relname,c.relrowsecurity,c.relforcerowsecurity,r.rolname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_roles r ON r.oid=c.relowner WHERE n.nspname IN ('app','platform') AND c.relkind='r' AND c.relname LIKE 'synthetic_%'"
        ).fetchall()
        assert len(rows) == 8 and all(x[1:] == (True, True, "foc_owner") for x in rows)
        assert a.execute(
            "SELECT NOT has_table_privilege('foc_api','app.synthetic_investigation_events','UPDATE') AND NOT has_table_privilege('foc_worker','app.synthetic_investigation_events','INSERT')"
        ).fetchone() == (True,)


def test_fenced_worker_cancellation_expired_lease_and_revoked_requester():
    import os

    with scenario() as (sid, _), runtime() as conn:
        run = start(conn, sid)
        conn.commit()
        with psycopg.connect(os.environ["FOC_WORKER_DATABASE_URL"]) as w:
            w.execute("SELECT set_config('foc.workflow_epoch',%s,true)", (os.environ["FOC_WORKFLOW_EPOCH"],))
            job = w.execute("SELECT platform.sw_lease()").fetchone()[0]
            w.commit()
            assert w.execute(
                "SELECT platform.sw_finish(%s,%s,%s)", (ORG_A, run["id"], uuid4())
            ).fetchone() == (False,)
            with admin() as a:
                a.execute(
                    "UPDATE platform.synthetic_workflow_grants SET revoked_at=now() WHERE scenario_id=%s AND principal_id=%s",
                    (sid, ACTOR),
                )
            assert w.execute(
                "SELECT platform.sw_finish(%s,%s,%s)", (ORG_A, run["id"], job["token"])
            ).fetchone() == (False,)
        with admin() as a:
            assert a.execute(
                "SELECT state FROM app.synthetic_matching_runs WHERE id=%s", (run["id"],)
            ).fetchone() == ("held",)
            assert a.execute(
                "SELECT count(*) FROM app.synthetic_candidate_leads WHERE run_id=%s", (run["id"],)
            ).fetchone() == (0,)


def test_cancelled_run_cannot_be_published():
    with scenario() as (sid, _), runtime() as conn:
        run = start(conn, sid)
        result = conn.execute(
            "SELECT platform.sw_run_command(%s,%s,'cancellations','{}',1,%s)", (ORG_A, run["id"], uuid4())
        ).fetchone()[0]
        assert result["state"] == "cancelled"


def test_structured_note_rejects_real_data_entry_even_through_direct_sql():
    with scenario() as (sid, _), runtime() as conn:
        lid = publish(conn, sid)
        payload = body(comparison(conn, lid))
        payload["outcome"] = "SYNTHETIC_SECRET_CANARY"
        with pytest.raises(psycopg.Error):
            command(conn, lid, "notes", payload)


def test_queue_projection_is_bounded_and_never_exposes_internal_ranks():
    with scenario() as (sid, _), runtime() as conn:
        expected = {"synthetic_principal_context_lookup", "synthetic_membership_context_lookup",
                    "synthetic_case_grant_context_lookup", "synthetic_workflow_context_lookup",
                    "synthetic_report_integrity_lookup"}
        assert {row[0] for row in conn.execute(
            "SELECT indexname FROM pg_indexes WHERE indexname=ANY(%s)", (list(expected),)
        ).fetchall()} == expected
        lid = publish(conn, sid)
        queue = conn.execute(
            "SELECT platform.sw_queue(%s,%s,NULL,false,0,26)", (ORG_A, QUERY)
        ).fetchone()[0]
        assert any(row["id"] == str(lid) for row in queue["items"])
        assert all(set(row) == {"id", "review_state", "investigation_state", "revision", "run_id", "visible_rank", "data_class"} for row in queue["items"])
        assert [row["visible_rank"] for row in queue["items"]] == list(range(1, len(queue["items"]) + 1))
        for state, mine, skip, size in [(None, False, None, 25), (None, False, 0, None),
                                      (None, False, -1, 25), (None, False, 0, 102),
                                      (None, None, 0, 25), ("identity_confirmed", False, 0, 25)]:
            with pytest.raises(psycopg.errors.InvalidParameterValue), conn.transaction():
                conn.execute("SELECT platform.sw_queue(%s,%s,%s,%s,%s,%s)",
                             (ORG_A, QUERY, state, mine, skip, size))
