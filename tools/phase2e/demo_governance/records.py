"""Bounded canonical wire format; this is deliberately not RFC8785/JCS.

No signing API. Tests alone generate disposable, untrusted keys. Verification
accepts only a private registry snapshot supplied by the trusted control plane.
"""

import base64
import hashlib
import json
import re
from datetime import UTC, datetime

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

DOMAIN = "FOC-PHASE2E-DEMO-APPROVAL-V2"
POLICY = "0ab396ebdbc7e2bdd11f8d4f8fb8ee24791d8f3990b9c3297ce2de2d009d3c8a"
# role, exact predecessor kinds, evidence keys, maximum seconds
KINDS = {
    "policy": ("O", (), {"decision"}, 86400),
    "scope": ("O", ("policy",), {"inventory", "rights", "retention", "qualification"}, 86400),
    "A1b-demo": (
        "T",
        ("scope",),
        {"source", "build", "abi", "sbom", "isolation", "negative", "waiver"},
        86400,
    ),
    "A2": ("O", ("scope", "A1b-demo"), {"inventory", "quarantine", "bounds"}, 86400),
    "A3": ("T", ("A2",), {"inventory", "byte_audit", "quarantine"}, 86400),
    "A4a": ("T", ("A3",), {"bounds", "scanner", "decoder", "isolation"}, 86400),
    "A4b": ("T", ("A4a",), {"outputs", "scan", "lineage"}, 86400),
    "A5-plan": ("T", ("A4b",), {"build", "bounds", "load_plan"}, 1800),
    "A5-result": ("T", ("A5-plan",), {"build", "load_result", "isolation"}, 1800),
    "A6": ("F", ("A4b",), {"fixtures", "images", "links", "gallery", "split", "blind_review"}, 86400),
    "A7": (
        "O",
        ("A5-result", "A6"),
        {"build", "models", "images", "gallery", "resources", "retention"},
        14400,
    ),
    "A8": ("O", ("A7",), {"technical_validation", "owner_acceptance"}, 86400),
}
FIELDS = {
    "domain",
    "kind",
    "id",
    "project",
    "instance",
    "policy",
    "key",
    "person",
    "operator",
    "epoch",
    "activation_epoch",
    "issued",
    "expires",
    "manifest",
    "build",
    "space",
    "fixture",
    "predecessors",
    "evidence",
    "decision",
    "blind",
    "reviewed",
    "data_class",
}


class Denied(ValueError):
    """Public error carries a fixed code, never untrusted content or secrets."""


def require(condition, code):
    if not condition:
        raise Denied(code)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode()


def _pairs(items):
    result = {}
    for k, v in items:
        require(k not in result, "duplicate_field")
        result[k] = v
    return result


def _shape(v, depth=0):
    require(depth <= 4, "depth")
    if isinstance(v, dict):
        require(len(v) <= 32, "field_count")
        for k, child in v.items():
            require(isinstance(k, str) and re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", k), "field_name")
            _shape(child, depth + 1)
    elif isinstance(v, list):
        require(len(v) <= 16, "list_limit")
        for child in v:
            _shape(child, depth + 1)
    elif type(v) is int:
        require(0 <= v <= 2**53 - 1, "integer")
    else:
        require(type(v) in {str, bool} and (type(v) is bool or len(v) <= 512), "scalar")


def decode(raw):
    require(type(raw) is bytes and 0 < len(raw) <= 16384, "wire_limit")
    try:
        value = json.loads(
            raw, object_pairs_hook=_pairs, parse_constant=lambda _: (_ for _ in ()).throw(Denied("nonfinite"))
        )
        _shape(value)
        require(canonical(value) == raw, "noncanonical")
        return value
    except (UnicodeError, json.JSONDecodeError, RecursionError, OverflowError):
        raise Denied("encoding") from None


def identifier(v):
    return type(v) is str and re.fullmatch(r"[a-zA-Z0-9_-]{1,96}", v) is not None


def sha(v):
    return type(v) is str and re.fullmatch(r"[a-f0-9]{64}", v) is not None


def time_value(v):
    require(type(v) is str and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", v), "time")
    try:
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError:
        raise Denied("time") from None


def public_key(encoded):
    require(type(encoded) is str and len(encoded) == 60, "key_encoding")
    try:
        der = base64.b64decode(encoded, validate=True)
        require(base64.b64encode(der).decode() == encoded, "key_encoding")
        key = serialization.load_der_public_key(der)
        require(isinstance(key, Ed25519PublicKey), "key_algorithm")
        require(
            key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
            == der,
            "key_encoding",
        )
        return key, digest(der)
    except (ValueError, TypeError):
        raise Denied("key_encoding") from None


def signature_verify(key, signature, message):
    require(type(signature) is str and len(signature) == 88, "signature_encoding")
    try:
        sig = base64.b64decode(signature, validate=True)
        require(len(sig) == 64 and base64.b64encode(sig).decode() == signature, "signature_encoding")
        key.verify(sig, message)
    except (ValueError, TypeError, InvalidSignature):
        raise Denied("signature") from None


def signed_bytes(payload):
    return DOMAIN.encode() + b"\x00" + payload["kind"].encode() + b"\x00" + canonical(payload)


def validate_chain(root, records, registry, binding, now, *, action, clock_trusted=True):
    """Verify an exact chain, not an execution capability or actual human review.

    Authority must be reloaded under the publication transaction; returning from
    this pure verifier cannot authorize later publication using cached state.
    """
    require(clock_trusted and now.tzinfo is not None, "clock_untrusted")
    require(
        type(action) is str and action in KINDS and type(records) is dict and len(records) <= 16,
        "action_or_chain",
    )
    registry.validate(now)
    require(
        binding["project"] == registry.project and binding["instance"] == registry.instance,
        "registry_project_binding",
    )
    seen, active = {}, set()

    def visit(identity):
        require(identity not in active and sha(identity), "cycle_or_digest")
        if identity in seen:
            return seen[identity]
        require(identity in records, "predecessor_missing")
        raw = records[identity]
        require(digest(raw) == identity, "record_digest")
        env = decode(raw)
        require(type(env) is dict and set(env) == {"payload", "signature"}, "envelope")
        p = env["payload"]
        require(
            type(p) is dict and set(p) == FIELDS and type(p["kind"]) is str and p["kind"] in KINDS,
            "record_fields",
        )
        role, dependencies, evidence, lifetime = KINDS[p["kind"]]
        require(
            p["domain"] == DOMAIN and p["policy"] == POLICY and p["data_class"] == "fictional_demo_only",
            "domain_or_policy",
        )
        for field in ["id", "person", "operator", "project", "instance", "space"]:
            require(identifier(p[field]), "identifier")
        for field in ["manifest", "build", "fixture", "key"]:
            require(sha(p[field]), "digest_field")
        for field in [
            "project",
            "instance",
            "manifest",
            "build",
            "space",
            "fixture",
            "epoch",
            "activation_epoch",
        ]:
            require(type(p[field]) is type(binding[field]) and p[field] == binding[field], "scope_binding")
        require(type(p["epoch"]) is int and p["epoch"] == registry.epoch, "registry_epoch")
        require(
            type(p["activation_epoch"]) is int and p["activation_epoch"] == registry.activation_epoch,
            "activation_epoch",
        )
        require(p["decision"] == "approved" and type(p["blind"]) is bool, "decision")
        require(
            type(p["evidence"]) is dict
            and set(p["evidence"]) == evidence
            and all(sha(x) for x in p["evidence"].values()),
            "evidence",
        )
        require(
            type(p["predecessors"]) is list
            and all(sha(x) for x in p["predecessors"])
            and len(set(p["predecessors"])) == len(p["predecessors"]),
            "predecessors",
        )
        issued, expires, reviewed = map(time_value, [p["issued"], p["expires"], p["reviewed"]])
        require(
            reviewed <= issued <= now < expires and 0 < (expires - issued).total_seconds() <= lifetime,
            "record_time",
        )
        entry = registry.key(p["key"], role, p["person"], now, gate=p["kind"], manifest=p["manifest"])
        require(expires <= time_value(entry["expires"]), "key_expiry")
        if role in {"T", "F"}:
            require(p["person"] != registry.owner_person, "owner_conflict")
        if role == "T":
            require(p["person"] != p["operator"], "operator_conflict")
        if role == "F":
            require(p["blind"] and reviewed <= time_value(registry.blind_until), "fixture_not_blind")
        key, _ = public_key(entry["der"])
        signature_verify(key, env["signature"], signed_bytes(p))
        active.add(identity)
        prior = [visit(x) for x in p["predecessors"]]
        require(sorted(x["kind"] for x in prior) == sorted(dependencies), "dependency_kinds")
        require(
            all(expires <= time_value(x["expires"]) and issued >= time_value(x["issued"]) for x in prior),
            "dependency_expiry",
        )
        active.remove(identity)
        seen[identity] = p
        return p

    result = visit(root)
    require(result["kind"] == action, "action_mismatch")
    # The entire chain is one operator/build/batch. Multiple aliases do not
    # turn the operator into an independent technical reviewer.
    require(all(p["operator"] == result["operator"] for p in seen.values()), "operator_chain")
    technical = {p["person"] for p in seen.values() if KINDS[p["kind"]][0] == "T"}
    require(
        not any(
            p["kind"] == "A6" and p["person"] == result["operator"] and p["person"] in technical
            for p in seen.values()
        ),
        "fixture_operator_technical_conflict",
    )
    return result
