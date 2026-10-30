import base64
import copy
from datetime import timedelta

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from tests.demo_governance.helpers import NOW, World
from tools.phase2e.demo_governance.records import Denied, public_key
from tools.phase2e.demo_governance.registry import PrivateRegistry, configured_registry, utc


def test_dg_r01_self_bootstrap_is_not_authority(tmp_path):
    tmp_path.chmod(0o700)
    with pytest.raises(Denied):
        PrivateRegistry(tmp_path, None, lambda: (0, 1), test_only=True)


def test_dg_r02_policy_without_appointments_denies():
    w = World()
    w.registry.entries = w.entries[:1]
    with pytest.raises(Denied):
        w.verify()
    with pytest.raises(Denied):
        configured_registry()


def test_dg_r05_algorithms_and_der_fingerprint():
    k = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    der = k.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    for data in [der, b"x", base64.b64decode(World().entries[0]["der"]) + b"trailing"]:
        with pytest.raises(Denied):
            public_key(base64.b64encode(data).decode())
    w = World()
    w.entries[0]["fingerprint"] = "0" * 64
    with pytest.raises(Denied):
        w.verify()


def test_dg_r06_shared_keys_and_person_aliases():
    w = World()
    w.entries.append(copy.deepcopy(w.entries[1]))
    with pytest.raises(Denied):
        w.verify()
    w = World()
    w.entries[1]["principal"] = w.entries[0]["principal"]
    with pytest.raises(Denied):
        w.verify()


def test_dg_r07_owner_cannot_be_reviewer_even_different_key():
    w = World()
    w.entries[1]["person"] = "synthetic-owner"
    with pytest.raises(Denied):
        w.verify()
    w = World()
    w.entries[0]["roles"].append("T")
    with pytest.raises(Denied):
        w.verify()


def test_dg_r08_technical_self_operator():
    w = World()
    p = w.payload("A1b-demo")
    p["operator"] = p["person"]
    with pytest.raises(Denied):
        w.verify("A1b-demo", root=w.sign(p))


def test_dg_r09_dual_reviewer_not_blind():
    w = World()
    w.registry.blind_until = utc(NOW - timedelta(seconds=1))
    with pytest.raises(Denied):
        w.verify()


def test_dg_r10_fixture_operator_also_technical():
    w = World()
    p = w.payload("A6")
    p["operator"] = p["person"]
    with pytest.raises(Denied):
        w.verify("A6", root=w.sign(p))


def test_dg_r11_expired_revoked_future_keys():
    for field, value in [
        ("revoked", True),
        ("expires", utc(NOW)),
        ("issued", utc(NOW + timedelta(seconds=1))),
    ]:
        w = World()
        w.entries[1][field] = value
        with pytest.raises(Denied):
            w.verify()


def test_dg_r12_wrong_project_instance_or_policy():
    for field in ["project", "instance"]:
        w = World()
        w.entries[1][field] = "foreign"
        with pytest.raises(Denied):
            w.verify()


def test_dg_r13_untrusted_path_not_a_registry(tmp_path):
    tmp_path.chmod(0o777)
    w = World()
    anchor = {
        "issuer": "x",
        "audience": "x",
        "subject": "x",
        "person": "x",
        "fingerprint": "x",
        "oidc_public_key": "x",
        "project": "x",
        "instance": "x",
    }
    with pytest.raises(Denied):
        PrivateRegistry(tmp_path, anchor, lambda: (1, 1), test_only=True)
    with pytest.raises(Denied):
        configured_registry()
    assert w.registry.test_only


def test_dg_r15_rollback_and_epoch_divergence():
    w = World()
    w.epoch[0] += 1
    with pytest.raises(Denied):
        w.verify()
    w = World()
    w.epoch[1] += 1
    with pytest.raises(Denied):
        w.verify()


def test_dg_r16_no_trusted_defaults_or_test_root():
    with pytest.raises(Denied):
        configured_registry()
    w = World()
    w.registry.test_only = False
    with pytest.raises(Denied):
        w.verify()


def test_frozen_48_fixture_linkages_and_post_score_changes():
    from tools.phase2e.demo_governance.fixtures import seal_review
    from tools.phase2e.demo_governance.records import canonical, digest

    images = [
        {"id": f"synthetic-{n}", "sha256": "a" * 64, "decision": "approved", "reviewed": utc(NOW)}
        for n in range(48)
    ]
    links = [
        {"left": images[n]["id"], "right": images[n + 1]["id"], "decision": "fictional_link"}
        for n in range(0, 48, 2)
    ]
    partitions = {
        "gallery": [images[n]["id"] for n in range(0, 48, 2)],
        "query": [images[n]["id"] for n in range(1, 48, 2)],
    }
    raw = canonical({"images": images, "links": links, "partitions": partitions})
    identity = digest(raw)
    assert seal_review(images, links, partitions, fixture=identity) == raw
    assert seal_review(images, links, partitions, fixture=identity, previous=raw, score_seen=True) == raw
    images[0]["decision"] = "rejected"
    changed = canonical({"images": images, "links": links, "partitions": partitions})
    with pytest.raises(Denied):
        seal_review(images, links, partitions, fixture=digest(changed), previous=raw, score_seen=True)
