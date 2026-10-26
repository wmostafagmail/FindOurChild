"""Offline qualification preparation. No real model or child-data permission exists here."""

import hashlib
import json
import math
import re
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path

from .pipeline import QualificationError, digest, fixture

ROOT = Path(__file__).resolve().parents[4]
MODEL_IDS = frozenset({"insightface-buffalo-l", "adaface-ir50-ms1mv2", "opencv-sface-fp32", "opencv-yunet-2023mar", "auraface-r100", "deepface-arcface-onnx", "deepface-sface-onnx", "deepface-facenet512-onnx"})
ARTIFACT = b"Find Our Child: synthetic artifact integrity fixture v1\n"
ARTIFACT_SHA256 = hashlib.sha256(ARTIFACT).hexdigest()
PROTOCOL = {"version": "qualification-preparation-1", "data_class": "synthetic", "real_data_allowed": False, "model_execution_allowed": False, "top_k": [1, 10, 50], "photo_cap": 3, "threshold_source": "calibration_only", "test_tuning_allowed": False, "training_overlap": "not_applicable_weight_free", "age_progression_allowed": False}
PROTOCOL_HASH = digest(PROTOCOL)


def closed(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        raise QualificationError("unreviewed or incomplete schema")


def verify_registry(registry, evidence):
    """Check preparation invariants, not grant lawfulness or validate a model binary."""
    closed(registry, {"schema_version", "data_policy", "real_models_qualified", "models"})
    if registry["schema_version"] != "qualification-preparation-1" or registry["data_policy"] != "synthetic-only" or type(registry["real_models_qualified"]) is not int or registry["real_models_qualified"] != 0:
        raise QualificationError("phase boundary")
    models = registry["models"]
    if type(models) is not list or len(models) != len(MODEL_IDS) or any(type(m) is not dict or type(m.get("id")) is not str for m in models) or {m.get("id") for m in models} != MODEL_IDS:
        raise QualificationError("candidate inventory incomplete")
    for model in models:
        closed(model, {"id", "source_revision", "artifact", "code_terms", "weight_terms", "training_provenance", "detector_alignment", "preprocessing", "hardware_plan", "evidence", "unresolved", "download_allowed", "execution_allowed", "operational_allowed", "decision"})
        if type(model["source_revision"]) is not str or not re.fullmatch(r"[a-f0-9]{40}", model["source_revision"]):
            raise QualificationError("unfrozen source revision")
        if any(model[k] is not False for k in ["download_allowed", "execution_allowed", "operational_allowed"]) or model["decision"] != "blocked":
            raise QualificationError("model clearance cannot be granted by configuration")
        for key in ["code_terms", "weight_terms", "training_provenance", "detector_alignment", "preprocessing", "hardware_plan"]:
            if type(model[key]) is not str or not 1 <= len(model[key]) <= 2000:
                raise QualificationError("missing candidate assessment")
        closed(model["artifact"], {"name", "publisher_sha256", "publisher_bytes", "identity_status", "bytes_verified"})
        artifact = model["artifact"]
        if type(artifact["name"]) is not str or not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", artifact["name"]) or artifact["bytes_verified"] is not False:
            raise QualificationError("binary identity is unverified")
        sha = artifact["publisher_sha256"]
        if sha is None:
            if artifact["identity_status"] != "unknown_binary_digest" or artifact["publisher_bytes"] is not None:
                raise QualificationError("missing identity evidence")
        elif not isinstance(sha, str) or not re.fullmatch(r"[a-f0-9]{64}", sha) or artifact["identity_status"] != "publisher_declared_not_downloaded" or type(artifact["publisher_bytes"]) is not int or artifact["publisher_bytes"] <= 0:
            raise QualificationError("invalid publisher declaration")
        for key in ["evidence", "unresolved"]:
            if type(model[key]) is not list or not model[key] or any(type(x) is not str or not x for x in model[key]):
                raise QualificationError("missing evidence or unresolved qualification")
        if any(x not in evidence for x in model["evidence"]):
            raise QualificationError("unresolved evidence reference")
    return digest(registry)


def load_registry(root=ROOT):
    evidence = set()
    revisions = {}
    for phase in ["phase2a", "phase2b"]:
        base = (root / "docs" / phase / "research").resolve()
        lock = json.loads((base / "source-lock.json").read_text())
        for entry in lock["sources"]:
            path = (base / entry["local"]).resolve()
            if not path.is_relative_to(base) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
                raise QualificationError("evidence integrity failure")
            evidence.add(phase + "/" + entry["local"])
            revisions[phase + "/" + entry["local"]] = (entry["candidate"].split("_")[0], entry["commit"])
    registry = json.loads((root / "config/qualification-models.json").read_text())
    verify_registry(registry, evidence)
    # Bind declared identities to the hashed publisher evidence, never to downloaded weights.
    published = {}
    for model_id, folder, name in [
        ("opencv-sface-fp32", "face_recognition_sface", "face_recognition_sface_2021dec.onnx"),
        ("deepface-sface-onnx", "face_recognition_sface", "face_recognition_sface_2021dec.onnx"),
        ("opencv-yunet-2023mar", "face_detection_yunet", "face_detection_yunet_2023mar.onnx"),
    ]:
        text = (root / f"docs/phase2b/research/opencv/models/{folder}/{name}.lfs-pointer.txt").read_text()
        match = re.fullmatch(r"version https://git-lfs.github.com/spec/v1\noid sha256:([a-f0-9]{64})\nsize ([0-9]+)\n", text)
        if not match:
            raise QualificationError("invalid publisher pointer")
        published[model_id] = (name, match[1], int(match[2]))
    files = json.loads((root / "docs/phase2b/research/auraface/publisher-tree.json").read_text())
    item = next(x for x in files if x["path"] == "glintr100.onnx")
    published["auraface-r100"] = (item["path"], item["lfs"]["oid"], item["size"])
    release = json.loads((root / "docs/phase2b/research/deepface/publisher-release-assets.json").read_text())
    for model_id, name in [("deepface-arcface-onnx", "arcface_weights.onnx"), ("deepface-facenet512-onnx", "facenet512_weights.onnx")]:
        item = next(x for x in release["assets"] if x["name"] == name)
        published[model_id] = (name, item["digest"].removeprefix("sha256:"), item["size"])
    published["insightface-buffalo-l"] = ("w600k_r50.onnx", None, None)
    published["adaface-ir50-ms1mv2"] = ("adaface_ir50_ms1mv2.ckpt", None, None)
    for model in registry["models"]:
        a = model["artifact"]
        if not any(revisions[ref] == (model["id"].split("-")[0], model["source_revision"]) for ref in model["evidence"]):
            raise QualificationError("source revision differs from publisher evidence")
        if (a["name"], a["publisher_sha256"], a["publisher_bytes"]) != published[model["id"]]:
            raise QualificationError("artifact differs from publisher evidence")
    return registry


def request_model_download(*args, **kwargs):
    # Deliberately no downloader, URL resolution, imports or acceptance flag.
    raise QualificationError("all real model acquisition is blocked in this phase")


def verify_synthetic_artifact(data, expected_sha256):
    if type(data) is not bytes or len(data) != len(ARTIFACT) or expected_sha256 != ARTIFACT_SHA256 or hashlib.sha256(data).hexdigest() != ARTIFACT_SHA256:
        raise QualificationError("unapproved or altered artifact")
    return ARTIFACT_SHA256


@lru_cache(maxsize=1)
def fixture_identity():
    return {hashlib.sha256(fixture(i)).hexdigest(): (f"fixture-subject-{i % 16}", f"fixture-family-{i % 16}", f"fixture-event-{i}") for i in range(32)}


def authorize_synthetic_dataset(manifest, grant, *, organization=None, principal=None, now=None, revoked_subjects=()):
    """Exercise synthetic governance only. Self-asserted real-data approvals never suffice."""
    now = now or datetime.now(timezone.utc)
    closed(manifest, {"schema_version", "organization", "data_class", "protocol_hash", "training_overlap", "test_used_for_tuning", "age_progression", "records"})
    if manifest["schema_version"] != "qualification-dataset-1" or manifest["data_class"] != "synthetic" or manifest["protocol_hash"] != PROTOCOL_HASH or manifest["training_overlap"] != "not_applicable_weight_free" or manifest["test_used_for_tuning"] is not False or manifest["age_progression"] is not False:
        raise QualificationError("unapproved data or evaluation protocol")
    closed(grant, {"data_class", "purpose", "dataset_hash", "protocol_hash", "organization", "principal", "issuer", "reviewer", "issued_at", "expires_at", "revoked"})
    if grant["data_class"] != "synthetic" or grant["purpose"] != "synthetic-qualification" or grant["dataset_hash"] != digest(manifest) or grant["protocol_hash"] != PROTOCOL_HASH or grant["revoked"] is not False:
        raise QualificationError("missing, stale or revoked permission")
    if organization is None or principal is None or grant["organization"] != organization or manifest["organization"] != organization or grant["principal"] != principal:
        raise QualificationError("missing or mismatched trusted context")
    for key in ["organization", "principal", "issuer", "reviewer"]:
        if type(grant[key]) is not str or not re.fullmatch(r"fixture-[a-z0-9-]{1,40}", grant[key]):
            raise QualificationError("invalid synthetic authority")
    if len({grant["principal"], grant["issuer"], grant["reviewer"]}) != 3:
        raise QualificationError("independent approval required")
    try:
        issued = datetime.fromisoformat(grant["issued_at"])
        expiry = datetime.fromisoformat(grant["expires_at"])
        valid = now.tzinfo is not None and issued.tzinfo is not None and expiry.tzinfo is not None and issued <= now < expiry <= issued + timedelta(days=30)
    except (ValueError, TypeError):
        valid = False
    if not valid:
        raise QualificationError("invalid permission lifetime")
    rows = manifest["records"]
    if type(rows) is not list or not 2 <= len(rows) <= 32:
        raise QualificationError("invalid synthetic manifest size")
    seen, splits = set(), {}
    for row in rows:
        closed(row, {"image_hash", "subject", "family", "capture_event", "partition", "role", "registry"})
        if any(type(x) is not str or not 1 <= len(x) <= 80 for x in row.values()):
            raise QualificationError("invalid fixture record")
        expected = fixture_identity().get(row["image_hash"])
        if expected != (row["subject"], row["family"], row["capture_event"]) or row["image_hash"] in seen or row["subject"] in revoked_subjects:
            raise QualificationError("nonfixture, duplicate, relabeled or withdrawn image")
        seen.add(row["image_hash"])
        if row["partition"] not in {"development", "calibration", "test"} or row["role"] not in {"gallery", "probe"} or row["registry"] not in {"missing", "found"}:
            raise QualificationError("invalid evaluation partition")
        for key in ["subject", "family", "capture_event"]:
            identity = (key, row[key])
            if identity in splits and splits[identity] != row["partition"]:
                raise QualificationError("evaluation split leakage")
            splits[identity] = row["partition"]
    if not any(r["role"] == "gallery" for r in rows) or not any(r["role"] == "probe" for r in rows):
        raise QualificationError("gallery and probe required")
    return {"status": "synthetic_engineering_only", "dataset_hash": digest(manifest), "records": len(rows), "real_data_authorized": False}


def zero_event_upper(independent_subjects, alpha=0.05):
    """One-sided exact binomial upper bound, valid only for independent trial units."""
    if type(independent_subjects) is not int or not 1 <= independent_subjects <= 10**9 or type(alpha) not in (float, int) or not math.isfinite(alpha) or not 0 < alpha < 1:
        raise QualificationError("invalid independent-trial protocol")
    return -math.expm1(math.log(alpha) / independent_subjects)


def absent_subject_budget(target, alpha=0.05):
    if type(target) not in (float, int) or not math.isfinite(target) or not 0 < target < 1:
        raise QualificationError("invalid target error bound")
    zero_event_upper(1, alpha)
    return math.ceil(math.log(alpha) / math.log1p(-target))


def wilson_interval(successes, total):
    if type(total) is not int or type(successes) is not int or not 0 <= successes <= total <= 10**9:
        raise QualificationError("invalid binomial counts")
    if total == 0:
        return None
    z = 1.959963984540054
    p, denominator = successes / total, 1 + z*z / total
    center = (p + z*z/(2*total)) / denominator
    radius = z * math.sqrt(p*(1-p)/total + z*z/(4*total*total)) / denominator
    return [max(0.0, center-radius), min(1.0, center+radius)]


def multi_photo_candidates(probes, gallery, k=50):
    """Synthetic max-pair case aggregation, with a fixed pre-score three-photo budget."""
    from .evaluation import retrieve

    if type(k) is not int or not 1 <= k <= 50 or not probes or len(probes) > 32:
        raise QualificationError("invalid synthetic query budget")
    first = probes[0]
    seen = set()
    for probe in probes:
        probe.validate()
        if probe.role != "probe" or (probe.case, probe.subject, probe.registry, probe.partition, probe.space_id) != (first.case, first.subject, first.registry, first.partition, first.space_id) or probe.image_hash in seen:
            raise QualificationError("incompatible query photographs")
        seen.add(probe.image_hash)
    if any(row.image_hash in seen for row in gallery):
        raise QualificationError("query-gallery image leakage")
    best = {}
    for probe in sorted(probes, key=lambda row: row.image_hash)[:3]:
        for candidate in retrieve(probe, gallery, k=k, photo_cap=3):
            case = candidate["case"]
            if case not in best or candidate["score"] > best[case]["score"]:
                best[case] = candidate
    return sorted(best.values(), key=lambda row: (-row["score"], row["case"]))[:k]
