"""Additional real-database fault and collaboration checks found during review."""

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import psycopg
import pytest
from psycopg import sql
from psycopg.types.json import Jsonb

from scripts.synthetic_workflow_setup import CANDIDATE
from tests.synthetic_workflow.helpers import (
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


@pytest.mark.parametrize("corruption", ["provider", "candidate_uuid"])
def test_corrupt_leased_fixture_never_publishes_empty_success(corruption):
    with scenario() as (sid, manifest), runtime() as conn, admin() as a:
        run = start(conn, sid)
        conn.commit()
        with psycopg.connect(os.environ["FOC_WORKER_DATABASE_URL"]) as w:
            w.execute("SELECT set_config('foc.workflow_epoch',%s,false)", (os.environ["FOC_WORKFLOW_EPOCH"],))
            job = w.execute("SELECT platform.sw_lease()").fetchone()[0]
            w.commit()
            assert job["id"] == run["id"]
            if corruption == "provider":
                manifest["provider"] = "uncleared-model"
            else:
                manifest["candidates"][0]["case_id"] = "not-a-uuid"
            a.execute(
                "UPDATE platform.synthetic_workflow_scenarios SET manifest=%s,manifest_digest=encode(sha256(convert_to(%s::jsonb::text,'UTF8')),'hex') WHERE id=%s",
                (Jsonb(manifest), Jsonb(manifest), sid),
            )
            if corruption == "provider":
                assert w.execute(
                    "SELECT platform.sw_finish(%s,%s,%s)", (ORG_A, run["id"], job["token"])
                ).fetchone() == (False,)
                w.commit()
            else:
                with pytest.raises(psycopg.Error):
                    w.execute("SELECT platform.sw_finish(%s,%s,%s)", (ORG_A, run["id"], job["token"]))
                w.rollback()
                a.execute(
                    "UPDATE app.synthetic_matching_runs SET attempts=5,lease_until=now()-interval '1 second' WHERE id=%s",
                    (run["id"],),
                )
                assert w.execute("SELECT platform.sw_lease()").fetchone() == (None,)
                w.commit()
        assert a.execute(
            "SELECT state FROM app.synthetic_matching_runs WHERE id=%s", (run["id"],)
        ).fetchone() == ("failed",)
        assert a.execute(
            "SELECT count(*) FROM app.synthetic_candidate_leads WHERE run_id=%s", (run["id"],)
        ).fetchone() == (0,)


def test_new_sealed_policy_snapshot_requires_fresh_review_and_retains_old_rejection():
    with scenario() as (old_sid, _), scenario() as (new_sid, manifest), runtime() as conn, admin() as a:
        old = publish(conn, old_sid)
        old_view = comparison(conn, old)
        command(conn, old, "reviews", body(old_view, "reject"))
        conn.commit()
        manifest["review_policy_revision"] = "synthetic-review-v2"
        a.execute(
            "UPDATE platform.synthetic_workflow_scenarios SET manifest=%s,manifest_digest=encode(sha256(convert_to(%s::jsonb::text,'UTF8')),'hex') WHERE id=%s",
            (Jsonb(manifest), Jsonb(manifest), new_sid),
        )
        new = publish(conn, new_sid)
        view = comparison(conn, new)
        assert view["snapshot_hash"] != old_view["snapshot_hash"] and view["review_state"] == "pending"
        assert any(p["outcome"] == "reject" and not p["same_snapshot"] for p in view["prior_reviews"])
        assert a.execute(
            "SELECT first_review FROM app.synthetic_candidate_leads WHERE id=%s", (new,)
        ).fetchone() == (None,)
        command(conn, new, "reviews", body(view, "hold"))
        conn.commit()
        assert comparison(conn, old)["review_state"] == "rejected"
        assert conn.execute("SELECT verification_status FROM app.cases WHERE id=%s", (QUERY,)).fetchone() == (
            "unverified",
        )


def test_concurrent_notes_conflict_then_explicit_retry_preserves_both():
    with scenario() as (sid, _), runtime() as conn:
        lid = publish(conn, sid)
        payload = body(comparison(conn, lid))
        conn.commit()

        def append(_):
            try:
                with runtime() as c:
                    command(c, lid, "notes", payload)
                return "committed"
            except psycopg.Error as error:
                return error.sqlstate

        with ThreadPoolExecutor(2) as pool:
            outcomes = list(pool.map(append, range(2)))
        assert sorted(outcomes) == ["P0412", "committed"]
        command(conn, lid, "notes", payload, expected=2)
        conn.commit()
        rows = conn.execute(
            "SELECT kind,revision,previous_hash,event_hash FROM app.synthetic_investigation_events WHERE lead_id=%s ORDER BY revision",
            (lid,),
        ).fetchall()
        assert [r[:2] for r in rows] == [("notes", 2), ("notes", 3)]
        assert rows[1][2] == rows[0][3]


@pytest.mark.parametrize("boundary", ["unknown_principal", "workflow", "membership", "query", "candidate"])
def test_assignment_expiry_never_outlives_any_underlying_authority(boundary):
    with scenario() as (sid, _), runtime() as conn, admin() as a:
        lid = publish(conn, sid)
        payload = body(comparison(conn, lid))
        payload.update(principal_id=PEER, expires_at=(datetime.now(UTC) + timedelta(minutes=5)).isoformat())
        table = {
            "workflow": "platform.synthetic_workflow_grants",
            "membership": "app.memberships",
            "query": "app.case_grants",
            "candidate": "app.case_grants",
        }.get(boundary)
        where = "organization_id=%s AND principal_id=%s"
        params = [ORG_A, PEER]
        if boundary == "workflow":
            where += " AND scenario_id=%s"
            params.append(sid)
        elif boundary in ["query", "candidate"]:
            where += " AND case_id=%s AND permission='case.read'"
            params.append(QUERY if boundary == "query" else CANDIDATE)
        previous = None
        if table:
            # These fixture predicates select one row except memberships (one per role).
            previous = a.execute(
                sql.SQL("SELECT {}expires_at FROM {} WHERE ").format(
                    sql.SQL("role," if boundary == "membership" else ""), sql.Identifier(*table.split("."))
                )
                + sql.SQL(where),
                params,
            ).fetchall()
            a.execute(
                sql.SQL("UPDATE {} SET expires_at=now()+interval '1 minute' WHERE ").format(
                    sql.Identifier(*table.split("."))
                )
                + sql.SQL(where),
                params,
            )
        else:
            payload["principal_id"] = str(uuid4())
        try:
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                command(conn, lid, "assignments", payload)
            conn.rollback()
            assert a.execute(
                "SELECT count(*) FROM app.synthetic_investigation_tasks WHERE lead_id=%s", (lid,)
            ).fetchone() == (0,)
        finally:
            if previous is not None:
                for row in previous:
                    if boundary == "membership":
                        a.execute(
                            "UPDATE app.memberships SET expires_at=%s WHERE organization_id=%s AND principal_id=%s AND role=%s",
                            (row[1], ORG_A, PEER, row[0]),
                        )
                    else:
                        assert len(previous) == 1
                        a.execute(
                            sql.SQL("UPDATE {} SET expires_at=%s WHERE ").format(
                                sql.Identifier(*table.split("."))
                            )
                            + sql.SQL(where),
                            [row[0], *params],
                        )


def test_membership_revocation_after_assignment_denies_task_access_and_action():
    with scenario() as (sid, _), runtime() as conn, admin() as a:
        lid = publish(conn, sid)
        view = comparison(conn, lid)
        first = command(conn, lid, "reviews", body(view, "escalate"))
        payload = body(view)
        payload.update(principal_id=PEER, expires_at=(datetime.now(UTC) + timedelta(minutes=5)).isoformat())
        command(conn, lid, "peer-review-requests", payload, expected=2)
        conn.commit()
        previous = a.execute(
            "SELECT role,revoked_at FROM app.memberships WHERE organization_id=%s AND principal_id=%s",
            (ORG_A, PEER),
        ).fetchall()
        a.execute(
            "UPDATE app.memberships SET revoked_at=now() WHERE organization_id=%s AND principal_id=%s",
            (ORG_A, PEER),
        )
        try:
            with runtime(actor=PEER) as peer:
                assert (
                    peer.execute(
                        "SELECT id FROM app.synthetic_investigation_tasks WHERE lead_id=%s", (lid,)
                    ).fetchall()
                    == []
                )
                with pytest.raises(psycopg.errors.InsufficientPrivilege), peer.transaction():
                    comparison(peer, lid)
                decision = body(view)
                decision.update(first_review_id=first["id"], outcome="workflow_review_complete")
                with pytest.raises(psycopg.errors.InsufficientPrivilege), peer.transaction():
                    command(peer, lid, "independent-reviews", decision, expected=3)
            assert a.execute(
                "SELECT investigation_state FROM app.synthetic_candidate_leads WHERE id=%s", (lid,)
            ).fetchone() == ("awaiting_independent_review",)
        finally:
            for role, revoked in previous:
                a.execute(
                    "UPDATE app.memberships SET revoked_at=%s WHERE organization_id=%s AND principal_id=%s AND role=%s",
                    (revoked, ORG_A, PEER, role),
                )


def test_outbox_insert_failure_rolls_back_decision_audit_and_idempotency():
    with scenario() as (sid, _), runtime() as conn, admin() as a:
        lid = publish(conn, sid)
        payload = body(comparison(conn, lid), "hold")
        conn.commit()
        name = "sw_outbox_fault_" + uuid4().hex
        a.execute(
            sql.SQL(
                "CREATE FUNCTION platform.{}() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.type='synthetic.workflow.changed' THEN RAISE EXCEPTION 'synthetic outbox unavailable'; END IF; RETURN NEW; END $$"
            ).format(sql.Identifier(name))
        )
        a.execute(
            sql.SQL(
                "CREATE TRIGGER {} BEFORE INSERT ON app.outbox_events FOR EACH ROW EXECUTE FUNCTION platform.{}()"
            ).format(sql.Identifier(name), sql.Identifier(name))
        )
        try:
            with pytest.raises(psycopg.Error):
                command(conn, lid, "reviews", payload)
            conn.rollback()
            assert a.execute(
                "SELECT revision FROM app.synthetic_candidate_leads WHERE id=%s", (lid,)
            ).fetchone() == (1,)
            assert a.execute(
                "SELECT count(*) FROM app.synthetic_investigation_events WHERE lead_id=%s", (lid,)
            ).fetchone() == (0,)
            assert a.execute(
                "SELECT count(*) FROM app.audit_events WHERE target_ref=%s AND action='synthetic.reviews'",
                (lid,),
            ).fetchone() == (0,)
            assert a.execute(
                "SELECT count(*) FROM platform.synthetic_workflow_commands WHERE aggregate_id=%s", (lid,)
            ).fetchone() == (0,)
        finally:
            a.execute(sql.SQL("DROP TRIGGER {} ON app.outbox_events").format(sql.Identifier(name)))
            a.execute(sql.SQL("DROP FUNCTION platform.{}()").format(sql.Identifier(name)))
