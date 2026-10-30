import base64
import json
from datetime import timedelta

import pytest

from tests.demo_governance.helpers import NOW, World
from tools.phase2e.demo_governance.records import (
    DOMAIN,
    Denied,
    canonical,
    decode,
    digest,
    public_key,
    signature_verify,
)
from tools.phase2e.demo_governance.registry import utc


def test_complete_chain_positive_and_distinct_actions():
    w = World()
    for kind in w.by_kind:
        assert w.verify(kind)["kind"] == kind


def test_dg_s01_wrong_domain_or_unknown_kind():
    w = World()
    for domain in ["operational", "FOC-PHASE2E-DEMO-APPROVAL-V1", "possession"]:
        p = w.payload()
        p["domain"] = domain
        with pytest.raises(Denied):
            w.verify(root=w.sign(p))
    p = w.payload()
    p["kind"] = "custody"
    with pytest.raises(Denied):
        w.verify(root=w.sign(p))


def test_dg_s02_bad_signature_and_payload():
    w = World()
    for sig in ["!", base64.b64encode(b"0" * 64).decode(), base64.b64encode(b"0" * 63).decode()]:
        env = {"payload": w.payload(), "signature": sig}
        raw = canonical(env)
        h = digest(raw)
        w.records[h] = raw
        with pytest.raises(Denied):
            w.verify(root=h)


def test_dg_s03_unknown_revoked_wrong_role():
    for mutation in [
        lambda e: e.update(revoked=True),
        lambda e: e.update(roles=["F"]),
        lambda e: e.update(person="unappointed"),
    ]:
        w = World()
        mutation(w.entries[1])
        with pytest.raises(Denied):
            w.verify()


def test_dg_s04_duplicates_unknown_trailing_noncanonical():
    for raw in [b'{"a":1,"a":2}', b'{ "a":1}', b"{} {}", b'{"a":1}\n']:
        with pytest.raises(Denied):
            decode(raw)
    w = World()
    p = w.payload()
    p["extra"] = "x"
    with pytest.raises(Denied):
        w.verify(root=w.sign(p))


def test_dg_s05_unsafe_scalars_and_times():
    for raw in [b'{"a":NaN}', b'{"a":1.2}', b'{"a":9007199254740992}', b'{"a":null}']:
        with pytest.raises(Denied):
            decode(raw)
    w = World()
    for field, value in [("epoch", True), ("issued", "2026-99-99T00:00:00Z"), ("decision", True)]:
        p = w.payload()
        p[field] = value
        with pytest.raises(Denied):
            w.verify(root=w.sign(p))


def test_dg_s06_wire_depth_list_limits():
    for raw in [b"x" * 16385, canonical({"a": {"b": {"c": {"d": {"e": 1}}}}}), canonical({"a": ["x"] * 17})]:
        with pytest.raises(Denied):
            decode(raw)


def test_dg_s07_exact_scope_and_epochs():
    w = World()
    for field in w.binding:
        p = w.payload()
        p[field] = 2 if type(p[field]) is int else "b" * 64
        with pytest.raises(Denied):
            w.verify(root=w.sign(p))


def test_dg_s08_dependencies_and_failed_evidence():
    w = World()
    p = w.payload()
    p["predecessors"] = []
    with pytest.raises(Denied):
        w.verify(root=w.sign(p))
    w = World()
    del w.records[w.by_kind["A3"]]
    with pytest.raises(Denied):
        w.verify()
    w = World()
    p = w.payload("A1b-demo")
    p["decision"] = "failed"
    with pytest.raises(Denied):
        w.verify("A1b-demo", root=w.sign(p))


def test_dg_s09_time_and_uncertain_clock():
    w = World()
    with pytest.raises(Denied):
        w.verify(clock_trusted=False)
    for field, time in [
        ("expires", NOW),
        ("issued", NOW + timedelta(seconds=1)),
        ("expires", NOW + timedelta(hours=5)),
    ]:
        p = w.payload()
        p[field] = utc(time)
        with pytest.raises(Denied):
            w.verify(root=w.sign(p))


def test_dg_s10_no_outliving_prerequisite_or_key():
    w = World()
    p = w.payload()
    p["expires"] = utc(NOW + timedelta(minutes=2))
    with pytest.raises(Denied):
        w.verify(root=w.sign(p))
    w = World()
    w.entries[0]["expires"] = utc(NOW + timedelta(seconds=30))
    with pytest.raises(Denied):
        w.verify()


def test_dg_s11_modified_replay_digest_denied():
    w = World()
    raw = w.records[w.by_kind["A7"]]
    w.records[w.by_kind["A7"]] = raw.replace(b"approved", b"rejected")
    with pytest.raises(Denied):
        w.verify()


def test_dg_s12_load_only_is_not_inference():
    w = World()
    for kind in ["A3", "A4a", "A4b", "A5-plan", "A5-result"]:
        with pytest.raises(Denied):
            w.verify(root=w.by_kind[kind])


def test_dg_s13_changed_fixture_or_informed_review():
    w = World()
    p = w.payload("A6")
    p["fixture"] = "b" * 64
    with pytest.raises(Denied):
        w.verify("A6", root=w.sign(p))
    p = w.payload("A6")
    p["blind"] = False
    with pytest.raises(Denied):
        w.verify("A6", root=w.sign(p))
    w.registry.blind_until = utc(NOW - timedelta(seconds=1))
    with pytest.raises(Denied):
        w.verify()


def test_dg_s14_no_custody_release_or_operational_action():
    w = World()
    for action in ["enrollment", "release", "custody", "public_search", "operational"]:
        with pytest.raises(Denied):
            w.verify(action, root=w.by_kind["A7"])


def test_dg_s16_test_authority_rejected_in_non_test_registry():
    w = World()
    w.registry.test_only = False
    with pytest.raises(Denied):
        w.verify()


def test_fixed_canonical_vector_and_ed25519_rfc8032_vector():
    # RFC8032 test1, public algorithm vector; not a trusted human identity/key.
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    key = Ed25519PublicKey.from_public_bytes(
        bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")
    )
    sig = bytes.fromhex(
        "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
    )
    signature_verify(key, base64.b64encode(sig).decode(), b"")
    assert canonical({"b": "ع", "a": 1}) == b'{"a":1,"b":"\\u0639"}'
    assert (
        DOMAIN.encode() + b"\x00policy\x00" + canonical({"kind": "policy"})
        == b'FOC-PHASE2E-DEMO-APPROVAL-V2\x00policy\x00{"kind":"policy"}'
    )
    with pytest.raises(Denied):
        public_key(base64.b64encode(b"not DER").decode())
    assert json.loads(canonical({"b": "ع"}))["b"] == "ع"
