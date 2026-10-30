"""Executed inside the offline builder; inventory exact build output and notices."""

import hashlib
import importlib.metadata
import json
import platform
import subprocess
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if not __debug__:
        raise RuntimeError("Build-manifest assertions cannot be disabled")
    root = Path("/build")
    output = root / "evidence"
    output.mkdir()
    notices = output / "dependency-notices"
    notices.mkdir()
    wheel, = (root / "dist").glob("*.whl")
    source = json.loads((root / "source-receipt.json").read_text())
    dependencies = json.loads((root / "dependency-lock.json").read_text())
    components = []
    for package in dependencies["packages"]:
        distribution = importlib.metadata.distribution(package["name"])
        assert distribution.version == package["version"]
        licenses = []
        for item in distribution.files or []:
            if any(token in str(item).lower() for token in ["license", "licence", "copying", "copyright", "notice"]):
                path = Path(distribution.locate_file(item))
                if path.is_file():
                    licenses.append({"path": str(item), "sha256": digest(path)})
                    (notices / (package["name"] + "-" + digest(path) + ".txt")).write_bytes(path.read_bytes())
        assert licenses, "Missing exact dependency license evidence"
        components.append({"type": "library", "name": package["name"], "version": package["version"],
                           "hashes": [{"alg": "SHA-256", "content": package["sha256"]}],
                           "properties": [{"name": "license-evidence", "value": json.dumps(licenses, sort_keys=True)}]})
    source_notices = [root / "source/LICENSE.txt", root / "source/dlib/LICENSE.txt",
                      root / "source/dlib/external/pybind11/LICENSE"]
    for p in source_notices:
        (output / p.parent.name).mkdir(exist_ok=True)
        (output / p.parent.name / p.name).write_bytes(p.read_bytes())
    packages = subprocess.check_output(["dpkg-query", "-W", "-f=${Package}\t${Version}\n"], text=True)
    for line in packages.splitlines():
        name, version = line.split("\t")
        components.append({"type": "operating-system", "name": name, "version": version})
        copyright = Path("/usr/share/doc") / name / "copyright"
        if copyright.is_file():
            (notices / (name.replace(":", "_") + "-copyright.txt")).write_bytes(copyright.read_bytes())
    sbom = {"bomFormat": "CycloneDX", "specVersion": "1.6", "version": 1, "components": components,
            "metadata": {"component": {"type": "library", "name": "foc-dlib-native-closed-interface", "version": "0.2.0"}}}
    # Inventory is not a claim that every transitive native license/security issue is resolved.
    (output / "sbom.cdx.json").write_text(json.dumps(sbom, indent=2) + "\n")
    (output / "source-receipt.json").write_text(json.dumps(source, indent=2) + "\n")
    (output / "source-policy-audit.json").write_bytes((root / "source-policy-audit.json").read_bytes())
    cache = root / "native-build/CMakeCache.txt"
    for key in ["DLIB_PNG_SUPPORT", "DLIB_JPEG_SUPPORT", "DLIB_USE_CUDA", "DLIB_USE_BLAS"]:
        assert key + ":BOOL=OFF" in cache.read_text()
    assert not (root / "source/dlib/image_processing/frontal_face_detector.h").exists()
    for p in Path("/runtime-notices").iterdir():
        (output / p.name).write_bytes(p.read_bytes())
    module, = (root / 'native-build').glob('_foc_dlib_native*.so')
    # Avoid demangler recursion/truncation and matches inside nested C++ names.
    # Exact GNU/Itanium namespace+length prefixes and TEXT symbols are required.
    symbols = subprocess.check_output(['nm', '--defined-only', str(module)], text=True)
    names = ['compiled_parse_cnn', 'compiled_parse_predictor', 'compiled_parse_encoder',
             'compiled_run_cnn', 'compiled_run_predictor', 'compiled_run_encoder']
    linked = {}
    witnesses = []
    for name in names:
        prefix = '_ZN3foc'+str(len(name))+name+'E'
        found = [s for s in symbols.splitlines() if len(s.split()) == 3 and s.split()[1] in {'t', 'T'}
                 and s.split()[2].startswith(prefix) and '.' not in s.split()[2]]
        print(json.dumps({'component_symbol': name, 'exact_text_matches': len(found)}), flush=True)
        assert len(found) == 1, 'Real component method missing from linked native module: '+name
        linked[name] = hashlib.sha256(found[0].encode()).hexdigest()
        witnesses.append(found[0])
    (output / 'component-symbols.txt').write_text('\n'.join(witnesses)+'\n')
    dependency_files = {}
    for dep in (root / 'native-build').rglob('*.o.d'):
        for name in dep.read_text().replace('\\\n', '').split()[1:]:
            # GCC depfiles retain ../ include spelling. Audit canonical actual
            # files against the lock instead of rejecting equivalent spellings.
            path = Path(name).resolve()
            if path.is_file():
                key = str(path)
                if key.startswith('/build/source/'):
                    assert key.removeprefix('/build/source/') in {r['path'] for r in source['entries']}
                dependency_files[key] = digest(path)
    assert dependency_files
    (output / 'compiled-dependencies.json').write_text(json.dumps(dependency_files, indent=2)+'\n')
    report = {"version": 3, "scope": "closed_component_interface_pending_second_review", "python": platform.python_version(),
              "architecture": platform.machine(), "source_commit": source["commit"],
              "source_receipt_sha256": digest(root / "source-receipt.json"),
              "dependency_lock_sha256": digest(root / "dependency-lock.json"),
              "wheel": {"name": wheel.name, "bytes": wheel.stat().st_size, "sha256": digest(wheel)},
              "cmake_version": subprocess.check_output(["cmake", "--version"], text=True).splitlines()[0],
              "compiler": subprocess.check_output(["c++", "--version"], text=True).splitlines()[0],
              "runtime_native_libraries": {p.name: digest(p) for p in Path("/runtime-libs").iterdir()},
              "runtime_native_notices": {p.name: digest(p) for p in Path("/runtime-notices").iterdir()},
              "cmake_cache_sha256": digest(cache), "sbom_sha256": digest(output / "sbom.cdx.json"),
              "source_policy_audit_sha256": digest(output / 'source-policy-audit.json'),
              "compiled_dependencies_sha256": digest(output / 'compiled-dependencies.json'),
              "linked_component_methods": linked,
              "component_symbols_sha256": digest(output / 'component-symbols.txt'),
              "native_contract_binary_sha256": digest(root / 'native-build/native_contract_tests'),
              "known_embedded_model_headers": 0, "standard_python_bindings_included": False,
              "pretrained_assets_present": False,
              "pretrained_asset_flag_scope": "no serialized model files; exact source RGB preprocessing constants retained",
              "transitive_review": "pending",
              "model_execution_api_available": False, "A1b_accepted": False}
    (output / "build-manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    (output / "CMakeCache.txt").write_bytes(cache.read_bytes())


if __name__ == "__main__":
    main()
