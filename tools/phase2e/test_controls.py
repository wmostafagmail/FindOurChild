"""Strict, source-bound E0 test runner. This never reports model inference passed."""

import hashlib
import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

from scripts.test import Results

ROOT = Path(__file__).resolve().parents[2]


def sources():
    paths = []
    for directory in ["tools/phase2e", "services/demo_recognition", "config/phase2e", "tests/phase2e"]:
        paths.extend(p for p in (ROOT / directory).rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts)
    paths += [ROOT / ".github/workflows/phase2e-source-preflight.yml", ROOT / "docs/phase2e/e0-required-tests.json"]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def main():
    if not __debug__:
        raise SystemExit("Required-result assertions cannot be disabled")
    manifest = json.loads((ROOT / "docs/phase2e/e0-required-tests.json").read_text())
    inventory = sources()
    result = Results()
    captured = io.StringIO()
    with redirect_stdout(captured), redirect_stderr(captured):
        code = pytest.main(["tests/phase2e", "-q", "--tb=short"], plugins=[result])
    raw = ROOT / "artifacts/raw/phase2e-e0"
    raw.mkdir(parents=True, exist_ok=True, mode=0o700)
    log = raw / "controls.log"
    log.write_text(captured.getvalue())
    log.chmod(0o600)
    required = manifest["e0_controls"]
    assert result.collected == required and required, "Required E0 inventory changed or missing"
    entries = [{"id": node, "status": "passed" if result.reports.get(node) == {
        "setup": "passed", "call": "passed", "teardown": "passed"} else "failed"} for node in result.collected]
    assert inventory == sources(), "Source changed while controls ran"
    output = ROOT / "artifacts/phase2e-e0-controls"
    output.mkdir(parents=True, exist_ok=True)
    (output / "results.json").write_text(json.dumps({"scope": "synthetic_e0_unit_controls_only", "exit_code": int(code),
        "tests": entries, "native_model_tests_executed": 0, "model_inference": "not_executed",
        "source_manifest": inventory}, indent=2) + "\n")
    failed = [entry["id"] for entry in entries if entry["status"] != "passed"]
    print(json.dumps({"e0_control_tests": len(entries), "failed": failed, "native_inference_tests": 0}))
    if code or failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
