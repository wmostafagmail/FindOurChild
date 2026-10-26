"""Strict isolated-lab suite. The host binds the result to the full source fingerprint."""
import io
import json
import time
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

from scripts.results_gate import python_gate
from scripts.test import Results


def main():
    results, captured = Results(), io.StringIO()
    started = time.time()
    with redirect_stdout(captured), redirect_stderr(captured):
        code = pytest.main(["tests/qualification", "--tb=short", "-p", "no:cacheprovider", "--cov=services/api/foc_api", "--cov-append", "--cov-report=", "--cov-fail-under=0"], plugins=[results])
    entries = [{"id": node, "stages": results.reports.get(node, {}), "status": "passed" if results.reports.get(node) == {"setup": "passed", "call": "passed", "teardown": "passed"} else "failed"} for node in results.collected]
    output = Path("/lab-output")
    (output / "pytest.log").write_text(captured.getvalue())
    report = {"exit_code": int(code), "started_at": started, "finished_at": time.time(), "source_digest": "bound_by_host_after_readonly_mount_validation", "tests": entries}
    (output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    expected = json.loads(Path("docs/phase2b/required-tests.json").read_text())["qualification"]
    print(f"qualification: {sum(t['status']=='passed' for t in entries)} passed / {len(entries)} executed; raw diagnostics private")
    for t in entries:
        if t["status"] != "passed" and t["id"] in expected:
            print("Nonpassing required test: " + t["id"])
    python_gate(report, {"python": expected}, report["source_digest"])


if __name__ == "__main__":
    main()
