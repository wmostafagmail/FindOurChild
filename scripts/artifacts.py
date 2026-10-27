"""Foundation-only allowlist exporter. Never copy raw reports, DOM, logs, downloads or credentials."""

import hashlib
import json
import math
import re
import shutil
import struct
import zlib
from pathlib import Path

from scripts.fingerprint import fingerprint, inventory
from scripts.results_gate import browser_gate, python_gate

ROOT = Path(__file__).resolve().parents[1]


# Screenshots are permitted only from the input-free synthetic foundation shell, after its assertions pass.
# This is not a general PII detector. Any future photo/contact-bearing page requires a new reviewed policy.
def clean_png(data):
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Not a PNG")
    out = data[:8]
    pos = 8
    seen = []
    while pos < len(data):
        if pos + 12 > len(data):
            raise ValueError("Truncated PNG")
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        if length > 16 * 1024 * 1024 or pos + length + 12 > len(data):
            raise ValueError("Invalid PNG chunk")
        chunk = data[pos : pos + length + 12]
        kind = chunk[4:8]
        payload = chunk[8:-4]
        if zlib.crc32(kind + payload) & 0xFFFFFFFF != struct.unpack(">I", chunk[-4:])[0]:
            raise ValueError("PNG CRC mismatch")
        if kind == b"IHDR":
            width, height = struct.unpack(">II", payload[:8])
            if width > 4096 or height > 4096:
                raise ValueError("Unexpected screenshot dimensions")
        if kind in {b"IHDR", b"PLTE", b"IDAT", b"IEND"}:
            out += chunk
            seen.append(kind)
        elif kind[:1].isupper():
            raise ValueError("Unknown critical PNG chunk")
        pos += length + 12
        if kind == b"IEND":
            break
    if not seen or seen[0] != b"IHDR" or seen[-1] != b"IEND" or b"IDAT" not in seen or pos != len(data):
        raise ValueError("Invalid PNG structure")
    return out


def artifact_path(root, relative):
    base = (root / ".e2e/results").resolve()
    path = (base / relative).resolve()
    if not path.is_relative_to(base) or not path.is_file():
        raise ValueError("Artifact path escaped or missing")
    return path


def safe_id(value):
    # IDs and filenames must come from the reviewed manifest, not exception or DOM contents.
    return hashlib.sha256(value.encode()).hexdigest()[:24]


def export(root=ROOT):
    output = root / "artifacts/sanitized"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    failures = []
    manifest = json.loads((root / "docs/phase1a/required-tests.json").read_text())
    digest = fingerprint()
    summaries = {}
    for name in ["python", "browser"]:
        try:
            if name == "python":
                report = json.loads((root / "artifacts/raw/python-results.json").read_text())
                summaries["python_observed"] = [
                    {
                        "id": t["id"] if t.get("id") in manifest["python"] else "unknown",
                        "status": t.get("status") if t.get("status") in ["passed", "failed"] else "unknown",
                    }
                    for t in report.get("tests", [])
                ]
                summaries[name] = python_gate(report, manifest, digest)
            else:
                report = json.loads((root / ".e2e/report.json").read_text())
                meta = json.loads((root / "artifacts/raw/browser-run.json").read_text())
                # Preserve truthful failed counts as well as the blocking result, with no raw error payloads.
                summaries["browser_observed"] = [
                    {
                        "id": r["titlePath"][-1]
                        if r["titlePath"][-1] in manifest["browser_titles"]
                        else "unknown",
                        "target": r["targetId"]
                        if re.fullmatch(
                            r"(chromium|firefox|webkit)-(ar-EG|en-GB)-(320|360|390|1280)", r["targetId"]
                        )
                        else "unknown",
                        "status": r["status"]
                        if r["status"] in ["passed", "failed", "error", "skipped", "interrupted"]
                        else "unknown",
                    }
                    for r in report["run"]["results"]
                ]
                summaries[name] = browser_gate(report, manifest, meta, digest)
        except (ValueError, KeyError, OSError, TypeError):
            failures.append(name + " required evidence incomplete or nonpassing")
    try:
        identity = json.loads((root / "artifacts/raw/identity-results.json").read_text())
        required_identity = json.loads((root / "docs/phase1b/required-tests.json").read_text())
        summaries["identity_observed"] = [
            {
                "id": t["id"] if t.get("id") in required_identity["python"] else "unknown",
                "status": t.get("status") if t.get("status") in ["passed", "failed"] else "unknown",
            }
            for t in identity.get("tests", [])
        ]
        if (
            identity["exit_code"] != 0
            or identity["source_digest"] != digest
            or sorted(t["id"] for t in identity["tests"]) != sorted(required_identity["python"])
            or any(
                t["stages"] != {"setup": "passed", "call": "passed", "teardown": "passed"}
                for t in identity["tests"]
            )
        ):
            raise ValueError("Identity suite incomplete")
        summaries["identity"] = [{"id": t["id"], "status": "passed"} for t in identity["tests"]]
    except (ValueError, KeyError, OSError, TypeError):
        failures.append("missing or nonpassing identity evidence")
    required_reporting = json.loads((root / "docs/phase1c/required-tests.json").read_text())
    for name, key, filename in [
        ("reporting", "python", "reporting-results.json"),
        ("reporting_http", "http", "reporting-http-results.json"),
        ("resilience", "resilience", "resilience-results.json"),
    ]:
        try:
            report = json.loads((root / "artifacts/raw" / filename).read_text())
            expected = required_reporting[key]
            summaries[name + "_observed"] = [
                {
                    "id": t["id"] if t.get("id") in expected else "unknown",
                    "status": t.get("status") if t.get("status") in ["passed", "failed"] else "unknown",
                }
                for t in report.get("tests", [])
            ]
            if (
                report["source_digest"] != digest
                or report["exit_code"] != 0
                or sorted(t["id"] for t in report["tests"]) != sorted(expected)
                or not report["tests"]
                or any(
                    (t["status"] != "passed" or t["stages"] != {"setup": "passed", "call": "passed", "teardown": "passed"})
                    for t in report["tests"]
                )
            ):
                raise ValueError("Incomplete reporting suite")
            summaries[name] = [{"id": t["id"], "status": "passed"} for t in report["tests"]]
        except (ValueError, KeyError, OSError, TypeError):
            failures.append(name + " required evidence incomplete or nonpassing")
    for lane in ["research", "research_http"]:
        try:
            required = json.loads((root / "docs/phase2a/required-tests.json").read_text())[lane]
            report = json.loads((root / "artifacts/raw" / (lane + "-results.json")).read_text())
            summaries[lane] = python_gate(report, {"python": required}, digest)
        except (ValueError, KeyError, OSError, TypeError):
            failures.append("missing or nonpassing " + lane + " evidence")
    try:
        required = json.loads((root / "docs/phase2b/required-tests.json").read_text())["qualification"]
        report = json.loads((root / "artifacts/raw/qualification-results.json").read_text())
        summaries["qualification"] = python_gate(report, {"python": required}, digest)
        isolation = {"separate_database": True, "network_internal": True, "published_ports": 0, "operational_credentials_mounted": False, "forced_rls_tables": 4, "metadata_backup_restore": "passed", "restored_revocation": "passed", "real_data_authorized": False}
        if report["lab_isolation"] != isolation:
            raise ValueError("qualification isolation or recovery incomplete")
        summaries["qualification_isolation"] = isolation
    except (ValueError, KeyError, OSError, TypeError):
        failures.append("missing or nonpassing qualification preparation evidence")
    for lane in ["synthetic_workflow", "synthetic_workflow_http"]:
        try:
            required = json.loads((root / "docs/phase2d/required-tests.json").read_text())[lane]
            report = json.loads((root / "artifacts/raw" / (lane + "-results.json")).read_text())
            summaries[lane] = python_gate(report, {"python": required}, digest)
        except (ValueError, KeyError, OSError, TypeError):
            failures.append("missing or nonpassing " + lane + " evidence")
    try:
        capacity = json.loads((root / "artifacts/raw/workflow-capacity.json").read_text())
        if (
            set(capacity) != {"source_digest","scope","sessions","queries","candidates_per_query","model_inference","p50_ms","p95_ms","p99_ms","database_p95_within_planning_1000ms","status"}
            or capacity["source_digest"] != digest
            or capacity["scope"] != "synthetic_database_retrieval_only"
            or (capacity["sessions"],capacity["queries"],capacity["candidates_per_query"]) != (20,100,50)
            or capacity["model_inference"] is not False or capacity["status"] != "measured"
            or any(type(capacity[k]) not in {int,float} or not math.isfinite(capacity[k]) or capacity[k]<0 for k in ["p50_ms","p95_ms","p99_ms"])
            or not capacity["p50_ms"] <= capacity["p95_ms"] <= capacity["p99_ms"]
            or capacity["database_p95_within_planning_1000ms"] != (capacity["p95_ms"]<=1000)
        ):
            raise ValueError("Unsafe or stale capacity evidence")
        summaries["synthetic_workflow_capacity"] = {k:v for k,v in capacity.items() if k!="source_digest"}
    except (ValueError,KeyError,OSError,TypeError):
        failures.append("missing or unsafe workflow capacity evidence")
    try:
        from scripts.research_evidence import aggregate

        summaries["synthetic_model_smoke"] = aggregate(
            json.loads((root / "artifacts/raw/research-benchmark.json").read_text()), digest
        )
    except (ValueError, KeyError, OSError, TypeError):
        failures.append("missing or unsafe synthetic model smoke evidence")
    cov = {}
    # Coverage is exported as counts and repository-relative filenames only, with no source snippets or contexts.
    try:
        cov = json.loads((root / "artifacts/raw/coverage.json").read_text())
        summaries["coverage"] = {
            "scope": "API and migration Python code only",
            "totals": {
                k: v
                for k, v in cov["totals"].items()
                if k in ["covered_lines", "num_statements", "percent_covered", "missing_lines"]
            },
        }
        if summaries["coverage"]["totals"]["percent_covered"] < 75:
            failures.append("coverage below threshold")
    except (ValueError, KeyError, OSError, TypeError):
        failures.append("missing coverage")
    try:
        recovery = json.loads((root / "artifacts/raw/recovery.json").read_text())
        if (
            recovery["status"] != "passed"
            or recovery["source_digest"] != digest
            or recovery["database"]["forced_rls"] != 46
        ):
            raise ValueError("Recovery incomplete")
        if recovery.get("research_vector_restore") != {"status": "passed", "vectors_verified": 1, "forced_research_tables": 4, "raw_vector_exported": False}:
            raise ValueError("Research restore incomplete")
        summaries["migration_and_recovery"] = {
            "status": "passed",
            "scope": "synthetic foundation backup/restore only",
            "tables": 46,
            "forced_rls": 46,
            "schema_version": "0001",
            "vector_version": "0.8.7",
            "migration_sha256": recovery["database"]["migration_sha"],
            "hardening_sha256": recovery["hardening_sha256"],
            "all_migrations": recovery["all_migrations"],
            "identity_session_rls": recovery["identity_session_rls"],
            "reporting_metadata_rls": recovery["reporting_metadata_rls"],
            "research_vector_restore": recovery["research_vector_restore"],
            "synthetic_workflow_restore": recovery["synthetic_workflow_restore"],
            "operational_erasure": "pending",
        }
    except (ValueError, KeyError, OSError, TypeError):
        failures.append("missing or stale recovery evidence")
    try:
        coverage_files = {}
        for name, entry in cov["files"].items():
            if name in inventory():
                coverage_files[name] = {
                    "executed_lines": [v for v in entry["executed_lines"] if isinstance(v, int)],
                    "missing_lines": [v for v in entry["missing_lines"] if isinstance(v, int)],
                }
        (output / "coverage.json").write_text(json.dumps(coverage_files, indent=2) + "\n")
    except (ValueError, KeyError, OSError, TypeError):
        failures.append("invalid coverage report")
    try:
        audit_meta = json.loads((root / "artifacts/raw/audit-meta.json").read_text())
        npm = json.loads((root / "artifacts/raw/npm-audit.json").read_text())
        python_audit = json.loads((root / "artifacts/raw/python-audit.json").read_text())
        if (
            audit_meta["source_digest"] != digest
            or audit_meta["exit_code"] != 0
            or npm["metadata"]["vulnerabilities"]["total"] != 0
            or any(d.get("vulns") or d.get("skip_reason") for d in python_audit["dependencies"])
        ):
            raise ValueError("Dependency audit incomplete")
        summaries["dependency_audit"] = {
            "status": "passed",
            "npm_known_vulnerabilities": 0,
            "python_known_vulnerabilities": 0,
        }
    except (ValueError, KeyError, OSError, TypeError):
        failures.append("missing, stale or nonpassing dependency audit")
    # Screenshots are released only for fully passed locale tests with the fixed no-input shell.
    try:
        run = json.loads((root / ".e2e/report.json").read_text())["run"]
        for result in run["results"]:
            if result["status"] != "passed" or result["titlePath"][-1] not in [
                "TC_FND_BROWSER_AR_READY",
                "TC_FND_BROWSER_EN_READY",
            ]:
                continue
            for attempt in result["attempts"]:
                for artifact in attempt.get("artifacts", []):
                    if artifact.get("kind") != "screenshot":
                        continue
                    # Resolve without following any path outside the private E2E output.
                    path = artifact_path(root, artifact["path"])
                    if "foundation-" not in path.name:
                        continue
                    cleaned = clean_png(path.read_bytes())
                    target = output / "screenshots" / (safe_id(result["id"] + str(path.name)) + ".png")
                    target.parent.mkdir(exist_ok=True)
                    target.write_bytes(cleaned)
        # Trace export retains only assertion/action names, status and elapsed time; no arguments, DOM or URLs.
        allowed_api = re.compile(r"^(app|browser|expect)\.[A-Za-z.]+$")
        traces = []
        for result in run["results"]:
            if result["titlePath"][-1] not in manifest["browser_titles"]:
                continue
            traces.append(
                {
                    "test": result["titlePath"][-1],
                    "target": result["targetId"]
                    if result["targetId"]
                    in {
                        f"{b}-{l}-{w}"
                        for b in ["chromium", "firefox", "webkit"]
                        for l in ["ar-EG", "en-GB"]
                        for w in [320, 360, 390, 1280]
                    }
                    else "unknown",
                    "steps": [
                        {
                            "api": step["api"] if allowed_api.fullmatch(step["api"]) else "other",
                            "status": step["status"]
                            if step["status"] in ["passed", "failed", "error", "skipped"]
                            else "unknown",
                        }
                        for attempt in result["attempts"]
                        for step in attempt.get("steps", [])
                    ],
                }
            )
        (output / "traces.json").write_text(json.dumps(traces, indent=2) + "\n")
    except (ValueError, KeyError, OSError, TypeError):
        failures.append("artifact sanitization failed")
    summaries["gate"] = {
        "status": "blocked" if failures else "passed",
        "reasons": failures,
        "source_digest": digest,
    }
    # Allowlisted log replaces arbitrary free-text process logs.
    (output / "validation.log").write_text("Phase 2D synthetic investigation required gate: " + summaries["gate"]["status"] + "\n")
    (output / "results.json").write_text(json.dumps(summaries, indent=2) + "\n")
    (output / "source-manifest.json").write_text(json.dumps(inventory(), indent=2) + "\n")
    (output / "checksums.json").write_text(
        json.dumps(
            {
                str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in output.rglob("*")
                if p.is_file()
            },
            indent=2,
        )
        + "\n"
    )
    return not failures


if __name__ == "__main__":
    raise SystemExit(0 if export() else 1)
