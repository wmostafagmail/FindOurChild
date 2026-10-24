"""Audit only package names/versions. No application records are sent to scanners."""

import json
import subprocess
import sys
from pathlib import Path

from scripts.fingerprint import fingerprint

ROOT = Path(__file__).resolve().parents[1]


def execute(args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)


def main():
    output = ROOT / "artifacts/raw"
    output.mkdir(parents=True, exist_ok=True)
    digest = fingerprint()
    if (
        execute(["node", "--version"]).stdout.strip() != "v24.18.0"
        or execute(["npm", "--version"]).stdout.strip() != "11.16.0"
    ):
        raise SystemExit("Pinned audit runtimes required")
    npm = execute(["npm", "audit", "--audit-level=low", "--json"])
    (output / "npm-audit.json").write_text(npm.stdout)
    export = execute(
        ["uv", "export", "--frozen", "--all-groups", "--format", "requirements-txt", "--no-emit-project"]
    )
    if export.returncode:
        raise SystemExit("Locked dependency export failed")
    requirements = ROOT / ".runtime/requirements-audit.txt"
    requirements.parent.mkdir(exist_ok=True)
    requirements.write_text(export.stdout)
    python = execute(
        [
            sys.executable,
            "-m",
            "pip_audit",
            "--requirement",
            str(requirements),
            "--disable-pip",
            "--no-deps",
            "--format",
            "json",
            "--output",
            str(output / "python-audit.json"),
        ]
    )
    code = 0 if npm.returncode == python.returncode == 0 and digest == fingerprint() else 1
    (output / "audit-meta.json").write_text(json.dumps({"source_digest": digest, "exit_code": code}) + "\n")
    print("Locked dependency audit " + ("passed" if code == 0 else "blocked"))
    raise SystemExit(code)


if __name__ == "__main__":
    main()
