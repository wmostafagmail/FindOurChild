"""Strict real-service/container reporting suite; private diagnostics, exact inventory reconciliation."""

import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

from scripts.fingerprint import fingerprint
from scripts.test import Results

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT / "artifacts/raw"
    output.mkdir(parents=True, exist_ok=True)
    results = Results()
    before = fingerprint()
    captured = io.StringIO()
    with redirect_stdout(captured), redirect_stderr(captured):
        code = pytest.main(
            [
                "tests/reporting",
                "--tb=short",
                "--cov=services/api/foc_api",
                "--cov=scripts.migrate",
                "--cov-append",
                "--cov-report=",
                "--cov-fail-under=0",
            ],
            plugins=[results],
        )
    import time

    history = output / "history" / str(time.time_ns())
    history.mkdir(parents=True, mode=0o700)
    for prior in ["reporting-results.json", "reporting-pytest.log"]:
        source = output / prior
        if source.exists():
            import shutil

            shutil.copyfile(source, history / prior)
            (history / prior).chmod(0o600)
    log = output / "reporting-pytest.log"
    log.write_text(captured.getvalue())
    log.chmod(0o600)
    entries = [
        {
            "id": node,
            "stages": results.reports.get(node, {}),
            "status": "passed"
            if results.reports.get(node) == {"setup": "passed", "call": "passed", "teardown": "passed"}
            else "failed",
        }
        for node in results.collected
    ]
    (output / "reporting-results.json").write_text(
        json.dumps({"exit_code": int(code), "source_digest": before, "tests": entries}, indent=2) + "\n"
    )
    print(
        f"Reporting assertions: {sum(t['status'] == 'passed' for t in entries)} passed / {len(entries)} executed; diagnostics private"
    )
    required = json.loads((ROOT / "docs/phase1c/required-tests.json").read_text())["python"]
    failed = [
        {"id": t["id"], "locations": results.failures.get(t["id"], {})}
        for t in entries
        if t["status"] != "passed" and t["id"] in required
    ]
    if failed:
        print("Sanitized failure locations: " + json.dumps(failed))
    if (
        before != fingerprint()
        or sorted(required) != sorted(results.collected)
        or not entries
        or any(t["status"] != "passed" for t in entries)
    ):
        raise SystemExit("Reporting inventory incomplete or nonpassing")
    raise SystemExit(int(code))


if __name__ == "__main__":
    main()
