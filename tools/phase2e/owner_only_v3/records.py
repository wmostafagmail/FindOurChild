"""Bounded, closed, canonical V3 records; schema approval is never execution authority."""

import copy
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

DOMAIN = "FOC-PHASE2E-DEMO-OWNER-AUTHORIZATION-V3"
POLICY = "1a136c3914a1b6213757172984459d0036031567905e1a77e82b9abe68948df7"
DESIGN_COMMIT = "51c29c0e39424db243f30ce4d6d5ee8900ee122f"
ROOT = Path(__file__).resolve().parents[3]
DESIGN = ROOT / "docs/phase2e/owner-only-demo"
ACTIONS = frozenset([
    "acquire_quarantine", "verify_bytes", "process_bounded", "load_qualification",
    "private_image_inference", "private_similarity_retrieval", "private_result_view",
])


class Denied(ValueError):
    """Only fixed public codes; never exception contents, tokens, paths or media."""


def require(condition, code):
    if not condition:
        raise Denied(code)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def digest(value):
    return sha(canonical(value))


def _shape(value, level, depth, arrays):
    require(level <= depth, "wire_depth")
    if isinstance(value, dict):
        require(len(value) <= 48, "wire_fields")
        for key, item in value.items():
            require(type(key) is str and len(key) <= 128, "wire_key")
            _shape(item, level + 1, depth, arrays)
    elif isinstance(value, list):
        require(len(value) <= arrays, "wire_array")
        for item in value:
            _shape(item, level + 1, depth, arrays)
    elif type(value) is int:
        require(0 <= value <= 9007199254740991, "wire_integer")
    elif type(value) is str:
        require(len(value) <= 512 and not any(ord(c) < 32 or 0x202A <= ord(c) <= 0x202E
                or 0x2066 <= ord(c) <= 0x2069 for c in value), "wire_string")
    else:
        require(value is None or type(value) is bool, "wire_scalar")


def decode(raw, *, ceiling=16384, depth=4, arrays=16):
    require(type(raw) is bytes and 0 < len(raw) <= ceiling, "wire_size")

    def pairs(rows):
        obj = {}
        for key, value in rows:
            require(key not in obj, "wire_duplicate")
            obj[key] = value
        return obj

    try:
        # Depth preflight bounds the parser itself, including hostile empty arrays.
        level, quoted, escaped = 0, False, False
        for c in raw.decode("utf-8", errors="strict"):
            if quoted:
                if escaped:
                    escaped = False
                elif c == "\\":
                    escaped = True
                elif c == '"':
                    quoted = False
            elif c == '"':
                quoted = True
            elif c in "[{":
                level += 1
                require(level <= depth, "wire_depth")
            elif c in "]}":
                level -= 1
        value = json.loads(raw, object_pairs_hook=pairs,
                           parse_float=lambda _: require(False, "wire_float"),
                           parse_constant=lambda _: require(False, "wire_constant"))
        _shape(value, 0, depth, arrays)
        require(canonical(value) == raw, "wire_noncanonical")
        return value
    except (UnicodeError, json.JSONDecodeError, RecursionError, OverflowError):
        raise Denied("wire_invalid") from None


def schema(value, name):
    expected = {"authorization-record.schema.json": "71bf66665ba17572714d7c7451c17ac657d8c9e45eeaff5368ee34fba126376c",
                "fixture-plan.schema.json": "775e9b3a2c297c685668018422eea202ec52b93b8fc0aeccfa01a1cd15a7e80a"}
    require(name in expected, "schema_identity")
    raw = (DESIGN / name).read_bytes()
    require(sha(raw) == expected[name], "schema_integrity")
    definition = json.loads(raw)
    require(not list(Draft202012Validator(definition, format_checker=FormatChecker()).iter_errors(value)),
            "closed_schema")


def instant(value):
    require(type(value) is str and value.endswith("Z"), "utc_required")
    try:
        date = datetime.fromisoformat(value)
    except ValueError:
        raise Denied("utc_invalid") from None
    return date.timestamp()


def utc(seconds):
    require(type(seconds) in (int, float), "trusted_time")
    return datetime.fromtimestamp(seconds, UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def reviewed_digest(record):
    draft = copy.deepcopy(record)
    draft["confirmation"].pop("reviewed_draft_sha256", None)
    return digest(draft)


def validate(raw, now):
    record = decode(raw)
    schema(record, "authorization-record.schema.json")
    # jsonschema's integer treats bool separately, but const(1)==True in Python: enforce types.
    require(type(record["schema_version"]) is int, "typed_version")
    for key in ["activation_epoch", "authority_epoch"]:
        require(type(record["deployment"][key]) is int, "typed_epoch")
    for key in ["model_count", "image_count", "fictional_pair_count"]:
        require(type(record["scope"][key]) is int, "typed_count")
    require(record["policy_digest"] == POLICY, "policy_mismatch")
    issued, start, end = [instant(record["time"][key]) for key in ["issued_at", "not_before", "expires_at"]]
    life = record["time"]["lifetime_seconds"]
    require(type(life) is int and 0 < life <= 14400 and end - issued == life, "authority_lifetime")
    require(issued <= start <= now < end and issued <= now, "authority_time")
    require(record["confirmation"]["reviewed_draft_sha256"] == reviewed_digest(record), "draft_digest")
    return record
