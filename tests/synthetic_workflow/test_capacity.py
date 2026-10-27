"""Declared synthetic database envelope; timings are not face-model or browser latency."""

import copy
import hashlib
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb

from scripts.fingerprint import fingerprint
from scripts.synthetic_workflow_setup import SCENARIO
from tests.synthetic_workflow.helpers import ACTOR, ORG_A, admin, runtime


def test_one_hundred_queries_fifty_candidates_twenty_real_rls_sessions():
    queries = [uuid4() for _ in range(100)]
    gallery = [uuid4() for _ in range(50)]
    scenarios = []
    actors = [uuid4() for _ in range(20)]
    owners = {query: actors[i % 20] for i, query in enumerate(queries)}
    try:
        with admin() as a:
            source = a.execute(
                "SELECT manifest FROM platform.synthetic_workflow_scenarios WHERE id=%s", (SCENARIO,)
            ).fetchone()[0]
            for actor in actors:
                a.execute(
                    "INSERT INTO app.staff_principals(id,oidc_issuer,oidc_subject) VALUES(%s,'https://synthetic.invalid',%s)",
                    (actor, str(actor)),
                )
                a.execute(
                    "INSERT INTO app.memberships(organization_id,principal_id,role,expires_at) VALUES(%s,%s,'reviewer',now()+interval '1 hour')",
                    (ORG_A, actor),
                )
            for cid, registry in [(q, "missing") for q in queries] + [(g, "found") for g in gallery]:
                a.execute(
                    "INSERT INTO app.cases(organization_id,id,registry,lifecycle) VALUES(%s,%s,%s,'review')",
                    (ORG_A, cid, registry),
                )
                for actor in [owners[cid]] if cid in owners else actors:
                    for permission in ["case.read", "case.write", "matching.request"]:
                        a.execute(
                            "INSERT INTO app.case_grants(organization_id,case_id,principal_id,permission,purpose,granted_by,expires_at) VALUES(%s,%s,%s,%s,'case_management',%s,now()+interval '1 hour')",
                            (ORG_A, cid, actor, permission, actor),
                        )
            for query in queries:
                sid = uuid4()
                scenarios.append(sid)
                manifest = copy.deepcopy(source)
                manifest.update(
                    query_case_id=str(query),
                    query_revision=1,
                    photos=[],
                    explanations=[],
                    candidates=[{"case_id": str(c)} for c in gallery],
                )
                manifest["result_source"]["photo_refs"] = []
                manifest["cases"] = [
                    {
                        "id": str(cid),
                        "revision": 1,
                        "generation": 0,
                        "registry": "missing" if cid == query else "found",
                        "claims_digest": hashlib.sha256(b"").hexdigest(),
                    }
                    for cid in [query, *gallery]
                ]
                a.execute(
                    "INSERT INTO platform.synthetic_workflow_scenarios SELECT organization_id,%s,version,instance_id,activation_epoch,%s,encode(public.digest(%s::jsonb::text,'sha256'),'hex'),expires_at,NULL FROM platform.synthetic_workflow_scenarios WHERE id=%s",
                    (sid, Jsonb(manifest), Jsonb(manifest), SCENARIO),
                )
                a.execute(
                    "INSERT INTO platform.synthetic_workflow_grants SELECT organization_id,%s,%s,%s,conflict_clear,purpose,actions,expires_at,NULL FROM platform.synthetic_workflow_grants WHERE scenario_id=%s AND principal_id=%s",
                    (sid, owners[query], owners[query], SCENARIO, ACTOR),
                )
                with runtime(actor=owners[query]) as c:
                    c.execute(
                        "SELECT platform.sw_run_command(%s,%s,'runs',%s,1,%s)",
                        (
                            ORG_A,
                            query,
                            Jsonb({"scenario_id": str(sid), "scenario_version": "fixture-2d-v1"}),
                            uuid4(),
                        ),
                    )
        with psycopg.connect(os.environ["FOC_WORKER_DATABASE_URL"]) as w:
            w.execute("SELECT set_config('foc.workflow_epoch',%s,false)", (os.environ["FOC_WORKFLOW_EPOCH"],))
            for _ in queries:
                job = w.execute("SELECT platform.sw_lease()").fetchone()[0]
                w.commit()
                assert job
                assert w.execute(
                    "SELECT platform.sw_finish(%s,%s,%s)", (ORG_A, job["id"], job["token"])
                ).fetchone() == (True,)
                w.commit()

        def read(query):
            with runtime(actor=owners[query]) as c:
                started = time.perf_counter()
                rows = c.execute(
                    "SELECT internal_rank FROM app.synthetic_candidate_leads WHERE organization_id=%s AND query_case_id=%s ORDER BY internal_rank",
                    (ORG_A, query),
                ).fetchall()
                elapsed = (time.perf_counter() - started) * 1000
                assert [r[0] for r in rows] == list(range(1, 51))
                return elapsed

        with ThreadPoolExecutor(20) as pool:
            timings = sorted(pool.map(read, queries))
        report = {
            "source_digest": fingerprint(),
            "scope": "synthetic_database_retrieval_only",
            "sessions": 20,
            "queries": 100,
            "candidates_per_query": 50,
            "model_inference": False,
            "p50_ms": timings[49],
            "p95_ms": timings[94],
            "p99_ms": timings[98],
            "database_p95_within_planning_1000ms": timings[94] <= 1000,
            "status": "measured",
        }
        Path("artifacts/raw/workflow-capacity.json").write_text(json.dumps(report, indent=2) + "\n")
    finally:
        with admin() as a:
            for table in ["synthetic_candidate_leads", "synthetic_matching_runs"]:
                a.execute("DELETE FROM app." + table + " WHERE scenario_id=ANY(%s)", (scenarios,))
            a.execute(
                "DELETE FROM platform.synthetic_workflow_grants WHERE scenario_id=ANY(%s)", (scenarios,)
            )
            a.execute("DELETE FROM platform.synthetic_workflow_scenarios WHERE id=ANY(%s)", (scenarios,))
            a.execute("DELETE FROM app.case_grants WHERE case_id=ANY(%s)", (queries + gallery,))
            a.execute("DELETE FROM app.outbox_events WHERE case_id=ANY(%s)", (queries,))
            a.execute("DELETE FROM app.cases WHERE id=ANY(%s)", (queries + gallery,))
            a.execute(
                "DELETE FROM platform.synthetic_workflow_commands WHERE principal_id=ANY(%s)", (actors,)
            )
            a.execute("DELETE FROM app.memberships WHERE principal_id=ANY(%s)", (actors,))
            a.execute("DELETE FROM app.staff_principals WHERE id=ANY(%s)", (actors,))
