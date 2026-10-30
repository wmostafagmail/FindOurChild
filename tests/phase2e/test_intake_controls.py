"""Synthetic intake guard fixtures only, never acquisition/model acceptance."""

import hashlib
import json
from copy import deepcopy

import pytest

from tools.phase2e.intake import (
    A0,
    IntakeError,
    RestrictedRedirect,
    approved_preflight,
    download,
    image_transport_policy,
    plan,
)


def synthetic_review():
    native = {"python": "3.13.13", "dlib": "20.0.0", "architecture": "x86_64", "model_files_loaded": 0,
              "images_processed": 0, "inference_executed": False, "native_transform_executed": True,
              "explicit_chip_parity": True, "nonroot": True, "read_only": True,
              "capabilities_dropped": True, "internet_probe_denied": True}
    native.update({"cuda": False, "avx": False, "soabi": "cpython-313-x86_64-linux-gnu", "gil_disabled": False,
                   "model_execution_api_available": True,
                   "runtime_dependency_inventory": {"loaded_libraries": {"fictional-lib.so": {"sha256": "0" * 64}}}})
    raw = json.dumps({"scope": "data_free_source_only_preflight", "host_architecture": "x86_64",
                      "native": native, "resource_limits": {"cpus": 2, "memory_bytes": 1073741824,
                                                             "pids": 64, "timeout_seconds": 60}}).encode()
    review = {"gate": "A1b", "decision": "approved", "owner_authorization_sha256": A0,
              "preflight_result_sha256": hashlib.sha256(raw).hexdigest(), "reviewer": "fictional-unit-operator",
              "review_record_sha256": "a" * 64, "critical_findings": [], "source_and_transitive_grants_reviewed": True}
    return raw, review


def test_exact_frozen_three_weight_and_48_image_plan_without_downloading():
    rows = plan()
    assert len([r for r in rows if r["kind"] == "weight"]) == 3
    assert len([r for r in rows if r["kind"] == "image"]) == 48
    assert sum(r["size"] for r in rows) == 131436335
    assert all(r.get("active_enrollment", False) is False for r in rows)
    assert not any("68_face" in r["id"] for r in rows)


@pytest.mark.parametrize("change", ["rejected", "no_review", "other_scope", "different_result", "critical",
                                     "integer_approval", "unknown_field"])
def test_pre_acquisition_review_cannot_be_omitted_or_rebound(change):
    raw, review = synthetic_review()
    if change == "rejected":
        review["decision"] = "pending"
    elif change == "no_review":
        review["reviewer"] = ""
    elif change == "other_scope":
        review["owner_authorization_sha256"] = "0" * 64
    elif change == "different_result":
        review["preflight_result_sha256"] = "0" * 64
    elif change == "critical":
        review["critical_findings"] = ["unresolved"]
    elif change == "integer_approval":
        review["source_and_transitive_grants_reviewed"] = 1
    else:
        review["auto_activate"] = True
    with pytest.raises(IntakeError):
        approved_preflight(raw, review)


@pytest.mark.parametrize("change", ["arm64", "no_transform", "privileged", "online", "image_processed",
                                     "gpu", "wrong_abi", "no_closure", "no_limits", "prototype_no_model_api"])
def test_incomplete_or_wrong_native_target_cannot_authorize_intake(change):
    raw, review = synthetic_review()
    value = json.loads(raw)
    if change == "arm64":
        value["host_architecture"] = "aarch64"
    elif change == "no_transform":
        value["native"]["native_transform_executed"] = False
    elif change == "privileged":
        value["native"]["nonroot"] = False
    elif change == "online":
        value["native"]["internet_probe_denied"] = False
    elif change == "image_processed":
        value["native"]["images_processed"] = 1
    elif change == "gpu":
        value["native"]["cuda"] = True
    elif change == "wrong_abi":
        value["native"]["soabi"] = "cpython-313t"
    elif change == "no_closure":
        value["native"]["runtime_dependency_inventory"] = {}
    elif change == "no_limits":
        value.pop("resource_limits")
    else:
        value["native"]["model_execution_api_available"] = False
    altered = json.dumps(value).encode()
    review["preflight_result_sha256"] = hashlib.sha256(altered).hexdigest()
    with pytest.raises(IntakeError):
        approved_preflight(altered, review)


@pytest.mark.parametrize("field,value", [("id", "shape_predictor_68_face_landmarks.dat.bz2"),
                                         ("url", "https://raw.githubusercontent.com/other/model"),
                                         ("size", 1234)])
def test_unapproved_model_or_modified_manifest_rejected_before_network(field, value):
    row = deepcopy(plan()[0])
    row[field] = value
    with pytest.raises(IntakeError, match="allowlist"):
        download(row, set())


@pytest.mark.parametrize("url", ["http://huggingface.co/file", "https://unapproved.invalid/file",
                                 "https://huggingface.co:444/file", "https://user@huggingface.co/file",
                                 "https://huggingface.co/file#fragment"])
def test_redirect_denied_before_contact_with_other_destination(url):
    handler = RestrictedRedirect({"huggingface.co"})
    with pytest.raises(IntakeError):
        handler.redirect_request(None, None, 302, "", {}, url)


def test_looping_redirect_denied_before_network():
    handler = RestrictedRedirect({"huggingface.co"})
    handler.hops = 3
    with pytest.raises(IntakeError):
        handler.redirect_request(None, None, 302, "", {}, "https://huggingface.co/file")


def test_exact_metadata_only_image_transport_policy():
    assert image_transport_policy() == {"us.aws.cdn.hf.co"}


def test_current_policy_blocks_before_any_review_read_or_network(tmp_path):
    from tools.phase2e.intake import acquire
    with pytest.raises(IntakeError, match="Acquisition blocked"):
        acquire(tmp_path / "unused-quarantine", tmp_path / "unused-keys",
                tmp_path / "nonexistent-result", tmp_path / "nonexistent-review")
    assert not (tmp_path / "unused-quarantine").exists() and not (tmp_path / "unused-keys").exists()


@pytest.mark.parametrize("change", ["host", "missing_reference", "changed_hash"])
def test_changed_transport_policy_denied_without_fetching_images(change, tmp_path, monkeypatch):
    from tools.phase2e import intake
    data = json.loads(intake.TRANSPORT_POLICY.read_text())
    if change == "host":
        data["reviewed_image_redirect_hosts"] = ["elsewhere.invalid"]
    elif change == "missing_reference":
        data["records"].pop()
    else:
        data["records"][0]["lfs_sha256"] = "0" * 64
    path = tmp_path / "synthetic-policy.json"
    path.write_text(json.dumps(data))
    monkeypatch.setattr(intake, "TRANSPORT_POLICY", path)
    with pytest.raises(IntakeError):
        image_transport_policy()
