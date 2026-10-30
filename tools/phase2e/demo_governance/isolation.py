"""Fixed source-only Linux helper execution. No arbitrary commands/models/assets."""

import json
import os
import subprocess
import time
import uuid
from pathlib import Path

from .records import require

MODES = {
    "ok",
    "sleep",
    "spin",
    "memory",
    "descendant",
    "fds",
    "output",
    "attack",
    "pids",
    "network",
    "stdout",
}


def profile(info, image_id):
    h = info["HostConfig"]
    require(info["Image"] == image_id and info["Config"]["User"] == "10001:10001", "image_identity")
    require(
        h["NetworkMode"] == "none"
        and h["ReadonlyRootfs"]
        and not h["Privileged"]
        and h["CapDrop"] == ["ALL"]
        and "no-new-privileges:true" in h["SecurityOpt"]
        and h["Memory"] == h["MemorySwap"] == 134217728
        and h["PidsLimit"] == 32
        and h["NanoCpus"] == 1000000000
        and not h.get("Devices")
        and not info["Mounts"],
        "isolation_profile",
    )
    require(h["Tmpfs"] == {"/tmp": "rw,noexec,nosuid,nodev,size=1m,mode=1777"}, "tmpfs_profile")


def run(image_id, mode, *, lose_client=False, kill_supervisor=False):
    require(mode in MODES and image_id.startswith("sha256:") and len(image_id) == 71, "fixed_probe")
    name = "foc-governance-probe-" + uuid.uuid4().hex
    started = time.monotonic()
    cid = (
        subprocess.check_output(
            [
                "docker",
                "create",
                "--name",
                name,
                "--network",
                "none",
                "--read-only",
                "--user",
                "10001:10001",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges:true",
                "--cpus",
                "1",
                "--memory",
                "128m",
                "--memory-swap",
                "128m",
                "--pids-limit",
                "32",
                "--tmpfs",
                "/tmp:rw,noexec,nosuid,nodev,size=1m,mode=1777",
                image_id,
                mode,
            ],
            timeout=15,
        )
        .decode()
        .strip()
    )
    require(len(cid) == 64, "container_identity")
    try:
        (info,) = json.loads(subprocess.check_output(["docker", "inspect", cid], timeout=10))
        profile(info, image_id)
        client = subprocess.Popen(
            ["docker", "start", "--attach", cid], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if lose_client or kill_supervisor:
            # Observe actual running PID namespace before killing our client.
            until = time.monotonic() + 10
            while True:
                (state,) = json.loads(subprocess.check_output(["docker", "inspect", cid], timeout=2))
                if state["State"]["Running"]:
                    break
                require(time.monotonic() < until, "probe_start")
            if lose_client:
                client.kill()
        if kill_supervisor:
            # Stable full container ID, never a recycled host PID/name.
            subprocess.run(
                ["docker", "kill", "--signal", "KILL", cid], check=True, timeout=5, capture_output=True
            )
        try:
            client.communicate(timeout=8)
        except subprocess.TimeoutExpired:
            require(False, "supervisor_failed_deadline")
        # No polling/control-plane kill enforces the helper's 3s deadline.
        until = time.monotonic() + 6
        while True:
            (state,) = json.loads(subprocess.check_output(["docker", "inspect", cid], timeout=2))
            if not state["State"]["Running"]:
                break
            require(time.monotonic() < until, "helper_survived_deadline")
            time.sleep(0.05)
        require(state["State"]["Pid"] == 0 and time.monotonic() - started < 15, "namespace_not_reaped")
        receipt = {
            "mode": mode,
            "exit": state["State"]["ExitCode"],
            "oom": state["State"]["OOMKilled"],
            "elapsed": time.monotonic() - started,
            "client_lost": lose_client,
            "supervisor_killed": kill_supervisor,
            "synthetic_only": True,
        }
        raw = subprocess.check_output(["docker", "logs", cid], timeout=5)
        if not kill_supervisor and not state["State"]["OOMKilled"]:
            native = json.loads(raw)
            require(
                set(native)
                == {
                    "synthetic_only",
                    "deadline_ms",
                    "status",
                    "inference",
                    "max_child_rss_kib",
                    "cpu_us",
                    "wall_ms",
                }
                and native["synthetic_only"] is True
                and native["inference"] is False
                and native["status"] == receipt["exit"]
                and native["deadline_ms"] == 3000
                and all(
                    type(native[k]) is int and native[k] >= 0
                    for k in ["max_child_rss_kib", "cpu_us", "wall_ms"]
                ),
                "native_resource_receipt",
            )
            receipt["native_metrics"] = native
        else:
            receipt["native_metrics"] = None
        receipt["image"] = image_id
        receipt["limits"] = {
            "memory_bytes": 134217728,
            "memory_swap_bytes": 134217728,
            "pids": 32,
            "cpu_nanos": 1000000000,
            "tmpfs_bytes": 1048576,
            "child_as_bytes": 67108864,
            "child_cpu_soft_seconds": 1,
            "child_cpu_hard_seconds": 2,
            "child_fds": 32,
            "child_processes": 16,
            "child_file_bytes": 65536,
            "deadline_ms": 3000,
        }
        directory = os.environ.get("FOC_GOVERNANCE_PROBE_EVIDENCE")
        require(directory is not None, "probe_evidence_required")
        path = Path(directory) / (name + ".json")
        with path.open("x") as stream:
            json.dump(receipt, stream, sort_keys=True)
        path.chmod(0o600)
        return receipt

    finally:
        subprocess.run(["docker", "rm", "--force", cid], timeout=10, check=True, capture_output=True)
