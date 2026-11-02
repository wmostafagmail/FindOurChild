"""Closed, data-free evidence and exact inventories. No clean skips or missing cases."""

from .records import digest, require


def enforce_inventory(collected, expected, reports):
    require(len(collected) == len(expected) and len(set(collected)) == len(collected)
            and set(collected) == set(expected), "required_inventory")
    require(set(reports) == set(expected) and all(
        stages == {"setup": "passed", "call": "passed", "teardown": "passed"}
        for stages in reports.values()), "mandatory_nonpassing")


def public_report(report):
    require(type(report) is dict and set(report) == {"source_digest", "tests", "scope", "actual_assets",
            "actual_owner_authorizations", "actual_inference", "database_p95_target_ms"}, "public_closed")
    require(type(report["source_digest"]) is str and len(report["source_digest"]) == 64
            and report["scope"] == "source_only_synthetic_engineering" and report["actual_assets"] == 0
            and report["actual_owner_authorizations"] == 0 and report["actual_inference"] is False
            and report["database_p95_target_ms"] == 1000, "public_scope")
    require(type(report["tests"]) is list and len(report["tests"]) <= 256, "public_tests")
    for row in report["tests"]:
        require(set(row) == {"selector", "status"} and type(row["selector"]) is str
                and row["selector"].startswith("tests/owner_only_v3/")
                and len(row["selector"]) < 256 and row["status"] in {"passed", "failed"}, "public_test_row")
    return report


def source_digest(files):
    return digest(files)
