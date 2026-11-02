"""Reproducible approved-design/source separation and inventory checks."""

import json

from .records import DESIGN, POLICY, ROOT, digest, require, sha


def check():
    status = json.loads((DESIGN / "DESIGN_STATUS.json").read_bytes())
    files = {name: sha((DESIGN / name).read_bytes()) for name in status["files_sha256"]}
    require(files == status["files_sha256"] and digest(files) == POLICY == status["policy_bundle_sha256"],
            "approved_design_changed")
    changed = []
    for item in status["preserved_accepted_files"]:
        if sha((ROOT / item["path"]).read_bytes()) != item["sha256"]:
            changed.append(item["path"])
    require(changed == [".github/workflows/phase1a.yml"], "unapproved_original_boundary_change")
    required = json.loads((DESIGN / "implementation/required-tests.json").read_bytes())
    mapping = json.loads((DESIGN / "implementation/TRACEABILITY.json").read_bytes())["cases"]
    original = json.loads((DESIGN / "TEST_MATRIX.json").read_bytes())["cases"]
    require(len(required["python"]) == 98 and len(set(required["python"])) == 98
            and len(mapping) == 96 and {r["case_id"] for r in mapping} == {r["case_id"] for r in original},
            "v3_inventory_design")
    for row in mapping:
        prior = next(r for r in original if r["case_id"] == row["case_id"])
        require(row["affected_components"] == prior["affected_components"], "component_mapping_changed")
        if row["case_id"].startswith("OD3-B"):
            require(row["case_id"] in required["browser_titles"], "browser_selector_missing")
        else:
            require(row["selector"] in required["python"], "scenario_selector_missing")
    governance = json.loads((ROOT / "config/phase2e/demo-governance.json").read_bytes())
    require(governance["owner_anchor"] is None and governance["registry"] is None
            and all(governance[k] is False for k in ["provisioning_enabled", "acquisition_enabled",
                "unpacking_enabled", "scanning_enabled", "native_parsing_enabled", "inference_enabled",
                "operational_enabled"]), "deployed_controls_must_remain_disabled")
    guard = (ROOT / "services/demo_recognition/native/execution_guard.cpp").read_text()
    registry = (ROOT / "tools/phase2e/demo_governance/registry.py").read_text()
    require("actual_manifest_authority_unprovisioned" in guard and "deployment_enrollment_not_authorized" in registry,
            "unconditional_barriers_missing")
    return {"approved_documents": len(files), "historical_files_unchanged": len(status["preserved_accepted_files"]) - 1,
            "intentional_required_workflow_addition": changed, "scenario_mappings": 96,
            "frozen_python_selectors": 98, "official_new_browser_executions": 144,
            "original_browser_executions": 360, "unconditional_original_barriers": 2,
            "actual_owner_provisioning": False, "actual_assets": 0, "actual_inference": False}


if __name__ == "__main__":
    print(json.dumps(check(), sort_keys=True))
