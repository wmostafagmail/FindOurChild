"""Reject missing, duplicated, retried, skipped, stale, mocked or nonpassing mandatory results."""

from collections import Counter

BROWSERS = ["chromium", "firefox", "webkit"]
LOCALES = ["ar-EG", "en-GB"]
WIDTHS = [320, 360, 390, 1280]
TARGETS = {f"{b}-{l}-{w}" for b in BROWSERS for l in LOCALES for w in WIDTHS}


class GateError(ValueError):
    pass


def require(value, message):
    if not value:
        raise GateError(message)


def python_gate(report, manifest, digest):
    tests = report["tests"]
    require(report["source_digest"] == digest, "stale Python evidence")
    require(report["exit_code"] == 0, "Python runner failed")
    require(report["finished_at"] >= report["started_at"], "invalid execution interval")
    require(
        Counter(t["id"] for t in tests) == Counter(manifest["python"]), "Python required inventory mismatch"
    )
    require(bool(tests), "zero tests")
    require(
        all(
            t["status"] == "passed"
            and t["stages"] == {"setup": "passed", "call": "passed", "teardown": "passed"}
            for t in tests
        ),
        "nonpassing Python result",
    )
    return [{"id": t["id"], "status": "passed"} for t in tests]


def browser_gate(report, manifest, meta, digest):
    run = report["run"]
    require(meta["source_digest"] == digest and meta["exit_code"] == 0, "stale or failed browser execution")
    require(report["schemaVersion"] == "report-1", "unsupported report version")
    require(run["runner"] == {"name": "e2e", "version": "0.21.3"}, "unexpected browser runner")
    require(run["exitCode"] == 0 and run["status"] == "passed", "browser runner failed")
    require(not run["errors"], "browser run errors")
    require(
        run["usage"]["modelTokens"] == 0 and run["usage"]["maxModelCallsInStep"] == 0,
        "model use in mandatory suite",
    )
    require(
        {t["id"] for t in run["targets"]} == TARGETS and len(run["targets"]) == 24, "missing browser targets"
    )
    require(
        all(
            t["engine"]["version"] == "0.15.3" and t["baseOrigin"] == "http://127.0.0.1:3000"
            for t in run["targets"]
        ),
        "unexpected engine or origin",
    )
    expected = {(title, target) for title in manifest["browser_titles"] for target in TARGETS}
    results = run["results"]
    observed = [(r["titlePath"][-1], r["targetId"]) for r in results]
    require(
        set(observed) == expected and len(observed) == len(expected), "browser required inventory mismatch"
    )
    require(
        all(
            r["selected"]
            and r["status"] == "passed"
            and len(r["attempts"]) == 1
            and r["attempts"][0]["status"] == "passed"
            and r["attempts"][0]["cleanup"] == "complete"
            and not r["attempts"][0]["secondaryErrors"]
            for r in results
        ),
        "nonpassing, retried or incomplete browser result",
    )
    summary = run["summary"]
    require(
        all(summary.get(k) == len(expected) for k in ["discovered", "selected", "executed", "passed"]),
        "incomplete browser execution",
    )
    require(
        all(summary.get(k) == 0 for k in ["failed", "interrupted", "flaky", "skipped"]),
        "nonpassing browser summary",
    )
    return [{"id": r["titlePath"][-1], "target": r["targetId"], "status": "passed"} for r in results]
