"""Actual TLS/BFF/IdP/API load; synthetic geometry-free metadata, no inference."""

import copy
import hashlib
import itertools
import json
import os
import platform
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

from psycopg.types.json import Jsonb

from scripts.fingerprint import fingerprint
from scripts.identity_setup import fixture_id
from scripts.synthetic_workflow_setup import SCENARIO
from tests.identity.helpers import real_login
from tests.synthetic_workflow.helpers import ORG_A, admin, runtime

BASE = "https://127.0.0.1:3443/v1/staff/synthetic-workflow"


def test_twenty_mfa_sessions_one_hundred_actual_api_queues_and_comparisons():
    names = [
        f"synthetic-workflow-{b}-{locale}-{width}-01-queue"
        for b, locale, width in itertools.product(
            ["chromium", "firefox", "webkit"], ["ar-EG", "en-GB"], [320, 360, 390, 1280]
        )
    ][:20]
    actors = [fixture_id(n) for n in names]
    queries, gallery = [uuid4() for _ in range(100)], [uuid4() for _ in range(50)]
    owners = {q: actors[i % 20] for i, q in enumerate(queries)}
    scenarios, clients = [], []
    try:
        with admin() as a:
            source = a.execute(
                "SELECT manifest FROM platform.synthetic_workflow_scenarios WHERE id=%s", (SCENARIO,)
            ).fetchone()[0]
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
                    query_case_id=str(query), query_revision=1, photos=[], explanations=[],
                    candidates=[{"case_id": str(c)} for c in gallery],
                )
                manifest["result_source"]["photo_refs"] = []
                manifest["cases"] = [
                    {"id": str(cid), "revision": 1, "generation": 0,
                     "registry": "missing" if cid == query else "found",
                     "claims_digest": hashlib.sha256(b"").hexdigest()}
                    for cid in [query, *gallery]
                ]
                a.execute(
                    "INSERT INTO platform.synthetic_workflow_scenarios SELECT organization_id,%s,version,instance_id,activation_epoch,%s,encode(public.digest(%s::jsonb::text,'sha256'),'hex'),expires_at,NULL FROM platform.synthetic_workflow_scenarios WHERE id=%s",
                    (sid, Jsonb(manifest), Jsonb(manifest), SCENARIO),
                )
                a.execute(
                    "INSERT INTO platform.synthetic_workflow_grants SELECT organization_id,%s,principal_id,person_id,conflict_clear,purpose,actions,expires_at,NULL FROM platform.synthetic_workflow_grants WHERE scenario_id=%s AND principal_id=%s",
                    (sid, SCENARIO, owners[query]),
                )
                with runtime(actor=owners[query]) as c:
                    c.execute(
                        "SELECT platform.sw_run_command(%s,%s,'runs',%s,1,%s)",
                        (ORG_A, query, Jsonb({"scenario_id": str(sid), "scenario_version": "fixture-2d-v1"}), uuid4()),
                    )
            # The running application worker, not this harness, leases and publishes.
            deadline = time.monotonic() + 240
            while time.monotonic() < deadline:
                states = dict(a.execute(
                    "SELECT state,count(*) FROM app.synthetic_matching_runs WHERE scenario_id=ANY(%s) GROUP BY state",
                    (scenarios,),
                ).fetchall())
                assert not (set(states) - {"queued", "running", "completed"}), states
                if states == {"completed": 100}:
                    break
                time.sleep(0.25)
            else:
                raise AssertionError("Actual synthetic worker did not finish the declared API load fixtures")
            assert a.execute(
                "SELECT count(*) FROM app.synthetic_candidate_leads WHERE scenario_id=ANY(%s)", (scenarios,)
            ).fetchone() == (5000,)
        clients = [real_login(name) for name in names]

        def measure(index):
            client, headers = clients[index % 20]
            suffix = "?organization_id=" + ORG_A
            started = time.perf_counter()
            queue = client.get(BASE + "/cases/" + str(queries[index]) + "/leads" + suffix, headers=headers)
            queue_ms = (time.perf_counter() - started) * 1000
            assert queue.status_code == 200
            rows = queue.json()
            assert len(rows["items"]) == 25 and rows["next_cursor"]
            lid = rows["items"][0]["id"]
            started = time.perf_counter()
            comparison = client.get(BASE + "/leads/" + lid + "/comparison" + suffix, headers=headers)
            comparison_ms = (time.perf_counter() - started) * 1000
            assert comparison.status_code == 200
            value = comparison.json()
            assert value["query_case_id"] == str(queries[index])
            assert value["data_class"] == "synthetic" and value["photos"] == []
            assert value["result_source"]["model_version"] is None
            return queue_ms, comparison_ms

        # One serial stream per actual staff session; 20 streams run concurrently.
        def stream(actor_index):
            return [measure(i) for i in range(actor_index, 100, 20)]

        with ThreadPoolExecutor(20) as pool:
            samples = [sample for stream_samples in pool.map(stream, range(20)) for sample in stream_samples]
        report = {"source_digest": fingerprint(), "scope": "actual_synthetic_tls_bff_api_metadata",
                  "sessions": 20, "queries": 100, "candidates_per_query": 50,
                  "requests": 200, "failed_requests": 0, "model_inference": False,
                  "host_logical_cpus": os.cpu_count(),
                  "host_memory_bytes": os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE"),
                  "host_architecture": platform.machine(), "status": "measured"}
        for position, name in enumerate(["queue", "comparison"]):
            times = sorted(s[position] for s in samples)
            target = 1000 if name == "queue" else 1500
            report[name] = {"samples": 100, "p50_ms": times[49], "p95_ms": times[94],
                            "p99_ms": times[98], "planning_target_ms": target,
                            "planning_target_met": times[94] <= target}
        Path("artifacts/raw/workflow-http-capacity.json").write_text(json.dumps(report, indent=2) + "\n")
    finally:
        for client, headers in clients:
            try:
                client.post("https://127.0.0.1:3443/identity/logout", headers=headers)
            finally:
                client.close()
        with admin() as a:
            for table in ["synthetic_candidate_leads", "synthetic_matching_runs"]:
                a.execute("DELETE FROM app." + table + " WHERE scenario_id=ANY(%s)", (scenarios,))
            a.execute("DELETE FROM platform.synthetic_workflow_grants WHERE scenario_id=ANY(%s)", (scenarios,))
            a.execute("DELETE FROM platform.synthetic_workflow_scenarios WHERE id=ANY(%s)", (scenarios,))
            a.execute("DELETE FROM app.case_grants WHERE case_id=ANY(%s)", (queries + gallery,))
            a.execute("DELETE FROM app.outbox_events WHERE case_id=ANY(%s)", (queries,))
            a.execute("DELETE FROM app.cases WHERE id=ANY(%s)", (queries + gallery,))
