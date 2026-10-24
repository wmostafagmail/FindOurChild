"""Foundation-only allowlist exporter. Never copy raw reports, DOM, logs, downloads or credentials."""

import hashlib
import json
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
            or recovery["database"]["forced_rls"] != 41
        ):
            raise ValueError("Recovery incomplete")
        summaries["migration_and_recovery"] = {
            "status": "passed",
            "scope": "synthetic foundation backup/restore only",
            "tables": 41,
            "forced_rls": 41,
            "schema_version": "0001",
            "vector_version": "0.8.7",
            "migration_sha256": recovery["database"]["migration_sha"],
            "hardening_sha256": recovery["hardening_sha256"],
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
    (output / "validation.log").write_text("Phase 1A required gate: " + summaries["gate"]["status"] + "\n")
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
