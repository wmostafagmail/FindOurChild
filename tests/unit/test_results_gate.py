import copy
import struct
import zlib

import pytest

from scripts.artifacts import clean_png
from scripts.results_gate import TARGETS, GateError, browser_gate, python_gate


def test_fnd_gate_rejects_missing_python_result():
    manifest = {"python": ["unit-fixture"]}
    report = {"tests": [], "source_digest": "same", "exit_code": 0, "started_at": 1, "finished_at": 2}
    with pytest.raises(GateError):
        python_gate(report, manifest, "same")


@pytest.mark.parametrize("stage", ["setup", "call", "teardown"])
@pytest.mark.parametrize("status", ["failed", "skipped"])
def test_fnd_gate_rejects_nonpassing_stage(stage, status):
    stages = {"setup": "passed", "call": "passed", "teardown": "passed"}
    stages[stage] = status
    report = {
        "tests": [{"id": "unit-fixture", "status": "passed", "stages": stages}],
        "source_digest": "same",
        "exit_code": 0,
        "started_at": 1,
        "finished_at": 2,
    }
    with pytest.raises(GateError):
        python_gate(report, {"python": ["unit-fixture"]}, "same")


def fixture_report():
    # Synthetic unit fixture for the result validator, never application execution evidence.
    results = [
        {
            "titlePath": ["unit-fixture"],
            "targetId": t,
            "selected": True,
            "status": "passed",
            "attempts": [{"status": "passed", "cleanup": "complete", "secondaryErrors": []}],
        }
        for t in TARGETS
    ]
    return {
        "schemaVersion": "report-1",
        "run": {
            "runner": {"name": "e2e", "version": "0.21.3"},
            "exitCode": 0,
            "status": "passed",
            "errors": [],
            "usage": {"modelTokens": 0, "maxModelCallsInStep": 0},
            "targets": [
                {"id": t, "engine": {"version": "0.15.3"}, "baseOrigin": "http://127.0.0.1:3000"}
                for t in TARGETS
            ],
            "results": results,
            "summary": {
                "discovered": 24,
                "selected": 24,
                "executed": 24,
                "passed": 24,
                "failed": 0,
                "interrupted": 0,
                "flaky": 0,
                "skipped": 0,
            },
        },
    }


def test_fnd_gate_accepts_complete_validator_fixture():
    assert (
        len(
            browser_gate(
                fixture_report(),
                {"browser_titles": ["unit-fixture"]},
                {"source_digest": "same", "exit_code": 0},
                "same",
            )
        )
        == 24
    )


@pytest.mark.parametrize(
    "defect",
    ["missing-target", "duplicate-result", "retry", "skip", "cleanup", "runner", "origin", "model", "stale"],
)
def test_fnd_gate_rejects_browser_defects(defect):
    report = fixture_report()
    run = report["run"]
    meta = {"source_digest": "same", "exit_code": 0}
    if defect == "missing-target":
        run["targets"].pop()
    if defect == "duplicate-result":
        run["results"].append(copy.deepcopy(run["results"][0]))
    if defect == "retry":
        run["results"][0]["attempts"].append(copy.deepcopy(run["results"][0]["attempts"][0]))
    if defect == "skip":
        run["results"][0]["status"] = "skipped"
    if defect == "cleanup":
        run["results"][0]["attempts"][0]["cleanup"] = "failed"
    if defect == "runner":
        run["runner"]["name"] = "mock"
    if defect == "origin":
        run["targets"][0]["baseOrigin"] = "https://external.invalid"
    if defect == "model":
        run["usage"]["modelTokens"] = 1
    if defect == "stale":
        meta["source_digest"] = "old"
    with pytest.raises(GateError):
        browser_gate(report, {"browser_titles": ["unit-fixture"]}, meta, "same")


def png_chunk(kind, payload):
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def test_fnd_png_sanitizer_strips_metadata_canary():
    image = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        + png_chunk(b"tEXt", b"cookie\x00SYNTHETIC_SECRET_CANARY")
        + png_chunk(b"IDAT", zlib.compress(b"\x00\xff\xff\xff"))
        + png_chunk(b"IEND", b"")
    )
    result = clean_png(image)
    assert b"CANARY" not in result
    assert clean_png(result) == result


@pytest.mark.parametrize("image", [b"not-a-png", b"\x89PNG\r\n\x1a\n", b"\x89PNG\r\n\x1a\n" + b"\x00" * 12])
def test_fnd_png_sanitizer_rejects_invalid_input(image):
    with pytest.raises(ValueError):
        clean_png(image)


def test_fnd_artifact_path_rejects_escape_and_symlink(tmp_path):
    from scripts.artifacts import artifact_path

    base = tmp_path / ".e2e/results"
    base.mkdir(parents=True)
    good = base / "foundation.png"
    good.write_bytes(b"synthetic fixture")
    outside = tmp_path / "private.txt"
    outside.write_text("SYNTHETIC_SECRET_CANARY")
    (base / "linked.png").symlink_to(outside)
    assert artifact_path(tmp_path, "foundation.png") == good
    for path in ["../../private.txt", str(outside), "linked.png", "missing.png"]:
        with pytest.raises(ValueError):
            artifact_path(tmp_path, path)
