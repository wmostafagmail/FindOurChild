"""Independent, data-free artifact verification; imports no application validator.

Usage: python tools/verify_owner_v3_evidence.py METADATA_JSON ZIP HEAD_SHA python|browser
Metadata must be the artifact object downloaded from the authenticated GitHub API.
This verifies engineering evidence, never human approval or neural qualification.
"""

import hashlib
import io
import json
import re
import struct
import subprocess
import sys
import zipfile
import zlib
from collections import Counter
from pathlib import Path


def h(data):
    return hashlib.sha256(data).hexdigest()


def main():
    root = Path(__file__).resolve().parents[1]
    metadata = json.loads(Path(sys.argv[1]).read_bytes())
    raw = Path(sys.argv[2]).read_bytes()
    head, kind = sys.argv[3:5]
    assert re.fullmatch("[a-f0-9]{40}", head) and kind in {"python", "browser"}
    assert metadata["digest"] == "sha256:" + h(raw) and metadata["expired"] is False
    assert metadata["workflow_run"]["head_sha"] == head

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=root)

    def committed(path):
        assert not Path(path).is_absolute() and ".." not in Path(path).parts
        return git("show", head + ":" + path)

    required = json.loads(committed("docs/phase2e/owner-only-demo/implementation/required-tests.json"))
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = [n for n in archive.namelist() if not n.endswith("/")]
        assert len(names) == len(set(names)) and all(not Path(n).is_absolute() and ".." not in Path(n).parts for n in names)
        assert sum(v.file_size for v in archive.infolist()) <= 128 * 1024 * 1024
        assert not any(n.endswith("failure.json") for n in names)
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["checkout_tree"] == git("rev-parse", head + "^{tree}").decode().strip()
        assert metadata["name"].endswith("-" + manifest["checkout"])
        sources = manifest["source_manifest"]
        tracked = git("ls-tree", "-r", "--name-only", head).decode().splitlines()
        bases = ["tools/phase2e/owner_only_v3", "tests/owner_only_v3", "tests/owner_only_v3_browser",
                 "database/owner_only_demo", "docs/phase2e/owner-only-demo"]
        expected_sources = {p for p in tracked if any(p.startswith(base + "/") for base in bases)}
        expected_sources.update([
            "services/api/foc_api/owner_only_demo.py", "services/api/foc_api/main.py",
            "e2e.owner-only-v3.config.ts", ".github/workflows/phase2e-owner-only-v3.yml",
            ".github/workflows/phase1a.yml", "tsconfig.e2e.json", "scripts/identity_setup.py",
            ".github/workflows/phase2e-owner-identity-preflight.yml",
            "scripts/owner_v3_test_fault.py", "apps/web/app/[locale]/demo-authorization/page.tsx",
            "apps/web/app/[locale]/demo-authorization/panel.tsx", "apps/web/app/demo-authorization/[...path]/route.ts",
            "apps/web/proxy.ts", "apps/web/app/style.css", "tools/verify_owner_v3_evidence.py",
            "pyproject.toml", "uv.lock", "package-lock.json",
        ])
        assert set(sources) == expected_sources, "Incomplete or unexpected V3 source inventory"
        for name, expected in sources.items():
            assert re.fullmatch("[a-f0-9]{64}", expected) and h(committed(name)) == expected, name
        source_digest = h(json.dumps(sources, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode())
        assert source_digest == manifest["source_digest"]
        payload = manifest["payload_sha256"]
        assert set(payload) == set(names) - {"manifest.json"}
        for name, expected in payload.items():
            assert h(archive.read(name)) == expected
        report = json.loads(archive.read("results.json"))
        assert report["source_digest"] == source_digest
        assert manifest["assets"] == 0 and manifest["inference"] is False
        proof = {"head": head, "checkout": manifest["checkout"], "tree": manifest["checkout_tree"],
                 "kind": kind, "artifact_id": metadata["id"], "zip_sha256": h(raw),
                 "source_digest": source_digest, "source_blobs_verified": len(sources),
                 "payload_files_verified": len(payload), "scope": "source_only_synthetic_engineering",
                 "real_owner_authorizations": 0, "assets": 0, "neural_inference": False}
        if kind == "python":
            assert Counter(r["selector"] for r in report["tests"]) == Counter(required["python"])
            assert len(report["tests"]) == 98 and all(r["status"] == "passed" for r in report["tests"])
            assert manifest["python_tests"] == 98 and manifest["python_scenarios"] == 90
            assert manifest["actual_owner_provisioning"] is False and manifest["actual_authorizations"] == 0
            assert manifest["recovery"]["restored_inactive"] is True and manifest["recovery"]["forced_rls_tables"] == 3
            assert manifest["database_p95_target_ms"] == 1000 and manifest["performance_gate"] == "unresolved_owner_demo_exception"
            assert len(manifest["probe_receipts"]) == 15
            for name, expected in manifest["probe_receipts"].items():
                data = archive.read("probe-receipts/" + name)
                assert h(data) == expected
                row = json.loads(data)
                assert row["limits"]["deadline_ms"] == 3000 and row["limits"]["memory_bytes"] == 134217728
                if row["native_metrics"] is not None:
                    assert row["native_metrics"]["inference"] is False
            for name, expected in manifest["build_outputs"].items():
                assert h(archive.read("source-only-build/" + name)) == expected
            proof.update(tests=98, scenario_selectors=90, native_probe_receipts=15,
                         build_outputs=manifest["build_outputs"], recovery=manifest["recovery"],
                         database_p95_target_ms=1000, performance_gate="unresolved_owner_demo_exception")
        else:
            targets = {f"{b}-{locale}-{width}" for b in ["chromium", "firefox", "webkit"]
                       for locale in ["ar-EG", "en-GB"] for width in [320, 360, 390, 1280]}
            traces = json.loads(archive.read("traces.json"))
            assert len(traces) == 144 and {(r["test"], r["target"]) for r in traces} == {
                (title, target) for title in required["browser_titles"] for target in targets}
            assert all(r["status"] == "passed" and set(r) == {"test", "target", "status", "steps"}
                       and all(set(s) == {"api", "status"} for s in r["steps"]) for r in traces)
            assert (report["total"], report["passed"], report["failed"]) == (144, 144, 0)
            assert report["browsers"] == {b: 48 for b in ["chromium", "firefox", "webkit"]}
            assert report["e2e_version"] == "0.21.3" and report["web_engine_version"] == "0.15.3"
            assert manifest["real_api_handlers"] is True and manifest["real_keycloak"] is True
            assert manifest["real_private_postgres"] is True and manifest["real_owner_provisioned"] is False
            screenshots = report["screenshots"]
            assert len(screenshots) == 144
            for name, expected in screenshots.items():
                assert re.fullmatch("[a-f0-9]{64}\\.png", name)
                data = archive.read("screenshots/" + name)
                assert h(data) == expected and data.startswith(b"\x89PNG\r\n\x1a\n")
                pos, kinds = 8, []
                while pos < len(data):
                    size = struct.unpack(">I", data[pos:pos + 4])[0]
                    chunk = data[pos + 4:pos + 8]
                    content = data[pos + 8:pos + 8 + size]
                    crc = struct.unpack(">I", data[pos + 8 + size:pos + 12 + size])[0]
                    assert chunk in {b"IHDR", b"PLTE", b"IDAT", b"IEND"} and zlib.crc32(chunk + content) & 0xFFFFFFFF == crc
                    kinds.append(chunk)
                    pos += size + 12
                assert pos == len(data) and kinds[0] == b"IHDR" and kinds[-1] == b"IEND" and b"IDAT" in kinds
            proof.update(tests=144, browsers=report["browsers"], sanitized_traces=144, sanitized_signed_out_shells=144,
                         checkpoint_fixture=manifest["checkpoint_fixture"])
        proof["status"] = "passed_engineering_evidence_only"
        print(json.dumps(proof, sort_keys=True))


if __name__ == "__main__":
    main()
