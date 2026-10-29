"""Documentation/metadata checks only; never downloads assets or runs inference.
Run from a full-history checkout: python3 docs/phase2e/check_specification.py.
Optional FOC_GIT_DIR selects an existing Git object mirror.
"""

import csv
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[2]
folder = root / "docs/phase2e"
checks = []


def require(ok, label):
    assert ok, label
    checks.append(label)


lock = json.loads((folder / "research/source-lock.json").read_text())
require(len(lock["sources"]) == 19, "Nineteen official text/metadata responses retained")
for x in lock["sources"]:
    relative = Path(x["local"])
    require(not relative.is_absolute() and ".." not in relative.parts, "Bounded source evidence path")
    b = (folder / "research" / relative).read_bytes()
    require(
        len(b) == x["bytes"] and hashlib.sha256(b).hexdigest() == x["sha256"], "Source lock " + x["local"]
    )
proposal = json.loads((root / "docs/planning/demo/DEMO_ASSET_PROPOSAL.json").read_text())
require(
    all(
        proposal[k] is False
        for k in ["download_authorized", "integration_authorized", "operational_authorized"]
    ),
    "Original proposal authorization flags preserved false",
)
ref = json.loads((folder / "research/dlib-tag.json").read_text())
require(
    ref["object"]["sha"] == proposal["code"]["commit"] and ref["object"]["type"] == "commit",
    "Pinned code tag resolves exact source",
)
weights = {
    x["path"]: x for x in json.loads((folder / "research/dlib-model-metadata.json").read_text())["tree"]
}
for x in proposal["weights"]["files"]:
    require(
        all(weights[x["path"]][k] == x[k] for k in ["sha", "size", "mode", "type"]),
        "Exact weight reference " + x["path"],
    )
    require(
        x["bytes_verified"] is False and x["binary_sha256"] is None,
        "Unacquired weight is not byte-verified " + x["path"],
    )
images = {
    x["path"]: x
    for name in ["synvis-base-tree.json", "synvis-headshot-tree.json"]
    for x in json.loads((folder / "research" / name).read_text())
}
links = {
    x["file_name"]: x["source"]
    for x in csv.DictReader((folder / "research/synvis-headshot-links.csv").read_text().splitlines())
}
total = 0
for group in proposal["dataset"]["groups"]:
    a, b = group["photos"]
    require(links[b["path"]] == a["path"], "Fictional group source link " + group["fictional_group"])
    for x in group["photos"]:
        y = images[x["path"]]
        require(
            (x["git_pointer_blob"], x["publisher_sha256"], x["bytes"])
            == (y["oid"], y["lfs"]["oid"], y["lfs"]["size"])
            and y["size"] == x["bytes"]
            and x["bytes_verified"] is False,
            "Image metadata-only reference " + x["path"],
        )
        total += x["bytes"]
require(total == 103606549, "Expected total image bytes only; none acquired")
for p in folder.glob("*.md"):
    for target in re.findall(r"\]\(([^)]+)\)", p.read_text()):
        if "://" in target or target.startswith("#"):
            continue
        require((p.parent / target.split("#")[0]).exists(), "Document link " + p.name + " " + target)
text = (folder / "TEST_MATRIX.md").read_text()
require(
    set(re.findall(r"T-2E-\d{3}", text)) == {f"T-2E-{i:03}" for i in range(1, 55)},
    "All 54 reserved non-browser scenario IDs present",
)
feature_rows = [line for line in text.splitlines() if line.startswith("| FE-2E-")]
require(
    len(feature_rows) == 27
    and {re.match(r"\| (FE-2E-\d{2})\b", line).group(1) for line in feature_rows}
    == {f"FE-2E-{i:02}" for i in range(1, 28)}
    and all(len(line.split("|")) == 9 for line in feature_rows),
    "All 27 unique feature groups have scenario/fixture/outcome/evidence rows",
)
require(text.count("None / pending") == 27, "Every new feature explicitly pending without execution evidence")
strategy = (folder / "TESTING_AND_ACCEPTANCE.md").read_text()
require(
    set(re.findall(r"E2E-2E-\d\d", strategy)) == {f"E2E-2E-{i:02}" for i in range(1, 9)},
    "Eight proposed browser journeys; no execution claimed",
)
package = json.loads((root / "package-lock.json").read_text())
for name, version in [("e2e", "0.21.3"), ("@e2e-dev/web", "0.15.3"), ("playwright-core", "1.64.1")]:
    require(
        package["packages"]["node_modules/" + name]["version"] == version, "Existing framework lock " + name
    )
registry = json.loads((root / "config/qualification-models.json").read_text())
require(
    registry["real_models_qualified"] == 0
    and len(registry["models"]) == 8
    and all(
        m["decision"] == "blocked"
        and not any(m[k] for k in ["download_allowed", "execution_allowed", "operational_allowed"])
        for m in registry["models"]
    ),
    "All eight previous runtime profiles remain blocked",
)
current = json.loads((root / "docs/contracts/synthetic-candidate-source-v1.schema.json").read_text())
require(
    current["$defs"]["FutureModelSource"]["properties"]["normalization"]["const"] == "unit_l2",
    "Current v1 normalization retained; proposed native v2 is not implemented",
)
git = ["git"]
if os.environ.get("FOC_GIT_DIR"):
    git += ["--git-dir=" + os.environ["FOC_GIT_DIR"]]
tracked = subprocess.check_output(
    [*git, "ls-tree", "-r", "-z", "e168e1361af565c80c8d12f6c729f3b9fcd05376"], cwd=root
).split(b"\0")
# Verify existing execution/contract/config/asset packet inputs unchanged using streaming Git hashes, never native execution.
count = 0
for raw in tracked:
    if not raw:
        continue
    header, name = raw.split(b"\t", 1)
    mode, kind, oid = header.split()
    name = name.decode()
    if not name.startswith(
        (
            "apps/",
            "services/",
            "scripts/",
            "tests/",
            "database/",
            "config/",
            ".github/",
            "docs/contracts/",
            "docs/planning/demo/",
        )
    ) and name not in [
        "package.json",
        "package-lock.json",
        "pyproject.toml",
        "uv.lock",
        "e2e.config.ts",
        "compose.yaml",
        "compose.qualification.yaml",
        "docs/ROADMAP_PHASES_2D_3.md",
    ]:
        continue
    p = root / name
    b = p.read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
    require(actual == oid.decode(), "Preserved approved input " + name)
    count += 1
report = {
    "status": "passed",
    "scope": "documentation/source-reference/preservation checks only; no Phase 2E functional/native tests executed",
    "checks": len(checks),
    "primary_text_metadata_sources": 19,
    "weight_metadata_references": 3,
    "image_metadata_references": 48,
    "existing_inputs_preserved": count,
    "planned_feature_groups": 27,
    "planned_nonbrowser_scenario_groups": 54,
    "planned_browser_journeys": 8,
    "new_phase2e_tests_executed": 0,
    "new_phase2e_validation": "pending",
    "assets_acquired": False,
    "inference_executed": False,
    "command": "python3 docs/phase2e/check_specification.py",
    "initial_preservation": {
        "tracked_files_verified": 864,
        "mismatches": 0,
        "method": "streamed Git blob hashes and modes against pre-existing committed source",
    },
}
(folder / "documentation-checks.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
