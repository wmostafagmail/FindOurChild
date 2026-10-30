"""Strict data-free governance evidence: no skips, missing tests or secret text."""

import re

from .records import require


def enforce(report, required, source):
    require(
        set(report) == {"source", "exit", "tests"} and report["source"] == source and report["exit"] == 0,
        "evidence_source_or_exit",
    )
    tests = report["tests"]
    require(type(tests) is dict and set(tests) == set(required), "evidence_inventory")
    require(
        all(value == {"setup": "passed", "call": "passed", "teardown": "passed"} for value in tests.values()),
        "evidence_test_failure",
    )
    return True


def sanitized(value):
    # Release only exact selector/stage metadata, numeric counters and fixed
    # errors. Never sanitize an arbitrary log by trying to enumerate its secrets.
    require(type(value) is dict and set(value) <= {"source", "exit", "tests"}, "artifact_fields")
    require(
        not re.search(r"canary|bearer|private.key|raw.vector|data:image", str(value), re.IGNORECASE),
        "artifact_canary",
    )
    return value
