import copy
import os
from contextlib import contextmanager
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb

from scripts.identity_setup import ORG_A, fixture_id
from scripts.synthetic_workflow_setup import QUERY, SCENARIO

ACTOR = fixture_id("synthetic-workflow-http")
PEER = fixture_id("synthetic-workflow-peer-http")
ALIAS = fixture_id("synthetic-workflow-alias-http")


@contextmanager
def admin():
    with psycopg.connect(os.environ["FOC_DATABASE_ADMIN_URL"], autocommit=True) as conn:
        assert conn.execute("SELECT data_class FROM platform.environment").fetchone() == ("synthetic",)
        yield conn


@contextmanager
def runtime(sid=None, actor=ACTOR, org=ORG_A, purpose="case_management", epoch=None):
    with psycopg.connect(os.environ["FOC_DATABASE_URL"]) as conn:
        for key, value in [
            ("organization", org),
            ("principal", actor),
            ("purpose", purpose),
            ("workflow_epoch", os.environ["FOC_WORKFLOW_EPOCH"] if epoch is None else epoch),
        ]:
            conn.execute("SELECT set_config(%s,%s,false)", ("foc." + key, str(value)))
        yield conn


@contextmanager
def scenario():
    sid = uuid4()
    with admin() as conn:
        source = conn.execute(
            "SELECT manifest FROM platform.synthetic_workflow_scenarios WHERE organization_id=%s AND id=%s",
            (ORG_A, SCENARIO),
        ).fetchone()[0]
        manifest = copy.deepcopy(source)
        conn.execute(
            "INSERT INTO platform.synthetic_workflow_scenarios SELECT organization_id,%s,version,instance_id,activation_epoch,manifest,manifest_digest,expires_at,revoked_at FROM platform.synthetic_workflow_scenarios WHERE organization_id=%s AND id=%s",
            (sid, ORG_A, SCENARIO),
        )
        conn.execute(
            "INSERT INTO platform.synthetic_workflow_grants SELECT organization_id,%s,principal_id,person_id,conflict_clear,purpose,actions,expires_at,revoked_at FROM platform.synthetic_workflow_grants WHERE organization_id=%s AND scenario_id=%s",
            (sid, ORG_A, SCENARIO),
        )
    try:
        yield sid, manifest
    finally:
        with admin() as conn:
            conn.execute(
                "DELETE FROM app.synthetic_investigation_assignments WHERE organization_id=%s AND task_id IN (SELECT id FROM app.synthetic_investigation_tasks WHERE lead_id IN (SELECT id FROM app.synthetic_candidate_leads WHERE scenario_id=%s))",
                (ORG_A, sid),
            )
            conn.execute(
                "DELETE FROM app.synthetic_investigation_tasks WHERE lead_id IN (SELECT id FROM app.synthetic_candidate_leads WHERE scenario_id=%s)",
                (sid,),
            )
            conn.execute(
                "UPDATE app.synthetic_candidate_leads SET first_review=NULL WHERE scenario_id=%s", (sid,)
            )
            conn.execute(
                "DELETE FROM app.synthetic_investigation_events WHERE lead_id IN (SELECT id FROM app.synthetic_candidate_leads WHERE scenario_id=%s)",
                (sid,),
            )
            conn.execute("DELETE FROM app.synthetic_candidate_leads WHERE scenario_id=%s", (sid,))
            conn.execute("DELETE FROM app.synthetic_matching_runs WHERE scenario_id=%s", (sid,))
            conn.execute("DELETE FROM platform.synthetic_workflow_grants WHERE scenario_id=%s", (sid,))
            conn.execute("DELETE FROM platform.synthetic_workflow_scenarios WHERE id=%s", (sid,))


def start(conn, sid, key=None):
    return conn.execute(
        "SELECT platform.sw_run_command(%s,%s,'runs',%s,1,%s)",
        (ORG_A, QUERY, Jsonb({"scenario_id": str(sid), "scenario_version": "fixture-2d-v1"}), key or uuid4()),
    ).fetchone()[0]


def publish(conn, sid):
    run = start(conn, sid)
    conn.commit()
    # Real PostgreSQL worker procedures, executed using the actual least-privilege worker role.
    with psycopg.connect(os.environ["FOC_WORKER_DATABASE_URL"]) as worker:
        worker.execute("SELECT set_config('foc.workflow_epoch',%s,true)", (os.environ["FOC_WORKFLOW_EPOCH"],))
        job = worker.execute("SELECT platform.sw_lease()").fetchone()[0]
        worker.commit()
        worker.execute("SELECT set_config('foc.workflow_epoch',%s,true)", (os.environ["FOC_WORKFLOW_EPOCH"],))
        assert job and job["id"] == run["id"]
        assert worker.execute(
            "SELECT platform.sw_finish(%s,%s,%s)", (ORG_A, run["id"], job["token"])
        ).fetchone()[0]
    row = conn.execute(
        "SELECT id FROM app.synthetic_candidate_leads WHERE run_id=%s ORDER BY internal_rank", (run["id"],)
    ).fetchone()
    assert row
    return row[0]


def comparison(conn, lid):
    return conn.execute("SELECT platform.sw_read(%s,%s,'comparison')", (ORG_A, lid)).fetchone()[0]


def body(view, outcome=None):
    result = {
        "snapshot_hash": view["snapshot_hash"],
        "uncertainty_acknowledged": True,
        "rationale_codes": ["SYNTHETIC_WORKFLOW_ONLY"],
        "evidence_refs": [],
    }
    if outcome is not None:
        result["outcome"] = outcome
        if outcome != "hold":
            result["evidence_refs"] = [view["explanations"][0]["source_ref"]]
    return result


def command(conn, lid, operation, payload, expected=1, key=None):
    return conn.execute(
        "SELECT platform.sw_event_command(%s,%s,%s,%s,%s,%s)",
        (ORG_A, lid, operation, Jsonb(payload), expected, key or uuid4()),
    ).fetchone()[0]
