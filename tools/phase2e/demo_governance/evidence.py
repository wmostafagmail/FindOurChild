"""Strict data-free governance evidence: no skips, missing tests or secret text."""

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


def sanitized(value, required=()):
    # Structural release allowlist: test names may themselves describe canary
    # tests. Never regex-scan arbitrary log text and call it sanitized.
    from .records import sha

    require(type(value) is dict and set(value) == {"source", "exit", "tests"}, "artifact_fields")
    require(
        sha(value["source"]) and type(value["exit"]) is int and 0 <= value["exit"] <= 5, "artifact_metadata"
    )
    require(type(value["tests"]) is dict and set(value["tests"]) <= set(required), "artifact_selectors")
    for stages in value["tests"].values():
        require(
            type(stages) is dict
            and set(stages) <= {"setup", "call", "teardown"}
            and all(type(v) is str and v in {"passed", "failed", "skipped"} for v in stages.values()),
            "artifact_stages",
        )
    return value
