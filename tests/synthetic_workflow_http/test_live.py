import time
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import httpx
import pytest

from scripts.identity_setup import ORG_A
from tests.identity.helpers import real_login
from tests.synthetic_workflow.helpers import PEER, body

BASE = "https://127.0.0.1:3443/v1/staff/synthetic-workflow"


def path(value):
    return BASE + value + "?organization_id=" + ORG_A


def write(client, headers, endpoint, payload, revision=1, key=None):
    return client.post(
        path(endpoint),
        json=payload,
        headers={**headers, "If-Match": '"' + str(revision) + '"', "Idempotency-Key": str(key or uuid4())},
    )


def new_lead(client, headers):
    response = client.get(path("/status"), headers=headers)
    assert response.status_code == 200
    scenario = response.json()["scenarios"][0]
    run = write(
        client,
        headers,
        "/cases/" + scenario["query_case_id"] + "/runs",
        {"scenario_id": scenario["id"], "scenario_version": scenario["version"]},
    )
    assert run.status_code == 202
    rid = run.json()["id"]
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        status = client.get(path("/runs/" + rid), headers=headers)
        assert status.status_code == 200
        if status.json()["state"] == "completed":
            break
        assert status.json()["state"] in ["queued", "running"]
        time.sleep(0.25)
    else:
        raise AssertionError("Actual fixture worker failed to complete")
    rows = client.get(path("/cases/" + scenario["query_case_id"] + "/leads"), headers=headers)
    assert rows.status_code == 200
    lead = next(r for r in rows.json()["items"] if r["run_id"] == rid)
    view = client.get(path("/leads/" + lead["id"] + "/comparison"), headers=headers)
    assert view.status_code == 200
    return view.json()


def test_actual_bff_mfa_worker_media_and_independent_safeguarding():
    client, headers = real_login("synthetic-workflow-http")
    try:
        view = new_lead(client, headers)
        lid = view["lead_id"]
        assert view["data_class"] == "synthetic" and len(view["photos"]) == 5
        for photo in view["photos"]:
            response = client.get(
                path("/leads/" + lid + "/photos/" + photo["id"] + "/content"), headers=headers
            )
            assert (
                response.status_code == 200
                and response.content.startswith(b"\x89PNG\r\n\x1a\n")
                and response.headers["cache-control"] == "no-store"
            )
        payload = body(view, "escalate")
        first = write(client, headers, "/leads/" + lid + "/reviews", payload)
        assert first.status_code == 201
        payload = body(view)
        payload.update(principal_id=PEER, expires_at=(datetime.now(UTC) + timedelta(minutes=5)).isoformat())
        result = write(client, headers, "/leads/" + lid + "/peer-review-requests", payload, 2)
        assert result.status_code == 201
        peer, peer_headers = real_login("synthetic-workflow-peer-http")
        try:
            payload = body(view)
            payload.update(outcome="workflow_review_complete", first_review_id=first.json()["id"])
            result = write(peer, peer_headers, "/leads/" + lid + "/independent-reviews", payload, 3)
            assert result.status_code == 201
            history = peer.get(path("/leads/" + lid + "/investigation"), headers=peer_headers)
            assert history.status_code == 200 and history.json()["investigation_state"] == "workflow_reviewed"
            assert len(history.json()["events"]["items"]) == 3
            assert peer.get(path("/leads/" + lid + "/audit"), headers=peer_headers).status_code == 200
            summary = peer.get(
                "https://127.0.0.1:3443/v1/staff/cases/"
                + view["candidate_case_id"]
                + "?organization_id="
                + ORG_A,
                headers=peer_headers,
            )
            assert summary.json()["summary"]["verification_status"] == "unverified"
        finally:
            peer.close()
    finally:
        client.close()


@pytest.mark.parametrize(
    "attack",
    [
        "cross_org",
        "unknown_lead",
        "unknown_photo",
        "csrf",
        "origin",
        "stale",
        "real_model",
        "identity_confirmation",
    ],
)
def test_actual_sensitive_operations_deny_unauthorized_or_invalid_requests(attack):
    client, headers = real_login("synthetic-workflow-http-invalid-" + attack)
    try:
        view = new_lead(client, headers)
        lid = view["lead_id"]
        payload = body(view, "hold")
        if attack == "cross_org":
            response = client.get(
                path("/leads/" + lid + "/comparison").replace(ORG_A, "10000000-0000-4000-8000-000000000002"),
                headers=headers,
            )
            expected = 404
        elif attack == "unknown_lead":
            response = client.get(path("/leads/" + str(uuid4()) + "/comparison"), headers=headers)
            expected = 404
        elif attack == "unknown_photo":
            response = client.get(
                path("/leads/" + lid + "/photos/" + str(uuid4()) + "/content"), headers=headers
            )
            expected = 404
        elif attack == "real_model":
            response = write(
                client,
                headers,
                "/leads/" + lid + "/reviews",
                {**payload, "model_url": "https://synthetic.invalid/blocked"},
            )
            expected = 422
        elif attack == "identity_confirmation":
            response = write(
                client, headers, "/leads/" + lid + "/reviews", {**payload, "outcome": "confirm_identity"}
            )
            expected = 422
        else:
            modified = {**headers}
            if attack == "csrf":
                modified["x-csrf-token"] = "forged"
            if attack == "origin":
                modified["origin"] = "https://synthetic.invalid"
            response = write(
                client, modified, "/leads/" + lid + "/reviews", payload, 99 if attack == "stale" else 1
            )
            expected = 412 if attack == "stale" else 403
        assert response.status_code == expected
        assert "SYNTHETIC_SECRET_CANARY" not in response.text
        history = client.get(path("/leads/" + lid + "/investigation"), headers=headers)
        assert history.status_code == 200 and history.json()["events"]["items"] == []
    finally:
        client.close()


def test_anonymous_staff_namespace_has_no_private_projection():
    with httpx.Client(
        verify=__import__("ssl").create_default_context(cafile=".runtime/tls/cert.pem"), trust_env=False
    ) as client:
        r = client.get(path("/status"))
        assert r.status_code == 401 and "scenarios" not in r.text


@pytest.fixture(scope="module")
def operation_inventory():
    client, headers = real_login("synthetic-workflow-http-inventory")
    try:
        view = new_lead(client, headers)
        lid = view["lead_id"]
        status = client.get(path("/status"), headers=headers).json()
        s = status["scenarios"][0]
        page = client.get(path("/cases/" + s["query_case_id"] + "/leads"), headers=headers).json()
        rid = page["items"][0]["run_id"]
        p = body(view)
        assigned = {
            **p,
            "principal_id": PEER,
            "expires_at": (datetime.now(UTC) + timedelta(minutes=5)).isoformat(),
        }
        yield [
            ("GET", "/status", None),
            (
                "POST",
                "/cases/" + s["query_case_id"] + "/runs",
                {"scenario_id": s["id"], "scenario_version": s["version"]},
            ),
            ("GET", "/runs/" + rid, None),
            ("POST", "/runs/" + rid + "/cancellations", {}),
            ("GET", "/cases/" + s["query_case_id"] + "/leads", None),
            ("GET", "/leads/" + lid + "/comparison", None),
            ("GET", "/leads/" + lid + "/photos/" + view["photos"][0]["id"] + "/content", None),
            ("POST", "/leads/" + lid + "/reviews", {**p, "outcome": "hold"}),
            ("GET", "/leads/" + lid + "/investigation", None),
            ("POST", "/leads/" + lid + "/assignments", assigned),
            ("POST", "/leads/" + lid + "/notes", p),
            ("POST", "/leads/" + lid + "/peer-review-requests", assigned),
            (
                "POST",
                "/leads/" + lid + "/independent-reviews",
                {**p, "outcome": "workflow_review_complete", "first_review_id": str(uuid4())},
            ),
            ("GET", "/leads/" + lid + "/audit", None),
        ]
    finally:
        client.close()


@pytest.mark.parametrize("index", range(14), ids=[f"SW-{i:02}" for i in range(1, 15)])
@pytest.mark.parametrize("actor", ["anonymous", "other_ngo", "admin_without_case"])
def test_every_operation_has_live_negative_authorization(operation_inventory, index, actor):
    if actor == "anonymous":
        client = httpx.Client(
            verify=__import__("ssl").create_default_context(cafile=".runtime/tls/cert.pem"), trust_env=False
        )
        headers = {}
    else:
        client, headers = real_login(
            "synthetic-workflow-denied-"
            + ("other" if actor == "other_ngo" else "admin")
            + f"-SW-{index + 1:02}"
        )
    try:
        method, endpoint, payload = operation_inventory[index]
        response = (
            client.get(path(endpoint), headers=headers)
            if method == "GET"
            else write(client, headers, endpoint, payload)
        )
        assert response.status_code == (401 if actor == "anonymous" else 404)
        assert (
            "snapshot_hash" not in response.text
            and "photos" not in response.text
            and "scenarios" not in response.text
        )
    finally:
        client.close()


def test_real_queue_pagination_filters_and_actor_bound_cursors():
    client, headers = real_login("synthetic-workflow-http-pagination")
    try:
        view = new_lead(client, headers)
        endpoint = path("/cases/" + view["query_case_id"] + "/leads") + "&limit=1"
        first = client.get(endpoint, headers=headers)
        assert first.status_code == 200
        page = first.json()
        assert len(page["items"]) == 1 and page["next_cursor"]
        second = client.get(
            endpoint + "&cursor=" + __import__("urllib.parse", fromlist=["quote"]).quote(page["next_cursor"]),
            headers=headers,
        )
        assert second.status_code == 200 and second.json()["items"][0]["visible_rank"] == 2
        assert page["items"][0]["id"] != second.json()["items"][0]["id"]
        forged = client.get(endpoint + "&cursor=forged", headers=headers)
        assert forged.status_code == 422
        filtered = client.get(endpoint + "&review_state=pending", headers=headers)
        assert filtered.status_code == 200
        assert all(x["review_state"] == "pending" for x in filtered.json()["items"])
        peer, peer_headers = real_login("synthetic-workflow-peer-http-pagination")
        try:
            assert (
                peer.get(
                    endpoint
                    + "&cursor="
                    + __import__("urllib.parse", fromlist=["quote"]).quote(page["next_cursor"]),
                    headers=peer_headers,
                ).status_code
                == 412
            )
        finally:
            peer.close()
    finally:
        client.close()


def test_hidden_candidate_does_not_leave_a_visible_rank_gap():
    from scripts.identity_setup import fixture_id
    from tests.synthetic_workflow.helpers import admin

    ACTOR = fixture_id("synthetic-workflow-http-hidden-rank")

    client, headers = real_login("synthetic-workflow-http-hidden-rank")
    try:
        view = new_lead(client, headers)
        endpoint = path("/cases/" + view["query_case_id"] + "/leads") + "&limit=3"
        original = client.get(endpoint, headers=headers)
        assert original.status_code == 200
        original = original.json()["items"]
        assert len(original) == 3 and len({x["run_id"] for x in original}) == 1
        hidden_case = fixture_id("workflow-found-contradictory")
        with admin() as a:
            previous = a.execute(
                "SELECT revoked_at FROM app.case_grants WHERE organization_id=%s AND principal_id=%s AND case_id=%s AND permission='case.read'",
                (ORG_A, ACTOR, hidden_case),
            ).fetchone()
            assert previous is not None
            a.execute(
                "UPDATE app.case_grants SET revoked_at=now() WHERE organization_id=%s AND principal_id=%s AND case_id=%s AND permission='case.read'",
                (ORG_A, ACTOR, hidden_case),
            )
            try:
                response = client.get(endpoint, headers=headers)
                assert response.status_code == 200
                visible = [x for x in response.json()["items"] if x["run_id"] == original[0]["run_id"]]
                assert [x["visible_rank"] for x in visible] == [1, 2]
                assert [x["id"] for x in visible] == [original[0]["id"], original[2]["id"]]
                assert original[1]["id"] not in response.text and "total" not in response.json()
            finally:
                a.execute(
                    "UPDATE app.case_grants SET revoked_at=%s WHERE organization_id=%s AND principal_id=%s AND case_id=%s AND permission='case.read'",
                    (previous[0], ORG_A, ACTOR, hidden_case),
                )
    finally:
        client.close()


def test_actual_private_storage_outage_denies_photo_then_recovers():
    from scripts.dev import compose

    client, headers = real_login("synthetic-workflow-http-storage")
    try:
        view = new_lead(client, headers)
        endpoint = path("/leads/" + view["lead_id"] + "/photos/" + view["photos"][0]["id"] + "/content")
        before = client.get(endpoint, headers=headers)
        assert before.status_code == 200 and before.content.startswith(b"\x89PNG\r\n\x1a\n")
        compose("stop", "storage")
        try:
            denied = client.get(endpoint, headers=headers)
            assert denied.status_code == 503
            assert denied.headers["cache-control"] == "no-store"
            assert not denied.content.startswith(b"\x89PNG")
            assert all(
                value not in denied.text
                for value in ["opaque_key", "wrapped_key", "object_version", "SYNTHETIC_SECRET_CANARY"]
            )
        finally:
            compose("up", "-d", "--wait", "storage")
        # A listening storage port is not evidence that its existing volumes
        # are ready. Require actual authorized object recovery within the bound.
        deadline = time.monotonic() + 30
        while True:
            after = client.get(endpoint, headers=headers)
            if after.status_code == 200:
                break
            assert after.status_code == 503 and not after.content.startswith(b"\x89PNG")
            if time.monotonic() >= deadline:
                raise AssertionError("Actual private object did not recover within 30 seconds")
            time.sleep(0.25)
        assert after.content == before.content
    finally:
        client.close()


@pytest.mark.parametrize(
    "projection", ["status", "run", "queue", "comparison", "history", "comparison_media"]
)
def test_live_read_denies_revocation_committed_during_audit_wait(projection):
    from concurrent.futures import ThreadPoolExecutor

    from scripts.identity_setup import fixture_id
    from scripts.synthetic_workflow_setup import CANDIDATE, QUERY
    from tests.synthetic_workflow.helpers import admin

    ACTOR = fixture_id("synthetic-workflow-http-race-" + projection)

    client, headers = real_login("synthetic-workflow-http-race-" + projection)
    try:
        view = new_lead(client, headers)
        page = client.get(path("/cases/" + view["query_case_id"] + "/leads"), headers=headers).json()
        rid = next(x["run_id"] for x in page["items"] if x["id"] == view["lead_id"])
        endpoints = {
            "status": "/status",
            "run": "/runs/" + rid,
            "queue": "/cases/" + view["query_case_id"] + "/leads",
            "comparison": "/leads/" + view["lead_id"] + "/comparison",
            "history": "/leads/" + view["lead_id"] + "/investigation",
            "comparison_media": "/leads/" + view["lead_id"] + "/comparison",
        }
        marker = (
            "SELECT platform.sw_status"
            if projection == "status"
            else "SELECT platform.sw_read"
            if projection in ["comparison", "history", "comparison_media"]
            else "SELECT platform.case_list_audit"
        )
        cid = QUERY if projection in ["status", "run"] else CANDIDATE
        permission = "media.read" if projection == "comparison_media" else "case.read"
        with admin() as a, admin() as lock:
            previous = a.execute(
                "SELECT revoked_at FROM app.case_grants WHERE organization_id=%s AND principal_id=%s AND case_id=%s AND permission=%s",
                (ORG_A, ACTOR, cid, permission),
            ).fetchone()
            assert previous is not None
            lock.execute("SELECT pg_advisory_lock(hashtextextended(%s,0))", (ORG_A,))
            with ThreadPoolExecutor(1) as pool:
                future = pool.submit(client.get, path(endpoints[projection]), headers=headers)
                try:
                    deadline = time.monotonic() + 2
                    while time.monotonic() < deadline:
                        if (
                            a.execute(
                                "SELECT count(*) FROM pg_stat_activity WHERE usename='foc_api' AND wait_event='advisory' AND query LIKE %s",
                                (marker + "%",),
                            ).fetchone()[0]
                            == 1
                        ):
                            break
                        time.sleep(0.02)
                    else:
                        raise AssertionError("Actual API read did not reach its audit boundary")
                    a.execute(
                        "UPDATE app.case_grants SET revoked_at=now() WHERE organization_id=%s AND principal_id=%s AND case_id=%s AND permission=%s",
                        (ORG_A, ACTOR, cid, permission),
                    )
                    lock.execute("SELECT pg_advisory_unlock(hashtextextended(%s,0))", (ORG_A,))
                    response = future.result(timeout=10)
                    if permission == "media.read":
                        assert response.status_code == 200
                        value = response.json()
                        forbidden = {p["id"] for p in view["photos"] if p["side"] == "candidate"}
                        assert len(value["photos"]) == 3 and all(
                            p["side"] == "query" for p in value["photos"]
                        )
                        assert all(pid not in response.text for pid in forbidden)
                        assert set(value["result_source"]["photo_refs"]) == {p["id"] for p in value["photos"]}
                        photo = client.get(
                            path(
                                "/leads/" + view["lead_id"] + "/photos/" + next(iter(forbidden)) + "/content"
                            ),
                            headers=headers,
                        )
                        assert photo.status_code == 404 and not photo.content.startswith(b"\x89PNG")
                    else:
                        assert response.status_code == 404
                        assert all(
                            secret not in response.text
                            for secret in [
                                view["lead_id"],
                                "snapshot_hash",
                                "photos",
                                "SYNTHETIC_SECRET_CANARY",
                            ]
                        )
                finally:
                    lock.execute("SELECT pg_advisory_unlock_all()")
                    future.result(timeout=10)
                    a.execute(
                        "UPDATE app.case_grants SET revoked_at=%s WHERE organization_id=%s AND principal_id=%s AND case_id=%s AND permission=%s",
                        (previous[0], ORG_A, ACTOR, cid, permission),
                    )
        assert client.get(path(endpoints[projection]), headers=headers).status_code == 200
    finally:
        client.close()


def test_actual_api_denies_bad_migration_ledger_then_recovers():
    from tests.synthetic_workflow.helpers import admin

    client, headers = real_login("synthetic-workflow-http-ledger")
    try:
        assert client.get(path("/status"), headers=headers).status_code == 200
        with admin() as a:
            previous = a.execute(
                "SELECT sha256 FROM platform.migrations WHERE version='0032_synthetic_ledger_guard'"
            ).fetchone()
            assert previous is not None
            a.execute(
                "UPDATE platform.migrations SET sha256=repeat('0',64) WHERE version='0032_synthetic_ledger_guard'"
            )
            try:
                denied = client.get(path("/status"), headers=headers)
                assert denied.status_code == 503 and "scenarios" not in denied.text
            finally:
                a.execute(
                    "UPDATE platform.migrations SET sha256=%s WHERE version='0032_synthetic_ledger_guard'",
                    previous,
                )
        assert client.get(path("/status"), headers=headers).status_code == 200
    finally:
        client.close()


def test_actual_cgroup_oom_recovers_fenced_worker_lease_without_duplicate_results():
    import json
    import os
    import subprocess
    from pathlib import Path
    from urllib.parse import urlparse

    import psycopg
    from foc_api.synthetic_workflow import epoch

    from scripts.dev import compose
    from tests.synthetic_workflow.helpers import admin, runtime, scenario, start

    def docker(*args, timeout=60):
        return subprocess.run(
            ["docker", *args], capture_output=True, text=True, check=True, timeout=timeout
        ).stdout.strip()

    compose("stop", "worker")
    name = "foc-synthetic-oom-" + uuid4().hex
    env_file = Path(".runtime") / (name + ".env")
    created = False
    try:
        with scenario() as (sid, _), runtime() as c, admin() as a:
            run = start(c, sid)
            c.commit()
            networks = json.loads(
                docker("inspect", "--format", "{{json .NetworkSettings.Networks}}", "foc-phase1a-worker-1")
            )
            assert len(networks) == 1
            network = next(iter(networks))
            assert docker("network", "inspect", "--format", "{{.Internal}}", network) == "true"
            image = docker("inspect", "--format", "{{.Image}}", "foc-phase1a-worker-1")
            assert image.startswith("sha256:")
            descriptor = os.open(env_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w") as stream:
                stream.write(
                    "FOC_DATABASE_URL="
                    + os.environ["FOC_WORKER_DATABASE_URL"]
                    + "\nFOC_WORKFLOW_EPOCH="
                    + os.environ["FOC_WORKFLOW_EPOCH"]
                    + "\nFOC_DATA_CLASS=synthetic\nFOC_EXPECTED_RUN="
                    + run["id"]
                    + "\n"
                )
            script = "import os,psycopg; from foc_api.synthetic_workflow import epoch; c=psycopg.connect(os.environ['FOC_DATABASE_URL']); epoch(c); job=c.execute('SELECT platform.sw_lease()').fetchone()[0]; assert job['id']==os.environ['FOC_EXPECTED_RUN']; c.commit(); print('synthetic lease committed',flush=True); chunks=[]\nfor _ in range(64): chunks.append(b'x'*(16*1024*1024))"
            docker(
                "create",
                "--name",
                name,
                "--network",
                network,
                "--memory",
                "384m",
                "--memory-swap",
                "384m",
                "--cpus",
                "1",
                "--pids-limit",
                "32",
                "--read-only",
                "--tmpfs",
                "/tmp:size=16m",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges:true",
                "--env-file",
                str(env_file),
                "--entrypoint",
                "python",
                image,
                "-c",
                script,
            )
            created = True
            process = subprocess.run(
                ["docker", "start", "--attach", name], capture_output=True, text=True, timeout=60, check=False
            )
            state = json.loads(docker("inspect", "--format", "{{json .State}}", name))
            assert process.returncode == 137 and state["OOMKilled"] is True and state["ExitCode"] == 137
            assert "synthetic lease committed" in process.stdout
            row = a.execute(
                "SELECT state,lease_token FROM app.synthetic_matching_runs WHERE id=%s", (run["id"],)
            ).fetchone()
            assert row[0] == "running" and row[1] is not None
            old_token = row[1]
            a.execute(
                "UPDATE app.synthetic_matching_runs SET lease_until=now()-interval '1 second' WHERE id=%s",
                (run["id"],),
            )
            host = urlparse(os.environ["FOC_DATABASE_URL"])
            with psycopg.connect(
                os.environ["FOC_WORKER_DATABASE_URL"], host=host.hostname, port=host.port
            ) as w:
                epoch(w)
                new = w.execute("SELECT platform.sw_lease()").fetchone()[0]
                w.commit()
                assert new["id"] == run["id"] and new["token"] != str(old_token)
                epoch(w)
                assert w.execute(
                    "SELECT platform.sw_finish(%s,%s,%s)", (ORG_A, run["id"], old_token)
                ).fetchone() == (False,)
                assert w.execute(
                    "SELECT platform.sw_finish(%s,%s,%s)", (ORG_A, run["id"], new["token"])
                ).fetchone() == (True,)
            assert a.execute(
                "SELECT count(*) FROM app.synthetic_candidate_leads WHERE run_id=%s", (run["id"],)
            ).fetchone() == (3,)
    finally:
        if created:
            docker("rm", "--force", name)
        env_file.unlink(missing_ok=True)
        compose("up", "-d", "worker")
