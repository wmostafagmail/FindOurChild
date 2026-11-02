"""Fixed V3 routing. Real effects remain unconditionally unavailable in D1–D4."""

from .receipts import DEPENDENCIES, chain
from .records import DOMAIN, require

STAGE = {"acquire_quarantine": "source", "verify_bytes": "quarantine", "process_bounded": "bytes",
         "load_qualification": "processed", "private_image_inference": "ready",
         "private_similarity_retrieval": "result", "private_result_view": "result"}


class Dispatcher:
    def __init__(self, fencing):
        self.fencing = fencing

    def check(self, token, session, inputs, *, job, action, revision=1):
        with self.fencing.confirmation.tx() as tx:
            self.fencing.validate(token, session, inputs, job=job, action=action, revision=revision, tx=tx)

    def execute(self, token, session, inputs, *, job, action, revision=1):
        self.check(token, session, inputs, job=job, action=action, revision=revision)
        # A valid intent or a configuration flag cannot create approved providers.
        # Separate acquisition, parser and inference provisioning are not authorized.
        require(False, "v3_actual_execution_not_authorized")

    def technical_admission(self, token, session, inputs, *, job, action, revision=1):
        with self.fencing.confirmation.tx() as tx:
            self.fencing.validate(token, session, inputs, job=job, action=action, revision=revision, tx=tx)
            require(action in STAGE, "closed_action")
            rows = {name: tx.get("receipt", job + ":" + name) for name in DEPENDENCIES}
            rows = {name: value for name, value in rows.items() if value is not None}
            expiry = chain(rows, STAGE[action], job=job, inputs=inputs,
                           now=self.fencing.confirmation.clock.now())
            require(token.expires_at <= expiry, "receipt_lease_intersection")
            return {"technical_stage_verified": STAGE[action], "execution_available": False}


def select_policy(requested=None):
    require(requested in (None, DOMAIN), "no_policy_fallback")
    return DOMAIN
