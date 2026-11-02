"""Short internal capabilities and repeated live checks; no bearer owner token crosses to workers."""

import hmac
import secrets
import time
from dataclasses import dataclass

from .records import canonical, digest, require, sha


@dataclass(frozen=True)
class Lease:
    job: str
    record_id: str
    action: str
    inputs_sha256: str
    instance: str
    tenant: str
    activation_epoch: int
    authority_epoch: int
    revision: int
    issued_at: float
    expires_at: float
    monotonic_deadline: float
    mac: str


class Fencing:
    def __init__(self, confirmation, live_grants, *, secret=None):
        self.confirmation, self.live_grants = confirmation, live_grants
        self.secret = secret if secret is not None else secrets.token_bytes(32)

    def _mac(self, fields):
        return hmac.new(self.secret, canonical(fields), "sha256").hexdigest()

    def issue(self, session, record_id, action, inputs, *, job, receipt_expiry, hard_deadline, revision=1):
        now = self.confirmation.clock.now()
        require(self.live_grants(session, action, inputs) is True, "current_grants")
        with self.confirmation.tx() as tx:
            record, end = self.confirmation.authorization(tx, record_id, session)
            require(action in record["scope"]["actions"], "action_scope")
            expiry = min(now + 30, end, receipt_expiry, hard_deadline)
            require(now < expiry, "capability_expired")
            dep = record["deployment"]
            fields = {"job": job, "record_id": record_id, "action": action, "inputs_sha256": digest(inputs),
                      "instance": dep["instance_id"], "tenant": dep["tenant_id"],
                      "activation_epoch": dep["activation_epoch"], "authority_epoch": dep["authority_epoch"],
                      "revision": revision, "issued_at": now, "expires_at": expiry,
                      "monotonic_deadline": time.monotonic() + expiry - now}
            token = Lease(**fields, mac=self._mac(fields))
            tx.put("job", sha((job + ":" + str(revision)).encode()), {"lease_digest": digest(vars(token))})
            tx.audit("capability_issued", digest(vars(token)))
            require(self.live_grants(session, action, inputs) is True, "current_grants")
            self.confirmation.current(session, self.confirmation.clock.now())
        return token

    def validate(self, token, session, inputs, *, job, action, revision, tx):
        fields = {k: v for k, v in vars(token).items() if k != "mac"}
        require(hmac.compare_digest(self._mac(fields), token.mac), "capability_mac")
        now = self.confirmation.clock.now()
        record, _ = self.confirmation.authorization(tx, token.record_id, session)
        dep = record["deployment"]
        require(token.job == job and token.action == action and token.revision == revision
                and token.inputs_sha256 == digest(inputs) and action in record["scope"]["actions"]
                and (token.instance, token.tenant, token.activation_epoch, token.authority_epoch)
                == (dep["instance_id"], dep["tenant_id"], dep["activation_epoch"], dep["authority_epoch"]),
                "capability_binding")
        require(token.issued_at <= now < token.expires_at <= token.issued_at + 30
                and time.monotonic() < token.monotonic_deadline, "capability_deadline")
        row = tx.get("job", sha((job + ":" + str(revision)).encode()))
        require(row == {"lease_digest": digest(vars(token))}, "job_revision")
        require(tx.get("revocation", job) is None and self.live_grants(session, action, inputs) is True,
                "job_or_grants_revoked")

    def publish(self, token, session, inputs, result_digest, *, revision=1):
        with self.confirmation.tx() as tx:
            self.validate(token, session, inputs, job=token.job, action=token.action, revision=revision, tx=tx)
            result = {"result_digest": result_digest, "lease_digest": digest(vars(token))}
            prior = tx.get("receipt", "result:" + token.job)
            require(prior is None or prior == result, "publication_replay_conflict")
            if prior is not None:
                return  # Current valid exact retry: no new result, audit event or outbox delivery.
            tx.audit("result_publication_requested", result_digest)
            # Explicit second check AFTER a potentially blocking audit operation.
            self.validate(token, session, inputs, job=token.job, action=token.action, revision=revision, tx=tx)
            tx.put("receipt", "result:" + token.job, result)

    def cancel(self, session, job):
        self.confirmation.current(session, self.confirmation.clock.now())
        with self.confirmation.tx() as tx:
            tx.put("revocation", job, {"job": job})
            tx.audit("job_cancelled", job)
