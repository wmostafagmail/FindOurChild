"""Data-free ABI/native transform check. Never loads a model or infers a face."""

import hashlib
import json
import os
import platform
import resource
import socket
import sys
import time
from pathlib import Path

import dlib
import numpy as np


def main():
    started = time.monotonic()
    assert sys.version_info[:3] == (3, 13, 13)
    assert platform.machine() == "x86_64"
    assert dlib.__version__ == "20.0.0"
    assert not dlib.DLIB_USE_CUDA and not dlib.USE_AVX_INSTRUCTIONS
    for name in ["cnn_face_detection_model_v1", "shape_predictor", "face_recognition_model_v1",
                 "get_face_chip", "get_face_chip_details", "extract_image_chip", "full_object_detection"]:
        assert callable(getattr(dlib, name))
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
    landmarks = dlib.points([dlib.point(174, 100), dlib.point(145, 100), dlib.point(81, 100),
                            dlib.point(110, 100), dlib.point(128, 145)])
    shape = dlib.full_object_detection(dlib.rectangle(48, 48, 207, 207), landmarks)
    chip = dlib.get_face_chip(image, shape, size=150, padding=0.25)
    details = dlib.get_face_chip_details(shape, size=150, padding=0.25)
    explicit = dlib.extract_image_chip(image, details)
    assert chip.shape == (150, 150, 3) and chip.dtype == np.uint8
    assert np.array_equal(chip, explicit) and np.array_equal(chip, dlib.get_face_chip(image, shape))
    assert np.std(chip) > 0 and not np.array_equal(chip[:, :, 0], chip[:, :, 1])
    assert dlib.length(dlib.dpoint(3.0, 4.0)) == 5.0
    assert not list(Path("/opt").rglob("*.dat")) and not list(Path("/opt").rglob("*.bz2"))
    report = {
        "scope": "data_free_source_only_preflight", "python": platform.python_version(),
        "architecture": platform.machine(), "dlib": dlib.__version__, "cuda": False, "avx": False,
        "native_transform_executed": True, "explicit_chip_parity": True,
        "chip_output_sha256": hashlib.sha256(chip.tobytes()).hexdigest(),
        "model_files_loaded": 0, "images_processed": 0, "inference_executed": False,
        "nonroot": True, "read_only": True, "capabilities_dropped": True, "internet_probe_denied": True,
        "elapsed_ms": (time.monotonic() - started) * 1000,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
