"""144 official TesterArmy executions against real IdP/BFF/API/private PostgreSQL.

The synthetic composition exists only in this CI runner. Never exports credentials,
raw IdP traces, owner records or fixture media. No assets or model execution.
"""

import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

import httpx
import uvicorn

from scripts.artifacts import clean_png
from scripts.dev import environment, sanitize_environment
from scripts.workflow_http_environment import private_sql_bridge
from tools.phase2e.demo_governance.run_checks import command

from .records import ROOT, digest, require, sha
from .run_checks import private_database, sources


def sanitize(report, expected, source, output):
    run = report["run"]
    titles = expected["browser_titles"]
    targets = [f"{b}-{locale}-{width}" for b in ["chromium", "firefox", "webkit"]
               for locale in ["ar-EG", "en-GB"] for width in [320, 360, 390, 1280]]
    results = run["results"]
    require(len(results) == 144 and {(r["titlePath"][-1], r["targetId"]) for r in results}
            == {(title, target) for title in titles for target in targets}, "official_v3_browser_inventory")
    traces, screenshots = [], {}
    passed = True
    for row in results:
        require(len(row["attempts"]) == 1, "browser_no_retry_masking")
        passed = passed and row["status"] == "passed"
        steps = [{"api": step["api"] if re.fullmatch(r"(?:app|browser|expect)\.[A-Za-z.]+", step["api"])
                  else "other", "status": step["status"] if step["status"] in
                  {"passed", "failed", "error", "skipped"} else "unknown"}
                 for attempt in row["attempts"] for step in attempt.get("steps", [])]
        traces.append({"test": row["titlePath"][-1], "target": row["targetId"],
                       "status": "passed" if row["status"] == "passed" else "failed", "steps": steps})
        if row["status"] == "passed":
            for artifact in row["attempts"][0].get("artifacts", []):
                if artifact.get("kind") != "screenshot" or "owner-v3-signed-out-shell" not in artifact["path"]:
                    continue
                candidate = Path(artifact["path"])
                base = (ROOT / ".e2e-owner-only-v3/results").resolve()
                path = (base / candidate).resolve()
                require(path.is_relative_to(base) and path.is_file(), "screenshot_path")
                name = sha((row["titlePath"][-1] + row["targetId"]).encode()) + ".png"
                data = clean_png(path.read_bytes())
                (output / "screenshots").mkdir(exist_ok=True)
                (output / "screenshots" / name).write_bytes(data)
                screenshots[name] = sha(data)
    (output / "traces.json").write_text(json.dumps(traces, indent=2) + "\n")
    (output / "results.json").write_text(json.dumps({"source_digest": source, "framework": "TesterArmy/e2e",
        "e2e_version": "0.21.3", "web_engine_version": "0.15.3", "total": 144,
        "passed": sum(r["status"] == "passed" for r in results), "failed": sum(r["status"] != "passed" for r in results),
        "browsers": {b: sum(r["status"] == "passed" for r in results if r["targetId"].startswith(b + "-"))
                     for b in ["chromium", "firefox", "webkit"]}, "screenshots": screenshots,
        "actual_assets": 0, "actual_owner_authorizations": 0, "actual_inference": False}, indent=2) + "\n")
    require(passed and len(screenshots) == 144, "official_v3_browser_nonpassing")


def main():
    require(os.environ.get("GITHUB_ACTIONS") == "true", "hosted_engineering_only")
    require(sys.argv[1:] in ([], ["--preflight-only"]), "closed_runner_arguments")
    preflight_only = sys.argv[1:] == ["--preflight-only"]
    expected = json.loads((ROOT / "docs/phase2e/owner-only-demo/implementation/required-tests.json").read_bytes())
    before, pg, server, thread = sources(), None, None, None
    source = digest(before)
    output = ROOT / ("artifacts/phase2e-owner-only-v3-preflight" if preflight_only else "artifacts/phase2e-owner-only-v3-browser")
    output.mkdir(parents=True, exist_ok=True)
    work = ROOT / "artifacts/raw/owner-only-v3-browser" / str(time.time_ns())
    work.mkdir(parents=True, mode=0o700)
    try:
        password = secrets.token_hex(24)
        private_env = {**os.environ, "POSTGRES_PASSWORD": password}
        pg = command(["docker", "run", "-d", "--label", "foc.scope=owner-v3-synthetic", "-e", "POSTGRES_PASSWORD",
                      "-e", "POSTGRES_DB=foc_v3_bootstrap", "-p", "127.0.0.1::5432", "--memory", "256m",
                      "--pids-limit", "128", "pgvector/pgvector:0.8.7-pg17-bookworm@sha256:ac08538c6f8b9904c33c8224c5e5706dbe760aca29db1d096972b4052c22a75d"], env=private_env).decode().strip()
        port = json.loads(command(["docker", "inspect", pg]))[0]["NetworkSettings"]["Ports"]["5432/tcp"][0]["HostPort"]
        original = f"postgresql://postgres:{password}@127.0.0.1:{port}/foc_v3_bootstrap"
        import psycopg

        deadline = time.monotonic() + 60
        while True:
            try:
                with psycopg.connect(original, connect_timeout=2):
                    break
            except psycopg.OperationalError:
                require(time.monotonic() < deadline, "v3_postgres_start")
                time.sleep(.2)
        admin, runtime = private_database(pg, original, "foc_v3_browser")
        os.environ.update(environment())
        os.environ.update(FOC_V3_TEST_ADMIN_URL=admin, FOC_V3_TEST_DATABASE_URL=runtime,
                          FOC_V3_TEST_MODE="hosted-real-postgres",
                          FOC_IDP_UPSTREAM="http://127.0.0.1:8080/realms/foc-synthetic")
        with private_sql_bridge():
            sys.path.insert(0, str(ROOT / "services/api"))
            from tests.identity.helpers import real_login
            from tests.owner_only_v3.http_harness import app, safe_claim_shape

            application = app()
            server = uvicorn.Server(uvicorn.Config(application, host="127.0.0.1", port=8001, log_level="critical", access_log=False))
            thread = threading.Thread(target=server.run, daemon=True)
            thread.start()
            until = time.monotonic() + 30
            while not server.started:
                require(thread.is_alive() and time.monotonic() < until, "v3_api_start")
                time.sleep(.1)
            with httpx.Client(trust_env=False) as client:
                require(client.get("http://127.0.0.1:8001/demo-authorization/status").status_code == 401, "real_api_closed")
            client, headers = real_login("synthetic-owner-v3-smoke")
            try:
                response = client.get("https://127.0.0.1:3443/demo-authorization/status", headers=headers)
                diagnostic = {"checkout": os.environ.get("GITHUB_SHA"), "source_digest": source,
                              "http_status": response.status_code, "claim_shape": safe_claim_shape(),
                              "fixed_denial_codes": application.state.owner_only_v3_backend.denial_codes,
                              "scope": "one_synthetic_real_identity_api_probe_not_browser_validation",
                              "official_browser_executions_counted": 0, "assets": 0, "inference": False}
                (output / "identity-preflight.json").write_text(json.dumps(diagnostic, indent=2) + "\n")
                require(response.status_code == 200, "actual_owner_identity_integration_preflight")
            finally:
                client.post("https://127.0.0.1:3443/identity/logout", headers=headers)
                client.close()
            if preflight_only:
                print(json.dumps({"identity_api_preflight": "passed", "official_browser_executions": 0}))
                return
            run_dir = ROOT / ".e2e-owner-only-v3"
            if run_dir.exists():
                shutil.move(str(run_dir), str(work / "prior-attempt"))
            env = {**sanitize_environment(os.environ), "E2E_TELEMETRY_DISABLED": "1", "DO_NOT_TRACK": "1"}
            for key in list(env):
                if key.endswith(("_TOKEN", "_SECRET", "_PASSWORD", "_KEY")) or key.startswith(("AWS_", "OPENAI_", "ANTHROPIC_")):
                    env.pop(key)
            with (work / "browser.log").open("wb") as log:
                result = subprocess.run(["./node_modules/.bin/e2e", "run", "--config", "e2e.owner-only-v3.config.ts",
                                         "--retries", "0", "--no-cache"], stdout=log, stderr=subprocess.STDOUT,
                                        env=env, timeout=5400, check=False)
            report = json.loads((run_dir / "report.json").read_bytes())
            sanitize(report, expected, source, output)
            require(result.returncode == 0 and sources() == before, "browser_exit_or_source")
        (output / "manifest.json").write_text(json.dumps({"checkout": os.environ.get("GITHUB_SHA"),
            "checkout_tree": command(["git", "rev-parse", "HEAD^{tree}"]).decode().strip(),
            "event": os.environ.get("GITHUB_EVENT_NAME"), "source_digest": source, "source_manifest": before,
            "official_framework": "e2e@0.21.3 + @e2e-dev/web@0.15.3", "executions": 144,
            "real_api_handlers": True, "real_private_postgres": True, "real_keycloak": True,
            "checkpoint_fixture": "in_process_synthetic_external_authority_adapter",
            "checkpoint_file_boundary": "separate_required_real_file_tests",
            "fixture_exposure": "explicit_generated_digest_simulation_no_image_calls",
            "private_database_credentials_in_e2e_environment": False,
            "payload_sha256": {str(p.relative_to(output)): sha(p.read_bytes())
                               for p in sorted(output.rglob("*")) if p.is_file()},
            "synthetic_principals_only": True, "real_owner_provisioned": False, "assets": 0, "inference": False}, indent=2) + "\n")
        print(json.dumps({"official_v3_browser_passed": 144, "per_browser": 48, "mandatory_skips": 0}))
    except BaseException as error:
        (output / "failure.json").write_text(json.dumps({"checkout": os.environ.get("GITHUB_SHA"),
            "source_digest": source, "error_class": type(error).__name__, "actual_assets": 0, "inference": False}) + "\n")
        raise
    finally:
        if server:
            server.should_exit = True
        if thread:
            thread.join(timeout=10)
        if pg:
            command(["docker", "rm", "--force", pg])


if __name__ == "__main__":
    main()
