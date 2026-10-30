"""Data-free ABI/native transform check. Never loads a model or infers a face."""

import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import socket
import subprocess
import sys
import sysconfig
import time
from pathlib import Path

import _foc_dlib_native as native
import numpy as np
from interface_checks import checks as interface_checks


def file_hash(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(65536):
            value.update(block)
    return value.hexdigest()


def dependency_inventory():
    # Source-only container: no photographs, models, host mounts or credentials.
    # Record actual loaded ELF bytes, including NumPy's bundled native libraries.
    libraries = {}
    for line in Path("/proc/self/maps").read_text().splitlines():
        fields = line.split()
        if len(fields) == 6 and fields[5].startswith("/") and ".so" in fields[5]:
            path = Path(fields[5])
            libraries[str(path)] = {"sha256": file_hash(path), "bytes": path.stat().st_size}
    packages = {d.metadata["Name"]: d.version for d in importlib.metadata.distributions()}
    debian = subprocess.check_output(["dpkg-query", "-W", "-f=${Package}\t${Version}\n"], text=True)
    return {"loaded_libraries": libraries, "python_packages": packages,
            "debian_packages": dict(row.split("\t") for row in debian.splitlines())}


def main():
    if not __debug__:
        raise RuntimeError("Native qualification assertions cannot be disabled")
    started = time.monotonic()
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1048576, 1048576))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    assert sys.version_info[:3] == (3, 13, 13)
    assert platform.machine() == "x86_64"
    assert native.dlib_version == "20.0.0"
    assert native.interface_version == "foc-dlib-closed-interface-v2"
    assert native.cuda_enabled is False and native.avx_enabled is False
    assert native.model_execution_api_available is False
    assert not hasattr(native, "get_frontal_face_detector")
    assert not hasattr(native, "load_image")
    assert not hasattr(native, "deserialize")
    assert native.compiled_cnn_type_bytes > 0 and native.compiled_encoder_type_bytes > 0
    assert native.compiled_predictor_type_bytes > 0
    for name in ["align_chip", "align_chip_batch"]:
        assert callable(getattr(native, name))
    assert os.getuid() == 10001
    status = Path("/proc/self/status").read_text()
    assert "CapEff:\t0000000000000000" in status and "NoNewPrivs:\t1" in status
    for destination in ["/root-write-test", "/opt/qualification/write-test"]:
        try:
            Path(destination).write_text("forbidden")
        except OSError:
            pass
        else:
            raise AssertionError("Read-only boundary failed")
    with socket.socket() as probe:
        probe.settimeout(0.2)
        assert probe.connect_ex(("1.1.1.1", 443)) != 0
    # Purely generated colored pixels and fictional coordinates; no photo bytes.
    rows, cols = np.indices((256, 256), dtype=np.uint16)
    image = np.stack((rows % 256, cols % 256, (rows + cols) % 256), axis=2).astype(np.uint8)
    points = [[174, 100], [145, 100], [81, 100], [110, 100], [128, 145]]
    chip = native.align_chip(image, points)
    explicit = native.align_chip_batch(image, points)
    assert chip.shape == (150, 150, 3) and chip.dtype == np.uint8
    assert np.array_equal(chip, explicit) and np.array_equal(chip, native.align_chip(image, points))
    assert np.std(chip) > 0 and not np.array_equal(chip[:, :, 0], chip[:, :, 1])
    negative_checks = 0
    for bad_image, bad_points in [(image.astype(np.float32), points), (image[::-1], points),
                                 (image, points[:4]), (image, points + points),
                                 (image, [[-1, 100], *points[1:]])]:
        try:
            native.align_chip(bad_image, bad_points)
        except (TypeError, ValueError):
            negative_checks += 1
        else:
            raise AssertionError("Invalid source-probe input accepted")
    assert negative_checks == 5
    interface = interface_checks(image, chip)
    stream_tests = json.loads(subprocess.check_output(["/opt/qualification/native_contract_tests"], text=True, timeout=10))
    inventory = json.loads(Path('/opt/qualification/native-test-inventory.json').read_text())
    for expected, actual in [(inventory['interface_cases'], interface['tests']),
                             (inventory['stream_cases'], stream_tests['tests'])]:
        assert actual == [{'id': name, 'status': 'passed'} for name in expected]
    assert stream_tests['model_deserializations'] == 0
    assert len(list(Path('/proc/self/task').iterdir())) == 1
    assert all(os.environ.get(name) == '1' for name in ['DLIB_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS'])
    assert not list(Path("/opt").rglob("*.dat")) and not list(Path("/opt").rglob("*.bz2"))
    report = {
        "closed_interface_tests": interface, "stream_integrity_tests": stream_tests,
        "process_limits": {"cpu_seconds": 10, "core_bytes": 0, "file_bytes": 1048576, "open_files": 64},
        "native_threads": len(list(Path('/proc/self/task').iterdir())),
        "scope": "data_free_source_only_preflight", "python": platform.python_version(),
        "soabi": sysconfig.get_config_var("SOABI"), "gil_disabled": bool(sysconfig.get_config_var("Py_GIL_DISABLED")),
        "architecture": platform.machine(), "dlib": native.dlib_version,
        "cuda": native.cuda_enabled, "avx": native.avx_enabled,
        "native_interface_version": native.interface_version,
        "model_execution_api_available": False, "A1b_accepted": False,
        "bundled_pretrained_components": [], "native_negative_checks": negative_checks,
        "native_transform_executed": True, "explicit_chip_parity": True,
        "chip_output_sha256": hashlib.sha256(chip.tobytes()).hexdigest(),
        "model_files_loaded": 0, "images_processed": 0, "inference_executed": False,
        "nonroot": True, "read_only": True, "capabilities_dropped": True, "internet_probe_denied": True,
        "elapsed_ms": (time.monotonic() - started) * 1000,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "runtime_dependency_inventory": dependency_inventory(),
    }
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
