"""Independent encrypted quarantine byte audit; no scan/decode/unpack/model load.

This verifies actual bytes. It never represents independent human A3 approval.
python -m tools.phase2e.verify_intake QUARANTINE_DIR SEPARATE_KEY_DIR
"""

import hashlib
import json
import sys
from pathlib import Path
from uuid import UUID

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def main():
    if not __debug__:
        raise SystemExit("Integrity assertions cannot be disabled")
    quarantine, keys = map(Path, sys.argv[1:])
    assert quarantine != keys and quarantine.is_dir() and keys.is_dir()
    raw_manifest = (quarantine / "manifest.json").read_bytes()
    manifest = json.loads(raw_manifest)
    root = Path(__file__).resolve().parents[2]
    raw_proposal = (root / "docs/planning/demo/DEMO_ASSET_PROPOSAL.json").read_bytes()
    assert hashlib.sha256(raw_proposal).hexdigest() == "15764ebc11994cf469a2b13d43653255b44a32c771194994c21d99c12cda502d"
    proposal = json.loads(raw_proposal)
    expected = {r["path"]: {"kind": "weight", "bytes": r["size"], "git_blob": r["sha"]}
                for r in proposal["weights"]["files"]}
    for group in proposal["dataset"]["groups"]:
        for row in group["photos"]:
            expected[row["path"]] = {"kind": "image", "bytes": row["bytes"], "sha256": row["publisher_sha256"]}
    ids = [r["source_id"] for r in manifest["assets"]]
    model_ids = {r["path"] for r in proposal["weights"]["files"]}
    assert len(ids) == len(set(ids)) and set(ids) in [model_ids, set(expected)]
    assert manifest["status"] == "bytes_verified_pending_independent_review"
    assert manifest["independent_digest_review"] == "pending"
    for field in ["decompression_approved", "native_loading_allowed", "inference_allowed", "image_decoding_allowed", "operational_allowed"]:
        assert manifest[field] is False
    instance = str(UUID(manifest["instance"]))
    assert instance == manifest["instance"]
    key = (keys / "quarantine.key").read_bytes()
    assert len(key) == 32
    total, counts = 0, {"weight": 0, "image": 0}
    for asset in manifest["assets"]:
        opaque = str(UUID(asset["asset_id"]))
        assert opaque == asset["asset_id"]
        reference = expected[asset["source_id"]]
        assert asset["kind"] == reference["kind"] and asset["size"] == reference["bytes"]
        path = quarantine / (opaque + ".enc")
        assert not path.is_symlink() and path.stat().st_size == asset["size"] + 28
        sealed = path.read_bytes()
        assert hashlib.sha256(sealed).hexdigest() == asset["ciphertext_sha256"]
        aad = f"{instance}:{opaque}:{asset['sha256']}".encode()
        data = AESGCM(key).decrypt(sealed[:12], sealed[12:], aad)
        assert len(data) == reference["bytes"] and hashlib.sha256(data).hexdigest() == asset["sha256"]
        if asset["kind"] == "weight":
            git_blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            assert git_blob == reference["git_blob"] == asset["git_blob"]
        else:
            assert asset["sha256"] == reference["sha256"]
            assert asset["active_enrollment"] is False and asset["independent_visual_review"] == "pending"
            assert asset["capture_date"] is None and asset["capture_age"] is None
        total += len(data)
        counts[asset["kind"]] += 1
    print(json.dumps({"scope": "actual_encrypted_byte_integrity_only", "counts": counts, "bytes_verified": total,
                      "manifest_sha256": hashlib.sha256(raw_manifest).hexdigest(), "data_decoded": False,
                      "model_files_loaded": 0, "inference_executed": False,
                      "independent_human_A3_review": "pending", "status": "integrity_verified"}, indent=2))


if __name__ == "__main__":
    main()
