"""Offline verification of independent gate receipts; no signing/approval endpoint.

Trusted review keys are provisioned out of band. A browser/operator cannot supply
their own trust root. Empty accepted configuration denies every permit.
"""

import base64
import json
import re
from datetime import UTC, datetime

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


class ApprovalError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value):
        raise ApprovalError("Invalid approval time")
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise ApprovalError("Invalid approval time") from None


def verify(envelope, trusted_keys, *, gate, manifest_digest, operator_id, now=None):
    """Bind a reviewed manifest to an independent, expiring, narrowly scoped permit.

    This verifies authentication/shape, not that a reviewer actually examined the
    evidence. Review records and owner administration remain necessary governance.
    """
    now = now or datetime.now(UTC)
    if gate not in {"A4", "A6", "A7"} or not re.fullmatch(r"[a-f0-9]{64}", manifest_digest):
        raise ApprovalError("Unknown gate or manifest")
    if not isinstance(envelope, dict) or set(envelope) != {"payload", "signature"}:
        raise ApprovalError("Closed approval envelope required")
    payload = envelope["payload"]
    required = {"version", "gate", "manifest_sha256", "reviewer_id", "key_id", "issued_at", "expires_at",
                "scope", "decision", "review_record_sha256", "blind_to_model_scores"}
    if not isinstance(payload, dict) or set(payload) != required:
        raise ApprovalError("Closed approval payload required")
    if (payload["version"], payload["gate"], payload["manifest_sha256"], payload["scope"], payload["decision"]) != (
        1, gate, manifest_digest, "private_synthetic_demo_only", "approved"
    ) or type(payload["version"]) is not int:
        raise ApprovalError("Wrong approval binding")
    key = trusted_keys.get(payload["key_id"])
    if not key or key.get("revoked") is not False or gate not in key.get("gates", []):
        raise ApprovalError("Untrusted/revoked reviewer")
    if payload["reviewer_id"] != key.get("reviewer_id") or payload["reviewer_id"] == operator_id:
        raise ApprovalError("Independent reviewer required")
    if not re.fullmatch(r"[a-f0-9]{64}", payload["review_record_sha256"]):
        raise ApprovalError("Missing review record")
    if type(payload["blind_to_model_scores"]) is not bool or (gate == "A6" and not payload["blind_to_model_scores"]):
        raise ApprovalError("Blinded fixture review required")
    issued, expires = timestamp(payload["issued_at"]), timestamp(payload["expires_at"])
    if not issued <= now < expires or not 0 < (expires - issued).total_seconds() <= 86400:
        raise ApprovalError("Expired/future/overlong permit")
    try:
        public = base64.b64decode(key["public_key"], validate=True)
        signature = base64.b64decode(envelope["signature"], validate=True)
        Ed25519PublicKey.from_public_bytes(public).verify(signature, canonical(payload))
    except (ValueError, TypeError, InvalidSignature):
        raise ApprovalError("Invalid gate signature") from None
    return {"gate": gate, "manifest_sha256": manifest_digest, "reviewer_id": payload["reviewer_id"]}
