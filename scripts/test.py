"""Strict required-results runner: collection, setup, call and teardown all count."""

import json
import time
from pathlib import Path

import pytest

from scripts.fingerprint import fingerprint
from scripts.preflight import verify

ROOT = Path(__file__).resolve().parents[1]


class Results:
    def __init__(self):
        self.collected = []
        self.reports = {}

    def pytest_collection_finish(self, session):
        self.collected = [item.nodeid for item in session.items]

    def pytest_runtest_logreport(self, report):
        self.reports.setdefault(report.nodeid, {})[report.when] = report.outcome


def main():
    verify()
    output = ROOT / "artifacts/raw"
    output.mkdir(parents=True, exist_ok=True)
    results = Results()
    digest = fingerprint()
    started = time.time()
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
            "--cov-fail-under=75",
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
    data = {
        "suite": "phase1a-python",
        "started_at": started,
        "finished_at": time.time(),
        "tests": entries,
        "exit_code": int(code),
        "source_digest": digest,
    }
    (output / "python-results.json").write_text(json.dumps(data, indent=2) + "\n")
    # No clean skips, empty discovery, uncollected mandatory cases or teardown failures count as success.
    expected = json.loads((ROOT / "docs/phase1a/required-tests.json").read_text())["python"]
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
