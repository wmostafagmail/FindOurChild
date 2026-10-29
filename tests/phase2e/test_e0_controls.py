"""Synthetic E0 control tests. None is a native model/inference acceptance test."""

import base64
import bz2
import hashlib
import json
from copy import deepcopy
from datetime import UTC, datetime

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.phase2e.approval import ApprovalError, canonical, verify
from tools.phase2e.quarantine import IntegrityError, unpack_bzip2, verify_bytes
from tools.phase2e.source_projection import (
    LOCK,
    NoRedirect,
    ProjectionError,
    allowed_path,
    validate_lock,
    verify_blob,
)

NOW = datetime(2026, 10, 29, 18, tzinfo=UTC)
DIGEST = "1" * 64


def receipt(gate="A4"):
    # Ephemeral synthetic signing key exists only in this unit fixture, never a review credential.
    private = Ed25519PrivateKey.generate()
    payload = {"version": 1, "gate": gate, "manifest_sha256": DIGEST, "reviewer_id": "fictional-reviewer",
               "key_id": "unit-key", "issued_at": "2026-10-29T17:00:00Z", "expires_at": "2026-10-29T19:00:00Z",
               "scope": "private_synthetic_demo_only", "decision": "approved",
               "review_record_sha256": "2" * 64, "blind_to_model_scores": True}
    keys = {"unit-key": {"public_key": base64.b64encode(private.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode(),
        "reviewer_id": "fictional-reviewer", "gates": [gate], "revoked": False}}
    envelope = {"payload": payload, "signature": base64.b64encode(private.sign(canonical(payload))).decode()}
    return private, envelope, keys


@pytest.mark.parametrize("gate", ["A3", "A4", "A6", "A7"])
def test_synthetic_independent_signature_binds_gate_and_manifest(gate):
    _, envelope, keys = receipt(gate)
    assert verify(envelope, keys, gate=gate, manifest_digest=DIGEST,
                  operator_id="fictional-operator", now=NOW)["gate"] == gate


@pytest.mark.parametrize("field,value", [
    ("manifest_sha256", "3" * 64), ("gate", "A7"), ("reviewer_id", "someone-else"),
    ("scope", "operational"), ("decision", "pending"), ("version", True),
    ("review_record_sha256", ""), ("blind_to_model_scores", "true"),
    ("expires_at", "2026-10-29T17:59:59Z"), ("issued_at", "2026-10-29T18:01:00Z"),
    ("expires_at", "2026-11-29T19:00:00Z"), ("issued_at", "yesterday"),
    ("issued_at", "2026-99-29T17:00:00Z"), ("unknown", "extra"),
])
def test_invalid_or_tampered_gate_receipt_denied(field, value):
    _, envelope, keys = receipt()
    envelope["payload"][field] = value
    with pytest.raises(ApprovalError):
        verify(envelope, keys, gate="A4", manifest_digest=DIGEST, operator_id="operator", now=NOW)


@pytest.mark.parametrize("mutation", ["self_approved", "revoked", "wrong_gate", "no_trust", "bad_signature",
                                      "different_signed_bytes", "unknown_envelope"])
def test_review_authority_and_cryptographic_negatives(mutation):
    _, envelope, keys = receipt()
    operator = "operator"
    if mutation == "self_approved":
        operator = "fictional-reviewer"
    elif mutation == "revoked":
        keys["unit-key"]["revoked"] = True
    elif mutation == "wrong_gate":
        keys["unit-key"]["gates"] = ["A7"]
    elif mutation == "no_trust":
        keys = {}
    elif mutation == "bad_signature":
        envelope["signature"] = "invalid"
    elif mutation == "different_signed_bytes":
        envelope["payload"]["review_record_sha256"] = "3" * 64
    else:
        envelope["extra"] = "browser-self-approval"
    with pytest.raises(ApprovalError):
        verify(envelope, keys, gate="A4", manifest_digest=DIGEST, operator_id=operator, now=NOW)


def test_even_valid_signature_cannot_skip_blinded_fixture_review():
    private, envelope, keys = receipt("A6")
    envelope["payload"]["blind_to_model_scores"] = False
    envelope["signature"] = base64.b64encode(private.sign(canonical(envelope["payload"]))).decode()
    with pytest.raises(ApprovalError):
        verify(envelope, keys, gate="A6", manifest_digest=DIGEST, operator_id="operator", now=NOW)


@pytest.mark.parametrize("field,value", [("key_id", []), ("reviewer_id", {}), ("issued_at", None),
                                        ("scope", "x" * 129), ("review_record_sha256", False)])
def test_malformed_field_types_do_not_bypass_approval_verifier(field, value):
    _, envelope, keys = receipt()
    envelope["payload"][field] = value
    with pytest.raises(ApprovalError):
        verify(envelope, keys, gate="A4", manifest_digest=DIGEST, operator_id="operator", now=NOW)


@pytest.mark.parametrize("path", [
    "examples/faces/a.jpg", "dlib/test/image.cpp", "dlib/test/ffmpeg_data/dog.jpg",
    "dlib/external/libjpeg/sample.jpg", "python_examples/demo.py", "../setup.py", "/setup.py",
    "dlib/../setup.py", "dlib//matrix.h", "dlib/./matrix.h", "dlib/model.dat", "dlib/model.dat.bz2",
    "dlib/picture.png", "dlib/archive.zip", "tools/python/tests/photo.py", "dlib/a.h?x=1",
    "dlib/a.h#photo", "dlib/a\\b.h", "dlib/a%2fb.h",
])
def test_source_projection_blocks_data_and_path_injection(path):
    assert not allowed_path(path)


@pytest.mark.parametrize("path", ["setup.py", "dlib/matrix.h", "tools/python/src/face_recognition.cpp",
                                   "dlib/external/pybind11/LICENSE"])
def test_source_projection_accepts_reviewed_code_and_notices(path):
    assert allowed_path(path)


def test_exact_source_inventory_has_no_model_image_or_unreviewed_dependency():
    lock = json.loads(LOCK.read_text())
    rows = validate_lock(lock)
    assert len(rows) == 1187
    assert sum(row["bytes"] for row in rows) == 15059168
    assert all(allowed_path(row["path"]) for row in rows)


@pytest.mark.parametrize("change", ["extra", "wrong_ref", "duplicate", "oversize", "sample_image", "missing_notice"])
def test_projection_lock_tampering_denied(change):
    lock = deepcopy(json.loads(LOCK.read_text()))
    if change == "extra":
        lock["approved"] = True
    elif change == "wrong_ref":
        lock["commit"] = "a" * 40
    elif change == "duplicate":
        lock["entries"].append(lock["entries"][-1])
    elif change == "oversize":
        lock["entries"][0]["bytes"] = 3_000_000
    elif change == "sample_image":
        lock["entries"][0]["path"] = "examples/faces/a.jpg"
    else:
        lock["entries"] = [r for r in lock["entries"] if r["path"] != "LICENSE.txt"]
    with pytest.raises(ProjectionError):
        validate_lock(lock)


def test_transport_redirect_is_never_followed():
    with pytest.raises(ProjectionError):
        NoRedirect().redirect_request(None, None, 302, "", {}, "https://unapproved.invalid/model")


def test_exact_text_git_blob_and_sha256_verified():
    data = b"// synthetic source\n"
    row = {"bytes": len(data), "git_blob": hashlib.sha1(b"blob 20\0" + data).hexdigest()}
    assert len(data) == 20
    assert verify_blob(data, row) == hashlib.sha256(data).hexdigest()


@pytest.mark.parametrize("data", [b"wrong-size", b"\0", b"xx"])
def test_source_bytes_not_trusted_from_extension(data):
    with pytest.raises(ProjectionError):
        verify_blob(data, {"bytes": len(data), "git_blob": "1" * 40})


def test_artifact_hash_algorithms_are_distinct_and_both_checked():
    data = b"synthetic nonmodel bytes"
    sha256 = hashlib.sha256(data).hexdigest()
    git = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    assert verify_bytes(data, size=len(data), sha256=sha256, git_blob=git) == sha256
    for wrong in [{"sha256": git}, {"git_blob": sha256}, {"sha256": "0" * 64}, {"git_blob": "0" * 40}, {}]:
        with pytest.raises(IntegrityError):
            verify_bytes(data, size=len(data), **wrong)


def test_bounded_single_bzip2_stream_exact_roundtrip():
    data = bytes(range(256)) * 10
    assert unpack_bzip2(bz2.compress(data), output_limit=2560, ratio_limit=20, time_limit=1) == data


@pytest.mark.parametrize("mutation", ["trailing", "concatenated", "truncated", "malformed", "empty", "bomb"])
def test_bzip2_bad_streams_never_reach_a_native_loader(mutation):
    encoded = bz2.compress(b"synthetic")
    values = {"trailing": encoded + b"x", "concatenated": encoded + encoded, "truncated": encoded[:-1],
              "malformed": b"BZh9garbage", "empty": bz2.compress(b""), "bomb": bz2.compress(b"x" * 100000)}
    with pytest.raises(IntegrityError):
        unpack_bzip2(values[mutation], output_limit=1000, ratio_limit=20, time_limit=1)


@pytest.mark.parametrize("parameters", [
    {"output_limit": 0}, {"output_limit": 2**31}, {"ratio_limit": 0}, {"ratio_limit": 513},
    {"time_limit": 0}, {"time_limit": float("nan")}, {"time_limit": float("inf")},
])
def test_unpack_limits_cannot_be_removed(parameters):
    limits = {"output_limit": 1000, "ratio_limit": 20, "time_limit": 1, **parameters}
    with pytest.raises(IntegrityError):
        unpack_bzip2(bz2.compress(b"synthetic"), **limits)


def test_unpack_deadline_failure_is_explicit():
    times = iter([0, 2])
    with pytest.raises(IntegrityError, match="deadline"):
        unpack_bzip2(bz2.compress(b"synthetic"), output_limit=1000, ratio_limit=20,
                     time_limit=1, clock=lambda: next(times))
