"""Fetch a reviewed code-only projection, never an upstream archive or model.

Transport accepts only the exact URLs, sizes and Git blobs in the committed lock.
This acquisition identity is not linked into the offline worker image.
"""

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import traceback
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
COMMIT = "2e0b3846b4dcd0953951a9c0172503c666975229"
TREE = "f7b2ad020a481144c4ccb3c47d24d654bbad2732"
LOCK = ROOT / "config/phase2e/source-projection.json"
MAX_FILE = 2_000_000
MAX_TOTAL = 30_000_000
ROOT_FILES = {"LICENSE.txt", "README.md"}
FORBIDDEN_EMBEDDED_MODELS = {"frontal_face_detector.h", "frontal_face_detector_abstract.h"}
SUFFIXES = {".h", ".hpp", ".cpp", ".c", ".cmake", ".txt", ".in", ".py", ".cu", ".rst", ".toml"}
EXTENSIONLESS = {
    "cassert", "cstring", "fstream", "iomanip", "iosfwd", "iostream", "istream",
    "locale", "ostream", "sstream", "release_build_by_default", "LICENSE", "README",
}


class ProjectionError(ValueError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ProjectionError("Redirect prohibited")


def allowed_path(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_./+-]+", value):
        return False
    p = PurePosixPath(value)
    if str(p) != value or p.is_absolute() or any(x in {"..", ".", ""} for x in p.parts):
        return False
    if value in ROOT_FILES:
        return True
    if not value.startswith("dlib/") or p.name in FORBIDDEN_EMBEDDED_MODELS:
        return False
    if value in {"dlib/gui_widgets/fonts.h", "dlib/gui_widgets/fonts_abstract.h"}:
        return True
    if value.startswith(("dlib/gui_widgets/", "dlib/gui_core/")) or value in {"dlib/gui_widgets.h", "dlib/gui_core.h"}:
        return False
    if value == "dlib/data_io/image_dataset_metadata.cpp":
        return False
    if value == "dlib/python.h" or value.startswith("dlib/python/"):
        return False
    if any(x in p.parts for x in ("test", "tests", "examples", "docs", "java", "matlab")):
        return False
    if value.startswith("dlib/external/") and not value.startswith("dlib/external/pybind11/"):
        return False
    return p.suffix in SUFFIXES or p.name in EXTENSIONLESS


def validate_lock(lock):
    if set(lock) != {"version", "commit", "tree", "scope", "entries"}:
        raise ProjectionError("Unknown projection fields")
    if (lock["version"], lock["commit"], lock["tree"], lock["scope"]) != (
        3, COMMIT, TREE, "minimal_fixed_interface_no_gui_or_pretrained_payloads"
    ):
        raise ProjectionError("Unapproved source identity")
    rows = lock["entries"]
    if not isinstance(rows, list) or not 500 <= len(rows) <= 2000:
        raise ProjectionError("Projection inventory outside limits")
    paths = []
    total = 0
    for row in rows:
        if set(row) != {"path", "git_blob", "bytes"} or not allowed_path(row["path"]):
            raise ProjectionError("Unapproved source path")
        if not re.fullmatch(r"[a-f0-9]{40}", row["git_blob"]):
            raise ProjectionError("Missing Git blob identity")
        if type(row["bytes"]) is not int or not 0 < row["bytes"] <= MAX_FILE:
            raise ProjectionError("Source file outside limits")
        paths.append(row["path"])
        total += row["bytes"]
    if paths != sorted(set(paths)) or total > MAX_TOTAL:
        raise ProjectionError("Duplicate/unordered/oversized projection")
    if not ROOT_FILES.issubset(paths) or "dlib/external/pybind11/LICENSE" not in paths:
        raise ProjectionError("Missing source notice")
    return rows


def verify_blob(data, row):
    if len(data) != row["bytes"] or b"\0" in data:
        raise ProjectionError("Not exact text source")
    if any(marker in data for marker in [b"get_serialized_frontal_faces", b"base64 encoded data from the file 'object_detector.dat'"]):
        raise ProjectionError("Unexpected embedded pretrained payload; no build permitted")
    actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if actual != row["git_blob"]:
        raise ProjectionError("Source Git blob mismatch")
    return hashlib.sha256(data).hexdigest()


def fetch(row, destination):
    target = destination / row["path"]
    if target.exists() or target.is_symlink():
        raise ProjectionError("Refusing existing source destination")
    url = f"https://raw.githubusercontent.com/davisking/dlib/{COMMIT}/{row['path']}"
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    with opener.open(url, timeout=30) as response:
        if response.status != 200 or response.geturl() != url:
            raise ProjectionError("Unexpected source response")
        if response.headers.get("Content-Encoding", "identity") != "identity":
            raise ProjectionError("Encoded response prohibited")
        data = response.read(row["bytes"] + 1)
    digest = verify_blob(data, row)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as handle:
        handle.write(data)
    return {**row, "sha256": digest}


def acquire(destination):
    lock_bytes = LOCK.read_bytes()
    rows = validate_lock(json.loads(lock_bytes))
    # A fresh private directory is required. No pre-existing parent may be a symlink.
    if destination.exists() or any(p.is_symlink() for p in [destination, *destination.parents]):
        raise ProjectionError("Fresh non-symlink destination required")
    destination.mkdir(parents=True, mode=0o700)
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            entries = list(pool.map(lambda row: fetch(row, destination), rows))
    except (OSError, ValueError):
        # Preserve partial evidence; no retry to another ref or provider, no build receipt.
        failure = destination.parent / (destination.name + '-failure.log')
        with failure.open('x') as stream:
            stream.write(traceback.format_exc())
        os.chmod(failure, 0o600)
        raise ProjectionError("Projection acquisition failed; partial files retained privately") from None
    receipt = {
        "version": 3, "scope": "minimal_fixed_interface_no_gui_or_pretrained_payloads", "commit": COMMIT, "tree": TREE,
        "lock_sha256": hashlib.sha256(lock_bytes).hexdigest(), "entries": entries,
        "model_files_acquired": 0, "dataset_images_acquired": 0,
    }
    receipt_path = destination.parent / (destination.name + "-receipt.json")
    with receipt_path.open("x") as handle:
        json.dump(receipt, handle, indent=2)
        handle.write("\n")
    os.chmod(receipt_path, 0o600)
    print(json.dumps({"source_files": len(entries), "bytes": sum(r["bytes"] for r in rows),
                      "receipt_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest()}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    acquire(args.destination.absolute())


if __name__ == "__main__":
    main()
