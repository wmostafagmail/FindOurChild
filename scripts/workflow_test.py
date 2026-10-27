"""Exact inventory runner; unit/real-PG and live HTTP are separately reported lanes."""

import io
import json
import os
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
    lane = sys.argv[1] if len(sys.argv) > 1 else "synthetic_workflow"
    if lane not in {"synthetic_workflow", "synthetic_workflow_http"}:
        raise SystemExit("Unknown workflow lane")
    if lane.endswith("_http"):
        from scripts.dev import environment

        os.environ.update(environment())
        os.environ["FOC_IDP_UPSTREAM"] = "http://127.0.0.1:8080/realms/foc-synthetic"
    result = Results()
    digest = fingerprint()
    started = time.time()
    captured = io.StringIO()
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
            plugins=[result],
        )
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
    report = {
        "started_at": started,
        "finished_at": time.time(),
        "source_digest": digest,
        "exit_code": int(code),
        "tests": entries,
    }
    output = ROOT / "artifacts/raw"
    output.mkdir(parents=True, exist_ok=True)
    history = output / "history" / str(time.time_ns())
    history.mkdir(parents=True, mode=0o700)
    for name, value in [
        (lane + "-results.json", json.dumps(report, indent=2) + "\n"),
        (lane + "-pytest.log", captured.getvalue()),
    ]:
        p = output / name
        if p.exists():
            (history / name).write_bytes(p.read_bytes())
            (history / name).chmod(0o600)
        p.write_text(value)
        p.chmod(0o600)
    print(f"{lane}: {sum(t['status'] == 'passed' for t in entries)} passed / {len(entries)} executed")
    for entry in entries:
        if entry["status"] != "passed":
            print("Required nonpassing selector: " + entry["id"])
    if digest != fingerprint():
        raise SystemExit("Source changed during validation")
    required = json.loads((ROOT / "docs/phase2d/required-tests.json").read_text())[lane]
    python_gate(report, {"python": required}, digest)


if __name__ == "__main__":
    main()
