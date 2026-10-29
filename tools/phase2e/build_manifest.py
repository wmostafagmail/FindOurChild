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
    root = Path("/build")
    output = root / "evidence"
    output.mkdir()
    wheel, = (root / "source/dist").glob("*.whl")
    source = json.loads((root / "source-receipt.json").read_text())
    dependencies = json.loads((root / "dependency-lock.json").read_text())
    components = []
    for package in dependencies["packages"]:
        distribution = importlib.metadata.distribution(package["name"])
        assert distribution.version == package["version"]
        licenses = []
        for item in distribution.files or []:
            if "license" in str(item).lower() or "copying" in str(item).lower():
                path = Path(distribution.locate_file(item))
                if path.is_file():
                    licenses.append({"path": str(item), "sha256": digest(path)})
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
    sbom = {"bomFormat": "CycloneDX", "specVersion": "1.6", "version": 1, "components": components,
            "metadata": {"component": {"type": "library", "name": "dlib-source-only-qualification", "version": "20.0.0"}}}
    # Inventory is not a claim that every transitive native license/security issue is resolved.
    (output / "sbom.cdx.json").write_text(json.dumps(sbom, indent=2) + "\n")
    (output / "source-receipt.json").write_text(json.dumps(source, indent=2) + "\n")
    cache, = (root / "source/build").glob("temp.*/CMakeCache.txt")
    assert "DLIB_PNG_SUPPORT:BOOL=ON" in cache.read_text()
    assert "PNG_LIBRARY_RELEASE:FILEPATH=/usr/lib/" in cache.read_text()
    assert "DLIB_JPEG_SUPPORT:BOOL=ON" in cache.read_text()
    assert "JPEG_LIBRARY_RELEASE:FILEPATH=/usr/lib/" in cache.read_text()
    for p in Path("/runtime-notices").iterdir():
        (output / p.name).write_bytes(p.read_bytes())
    report = {"version": 1, "scope": "data_free_cpu_build_only", "python": platform.python_version(),
              "architecture": platform.machine(), "source_commit": source["commit"],
              "source_receipt_sha256": digest(root / "source-receipt.json"),
              "dependency_lock_sha256": digest(root / "dependency-lock.json"),
              "wheel": {"name": wheel.name, "bytes": wheel.stat().st_size, "sha256": digest(wheel)},
              "cmake_version": subprocess.check_output(["cmake", "--version"], text=True).splitlines()[0],
              "compiler": subprocess.check_output(["c++", "--version"], text=True).splitlines()[0],
              "runtime_native_libraries": {p.name: digest(p) for p in Path("/runtime-libs").iterdir()},
              "runtime_native_notices": {p.name: digest(p) for p in Path("/runtime-notices").iterdir()},
              "cmake_cache_sha256": digest(cache), "sbom_sha256": digest(output / "sbom.cdx.json"),
              "pretrained_assets_present": False, "transitive_review": "pending"}
    (output / "build-manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    (output / "CMakeCache.txt").write_bytes(cache.read_bytes())


if __name__ == "__main__":
    main()
