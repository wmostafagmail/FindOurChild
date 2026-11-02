"""One explicit same-session confirmation of a server-held immutable campaign."""

import copy
import hmac
import secrets
import time
from threading import Lock
from uuid import uuid4

from .records import canonical, digest, instant, require, reviewed_digest, sha, utc, validate


class Clock:
    def __init__(self):
        self.wall, self.monotonic = time.time(), time.monotonic()
        self.lock = Lock()

    def now(self):
        with self.lock:
            wall, mono = time.time(), time.monotonic()
            require(abs((wall - self.wall) - (mono - self.monotonic)) <= 2, "clock_uncertain")
            require(wall >= self.wall, "clock_rollback")
            self.wall, self.monotonic = wall, mono
            return wall


class Confirmation:
    def __init__(self, store, template, clock, live):
        # Template is approved privileged immutable composition, not a request body.
        self.store, self.template, self.clock, self.live = store, copy.deepcopy(template), clock, live

    def current(self, session, now):
        require(self.live(session) is True and 0 <= now - session.authenticated_at <= 300
                and now < session.expires_at, "owner_current")
        require((session.issuer, session.audience, session.subject)
                == tuple(self.template["owner"][k] for k in ["issuer", "audience", "subject"]), "owner_pinned")

    def tx(self):
        dep = self.template["deployment"]
        return self.store.transaction(dep["activation_epoch"], dep["authority_epoch"])

    def prepare(self, session):
        now = self.clock.now()
        self.current(session, now)
        from .fixtures import validate_plan

        require(hasattr(self, "fixture_plan"), "fixture_plan_unprovisioned")
        plan = validate_plan(canonical(self.fixture_plan))
        require(digest(plan) == self.template["scope"]["fixture_plan_sha256"], "fixture_scope_digest")
        record = copy.deepcopy(self.template)
        nonce = secrets.token_urlsafe(32)
        record["record_id"] = str(uuid4())
        record["owner"].update(authentication_event_id=session.authentication_event_id,
                               authenticated_at=utc(session.authenticated_at))
        record["time"] = {"issued_at": utc(now), "not_before": utc(now), "expires_at": utc(now + 14400),
                          "lifetime_seconds": 14400}
        record["confirmation"] = {"event_id": str(uuid4()), "nonce_sha256": sha(nonce.encode())}
        record["confirmation"]["reviewed_draft_sha256"] = reviewed_digest(record)
        validate(canonical(record), now)
        draft = {"record": record, "session": session.session_digest, "challenge_expires": now + 300,
                 "authentication_event": session.authentication_event_id}
        with self.tx() as tx:
            self.current(session, self.clock.now())
            tx.put("draft", record["record_id"], draft)
            tx.audit("draft_prepared", digest(record))
        # Nonce only in private response, never persisted in plaintext or public artifacts.
        return {"record": record, "nonce": nonce, "challenge_expires_at": utc(now + 300)}

    def confirm(self, session, body):
        require(type(body) is dict and set(body) == {"record_id", "nonce", "reviewed_draft_sha256"}
                and all(type(v) is str and len(v) <= 128 for v in body.values()), "confirmation_closed")
        now = self.clock.now()
        self.current(session, now)
        with self.tx() as tx:
            draft = tx.get("draft", body["record_id"])
            require(draft is not None and draft["session"] == session.session_digest
                    and draft["authentication_event"] == session.authentication_event_id, "confirmation_session")
            record = draft["record"]
            require(hmac.compare_digest(sha(body["nonce"].encode()), record["confirmation"]["nonce_sha256"])
                    and hmac.compare_digest(body["reviewed_draft_sha256"], reviewed_digest(record)), "confirmation_digest")
            prior = tx.get("authorization", record["record_id"])
            # Exact retry returns the original only while still valid; never extends it.
            validate(canonical(record), now)
            require(tx.get("revocation", record["record_id"]) is None, "authorization_revoked")
            if prior is None:
                require(now < draft["challenge_expires"], "challenge_expired")
                tx.put("authorization", record["record_id"], record)
                tx.audit("owner_confirmed", digest(record))
            self.current(session, self.clock.now())
        return {"record_id": record["record_id"], "record_sha256": digest(record),
                "expires_at": record["time"]["expires_at"], "execution_available": False}

    def revoke(self, session, record_id):
        self.current(session, self.clock.now())
        with self.tx() as tx:
            require(tx.get("authorization", record_id) is not None, "authorization_unknown")
            if tx.get("revocation", record_id) is None:
                tx.put("revocation", record_id, {"record_id": record_id})
                tx.audit("owner_revoked", record_id)
            self.current(session, self.clock.now())
        return {"status": "revoked", "execution_available": False}

    def authorization(self, tx, record_id, session):
        now = self.clock.now()
        self.current(session, now)
        record = tx.get("authorization", record_id)
        require(record is not None and tx.get("revocation", record_id) is None, "authorization_missing_or_revoked")
        validate(canonical(record), now)
        require(record["deployment"] == self.template["deployment"] and record["source"] == self.template["source"]
                and record["scope"] == self.template["scope"], "authorization_binding")
        return record, min(instant(record["time"]["expires_at"]), session.expires_at)
