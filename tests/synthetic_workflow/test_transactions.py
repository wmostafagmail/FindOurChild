import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import psycopg
import pytest
from psycopg import sql

from tests.synthetic_workflow.helpers import (
    ACTOR,
    ORG_A,
    admin,
    body,
    command,
    comparison,
    publish,
    runtime,
    scenario,
    start,
)


def test_twenty_actual_database_sessions_preserve_one_revision_and_audit():
    with scenario() as (sid, _), runtime() as conn:
        lid = publish(conn, sid)
        payload = body(comparison(conn, lid), "hold")
        conn.commit()

        def write(_):
            started = time.monotonic()
            try:
                with runtime() as c:
                    command(c, lid, "reviews", payload)
                return "passed", time.monotonic() - started
            except psycopg.Error as error:
                return error.sqlstate, time.monotonic() - started

        with ThreadPoolExecutor(20) as executor:
            results = list(executor.map(write, range(20)))
        assert [r[0] for r in results].count("passed") == 1
        assert [r[0] for r in results].count("P0412") == 19
        with admin() as a:
            assert a.execute(
                "SELECT count(*) FROM app.synthetic_investigation_events WHERE lead_id=%s", (lid,)
            ).fetchone() == (1,)
            assert a.execute(
                "SELECT count(*) FROM app.audit_events WHERE target_ref=%s AND action='synthetic.reviews'",
                (lid,),
            ).fetchone() == (1,)
        assert max(r[1] for r in results) < 15


def test_actual_process_exit_after_lease_is_recovered_and_old_fence_cannot_publish():
    with scenario() as (sid, _), runtime() as conn:
        run = start(conn, sid)
        conn.commit()
        script = "import os,psycopg; c=psycopg.connect(os.environ['FOC_WORKER_DATABASE_URL']); c.execute(\"SELECT set_config('foc.workflow_epoch',%s,true)\",(os.environ['FOC_WORKFLOW_EPOCH'],)); c.execute('SELECT platform.sw_lease()'); c.commit(); os._exit(71)"
        process = subprocess.run([sys.executable, "-c", script], capture_output=True, timeout=15, check=False)
        assert process.returncode == 71
        with admin() as a:
            state, old = a.execute(
                "SELECT state,lease_token FROM app.synthetic_matching_runs WHERE id=%s", (run["id"],)
            ).fetchone()
            assert state == "running"
            a.execute(
                "UPDATE app.synthetic_matching_runs SET lease_until=now()-interval '1 second' WHERE id=%s",
                (run["id"],),
            )
        with psycopg.connect(os.environ["FOC_WORKER_DATABASE_URL"]) as w:
            w.execute("SELECT set_config('foc.workflow_epoch',%s,false)", (os.environ["FOC_WORKFLOW_EPOCH"],))
            job = w.execute("SELECT platform.sw_lease()").fetchone()[0]
            w.commit()
            assert job["id"] == run["id"] and job["token"] != str(old)
            assert w.execute("SELECT platform.sw_finish(%s,%s,%s)", (ORG_A, run["id"], old)).fetchone() == (
                False,
            )
            assert w.execute(
                "SELECT platform.sw_finish(%s,%s,%s)", (ORG_A, run["id"], job["token"])
            ).fetchone() == (True,)
        assert conn.execute(
            "SELECT count(*) FROM app.synthetic_candidate_leads WHERE run_id=%s", (run["id"],)
        ).fetchone() == (3,)


def test_audit_outage_rolls_back_event_task_revision_command_and_outbox():
    with scenario() as (sid, _), runtime() as conn:
        lid = publish(conn, sid)
        payload = body(comparison(conn, lid), "hold")
        conn.commit()
        name = "sw_failure_" + uuid4().hex
        with admin() as a:
            a.execute(
                sql.SQL(
                    "CREATE FUNCTION platform.{}() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.target_ref={}::uuid AND NEW.action='synthetic.reviews' THEN RAISE EXCEPTION 'synthetic audit unavailable'; END IF; RETURN NEW; END $$"
                ).format(sql.Identifier(name), sql.Literal(str(lid)))
            )
            a.execute(
                sql.SQL(
                    "CREATE TRIGGER {} BEFORE INSERT ON app.audit_events FOR EACH ROW EXECUTE FUNCTION platform.{}()"
                ).format(sql.Identifier(name), sql.Identifier(name))
            )
            try:
                try:
                    with runtime() as c:
                        command(c, lid, "reviews", payload)
                except psycopg.Error:
                    pass
                else:
                    raise AssertionError("Audit outage did not fail closed")
                assert a.execute(
                    "SELECT revision FROM app.synthetic_candidate_leads WHERE id=%s", (lid,)
                ).fetchone() == (1,)
                assert a.execute(
                    "SELECT count(*) FROM app.synthetic_investigation_events WHERE lead_id=%s", (lid,)
                ).fetchone() == (0,)
                assert a.execute(
                    "SELECT count(*) FROM platform.synthetic_workflow_commands WHERE aggregate_id=%s", (lid,)
                ).fetchone() == (0,)
            finally:
                a.execute(sql.SQL("DROP TRIGGER {} ON app.audit_events").format(sql.Identifier(name)))
                a.execute(sql.SQL("DROP FUNCTION platform.{}()").format(sql.Identifier(name)))


def test_assignment_does_not_create_or_extend_case_permissions():
    from datetime import UTC, datetime, timedelta

    from tests.synthetic_workflow.helpers import PEER

    with scenario() as (sid, _), runtime() as conn:
        lid = publish(conn, sid)
        payload = body(comparison(conn, lid))
        payload.update(principal_id=PEER, expires_at=(datetime.now(UTC) + timedelta(minutes=5)).isoformat())
        with admin() as a:
            before = a.execute(
                "SELECT id,expires_at,revoked_at FROM app.case_grants WHERE principal_id=%s ORDER BY id",
                (PEER,),
            ).fetchall()
        command(conn, lid, "assignments", payload)
        conn.commit()
        with admin() as a:
            assert (
                a.execute(
                    "SELECT id,expires_at,revoked_at FROM app.case_grants WHERE principal_id=%s ORDER BY id",
                    (PEER,),
                ).fetchall()
                == before
            )


def test_no_media_grant_withholds_photo_ids_and_never_originals():
    from scripts.synthetic_workflow_setup import CANDIDATE

    with scenario() as (sid, _), runtime() as conn:
        lid = publish(conn, sid)
        conn.commit()
        with admin() as a:
            a.execute(
                "UPDATE app.case_grants SET revoked_at=now() WHERE principal_id=%s AND case_id=%s AND permission='media.read'",
                (ACTOR, CANDIDATE),
            )
            try:
                value = comparison(conn, lid)
                assert {p["side"] for p in value["photos"]} == {"query"}
                assert set(value["result_source"]["photo_refs"]) == {p["id"] for p in value["photos"]}
            finally:
                a.execute(
                    "UPDATE app.case_grants SET revoked_at=NULL WHERE principal_id=%s AND case_id=%s AND permission='media.read'",
                    (ACTOR, CANDIDATE),
                )


def test_identical_rejected_snapshot_is_held_and_cannot_be_reescalated():
    with scenario() as (sid, _), runtime() as conn:
        original = publish(conn, sid)
        payload = body(comparison(conn, original), "reject")
        key = uuid4()
        first = command(conn, original, "reviews", payload, key=key)
        conn.commit()
        assert command(conn, original, "reviews", payload, key=key) == first
        conn.commit()
        second = publish(conn, sid)
        view = comparison(conn, second)
        assert view["review_state"] == "held" and any(
            p["outcome"] == "reject" and p["same_snapshot"] for p in view["prior_reviews"]
        )
        try:
            with runtime() as c:
                command(c, second, "reviews", body(view, "escalate"))
        except psycopg.Error as error:
            assert error.sqlstate == "P0409"
        else:
            raise AssertionError("Rejected evidence was silently reused")


def test_ranked_candidates_include_metadata_only_records_without_fabricated_quality():
    with scenario() as (sid, _), runtime() as conn:
        run = start(conn, sid)
        conn.commit()
        with psycopg.connect(os.environ["FOC_WORKER_DATABASE_URL"]) as w:
            w.execute("SELECT set_config('foc.workflow_epoch',%s,false)", (os.environ["FOC_WORKFLOW_EPOCH"],))
            job = w.execute("SELECT platform.sw_lease()").fetchone()[0]
            w.commit()
            assert w.execute(
                "SELECT platform.sw_finish(%s,%s,%s)", (ORG_A, run["id"], job["token"])
            ).fetchone() == (True,)
        rows = conn.execute(
            "SELECT id,internal_rank FROM app.synthetic_candidate_leads WHERE run_id=%s ORDER BY internal_rank",
            (run["id"],),
        ).fetchall()
        assert [r[1] for r in rows] == [1, 2, 3]
        for lid, rank in rows:
            view = comparison(conn, lid)
            assert view["result_source"]["score"]["value"] is None
            assert all(
                e["case_id"] in [view["query_case_id"], view["candidate_case_id"]]
                for e in view["explanations"]
            )
            if rank > 1:
                assert not any(p["side"] == "candidate" for p in view["photos"])


@pytest.mark.parametrize("side", ["query", "candidate"])
def test_both_case_write_permissions_are_required_for_human_decisions(side):
    from scripts.synthetic_workflow_setup import CANDIDATE, QUERY

    cid = QUERY if side == "query" else CANDIDATE
    with scenario() as (sid, _), runtime() as conn:
        lid = publish(conn, sid)
        payload = body(comparison(conn, lid), "hold")
        conn.commit()
        with admin() as a:
            a.execute(
                "UPDATE app.case_grants SET revoked_at=now() WHERE principal_id=%s AND case_id=%s AND permission='case.write'",
                (ACTOR, cid),
            )
            try:
                with pytest.raises(psycopg.errors.InsufficientPrivilege), runtime() as c:
                    command(c, lid, "reviews", payload)
            finally:
                a.execute(
                    "UPDATE app.case_grants SET revoked_at=NULL WHERE principal_id=%s AND case_id=%s AND permission='case.write'",
                    (ACTOR, cid),
                )


def test_new_notification_recipient_checks_do_not_disclose_pairs_to_case_only_staff():
    with scenario() as (sid, _), runtime() as conn:
        lid = publish(conn, sid)
        command(conn, lid, "reviews", body(comparison(conn, lid), "hold"))
        conn.commit()
        with admin() as a:
            eid = a.execute(
                "SELECT id FROM app.outbox_events WHERE aggregate_id IN (SELECT id FROM app.synthetic_investigation_events WHERE lead_id=%s) AND type='synthetic.workflow.changed'",
                (lid,),
            ).fetchone()[0]
            a.execute("UPDATE app.outbox_events SET occurred_at='1980-01-01' WHERE id=%s", (eid,))
        with psycopg.connect(os.environ["FOC_WORKER_DATABASE_URL"]) as w:
            w.execute("SELECT set_config('foc.workflow_epoch',%s,false)", (os.environ["FOC_WORKFLOW_EPOCH"],))
            event = w.execute("SELECT platform.outbox_next()").fetchone()[0]
            w.commit()
            assert event["event_id"] == str(eid) and event["recipients"] == [ACTOR]
            with admin() as a:
                a.execute(
                    "UPDATE platform.synthetic_workflow_grants SET revoked_at=now() WHERE scenario_id=%s AND principal_id=%s",
                    (sid, ACTOR),
                )
            assert w.execute(
                "SELECT platform.outbox_recipient_current(%s,%s,%s)", (eid, ACTOR, event["attempt"])
            ).fetchone() == (False,)
