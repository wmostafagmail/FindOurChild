"""Exact inventory and private diagnostics for controlled real-service outage tests."""

import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

from scripts.fingerprint import fingerprint
from scripts.test import Results

ROOT = Path(__file__).resolve().parents[1]


def main():
    result = Results()
    before = fingerprint()
    captured = io.StringIO()
    with redirect_stdout(captured), redirect_stderr(captured):
        code = pytest.main(
            [
                "tests/resilience",
                "--tb=short",
                "--cov=services/api/foc_api",
                "--cov=scripts.migrate",
                "--cov-append",
                "--cov-report=",
                "--cov-fail-under=0",
            ],
            plugins=[result],
        )
    log = ROOT / "artifacts/raw/resilience-pytest.log"
    log.write_text(captured.getvalue())
    log.chmod(0o600)
    entries = [
        {
            "id": node,
            "stages": result.reports.get(node, {}),
            "status": "passed"
            if result.reports.get(node) == {"setup": "passed", "call": "passed", "teardown": "passed"}
            else "failed",
        }
        for node in result.collected
    ]
    (ROOT / "artifacts/raw/resilience-results.json").write_text(
        json.dumps({"exit_code": int(code), "source_digest": before, "tests": entries}, indent=2) + "\n"
    )
    print(
        f"Real scanner-outage assertions: {sum(e['status'] == 'passed' for e in entries)} passed / {len(entries)} executed"
    )
    expected = json.loads((ROOT / "docs/phase1c/required-tests.json").read_text())["resilience"]
    failed = [
        {"id": t["id"], "locations": result.failures.get(t["id"], {})}
        for t in entries
        if t["status"] != "passed" and t["id"] in expected
    ]
    if failed:
        print("Sanitized failure locations: " + json.dumps(failed))
    if (
        before != fingerprint()
        or sorted(expected) != sorted(result.collected)
        or not entries
        or any(e["status"] != "passed" for e in entries)
    ):
        raise SystemExit("Mandatory resilience results incomplete or nonpassing")
    raise SystemExit(int(code))


if __name__ == "__main__":
    main()
