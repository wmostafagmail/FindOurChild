"""Private transactional registry. No default root, human key generator or signer.

Bootstrap requires a pinned OIDC issuer/audience/subject, MFA and owner key proof.
The OIDC verification key is administrator-installed, never supplied by a request.
Storage is operator-private; an independently held epoch must be reconciled after
restore. SQLite serializes enrollment/revocation/challenge consumption and audit.
"""

import json
import os
import secrets
import sqlite3
import stat
from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path

import jwt

from .records import DOMAIN, POLICY, canonical, digest, public_key, require, signature_verify, time_value

ENROLLMENT = {
    "person",
    "principal",
    "der",
    "roles",
    "project",
    "instance",
    "issued",
    "expires",
    "test_only",
    "manifest",
    "gates",
}


def utc(value):
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


class Registry:
    def __init__(
        self,
        *,
        entries,
        owner_person,
        project,
        instance,
        epoch,
        activation_epoch,
        current_epoch,
        blind_until,
        test_only=False,
    ):
        require(type(entries) is list, "registry_entries")
        self.entries, self.owner_person = entries, owner_person
        self.project, self.instance = project, instance
        self.epoch, self.activation_epoch, self.current_epoch = epoch, activation_epoch, current_epoch
        self.blind_until, self.test_only = blind_until, test_only

    def validate(self, now):
        require(
            type(self.epoch) is int
            and self.epoch > 0
            and (self.epoch, self.activation_epoch) == self.current_epoch(),
            "stale_registry",
        )
        require(bool(self.owner_person), "owner_unprovisioned")
        people, principals, fingerprints = {}, {}, set()
        owners = []
        for entry in self.entries:
            require(
                type(entry) is dict and set(entry) == ENROLLMENT | {"revoked", "fingerprint"},
                "registry_fields",
            )
            _, fp = public_key(entry["der"])
            require(entry["fingerprint"] == fp and fp not in fingerprints, "shared_key")
            fingerprints.add(fp)
            require(type(entry["test_only"]) is bool and entry["test_only"] == self.test_only, "test_trust")
            require(entry["project"] == self.project and entry["instance"] == self.instance, "registry_scope")
            require(type(entry["revoked"]) is bool, "revocation_type")
            from .records import KINDS, sha

            require(
                sha(entry["manifest"])
                and type(entry["gates"]) is list
                and entry["gates"]
                and len(set(entry["gates"])) == len(entry["gates"])
                and all(g in KINDS and KINDS[g][0] in entry["roles"] for g in entry["gates"]),
                "key_gates",
            )
            roles = entry["roles"]
            require(
                type(roles) is list
                and roles
                and len(set(roles)) == len(roles)
                and set(roles) <= {"O", "T", "F"},
                "roles",
            )
            require(not ("O" in roles and set(roles) & {"T", "F"}), "owner_conflict")
            person, principal = entry["person"], entry["principal"]
            require(type(person) is str and person and type(principal) is str and principal, "identity")
            require(
                people.get(person, principal) == principal and principals.get(principal, person) == person,
                "identity_alias",
            )
            people[person], principals[principal] = principal, person
            require(not (person == self.owner_person and set(roles) & {"T", "F"}), "owner_alias")
            issued, expires = time_value(entry["issued"]), time_value(entry["expires"])
            require(0 < (expires - issued).total_seconds() <= 90 * 86400, "enrollment_lifetime")
            if "O" in roles and not entry["revoked"] and issued <= now < expires:
                owners.append(person)
        require(owners == [self.owner_person], "owner_authority")

    def key(self, fingerprint, role, person, now, *, gate=None, manifest=None):
        matches = [x for x in self.entries if x["fingerprint"] == fingerprint]
        require(len(matches) == 1, "unknown_key")
        e = matches[0]
        require(
            e["person"] == person
            and role in e["roles"]
            and not e["revoked"]
            and time_value(e["issued"]) <= now < time_value(e["expires"]),
            "inactive_key",
        )
        if gate is not None:
            require(gate in e["gates"] and manifest == e["manifest"], "key_scope")
        return e


class PrivateRegistry:
    """The directory and anchor are privileged deployment inputs, not API fields.

    The caller must keep the external epoch outside this store's backup set.
    No method issues an inference/acquisition permit or edits production switches.
    """

    def __init__(self, directory, anchor, external_epoch, *, test_only=False):
        self.directory, self.anchor = Path(directory), anchor
        self.external_epoch, self.test_only = external_epoch, test_only
        require(
            anchor is not None
            and set(anchor)
            == {
                "issuer",
                "audience",
                "subject",
                "person",
                "fingerprint",
                "oidc_public_key",
                "project",
                "instance",
            },
            "no_anchor",
        )
        info = self.directory.lstat()
        require(
            stat.S_ISDIR(info.st_mode)
            and not stat.S_ISLNK(info.st_mode)
            and info.st_uid == os.geteuid()
            and info.st_mode & 0o077 == 0,
            "private_directory",
        )
        # Reject writable ancestors owned by an untrusted different UID. /tmp is
        # permitted only as sticky root ancestor for disposable synthetic tests.
        for parent in self.directory.parents:
            s = parent.lstat()
            require(stat.S_ISDIR(s.st_mode) and not stat.S_ISLNK(s.st_mode), "registry_parent")
            require(not s.st_mode & 0o022 or (test_only and s.st_mode & stat.S_ISVTX), "registry_parent")
        self.path = self.directory / "registry.sqlite"
        if self.path.exists() or self.path.is_symlink():
            s = self.path.lstat()
            require(
                stat.S_ISREG(s.st_mode)
                and s.st_nlink == 1
                and s.st_uid == os.geteuid()
                and s.st_mode & 0o077 == 0,
                "registry_file",
            )
        else:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
            os.close(fd)
        with self.transaction() as c:
            c.executescript("""CREATE TABLE IF NOT EXISTS state(singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                epoch INTEGER NOT NULL, activation INTEGER NOT NULL, snapshot TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS challenges(nonce TEXT PRIMARY KEY, payload BLOB NOT NULL,
                expires TEXT NOT NULL, used INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY, event TEXT NOT NULL,
                payload TEXT NOT NULL, previous TEXT NOT NULL, digest TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS records(digest TEXT PRIMARY KEY, record_id TEXT UNIQUE NOT NULL, body BLOB NOT NULL);
                CREATE TABLE IF NOT EXISTS score_access(person TEXT PRIMARY KEY, first_seen TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS changes(epoch INTEGER PRIMARY KEY, action TEXT NOT NULL,
                message BLOB NOT NULL, signature TEXT NOT NULL, challenge BLOB, proof TEXT);
            """)

    @contextmanager
    def transaction(self):
        c = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        try:
            c.execute("PRAGMA synchronous=FULL")
            c.execute("PRAGMA journal_mode=DELETE")
            c.execute("BEGIN IMMEDIATE")
            yield c
            c.commit()
        except BaseException:
            c.rollback()
            raise
        finally:
            c.close()

    def authenticate_owner(self, token, now):
        require(
            type(token) is str and 0 < len(token) <= 8192 and now.tzinfo is not None, "owner_authentication"
        )
        try:
            p = jwt.decode(
                token,
                self.anchor["oidc_public_key"],
                algorithms=["RS256"],
                audience=self.anchor["audience"],
                issuer=self.anchor["issuer"],
                options={"require": ["exp", "iat", "sub", "auth_time", "amr"]},
            )
        except jwt.PyJWTError:
            require(False, "owner_authentication")
        require(
            p["sub"] == self.anchor["subject"]
            and {"pwd", "otp"}.issubset(set(p["amr"]))
            and 0 <= now.timestamp() - p["auth_time"] <= 300,
            "owner_authentication",
        )
        return self.anchor["person"]

    def audit(self, c, event, payload):
        previous = c.execute("SELECT digest FROM audit ORDER BY seq DESC LIMIT 1").fetchone()
        previous = previous[0] if previous else "0" * 64
        raw = canonical({"event": event, "payload": payload, "previous": previous})
        c.execute(
            "INSERT INTO audit(event,payload,previous,digest) VALUES(?,?,?,?)",
            (event, canonical(payload).decode(), previous, digest(raw)),
        )

    def challenge(self, token, enrollment, now):
        self.authenticate_owner(token, now)
        require(
            set(enrollment) == ENROLLMENT and enrollment["test_only"] is self.test_only, "enrollment_fields"
        )
        require(
            enrollment["project"] == self.anchor["project"]
            and enrollment["instance"] == self.anchor["instance"],
            "enrollment_scope",
        )
        public_key(enrollment["der"])
        # No authority is created by receiving this nonce.
        nonce = secrets.token_hex(32)
        payload = {
            "domain": DOMAIN,
            "kind": "possession",
            "policy": POLICY,
            "nonce": nonce,
            "enrollment": enrollment,
            "expires": utc(now + timedelta(minutes=5)),
        }
        from .records import decode

        decode(canonical(payload))
        with self.transaction() as c:
            require(c.execute("SELECT count(*) FROM challenges").fetchone()[0] < 1024, "challenge_quota")
            c.execute(
                "INSERT INTO challenges(nonce,payload,expires) VALUES(?,?,?)",
                (nonce, canonical(payload), payload["expires"]),
            )
            self.audit(c, "challenge", {"nonce_digest": digest(nonce.encode())})
        return canonical(payload)

    def enroll(self, token, challenge, proof, owner_signature, now):
        self.authenticate_owner(token, now)
        from .records import decode

        payload = decode(challenge)
        require(
            set(payload) == {"domain", "kind", "policy", "nonce", "enrollment", "expires"}
            and payload["domain"] == DOMAIN
            and payload["kind"] == "possession"
            and payload["policy"] == POLICY,
            "possession_domain",
        )
        e = payload["enrollment"]
        require(set(e) == ENROLLMENT and e["test_only"] is self.test_only, "enrollment_fields")
        key, fp = public_key(e["der"])
        signature_verify(key, proof, DOMAIN.encode() + b"\x00possession\x00" + challenge)
        with self.transaction() as c:
            row = c.execute(
                "SELECT payload,expires,used FROM challenges WHERE nonce=?", (payload["nonce"],)
            ).fetchone()
            require(
                row and bytes(row[0]) == challenge and row[2] == 0 and now < time_value(row[1]),
                "challenge_state",
            )
            old = c.execute("SELECT epoch,activation,snapshot FROM state WHERE singleton=1").fetchone()
            epoch, activation, entries = (old[0], old[1], json.loads(old[2])) if old else (0, 1, [])
            require((epoch, activation) == self.external_epoch(), "external_epoch")
            if not old:
                require(
                    fp == self.anchor["fingerprint"]
                    and e["person"] == self.anchor["person"]
                    and e["principal"] == self.anchor["subject"]
                    and e["roles"] == ["O"],
                    "bootstrap_anchor",
                )
                owner_key = key
            else:
                self._verify_history(c, entries, epoch, activation)
                snapshot = self._snapshot(entries, epoch, activation)
                snapshot.validate(now)
                owner = next(x for x in entries if "O" in x["roles"] and not x["revoked"])
                owner_key, _ = public_key(owner["der"])
            authorization = canonical(
                {
                    "domain": DOMAIN,
                    "kind": "enrollment",
                    "policy": POLICY,
                    "challenge": digest(challenge),
                    "epoch": epoch + 1,
                }
            )
            signature_verify(owner_key, owner_signature, authorization)
            entry = dict(e, fingerprint=fp, revoked=False)
            entries.append(entry)
            c.execute(
                "INSERT INTO changes VALUES(?,?,?,?,?,?)",
                (epoch + 1, "enrollment", authorization, owner_signature, challenge, proof),
            )
            self._snapshot(entries, epoch + 1, activation, epoch_override=(epoch + 1, activation)).validate(
                now
            )
            c.execute(
                "INSERT INTO state VALUES(1,?,?,?) ON CONFLICT(singleton) DO UPDATE SET "
                "epoch=excluded.epoch,activation=excluded.activation,snapshot=excluded.snapshot",
                (epoch + 1, activation, canonical(entries).decode()),
            )
            c.execute("UPDATE challenges SET used=1 WHERE nonce=? AND used=0", (payload["nonce"],))
            self.audit(c, "enrolled", {"fingerprint": fp, "epoch": epoch + 1})
            # External epoch installation is deliberately a separate controlled
            # step. Until installed, readback fails closed (also after restore).
        return epoch + 1, activation

    def _snapshot(self, entries, epoch, activation, epoch_override=None):
        return Registry(
            entries=entries,
            owner_person=self.anchor["person"],
            project=self.anchor["project"],
            instance=self.anchor["instance"],
            epoch=epoch,
            activation_epoch=activation,
            current_epoch=(lambda: epoch_override) if epoch_override else self.external_epoch,
            blind_until="1970-01-01T00:00:00Z",
            test_only=self.test_only,
        )

    def snapshot(self, now):
        with self.transaction() as c:
            row = c.execute("SELECT epoch,activation,snapshot FROM state WHERE singleton=1").fetchone()
            require(row is not None, "unprovisioned")
            entries = json.loads(row[2])
            self._verify_history(c, entries, row[0], row[1])
            result = self._snapshot(entries, row[0], row[1])
            result.validate(now)
            return result

    def revoke(self, token, fingerprint, signature, now):
        self.authenticate_owner(token, now)
        with self.transaction() as c:
            epoch, activation, raw = c.execute(
                "SELECT epoch,activation,snapshot FROM state WHERE singleton=1"
            ).fetchone()
            entries = json.loads(raw)
            self._verify_history(c, entries, epoch, activation)
            snap = self._snapshot(entries, epoch, activation)
            snap.validate(now)
            owner = next(e for e in entries if "O" in e["roles"] and not e["revoked"])
            message = canonical(
                {
                    "domain": DOMAIN,
                    "kind": "revocation",
                    "policy": POLICY,
                    "fingerprint": fingerprint,
                    "epoch": epoch + 1,
                    "activation_epoch": activation + 1,
                }
            )
            signature_verify(public_key(owner["der"])[0], signature, message)
            target = [e for e in entries if e["fingerprint"] == fingerprint and not e["revoked"]]
            require(len(target) == 1, "revocation_target")
            target[0]["revoked"] = True
            c.execute(
                "INSERT INTO changes VALUES(?,?,?,?,NULL,NULL)", (epoch + 1, "revocation", message, signature)
            )
            c.execute(
                "UPDATE state SET epoch=?,activation=?,snapshot=? WHERE singleton=1",
                (epoch + 1, activation + 1, canonical(entries).decode()),
            )
            self.audit(c, "revoked", {"fingerprint": fingerprint, "epoch": epoch + 1})
        return epoch + 1, activation + 1

    def _verify_history(self, c, entries, epoch, activation):
        from .records import decode

        derived, expected_epoch, expected_activation = [], 0, 1
        seen_scores = {}
        owner_key = None
        for revision, action, raw, sig, challenge, proof in c.execute("SELECT * FROM changes ORDER BY epoch"):
            expected_epoch += 1
            require(revision == expected_epoch, "history_gap")
            message = decode(bytes(raw))
            require(
                message["domain"] == DOMAIN
                and message["policy"] == POLICY
                and message["kind"] == action
                and message["epoch"] == revision,
                "history_domain",
            )
            if action == "enrollment":
                require(set(message) == {"domain", "kind", "policy", "challenge", "epoch"}, "history_fields")
                payload = decode(bytes(challenge))
                require(digest(bytes(challenge)) == message["challenge"], "history_challenge")
                e = payload["enrollment"]
                key, fp = public_key(e["der"])
                signature_verify(key, proof, DOMAIN.encode() + b"\x00possession\x00" + bytes(challenge))
                if not derived:
                    require(
                        fp == self.anchor["fingerprint"]
                        and e["person"] == self.anchor["person"]
                        and e["principal"] == self.anchor["subject"]
                        and e["roles"] == ["O"],
                        "history_root",
                    )
                    owner_key = key
                derived.append(dict(e, fingerprint=fp, revoked=False))
            elif action == "score-access":
                require(
                    set(message) == {"domain", "kind", "policy", "person", "at", "permit", "epoch"},
                    "score_history_fields",
                )
                require(any(e["person"] == message["person"] for e in derived), "score_history_person")
                time_value(message["at"])
                seen_scores.setdefault(message["person"], message["at"])
            else:
                require(
                    action == "revocation"
                    and set(message)
                    == {"domain", "kind", "policy", "fingerprint", "epoch", "activation_epoch"},
                    "history_action",
                )
                expected_activation += 1
                require(message["activation_epoch"] == expected_activation, "history_activation")
                matches = [
                    e for e in derived if e["fingerprint"] == message["fingerprint"] and not e["revoked"]
                ]
                require(len(matches) == 1, "history_revocation")
                matches[0]["revoked"] = True
            require(owner_key is not None, "history_owner")
            signature_verify(owner_key, sig, bytes(raw))
        require(
            (expected_epoch, expected_activation) == (epoch, activation) and derived == entries,
            "unsigned_registry_or_rollback",
        )
        require(
            dict(c.execute("SELECT person,first_seen FROM score_access")) == seen_scores,
            "unsigned_score_history",
        )
        previous = "0" * 64
        for event, payload, prior, actual in c.execute(
            "SELECT event,payload,previous,digest FROM audit ORDER BY seq"
        ):
            require(prior == previous, "audit_history")
            raw = canonical({"event": event, "payload": json.loads(payload), "previous": previous})
            require(digest(raw) == actual, "audit_integrity")
            previous = actual

    def accept(self, root, records, binding, now, *, action):
        """Consume verified signed records idempotently; never signs/activates.

        Exact replay returns the same digest. A changed record-ID conflicts.
        Persisted audit, record and epoch readback are one transaction.
        """
        from .records import decode, validate_chain

        with self.transaction() as c:
            row = c.execute("SELECT epoch,activation,snapshot FROM state WHERE singleton=1").fetchone()
            require(row is not None, "unprovisioned")
            entries = json.loads(row[2])
            self._verify_history(c, entries, row[0], row[1])
            registry = self._snapshot(entries, row[0], row[1])
            earliest = c.execute("SELECT min(first_seen) FROM score_access").fetchone()[0]
            registry.blind_until = earliest or utc(now)
            payload = validate_chain(root, records, registry, binding, now, action=action)
            needed = set()

            def walk(identity):
                if identity in needed:
                    return
                needed.add(identity)
                for dep in decode(records[identity])["payload"]["predecessors"]:
                    walk(dep)

            walk(root)
            for identity in needed:
                raw = records[identity]
                record = decode(raw)["payload"]
                old = c.execute("SELECT digest FROM records WHERE record_id=?", (record["id"],)).fetchone()
                require(old is None or old[0] == identity, "changed_record_replay")
                c.execute("INSERT OR IGNORE INTO records VALUES(?,?,?)", (identity, record["id"], raw))
            self.audit(c, "record_validated", {"digest": root, "action": action})
            require((row[0], row[1]) == self.external_epoch(), "authority_changed_during_audit")
            return payload["id"]

    def note_score_access(self, token, person, root, records, binding, now, owner_signature):
        """Future trusted score projection must call BEFORE releasing any score.

        This only records a monotonic blinding fence; it exposes no scores and
        cannot activate a provider. A7 is necessary even for technical tooling.
        """
        from .records import validate_chain

        self.authenticate_owner(token, now)
        with self.transaction() as c:
            row = c.execute("SELECT epoch,activation,snapshot FROM state WHERE singleton=1").fetchone()
            require(row is not None, "unprovisioned")
            entries = json.loads(row[2])
            self._verify_history(c, entries, row[0], row[1])
            registry = self._snapshot(entries, row[0], row[1])
            earliest = c.execute("SELECT min(first_seen) FROM score_access").fetchone()[0]
            registry.blind_until = earliest or utc(now)
            validate_chain(root, records, registry, binding, now, action="A7")
            require(any(e["person"] == person for e in entries), "unknown_score_viewer")
            require((row[0], row[1]) == self.external_epoch(), "authority_changed_during_audit")
            owner = next(e for e in entries if "O" in e["roles"] and not e["revoked"])
            message = canonical(
                {
                    "domain": DOMAIN,
                    "kind": "score-access",
                    "policy": POLICY,
                    "person": person,
                    "at": utc(now),
                    "permit": root,
                    "epoch": row[0] + 1,
                }
            )
            signature_verify(public_key(owner["der"])[0], owner_signature, message)
            c.execute(
                "INSERT INTO changes VALUES(?,?,?,?,NULL,NULL)",
                (row[0] + 1, "score-access", message, owner_signature),
            )
            c.execute("INSERT OR IGNORE INTO score_access VALUES(?,?)", (person, utc(now)))
            c.execute("UPDATE state SET epoch=? WHERE singleton=1", (row[0] + 1,))
            self.audit(c, "score_access_fence", {"person": person, "permit": root, "epoch": row[0] + 1})
        # Deny further reads/publication until the independently held epoch is
        # installed. This also prevents pre-score backup restoration at the
        # same epoch. Existing A7 authority needs fresh owner review/renewal.
        return row[0] + 1, row[1]


def configured_registry():
    """No path override, test registry, or automatically trusted default."""
    config = json.loads(
        (Path(__file__).resolve().parents[3] / "config/phase2e/demo-governance.json").read_text()
    )
    require(config["owner_anchor"] is not None and config["registry"] is not None, "unprovisioned")
    require(False, "deployment_enrollment_not_authorized")
