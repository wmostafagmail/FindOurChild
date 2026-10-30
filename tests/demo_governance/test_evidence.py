import pytest

from tools.phase2e.demo_governance.evidence import enforce, sanitized
from tools.phase2e.demo_governance.records import Denied


def test_dg_w16_inventory_skip_false_pass_and_canary():
    stages = {"setup": "passed", "call": "passed", "teardown": "passed"}
    report = {"source": "a" * 64, "exit": 0, "tests": {"synthetic-test": stages}}
    assert enforce(report, ["synthetic-test"], "a" * 64)
    for wrong in [
        dict(report, tests={}),
        dict(report, exit=1),
        dict(report, source="b" * 64),
        dict(report, tests={"synthetic-test": dict(stages, call="skipped")}),
        dict(report, tests={"synthetic-test": dict(stages, teardown="failed")}),
    ]:
        with pytest.raises(Denied):
            enforce(wrong, ["synthetic-test"], "a" * 64)
    for wrong in [{"trace": "canary-image"}, {"tests": {"canary-token": "passed"}}, {"raw_vector": []}]:
        with pytest.raises(Denied):
            sanitized(wrong)
