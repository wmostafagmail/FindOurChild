"""V3 adapter for the existing fixed, non-neural Linux isolation probe only.

This is not a model provider. Native model gates remain unchanged and disabled.
"""

from tools.phase2e.demo_governance.isolation import run

from .dispatcher import Dispatcher
from .records import digest, require


def run_benign_job(fencing, token, session, inputs, image):
    Dispatcher(fencing).check(token, session, inputs, job=token.job, action=token.action)
    require(token.expires_at - fencing.confirmation.clock.now() >= 5, "probe_deadline_insufficient")
    # Fixed compiled helper, no input bytes, caller command, model, network or decoder.
    receipt = run(image, "ok")
    require(receipt["exit"] == 0 and receipt["elapsed"] < 15, "benign_worker_failed")
    fencing.publish(token, session, inputs, digest(receipt))
    return {"kind": "non_neural_engineering_probe", "receipt_sha256": digest(receipt), "inference": False}
