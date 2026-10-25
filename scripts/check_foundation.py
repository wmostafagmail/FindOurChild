"""Historical Phase 0 checks plus current executable contract/configuration checks."""

import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import tomllib
from pathlib import Path

import yaml
from openapi_spec_validator import validate

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "40231be73ab9a5eb577ccf5308c86f6b7282976b"


def main():
    checks = []

    def require(ok, message):
        if not ok:
            raise AssertionError(message)
        checks.append(message)

    # The original documentary validators require a preimplementation tree. Run them against its immutable commit.
    git = ["git"]
    if os.environ.get("FOC_GIT_DIR"):
        git += ["--git-dir=" + os.environ["FOC_GIT_DIR"]]
    archive = subprocess.check_output([*git, "archive", BASELINE], cwd=ROOT)
    historical = []
    with tempfile.TemporaryDirectory(prefix="foc-phase0-") as directory:
        with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
            bundle.extractall(directory, filter="data")
        for script in ["validate_phase0.py", "validate_testing_architecture.py"]:
            result = subprocess.run(
                [sys.executable, str(Path(directory) / "tools" / script)],
                check=False,
                cwd=directory,
                capture_output=True,
                text=True,
            )
            require(result.returncode == 0, "Historical " + script + " passes")
            historical.append({"validator": script, "status": "passed", "output": result.stdout.strip()})
    protected = json.loads((ROOT / "docs/research/e2e/protected-baseline.json").read_text())["files"]
    for entry in protected:
        # These two status descriptions are versioned in 1A; original specifications remain available at BASELINE.
        if entry["path"] in ["docs/API_CONTRACTS.md", "docs/DATABASE_SCHEMA.md"]:
            continue
        require(
            hashlib.sha256((ROOT / entry["path"]).read_bytes()).hexdigest() == entry["sha256"],
            "Preserved " + entry["path"],
        )
    contract = json.loads((ROOT / "docs/contracts/openapi.json").read_text())
    validate(contract)
    operations = [(p, m, o) for p, item in contract["paths"].items() for m, o in item.items()]
    require(len(operations) == 49, "32 domain contracts plus 3 foundation, 8 identity/capability and 6 reporting additions")
    require(len({o["operationId"] for _, _, o in operations}) == 49, "Unique operation IDs")
    for path, method, operation in operations:
        require(
            "503" in operation["responses"] or not path.startswith("/v1/"),
            "Disabled domain operations declare 503",
        )
        if path.startswith("/v1/") and method == "post" and path != "/v1/public/intake-challenges":
            require(operation["requestBody"]["required"], "All domain writes have typed bodies")
    package = json.loads((ROOT / "package.json").read_text())
    lock = json.loads((ROOT / "package-lock.json").read_text())
    for group in ["dependencies", "devDependencies"]:
        for name, version in package[group].items():
            require(bool(re.fullmatch(r"\d+\.\d+\.\d+", version)), "Exact npm version " + name)
            require(lock["packages"]["node_modules/" + name]["version"] == version, "Locked " + name)
    for name, version in {
        "e2e": "0.21.3",
        "@e2e-dev/web": "0.15.3",
        "playwright-core": "1.64.1",
        "zod": "4.6.6",
    }.items():
        require(
            lock["packages"]["node_modules/" + name]["version"] == version, "Framework/security pin " + name
        )
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    python_lock = tomllib.loads((ROOT / "uv.lock").read_text())
    python_versions = {p["name"].replace("_", "-"): p["version"] for p in python_lock["package"]}
    for dependency in project["project"]["dependencies"] + project["dependency-groups"]["dev"]:
        match = re.fullmatch(r"([A-Za-z0-9_-]+)(?:\[[^]]+\])?==(\d+\.\d+\.\d+)", dependency)
        require(bool(match), "Exact Python dependency " + dependency)
        require(
            python_versions[match[1].lower().replace("_", "-")] == match[2],
            "Python lock agrees " + dependency,
        )

    compose = yaml.safe_load((ROOT / "compose.yaml").read_text())
    require(compose["networks"]["private"]["internal"] is True, "Database network stays private")
    require(
        compose["services"]["db"]["networks"] == ["private"] and "ports" not in compose["services"]["db"],
        "No published DB port or edge attachment",
    )
    require(
        "FOC_DATABASE_ADMIN_URL" not in compose["services"]["api"]["environment"], "No API admin credentials"
    )
    require("@sha256:" in compose["services"]["db"]["image"], "Database image digest pinned")
    workflow = yaml.safe_load((ROOT / ".github/workflows/phase1a.yml").read_text())
    for step in workflow["jobs"]["phase1a-required"]["steps"]:
        if "uses" in step:
            require(bool(re.search(r"@[a-f0-9]{40}$", step["uses"])), "Immutable action pin")
        require(not step.get("continue-on-error", False), "No hidden CI failures")
    manifest = json.loads((ROOT / "docs/phase1a/required-tests.json").read_text())
    require(
        bool(manifest["python"]) and len(manifest["python"]) == len(set(manifest["python"])),
        "Explicit unique required tests",
    )
    output = ROOT / "artifacts/raw"
    output.mkdir(parents=True, exist_ok=True)
    (output / "configuration-checks.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "checks": len(checks),
                "historical": historical,
                "remote_ci_enforcement": "pending",
            },
            indent=2,
        )
        + "\n"
    )
    print(
        f"{len(checks)} foundation structural/configuration checks passed; historical Phase 0 checks passed; application execution reported separately"
    )


if __name__ == "__main__":
    main()
