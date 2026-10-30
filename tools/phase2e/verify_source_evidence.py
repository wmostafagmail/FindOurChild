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
            assert (lock['version'], len(lock['entries'])) in {(2, 1141), (3, 1114)}
            assert not any(r["path"].startswith("tools/python/") for r in lock["entries"])
            assert build["known_embedded_model_headers"] == 0 and build["model_execution_api_available"] is False
            assert native["model_execution_api_available"] is False and native["native_negative_checks"] == 5
            assert result["A1b_accepted"] is False
            proof["status"] = "minimal_source_prototype_verified_pending_design_review"
            proof["A1b_accepted"] = False
            if lock['version'] == 3:
                assert build['version'] == 3 and build['scope'] == 'closed_component_interface_pending_second_review'
                assert len(build['linked_component_methods']) == 6
                assert set(build['linked_component_methods']) == {'compiled_parse_cnn', 'compiled_parse_predictor',
                    'compiled_parse_encoder', 'compiled_run_cnn', 'compiled_run_predictor', 'compiled_run_encoder'}
                assert all(re.fullmatch('[a-f0-9]{64}', d) for d in build['linked_component_methods'].values())
                symbols = one('/sanitized/component-symbols.txt')
                assert hashlib.sha256(symbols).hexdigest() == build['component_symbols_sha256']
                actual_methods = {}
                for line in symbols.decode().splitlines():
                    fields = line.split()
                    assert len(fields) == 3 and fields[1] in {'t', 'T'} and '.' not in fields[2]
                    match = re.match(r'^_ZN3foc(\d+)(compiled_(?:parse|run)_[a-z]+)E', fields[2])
                    assert match and int(match[1]) == len(match[2]) and match[2] not in actual_methods
                    actual_methods[match[2]] = hashlib.sha256(line.encode()).hexdigest()
                assert actual_methods == build['linked_component_methods']
                inventory = json.loads(blob('config/phase2e/native-test-inventory.json'))
                interface = native['closed_interface_tests']
                streams = native['stream_integrity_tests']
                assert interface['tests'] == [{'id': n, 'status': 'passed'} for n in inventory['interface_cases']]
                assert streams['tests'] == [{'id': n, 'status': 'passed'} for n in inventory['stream_cases']]
                assert streams['model_deserializations'] == 0 and interface['model_inference_executed'] is False
                for key in ['model_open_attempts', 'deserialization_attempts', 'inference_attempts']:
                    assert interface['boundary_counters'][key] == 0
                assert native['native_threads'] == 1 and native['peak_rss_kib'] < 262144
                assert native['process_limits'] == {'cpu_seconds': 10, 'core_bytes': 0,
                                                   'file_bytes': 1048576, 'open_files': 64}
                for name, field in [('source-policy-audit.json', 'source_policy_audit_sha256'),
                                    ('compiled-dependencies.json', 'compiled_dependencies_sha256')]:
                    assert hashlib.sha256(one('/sanitized/'+name)).hexdigest() == build[field]
                audit_source = json.loads(one('/sanitized/source-policy-audit.json'))
                assert audit_source['unresolved_heuristic_hits'] == 0 and audit_source['universal_absence_claim'] is False
                expected = {r['path']: {'path': r['path'], 'sha256': r['sha256'], 'git_blob': r['git_blob']}
                            for r in receipt['entries']}
                assert audit_source['files'] == list(expected.values())
                dependencies = json.loads(one('/sanitized/compiled-dependencies.json'))
                assert dependencies and all(re.fullmatch('[a-f0-9]{64}', d) for d in dependencies.values())
                for path, digest in dependencies.items():
                    if path.startswith('/build/source/'):
                        assert expected[path.removeprefix('/build/source/')]['sha256'] == digest
                    elif path.startswith('/build/native/'):
                        assert hashlib.sha256(blob('services/demo_recognition/native/'+path.removeprefix('/build/native/'))).hexdigest() == digest
                proof['source_only_native_cases_passed'] = len(interface['tests'])+len(streams['tests'])
                proof['status'] = 'closed_interface_verified_second_A1b_review_pending'
        print(json.dumps(proof, indent=2))


if __name__ == "__main__":
    main()
