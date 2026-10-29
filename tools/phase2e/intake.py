"""A2/A3 encrypted byte intake only. Never decompresses, decodes or loads assets.

Requires an actual source-only result and its completed A1b technical review.
A3 independent digest review and every later gate remain separate prerequisites.
This is an operator CLI, with no application/browser approval or download route.
"""

import argparse
import hashlib
import json
import os
import re
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from tools.phase2e.quarantine import verify_bytes
from tools.phase2e.source_projection import ROOT

PROPOSAL = ROOT / "docs/planning/demo/DEMO_ASSET_PROPOSAL.json"
PROPOSAL_SHA256 = "15764ebc11994cf469a2b13d43653255b44a32c771194994c21d99c12cda502d"
A0 = "3fa889d0ac10bc5818e8ba1120d61536f54ddeb4b0837669b05d179c64ba9270"
MODELS_REV = "fd81b6308a6a73d4ce08859eb2f4b628a21e27a2"
DATASET_REV = "100262732989e77f38cd831d70a376a93735006a"
TOTAL_LIMIT = 160_000_000
TRANSPORT_POLICY = ROOT / "config/phase2e/transport-policy.json"


class IntakeError(ValueError):
    pass


def plan():
    raw = PROPOSAL.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PROPOSAL_SHA256:
        raise IntakeError("Frozen proposal changed")
    proposal = json.loads(raw)
    if proposal["weights"]["commit"] != MODELS_REV or proposal["dataset"]["commit"] != DATASET_REV:
        raise IntakeError("Unapproved repository revision")
    rows = []
    for weight in proposal["weights"]["files"]:
        rows.append({"id": weight["path"], "kind": "weight", "size": weight["size"],
                     "git_blob": weight["sha"], "sha256": None,
                     "url": f"https://raw.githubusercontent.com/davisking/dlib-models/{MODELS_REV}/{weight['path']}"})
    for group in proposal["dataset"]["groups"]:
        for image in group["photos"]:
            rows.append({"id": image["path"], "kind": "image", "size": image["bytes"],
                         "git_blob": None, "sha256": image["publisher_sha256"],
                         "url": f"https://huggingface.co/datasets/retowyss/Syn-Vis-v0/resolve/{DATASET_REV}/{image['path']}",
                         "group": group["fictional_group"], "partition": group["planned_partition"],
                         "planned_enrollment": group["planned_enrollment"], "active_enrollment": False})
    if len(rows) != 51 or len({r["id"] for r in rows}) != 51:
        raise IntakeError("Exact three-weight/48-image inventory required")
    if sum(r["size"] for r in rows) != 131436335 or any(not 0 < r["size"] <= 32_000_000 for r in rows):
        raise IntakeError("Artifact inventory byte limits changed")
    return rows


def approved_preflight(result_bytes, review):
    """Verify a local operator review binding, not manufacture an independent approval."""
    expected = {"gate", "decision", "owner_authorization_sha256", "preflight_result_sha256", "reviewer",
                "review_record_sha256", "critical_findings", "source_and_transitive_grants_reviewed"}
    if not isinstance(review, dict) or set(review) != expected:
        raise IntakeError("Closed completed A1b technical review required")
    if (review["gate"], review["decision"], review["owner_authorization_sha256"], review["critical_findings"],
        review["source_and_transitive_grants_reviewed"]) != ("A1b", "approved", A0, [], True):
        raise IntakeError("Pre-acquisition technical review not approved")
    if review["source_and_transitive_grants_reviewed"] is not True:
        raise IntakeError("Explicit technical review required")
    if review["preflight_result_sha256"] != hashlib.sha256(result_bytes).hexdigest():
        raise IntakeError("Technical review references different build evidence")
    if not isinstance(review["reviewer"], str) or not review["reviewer"]:
        raise IntakeError("Reviewer record required")
    if not re.fullmatch(r"[a-f0-9]{64}", review["review_record_sha256"]):
        raise IntakeError("Review record required")
    result = json.loads(result_bytes)
    native = result["native"]
    if result["scope"] != "data_free_source_only_preflight" or result["host_architecture"] != "x86_64":
        raise IntakeError("Native target not qualified")
    if result.get("resource_limits") != {"cpus": 2, "memory_bytes": 1073741824, "pids": 64, "timeout_seconds": 60}:
        raise IntakeError("Resource restriction proof missing or changed")
    if native.get("cuda") is not False or native.get("avx") is not False:
        raise IntakeError("Wrong CPU-only build profile")
    if native.get("soabi") != "cpython-313-x86_64-linux-gnu" or native.get("gil_disabled") is not False:
        raise IntakeError("Unqualified Python/native ABI")
    if not native.get("runtime_dependency_inventory", {}).get("loaded_libraries"):
        raise IntakeError("Actual native dependency closure missing")
    if (native["python"], native["dlib"], native["architecture"], native["model_files_loaded"],
        native["images_processed"], native["inference_executed"]) != ("3.13.13", "20.0.0", "x86_64", 0, 0, False):
        raise IntakeError("Wrong source-only compatibility result")
    for field in ["native_transform_executed", "explicit_chip_parity", "nonroot", "read_only",
                  "capabilities_dropped", "internet_probe_denied"]:
        if native[field] is not True:
            raise IntakeError("Incomplete source-only restriction proof")


def image_transport_policy():
    policy = json.loads(TRANSPORT_POLICY.read_text())
    if (policy["version"], policy["scope"], policy["source_revision"], policy["reviewed_image_redirect_hosts"]) != (
        1, "pinned_51_assets_byte_quarantine_only", DATASET_REV, ["us.aws.cdn.hf.co"]
    ):
        raise IntakeError("Unreviewed image transport policy")
    expected = {(r["id"], r["size"], r["sha256"]) for r in plan() if r["kind"] == "image"}
    actual = {(r["source_path"], r["declared_bytes"], r["lfs_sha256"]) for r in policy["records"]}
    if expected != actual or len(policy["records"]) != 48:
        raise IntakeError("Image transport identity inventory changed")
    if not all(r["status"] == 302 and r["delegated_https_host"] == "us.aws.cdn.hf.co"
               and r["image_body_bytes_read"] == 0 for r in policy["records"]):
        raise IntakeError("Incomplete metadata-only transport review")
    return {"us.aws.cdn.hf.co"}


class RestrictedRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, hosts):
        super().__init__()
        self.hosts, self.hops = hosts, 0

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.hops += 1
        target = urllib.parse.urlsplit(newurl)
        if (self.hops > 3 or target.scheme != "https" or target.hostname not in self.hosts
                or target.port not in {None, 443} or target.username or target.password or target.fragment):
            raise IntakeError("Redirect outside reviewed transport policy")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(row, image_hosts):
    if row not in plan():
        raise IntakeError("Artifact outside exact frozen allowlist")
    hosts = {"raw.githubusercontent.com"} if row["kind"] == "weight" else {"huggingface.co", *image_hosts}
    parsed = urllib.parse.urlsplit(row["url"])
    if parsed.scheme != "https" or parsed.hostname not in hosts:
        raise IntakeError("Unknown source")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), RestrictedRedirect(hosts))
    started, data = time.monotonic(), bytearray()
    with opener.open(row["url"], timeout=10) as response:
        if response.status != 200 or response.headers.get("Content-Encoding", "identity") != "identity":
            raise IntakeError("Unexpected transport response")
        while True:
            if time.monotonic() - started > 60:
                raise IntakeError("Transfer deadline")
            block = response.read(min(65536, row["size"] - len(data) + 1))
            if not block:
                break
            data.extend(block)
            if len(data) > row["size"]:
                raise IntakeError("Transfer byte limit")
    raw = bytes(data)
    actual = verify_bytes(raw, size=row["size"], sha256=row["sha256"], git_blob=row["git_blob"])
    return raw, actual


def write_private(path, data):
    with path.open("xb") as handle:
        os.chmod(path, 0o600)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def acquire(work, keys, result_path, review_path, *, include_images=False):
    policy = json.loads((ROOT / "config/phase2e/qualification-policy.json").read_text())
    if policy["acquisition_enabled"] is not True:
        raise IntakeError("Acquisition blocked: clean native worker design review is incomplete")
    result_bytes, review_bytes = result_path.read_bytes(), review_path.read_bytes()
    approved_preflight(result_bytes, json.loads(review_bytes))
    if work == keys or work in keys.parents or keys in work.parents:
        raise IntakeError("Quarantine and keys must use separate directories")
    image_hosts = image_transport_policy() if include_images else set()
    for directory in [work, keys]:
        if directory.exists() or any(p.is_symlink() for p in [directory, *directory.parents]):
            raise IntakeError("Fresh private directories required")
    work.mkdir(mode=0o700, parents=True)
    keys.mkdir(mode=0o700, parents=True)
    key, instance = AESGCM.generate_key(bit_length=256), str(uuid4())
    write_private(keys / "quarantine.key", key)
    rows = [r for r in plan() if include_images or r["kind"] == "weight"]
    receipt = {"version": 1, "instance": instance, "scope": "encrypted_byte_quarantine_only",
               "owner_authorization_sha256": A0, "proposal_sha256": PROPOSAL_SHA256,
               "preflight_review_sha256": hashlib.sha256(review_bytes).hexdigest(), "assets": [],
               "independent_digest_review": "pending", "decompression_approved": False,
               "native_loading_allowed": False, "inference_allowed": False, "image_decoding_allowed": False,
               "operational_allowed": False, "status": "incomplete"}
    receipt["transport_policy_sha256"] = hashlib.sha256(TRANSPORT_POLICY.read_bytes()).hexdigest() if include_images else None
    receipt["curation_license"] = "CC-BY-SA-4.0"
    receipt["individual_image_license"] = "CC0-1.0"
    receipt["attribution"] = "Reto Wyss, Syn-Vis-v0 (2025), pinned revision " + DATASET_REV
    receipt["curation_changes"] = "fixed approved 48-image subset; byte verification and encrypted quarantine only"
    receipt["operator"] = json.loads(review_bytes)["reviewer"]
    receipt["started_at"] = datetime.now(UTC).isoformat()
    total, started = 0, time.monotonic()
    for row in rows:
        if time.monotonic() - started > (600 if include_images else 180) or total + row["size"] > TOTAL_LIMIT:
            raise IntakeError("Acquisition budget exceeded")
        try:
            data, sha256 = download(row, image_hosts)
        except (OSError, ValueError) as error:
            failure = {**receipt, "status": "failed", "failed_source_id": row["id"],
                       "error_type": type(error).__name__, "http_status": getattr(error, "code", None)}
            write_private(work / "failure.json", (json.dumps(failure, indent=2) + "\n").encode())
            raise IntakeError("Acquisition failed; sanitized private failure receipt retained") from None
        opaque = str(uuid4())
        aad = f"{instance}:{opaque}:{sha256}".encode()
        nonce = secrets.token_bytes(12)
        sealed = nonce + AESGCM(key).encrypt(nonce, data, aad)
        write_private(work / (opaque + ".enc"), sealed)
        receipt["assets"].append({"asset_id": opaque, "source_id": row["id"], "kind": row["kind"],
                                  "source_uri": row["url"], "received_at": datetime.now(UTC).isoformat(),
                                  "size": len(data), "git_blob": row["git_blob"], "sha256": sha256,
                                  "ciphertext_sha256": hashlib.sha256(sealed).hexdigest(), "bytes_verified": True})
        if row["kind"] == "image":
            receipt["assets"][-1].update({"group": row["group"], "partition": row["partition"],
                "planned_enrollment": row["planned_enrollment"], "active_enrollment": False,
                "independent_visual_review": "pending", "capture_date": None, "capture_age": None,
                "capture_information": "unknown_not_inferred_from_pixels_or_exif"})
        total += len(data)
        write_private(work / f"receipt-{len(receipt['assets'])}.json", (json.dumps(receipt, indent=2) + "\n").encode())
    receipt["status"] = "bytes_verified_pending_independent_review"
    write_private(work / "manifest.json", (json.dumps(receipt, indent=2) + "\n").encode())
    print(json.dumps({"assets_verified": len(rows), "bytes": total,
                      "manifest_sha256": hashlib.sha256((work / "manifest.json").read_bytes()).hexdigest(),
                      "native_execution": False, "independent_review": "pending"}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work", type=Path)
    parser.add_argument("keys", type=Path)
    parser.add_argument("preflight_result", type=Path)
    parser.add_argument("technical_review", type=Path)
    parser.add_argument("--include-images", action="store_true", help="Only the exact 48 metadata-reviewed image refs")
    args = parser.parse_args()
    try:
        acquire(args.work.absolute(), args.keys.absolute(), args.preflight_result, args.technical_review,
                include_images=args.include_images)
    except (OSError, ValueError, KeyError, TypeError) as error:
        # Never print a redirect's signed URL, response headers, key or raw asset.
        print(json.dumps({"intake": "failed", "error_type": type(error).__name__, "native_execution": False}))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
