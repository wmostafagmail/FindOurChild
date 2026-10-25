"""Operator-only synthetic delivery reader; never exposed as an application route.

Read the running API's private sink/key as its existing unprivileged owner.
No root/DAC override, permission changes, new container/configuration,
remote model, raw subprocess output or secret-bearing diagnostics are required.
"""

import hashlib
import json
import subprocess

from scripts.dev import ROOT, environment


def read_code():
    receipt = json.loads((ROOT / ".runtime/e2e-receipt.json").read_text())["receipt"]
    if not isinstance(receipt, str) or len(receipt) != 43:
        raise RuntimeError("Invalid isolated receipt fixture")
    name = hashlib.sha256(receipt.encode()).hexdigest() + ".json"
    program = (
        "import os,json;from pathlib import Path;from cryptography.fernet import Fernet;"
        "print(json.loads(Fernet(os.environ['FOC_CONTACT_KEY'].encode()).decrypt("
        "Path('/delivery/' + " + repr(name) + ").read_bytes()))['code'])"
    )
    result = subprocess.run(
        ["docker", "compose", "-f", str(ROOT / "compose.yaml"), "exec", "-T", "api", "python", "-c", program],
        env=environment(), cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
    )
    if result.returncode:
        # Only fixed diagnostic categories may leave this privileged fixture.
        reason = "fixture_process_failed"
        for marker, category in [
            ("FileNotFoundError", "delivery_missing"),
            ("InvalidToken", "delivery_key_mismatch"),
            ("PermissionError", "delivery_permission_denied"),
            ("is not running", "api_not_running"),
        ]:
            if marker in result.stderr:
                reason = category
                break
        raise RuntimeError("Synthetic delivery fixture unavailable: " + reason)
    code = result.stdout.strip()
    if not 16 <= len(code) <= 64 or not code.replace("-", "").replace("_", "").isalnum():
        raise RuntimeError("Invalid isolated verification fixture")
    return code


def main():
    print(read_code())


if __name__ == "__main__":
    main()
