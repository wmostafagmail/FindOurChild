"""Strict required-results runner: collection, setup, call and teardown all count."""

import io
import json
import time
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

from scripts.fingerprint import fingerprint
from scripts.preflight import verify

ROOT = Path(__file__).resolve().parents[1]


class Results:
    def __init__(self):
        self.collected = []
        self.reports = {}
        self.failures = {}

    def pytest_collection_finish(self, session):
        self.collected = [item.nodeid for item in session.items]

    def pytest_runtest_logreport(self, report):
        self.reports.setdefault(report.nodeid, {})[report.when] = report.outcome
        if report.failed:
            crash = getattr(report.longrepr, "reprcrash", None)
            if crash:
                candidate = Path(crash.path)
                try:
                    location = str(candidate.resolve().relative_to(ROOT))
                except ValueError:
                    location = "external"
                line = getattr(crash, "lineno", 0)
                self.failures.setdefault(report.nodeid, {})[report.when] = {
                    "file": location if location.startswith(("tests/", "scripts/", "services/api/")) else "external",
                    "line": line if isinstance(line, int) and 0 <= line <= 20000 else 0,
                }
                message = getattr(crash, "message", "")
                for category in ["delivery_missing", "delivery_key_mismatch", "delivery_permission_denied", "api_not_running", "fixture_process_failed"]:
                    if "Synthetic delivery fixture unavailable: " + category in message:
                        self.failures[report.nodeid][report.when]["reason"] = category
                        break


def main():
    verify()
    output = ROOT / "artifacts/raw"
    output.mkdir(parents=True, exist_ok=True)
    results = Results()
    digest = fingerprint()
    started = time.time()
    captured = io.StringIO()
    with redirect_stdout(captured), redirect_stderr(captured):
        code = pytest.main(
            [
                "tests/unit",
                "tests/api",
                "tests/database",
                "tests/security",
                "tests/integration",
                "--tb=short",
                "--junitxml=artifacts/raw/python.junit.xml",
                "--cov=services/api/foc_api",
                "--cov=scripts.migrate",
                "--cov-report=json:artifacts/raw/coverage.json",
                "--cov-report=xml:artifacts/raw/coverage.xml",
                "--cov-fail-under=0",
            ],
            plugins=[results],
        )
    private_log = ROOT / "artifacts/raw/python-pytest.log"
    private_log.write_text(captured.getvalue())
    private_log.chmod(0o600)

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
    data = {
        "suite": "phase1a-python",
        "started_at": started,
        "finished_at": time.time(),
        "tests": entries,
        "exit_code": int(code),
        "source_digest": digest,
    }
    (output / "python-results.json").write_text(json.dumps(data, indent=2) + "\n")
    print(
        "python assertions: "
        + str(sum(e["status"] == "passed" for e in entries))
        + " passed / "
        + str(len(entries))
        + " executed; detailed diagnostics retained privately"
    )

    # Combined API-process + baseline + host identity coverage is enforced at 75% in the final CI gate.
    # No clean skips, empty discovery, uncollected mandatory cases or teardown failures count as success.
    expected = json.loads((ROOT / "docs/phase1a/required-tests.json").read_text())["python"]
    failed = [
        {"id": t["id"], "locations": results.failures.get(t["id"], {})}
        for t in entries
        if t["status"] != "passed" and t["id"] in expected
    ]
    if failed:
        print("Sanitized failure locations: " + json.dumps(failed))
    if (
        digest != fingerprint()
        or set(expected) != set(results.collected)
        or len(expected) != len(results.collected)
        or not entries
        or any(t["status"] != "passed" for t in entries)
    ):
        raise SystemExit("Required test inventory incomplete or nonpassing; review private raw artifacts")
    raise SystemExit(int(code))


if __name__ == "__main__":
    main()
