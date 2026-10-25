"""Strict Phase 2A suites with private diagnostics and exact reviewed inventories."""

import io
import json
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

from scripts.fingerprint import fingerprint
from scripts.results_gate import python_gate
from scripts.test import Results

ROOT = Path(__file__).resolve().parents[1]


def main():
    lane = sys.argv[1] if len(sys.argv) > 1 else "research"
    if lane not in {"research", "research_http"}:
        raise SystemExit("unknown research lane")
    output = ROOT / "artifacts/raw"
    output.mkdir(parents=True, exist_ok=True)
    captured = io.StringIO()
    results = Results()
    started = time.time()
    before = fingerprint()
    with redirect_stdout(captured), redirect_stderr(captured):
        code = pytest.main(
            [
                "tests/" + lane,
                "--tb=short",
                "--cov=services/api/foc_api",
                "--cov=scripts.migrate",
                "--cov-append",
                "--cov-report=",
                "--cov-fail-under=0",
            ],
            plugins=[results],
        )
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
    report = {
        "exit_code": int(code),
        "source_digest": before,
        "started_at": started,
        "finished_at": time.time(),
        "tests": entries,
    }
    target = output / (lane + "-results.json")
    if target.exists():
        history = output / "history" / str(time.time_ns())
        history.mkdir(parents=True, mode=0o700)
        (history / target.name).write_bytes(target.read_bytes())
    target.write_text(json.dumps(report, indent=2) + "\n")
    target.chmod(0o600)
    log = output / (lane + "-pytest.log")
    log.write_text(captured.getvalue())
    log.chmod(0o600)
    print(
        f"{lane}: {sum(t['status'] == 'passed' for t in entries)} passed / {len(entries)} executed; diagnostics private"
    )
    expected = json.loads((ROOT / "docs/phase2a/required-tests.json").read_text())[lane]
    python_gate(report, {"python": expected}, fingerprint())
    if before != fingerprint():
        raise SystemExit("source changed during validation")


if __name__ == "__main__":
    main()
