"""Host runner for real IdP/BFF flows plus explicit cryptographic unit cases. No skipped cases accepted."""

import json
import os
from pathlib import Path

import pytest

from scripts.fingerprint import fingerprint
from scripts.test import Results

ROOT = Path(__file__).resolve().parents[1]


def main():
    private = json.loads((ROOT / ".runtime/identity.json").read_text())
    local = json.loads((ROOT / ".runtime/local.json").read_text())
    os.environ.update({k: v for k, v in private.items() if k.startswith("FOC_")})
    os.environ.update(local)
    os.environ["FOC_IDP_UPSTREAM"] = "http://127.0.0.1:8080/realms/foc-synthetic"
    result = Results()
    before = fingerprint()
    code = pytest.main(
        [
            "tests/identity",
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
    output = {"exit_code": int(code), "source_digest": before, "tests": entries}
    (ROOT / "artifacts/raw/identity-results.json").write_text(json.dumps(output, indent=2) + "\n")
    required = json.loads((ROOT / "docs/phase1b/required-tests.json").read_text())["python"]
    if (
        before != fingerprint()
        or set(required) != set(result.collected)
        or len(entries) != len(required)
        or any(e["status"] != "passed" for e in entries)
    ):
        raise SystemExit("Mandatory identity inventory failed or incomplete")
    raise SystemExit(int(code))


if __name__ == "__main__":
    main()
