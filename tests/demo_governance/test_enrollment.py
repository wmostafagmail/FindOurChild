import base64
import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from tests.demo_governance.helpers import World
from tools.phase2e.demo_governance.records import DOMAIN, POLICY, Denied, canonical, digest, review_identity
from tools.phase2e.demo_governance.registry import ENROLLMENT, PrivateRegistry, utc


class Enrollment:
    def __init__(self, path):
        self.w = World()
        self.now = datetime.now(UTC).replace(microsecond=0)
        self.epochs = [0, 1]
        self.oidc = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.anchor = {
            "issuer": "https://synthetic.invalid",
            "audience": "synthetic-governance",
            "subject": "synthetic-owner",
            "person": "synthetic-owner",
            "fingerprint": self.w.entries[0]["fingerprint"],
            "oidc_public_key": self.oidc.public_key()
            .public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
            .decode(),
            "project": "synthetic-test",
            "instance": "synthetic-instance",
        }
        path.chmod(0o700)
        self.store = PrivateRegistry(path.resolve(), self.anchor, lambda: tuple(self.epochs), test_only=True)
        t = int(time.time())
        self.now = datetime.fromtimestamp(t, UTC)
        self.token = jwt.encode(
            {
                "iss": self.anchor["issuer"],
                "aud": self.anchor["audience"],
                "sub": "synthetic-owner",
                "iat": t,
                "exp": t + 300,
                "auth_time": t,
                "amr": ["pwd", "otp"],
            },
            self.oidc,
            algorithm="RS256",
        )

    def prepare(self, index=0):
        e = {k: v for k, v in self.w.entries[index].items() if k in ENROLLMENT}
        e["issued"] = utc(self.now)
        e["expires"] = utc(self.now + timedelta(hours=1))
        challenge = self.store.challenge(self.token, e, self.now)
        proof = self.w.keys[e["person"]].sign(DOMAIN.encode() + b"\x00possession\x00" + challenge)
        message = canonical(
            {
                "domain": DOMAIN,
                "kind": "enrollment",
                "policy": POLICY,
                "challenge": digest(challenge),
                "epoch": self.epochs[0] + 1,
            }
        )
        owner = self.w.keys["synthetic-owner"].sign(message)
        return challenge, base64.b64encode(proof).decode(), base64.b64encode(owner).decode()

    def enroll(self, args):
        result = self.store.enroll(self.token, *args, self.now)
        return result


def test_authenticated_bootstrap_then_two_human_fixture_positive(tmp_path):
    e = Enrollment(tmp_path)
    e.epochs[:] = e.enroll(e.prepare())
    e.epochs[:] = e.enroll(e.prepare(1))
    snap = e.store.snapshot(e.now)
    assert len(snap.entries) == 2 and snap.epoch == 2 and snap.test_only
    assert not (tmp_path / "registry.sqlite").stat().st_mode & 0o077


def test_dg_r03_possession_bound_to_exact_enrollment(tmp_path):
    e = Enrollment(tmp_path)
    args = list(e.prepare())
    raw = json.loads(args[0])
    raw["enrollment"]["person"] = "foreign"
    args[0] = canonical(raw)
    with pytest.raises(Denied):
        e.enroll(args)
    with pytest.raises(Denied):
        e.store.enroll("unauthenticated", *e.prepare(), e.now)


def test_dg_r04_nonce_single_use_concurrent_and_expired(tmp_path):
    e = Enrollment(tmp_path)
    args = e.prepare()

    def attempt(_):
        try:
            return e.enroll(args)
        except Denied:
            return "denied"

    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(attempt, range(2)))
    assert results.count((1, 1)) == 1 and results.count("denied") == 1
    with pytest.raises(Denied):
        e.enroll(args)
    e.epochs[:] = [1, 1]
    args = e.prepare(1)
    with e.store.transaction() as c:
        c.execute("UPDATE challenges SET expires='2000-01-01T00:00:00Z'")
    with pytest.raises(Denied):
        e.enroll(args)


def test_dg_r14_corrupt_registry_and_audit_crash_atomicity(tmp_path):
    e = Enrollment(tmp_path)
    args = e.prepare()
    with e.store.transaction() as c:
        c.execute(
            "CREATE TRIGGER fail_audit BEFORE INSERT ON audit BEGIN SELECT RAISE(ABORT,'synthetic audit outage'); END"
        )
    import sqlite3

    with pytest.raises(sqlite3.DatabaseError):
        e.enroll(args)
    with e.store.transaction() as c:
        assert c.execute("SELECT count(*) FROM state").fetchone() == (0,)
        assert c.execute("SELECT used FROM challenges").fetchone() == (0,)
        c.execute("DROP TRIGGER fail_audit")
    e.epochs[:] = e.enroll(args)
    with e.store.transaction() as c:
        c.execute("UPDATE state SET snapshot='{}'")
    with pytest.raises((Denied, TypeError)):
        e.store.snapshot(e.now)


def test_revocation_and_restore_fail_closed(tmp_path):
    e = Enrollment(tmp_path)
    e.epochs[:] = e.enroll(e.prepare())
    e.epochs[:] = e.enroll(e.prepare(1))
    fp = e.w.entries[1]["fingerprint"]
    message = canonical(
        {
            "domain": DOMAIN,
            "kind": "revocation",
            "policy": POLICY,
            "fingerprint": fp,
            "epoch": 3,
            "activation_epoch": 2,
        }
    )
    sig = base64.b64encode(e.w.keys["synthetic-owner"].sign(message)).decode()
    assert e.store.revoke(e.token, fp, sig, e.now) == (3, 2)
    # Failed/missing external epoch reconciliation denies every readback.
    with pytest.raises(Denied):
        e.store.snapshot(e.now)
    e.epochs[:] = [3, 2]
    snap = e.store.snapshot(e.now)
    with pytest.raises(Denied):
        snap.key(fp, "T", "synthetic-reviewer", e.now)
    with e.store.transaction() as c:
        c.execute("UPDATE state SET epoch=2,activation=1")
    with pytest.raises(Denied):
        e.store.snapshot(e.now)


def store_chain(e):
    w = e.w
    w.binding.update(epoch=e.epochs[0], activation_epoch=e.epochs[1])
    for kind in w.by_kind:
        p = w.payload(kind)
        p.update(
            epoch=e.epochs[0],
            activation_epoch=e.epochs[1],
            issued=utc(e.now),
            reviewed=utc(e.now),
            expires=utc(e.now + timedelta(seconds=60)),
        )
        from tools.phase2e.demo_governance.records import KINDS

        p["predecessors"] = [w.by_kind[x] for x in KINDS[kind][1]]
        w.by_kind[kind] = w.sign(p)
    # Only exact updated chain, not superseded fixture records.
    w.records = {identity: w.records[identity] for identity in w.by_kind.values()}
    return w


def test_transactional_records_replay_and_blinding_fence(tmp_path):
    e = Enrollment(tmp_path)
    e.epochs[:] = e.enroll(e.prepare())
    e.epochs[:] = e.enroll(e.prepare(1))
    w = store_chain(e)
    assert e.store.accept(w.by_kind["A7"], w.records, w.binding, e.now, action="A7") == "synthetic-A7"
    assert e.store.accept(w.by_kind["A7"], w.records, w.binding, e.now, action="A7") == "synthetic-A7"
    p = w.payload()
    p["evidence"]["resources"] = "b" * 64
    changed = w.sign(p)
    with pytest.raises(Denied):
        e.store.accept(changed, w.records, w.binding, e.now, action="A7")
    message = canonical(
        {
            "domain": DOMAIN,
            "kind": "score-access",
            "policy": POLICY,
            "person": "synthetic-reviewer",
            "at": utc(e.now),
            "permit": w.by_kind["A7"],
            "epoch": e.epochs[0] + 1,
            "fixture": w.payload("A6")["fixture"],
            "reviewer": w.payload("A6")["person"],
            "reviewed": w.payload("A6")["reviewed"],
            "fixture_record": w.by_kind["A6"],
            "review_content": review_identity(w.payload("A6")),
        }
    )
    signature = base64.b64encode(w.keys["synthetic-owner"].sign(message)).decode()
    e.epochs[:] = e.store.note_score_access(
        e.token, "synthetic-reviewer", w.by_kind["A7"], w.records, w.binding, e.now, signature
    )
    # Score exposure is an owner-signed monotonic authority revision. Restoring
    # a pre-score DB at the old registry epoch cannot restore blinding.
    with e.store.transaction() as c:
        c.execute("DELETE FROM score_access")
    with pytest.raises(Denied):
        e.store.snapshot(e.now)
    with e.store.transaction() as c:
        c.execute("INSERT INTO score_access VALUES(?,?)", ("synthetic-reviewer", utc(e.now)))
    p = w.payload("A6")
    p["issued"] = utc(e.now + timedelta(seconds=1))
    p["reviewed"] = p["issued"]
    new = w.sign(p)
    with pytest.raises(Denied):
        e.store.accept(new, w.records, w.binding, e.now + timedelta(seconds=1), action="A6")


def test_unsigned_registry_edit_and_audit_tamper_rejected(tmp_path):
    e = Enrollment(tmp_path)
    e.epochs[:] = e.enroll(e.prepare())
    with e.store.transaction() as c:
        entries = json.loads(c.execute("SELECT snapshot FROM state").fetchone()[0])
        entries[0]["expires"] = "2099-01-01T00:00:00Z"
        c.execute("UPDATE state SET snapshot=?", (json.dumps(entries),))
    with pytest.raises(Denied):
        e.store.snapshot(e.now)
