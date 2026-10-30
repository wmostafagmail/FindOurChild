"""Disposable synthetic authority. NEVER copied into config, deployment or CI secrets."""

import base64
from datetime import UTC, datetime, timedelta

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.phase2e.demo_governance.records import DOMAIN, KINDS, POLICY, canonical, digest, signed_bytes
from tools.phase2e.demo_governance.registry import Registry, utc

NOW = datetime(2026, 10, 30, 16, tzinfo=UTC)
H = "a" * 64


class World:
    def __init__(self):
        self.keys = {p: Ed25519PrivateKey.generate() for p in ["synthetic-owner", "synthetic-reviewer"]}
        self.entries = []
        self.epoch = [1, 1]
        for person, roles in [("synthetic-owner", ["O"]), ("synthetic-reviewer", ["T", "F"])]:
            key = self.keys[person]
            der = key.public_key().public_bytes(
                serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
            )
            self.entries.append(
                {
                    "person": person,
                    "principal": person,
                    "der": base64.b64encode(der).decode(),
                    "fingerprint": digest(der),
                    "roles": roles,
                    "manifest": H,
                    "gates": [kind for kind, spec in KINDS.items() if spec[0] in roles],
                    "project": "synthetic-test",
                    "instance": "synthetic-instance",
                    "issued": utc(NOW - timedelta(days=1)),
                    "expires": utc(NOW + timedelta(days=1)),
                    "revoked": False,
                    "test_only": True,
                }
            )
        self.registry = Registry(
            entries=self.entries,
            owner_person="synthetic-owner",
            project="synthetic-test",
            instance="synthetic-instance",
            epoch=1,
            activation_epoch=1,
            current_epoch=lambda: tuple(self.epoch),
            blind_until=utc(NOW),
            test_only=True,
        )
        self.binding = {
            "project": "synthetic-test",
            "instance": "synthetic-instance",
            "manifest": H,
            "build": H,
            "space": "synthetic-space",
            "fixture": H,
            "epoch": 1,
            "activation_epoch": 1,
        }
        self.records, self.by_kind = {}, {}
        for kind, (role, deps, evidence, lifetime) in KINDS.items():
            person = "synthetic-owner" if role == "O" else "synthetic-reviewer"
            p = dict(
                self.binding,
                domain=DOMAIN,
                policy=POLICY,
                kind=kind,
                id="synthetic-" + kind,
                key=self.entries[0 if role == "O" else 1]["fingerprint"],
                person=person,
                operator="synthetic-owner",
                issued=utc(NOW),
                expires=utc(NOW + timedelta(seconds=60)),
                reviewed=utc(NOW),
                decision="approved",
                blind=role == "F",
                data_class="fictional_demo_only",
                predecessors=[self.by_kind[d] for d in deps],
                evidence={e: H for e in evidence},
            )
            self.by_kind[kind] = self.sign(p)

    def sign(self, payload):
        sig = self.keys[payload["person"]].sign(signed_bytes(payload))
        raw = canonical({"payload": payload, "signature": base64.b64encode(sig).decode()})
        identity = digest(raw)
        self.records[identity] = raw
        return identity

    def payload(self, kind="A7"):
        import json

        return json.loads(self.records[self.by_kind[kind]])["payload"]

    def verify(self, kind="A7", root=None, **kwargs):
        from tools.phase2e.demo_governance.records import validate_chain

        return validate_chain(
            root or self.by_kind[kind], self.records, self.registry, self.binding, NOW, action=kind, **kwargs
        )
