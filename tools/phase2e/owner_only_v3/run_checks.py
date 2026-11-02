"""Source-bound, zero-skip V3 PostgreSQL/benign-native runner; no real authority."""

import io
import json
import os
import secrets
import shutil
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from urllib.parse import quote

import psycopg
import pytest
from psycopg import sql

from tools.phase2e.demo_governance.run_checks import Results, command, prepare

from .evidence import enforce_inventory, public_report
from .records import ROOT, digest, require, sha


def sources():
    paths = []
    for base in ["tools/phase2e/owner_only_v3", "tests/owner_only_v3", "tests/owner_only_v3_browser",
                 "database/owner_only_demo", "docs/phase2e/owner-only-demo"]:
        paths += [p for p in (ROOT / base).rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    paths += [ROOT / p for p in ["services/api/foc_api/owner_only_demo.py", "services/api/foc_api/main.py",
                                "e2e.owner-only-v3.config.ts", ".github/workflows/phase2e-owner-only-v3.yml",
                                ".github/workflows/phase1a.yml", "tsconfig.e2e.json", "scripts/identity_setup.py",
                                "apps/web/app/[locale]/demo-authorization/page.tsx",
                                "apps/web/app/[locale]/demo-authorization/panel.tsx",
                                "apps/web/app/demo-authorization/[...path]/route.ts",
                                "apps/web/proxy.ts", "apps/web/app/style.css",
                                "pyproject.toml", "uv.lock", "package-lock.json"]]
    return {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in sorted(paths)}


def private_database(pg, original_url, name="foc_owner_v3"):
    with psycopg.connect(original_url, autocommit=True) as conn:
        conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    admin = original_url.rsplit("/", 1)[0] + "/" + name
    password = secrets.token_hex(24)
    with psycopg.connect(admin, autocommit=True) as conn:
        conn.execute((ROOT / "database/owner_only_demo/0001_authority.sql").read_text())
        login = "foc_v3_test_" + secrets.token_hex(6)
        conn.execute(sql.SQL("CREATE ROLE {} LOGIN NOSUPERUSER NOBYPASSRLS PASSWORD {}").format(
            sql.Identifier(login), sql.Literal(password)))
        conn.execute(sql.SQL("GRANT foc_v3_service TO {}").format(sql.Identifier(login)))
        conn.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
    host = original_url.split("@", 1)[1].rsplit("/", 1)[0]
    runtime = "postgresql://" + login + ":" + quote(password) + "@" + host + "/" + name
    return admin, runtime


def recovery(pg):
    import subprocess

    dump = command(["docker", "exec", pg, "pg_dump", "-U", "postgres", "-d", "foc_owner_v3", "--no-owner"])
    command(["docker", "exec", pg, "createdb", "-U", "postgres", "foc_owner_v3_restored"])
    subprocess.run(["docker", "exec", "-i", pg, "psql", "-U", "postgres", "-d", "foc_owner_v3_restored",
                    "-v", "ON_ERROR_STOP=1"], input=dump, capture_output=True, check=True, timeout=30)
    result = command(["docker", "exec", pg, "psql", "-XAt", "-U", "postgres", "-d", "foc_owner_v3_restored",
                      "-v", "ON_ERROR_STOP=1", "-c", ("UPDATE owner_only_demo.authority SET enabled=false; "
                      "SELECT count(*) FROM owner_only_demo.authority WHERE enabled; "
                      "SELECT count(*) FROM pg_class WHERE relnamespace='owner_only_demo'::regnamespace "
                      "AND relrowsecurity AND relforcerowsecurity;")])
    require(result.decode().splitlines()[-2:] == ["0", "3"], "v3_restore_inactive_rls")
    return {"backup_sha256": sha(dump), "restored_inactive": True, "forced_rls_tables": 3}


def main():
    from .check_source import check

    documentation = check()
    required = json.loads((ROOT / "docs/phase2e/owner-only-demo/implementation/required-tests.json").read_bytes())["python"]
    before = sources()
    source = digest(before)
    work = ROOT / "artifacts/raw/owner-only-v3" / str(time.time_ns())
    work.mkdir(parents=True, mode=0o700)
    output = ROOT / "artifacts/phase2e-owner-only-v3"
    output.mkdir(parents=True, exist_ok=True)
    result, capture, pg = Results(), io.StringIO(), None
    try:
        (work / "probe-receipts").mkdir()
        os.environ["FOC_GOVERNANCE_PROBE_EVIDENCE"] = str(work / "probe-receipts")
        pg, original, image = prepare(work)
        admin, runtime = private_database(pg, original)
        os.environ.update(FOC_V3_TEST_ADMIN_URL=admin, FOC_V3_TEST_DATABASE_URL=runtime,
                          FOC_V3_TEST_MODE="hosted-real-postgres")
        with redirect_stdout(capture), redirect_stderr(capture):
            code = pytest.main(["--confcutdir=tests/owner_only_v3", "tests/owner_only_v3", "-q", "--tb=short"],
                               plugins=[result])
        (work / "pytest.log").write_text(capture.getvalue())
        report = {"source_digest": source, "tests": [{"selector": n, "status": "passed" if
                  result.stages.get(n) == {"setup": "passed", "call": "passed", "teardown": "passed"} else "failed"}
                  for n in result.nodes], "scope": "source_only_synthetic_engineering", "actual_assets": 0,
                  "actual_owner_authorizations": 0, "actual_inference": False, "database_p95_target_ms": 1000}
        (output / "results.json").write_text(json.dumps(public_report(report), indent=2) + "\n")
        enforce_inventory(result.nodes, required, result.stages)
        require(code == 0 and before == sources(), "source_or_pytest_changed")
        restored = recovery(pg)
        probes = list((work / "probe-receipts").glob("*.json"))
        require(len(probes) == 15, "v3_native_probe_inventory")
        shutil.copytree(work / "probe-receipts", output / "probe-receipts")
        shutil.copytree(work / "native", output / "source-only-build")
        (output / "manifest.json").write_text(json.dumps({"checkout": os.environ.get("GITHUB_SHA"),
            "event": os.environ.get("GITHUB_EVENT_NAME"), "source_digest": source, "source_manifest": before,
            "design_checkpoint": "51c29c0e39424db243f30ce4d6d5ee8900ee122f", "python_tests": len(required),
            "scenario_designs": 96, "python_scenarios": 90, "browser_designs_pending_separate_run": 6,
            "native_probe_receipts": 15, "image": image, "recovery": restored,
            "documentation_checks": documentation,
            "actual_owner_provisioning": False, "actual_authorizations": 0, "assets": 0, "inference": False,
            "database_p95_target_ms": 1000, "performance_gate": "unresolved_owner_demo_exception"}, indent=2) + "\n")
        print(json.dumps({"v3_python_passed": len(required), "skipped": 0, "real_postgres": True,
                          "actual_inference": False}))
    except BaseException as error:
        (output / "failure.json").write_text(json.dumps({"checkout": os.environ.get("GITHUB_SHA"),
            "source_digest": source, "error_class": type(error).__name__, "diagnostics": result.diagnostics,
            "tests": result.stages, "scope": "source_only_failed_no_assets_no_inference"}, indent=2) + "\n")
        raise
    finally:
        (work / "pytest.log").write_text(capture.getvalue())
        (work / "pytest.log").chmod(0o600)
        rooted = os.environ.get("FOC_GOVERNANCE_ROOTED_FIXTURE")
        if rooted:
            command(["sudo", sys.executable, "-c", ("import shutil,sys;from pathlib import Path; "
                     "p=Path(sys.argv[1]);assert p.parent==Path('/var/lib/foc-governance-synthetic');shutil.rmtree(p)"), rooted])
        if pg:
            command(["docker", "rm", "--force", pg])


if __name__ == "__main__":
    main()
