"""Independent stdlib audit of source-only qualification ZIP against Git objects.

python -m tools.phase2e.verify_source_evidence META_JSON ARCHIVE HEAD GIT_DIR
Metadata must be fetched independently from GitHub's artifact API over TLS.
No application runner, test helper, fixture, dlib or model loader is imported.
"""

import hashlib
import json
import re
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path


def main():
    if not __debug__:
        raise SystemExit("Evidence assertions cannot be disabled")
    meta_path, archive_path, sha, git_dir = sys.argv[1:]
    assert re.fullmatch(r"[a-f0-9]{40}", sha)
    metadata = json.loads(Path(meta_path).read_text())
    archive = Path(archive_path).read_bytes()
    assert metadata["digest"] == "sha256:" + hashlib.sha256(archive).hexdigest()

    def blob(path):
        return subprocess.check_output(["git", "--git-dir=" + git_dir, "show", sha + ":" + path])

    tracked = subprocess.check_output(["git", "--git-dir=" + git_dir, "ls-tree", "-r", "--name-only", sha], text=True).splitlines()
    expected_sources = {p for p in tracked if p.startswith(("tools/phase2e/", "services/demo_recognition/",
                                                           "config/phase2e/", "tests/phase2e/"))}
    expected_sources.update({".github/workflows/phase2e-source-preflight.yml", "docs/phase2e/e0-required-tests.json"})
    with zipfile.ZipFile(Path(archive_path)) as z:
        names = [name for name in z.namelist() if not name.endswith("/")]
        assert len(names) == len(set(names)) and all(not n.startswith("/") and ".." not in Path(n).parts for n in names)
        assert all(not n.endswith((".dat", ".bz2", ".png", ".jpg", ".enc", ".key", ".whl", ".so")) for n in names)

        def one(suffix):
            found = [n for n in names if n.endswith(suffix)]
            assert len(found) == 1, suffix
            return z.read(found[0])

        checks = json.loads(one("/sanitized/checksums.json"))
        for path, digest in checks.items():
            assert re.fullmatch(r"[a-f0-9]{64}", digest) and not Path(path).is_absolute() and ".." not in Path(path).parts
            assert hashlib.sha256(one("/sanitized/" + path)).hexdigest() == digest
        sanitized = {n.split("/sanitized/", 1)[1] for n in names if "/sanitized/" in n} - {"checksums.json"}
        assert set(checks) == sanitized
        controls = json.loads(one("/phase2e-e0-controls/results.json"))
        assert set(controls["source_manifest"]) == expected_sources
        for path, digest in controls["source_manifest"].items():
            assert hashlib.sha256(blob(path)).hexdigest() == digest, path
        required = json.loads(blob("docs/phase2e/e0-required-tests.json"))["e0_controls"]
        assert Counter(t["id"] for t in controls["tests"]) == Counter(required) and required
        assert all(t["status"] == "passed" for t in controls["tests"]) and controls["exit_code"] == 0
        assert controls["native_model_tests_executed"] == 0 and controls["model_inference"] == "not_executed"
        audit = json.loads(one("/phase2e-e0-controls/dependency-audit.json"))
        assert not audit["fixes"] and all(not p["vulns"] for p in audit["dependencies"])
        result = json.loads(one("/sanitized/source-only-result.json"))
        assert result["head_sha"] == sha and result["scope"] == "data_free_source_only_preflight"
        assert result["E0_complete"] is False and result["model_acquisition_authorized"] is False
        native = result["native"]
        assert native == json.loads(one("/raw/native.log"))
        assert (native["dlib"], native["python"], native["architecture"]) == ("20.0.0", "3.13.13", "x86_64")
        assert native["cuda"] is False and native["avx"] is False
        assert native["model_files_loaded"] == native["images_processed"] == 0 and native["inference_executed"] is False
        assert all(native[p] is True for p in ["native_transform_executed", "explicit_chip_parity", "nonroot",
                                               "read_only", "capabilities_dropped", "internet_probe_denied"])
        build = json.loads(one("/sanitized/build-manifest.json"))
        assert build["source_commit"] == "2e0b3846b4dcd0953951a9c0172503c666975229"
        assert build["dependency_lock_sha256"] == hashlib.sha256(blob("config/phase2e/build-dependencies.json")).hexdigest()
        assert build["source_receipt_sha256"] == hashlib.sha256(one("/sanitized/source-receipt.json")).hexdigest()
        assert build["sbom_sha256"] == hashlib.sha256(one("/sanitized/sbom.cdx.json")).hexdigest()
        receipt = json.loads(one("/sanitized/source-receipt.json"))
        lock = json.loads(blob("config/phase2e/source-projection.json"))
        assert receipt["lock_sha256"] == hashlib.sha256(blob("config/phase2e/source-projection.json")).hexdigest()
        assert len(receipt["entries"]) == len(lock["entries"])
        assert receipt["model_files_acquired"] == receipt["dataset_images_acquired"] == 0
        for actual, expected in zip(receipt["entries"], lock["entries"], strict=True):
            assert {k: actual[k] for k in expected} == expected and re.fullmatch(r"[a-f0-9]{64}", actual["sha256"])
        assert hashlib.sha256(one("/sanitized/CMakeCache.txt")).hexdigest() == build["cmake_cache_sha256"]
        proof = {"head_sha": sha, "artifact_id": metadata["id"], "archive_sha256": hashlib.sha256(archive).hexdigest(),
                 "source_only_controls_passed": len(required), "source_inputs_verified": len(expected_sources),
                 "upstream_source_blobs": len(receipt["entries"]), "sanitized_payload_checksums": len(checks),
                 "build": build, "native": native, "independent_human_review": "pending",
                 "E0_complete": False, "native_inference_tests": 0, "status": "source_only_verified"}
        forbidden = [r["path"] for r in lock["entries"] if r["path"].endswith("/frontal_face_detector.h")]
        if forbidden:
            proof["status"] = "integrity_verified_source_policy_blocked"
            proof["unexpected_pretrained_source_components"] = forbidden
            proof["A1b_accepted"] = False
        else:
            assert lock["version"] == 2 and len(lock["entries"]) == 1141
            assert not any(r["path"].startswith("tools/python/") for r in lock["entries"])
            assert build["known_embedded_model_headers"] == 0 and build["model_execution_api_available"] is False
            assert native["model_execution_api_available"] is False and native["native_negative_checks"] == 5
            assert result["A1b_accepted"] is False
            proof["status"] = "minimal_source_prototype_verified_pending_design_review"
            proof["A1b_accepted"] = False
        print(json.dumps(proof, indent=2))


if __name__ == "__main__":
    main()
