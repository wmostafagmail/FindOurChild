"""Host runner for real IdP/BFF flows plus explicit cryptographic unit cases. No skipped cases accepted."""

import io
import json
import os
from contextlib import redirect_stderr, redirect_stdout
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
    captured = io.StringIO()
    with redirect_stdout(captured), redirect_stderr(captured):
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
    private_log = ROOT / "artifacts/raw/identity-pytest.log"
    private_log.write_text(captured.getvalue())
    private_log.chmod(0o600)

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
    print(
        "identity assertions: "
        + str(sum(e["status"] == "passed" for e in entries))
        + " passed / "
        + str(len(entries))
        + " executed; detailed diagnostics retained privately"
    )

    required = json.loads((ROOT / "docs/phase1b/required-tests.json").read_text())["python"]
    failed = [
        {"id": t["id"], "locations": result.failures.get(t["id"], {})}
        for t in entries
        if t["status"] != "passed" and t["id"] in required
    ]
    if failed:
        print("Sanitized failure locations: " + json.dumps(failed))
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
