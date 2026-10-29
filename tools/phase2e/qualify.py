"""Source-only x86_64 qualification. Never acquires weights or dataset images."""

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

from tools.phase2e.source_projection import ROOT, NoRedirect, acquire

CONFIG = ROOT / "config/phase2e"
WORKER = ROOT / "services/demo_recognition"


def command(args, log, *, timeout):
    with log.open("ab") as stream:
        result = subprocess.run(args, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout, check=False)
    if result.returncode:
        raise RuntimeError(f"Qualification subprocess failed ({result.returncode}); original log retained")


def prepare(work):
    source = work / "source"
    acquire(source)
    context = work / "context"
    context.mkdir()
    shutil.copytree(source, context / "source")
    shutil.copyfile(work / "source-receipt.json", context / "source-receipt.json")
    lock = json.loads((CONFIG / "build-dependencies.json").read_text())
    assert lock["platform"] == "linux/amd64" and lock["python"] == "3.13.13"
    wheels = context / "wheels"
    wheels.mkdir()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    for package in lock["packages"]:
        url = package["url"]
        # Exact committed paths only. No redirects, indexes, package resolution or sdists.
        assert url.startswith("https://files.pythonhosted.org/packages/")
        assert url.endswith("/" + package["filename"]) and Path(package["filename"]).name == package["filename"]
        assert 0 < package["size"] < 32_000_000
        with opener.open(url, timeout=30) as response:
            assert response.status == 200 and response.geturl() == url
            data = response.read(package["size"] + 1)
        assert len(data) == package["size"] and hashlib.sha256(data).hexdigest() == package["sha256"]
        (wheels / package["filename"]).write_bytes(data)
    shutil.copyfile(CONFIG / "build-dependencies.json", context / "dependency-lock.json")
    for filename in ["Dockerfile.preflight", "requirements-build.txt", "preflight.py"]:
        shutil.copyfile(WORKER / filename, context / filename)
    shutil.copyfile(ROOT / "tools/phase2e/build_manifest.py", context / "build_manifest.py")
    return context


def qualify(work):
    # Container uname under emulation is not proof of native host compatibility.
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise RuntimeError("Native Linux x86_64 host required; ARM/emulation is not qualification")
    if work.exists() or any(p.is_symlink() for p in [work, *work.parents]):
        raise RuntimeError("Fresh non-symlink work directory required")
    work.mkdir(parents=True, mode=0o700)
    raw = work / "raw"
    raw.mkdir(mode=0o700)
    output = work / "sanitized"
    output.mkdir()
    context = prepare(work)
    identity = hashlib.sha256((CONFIG / "source-projection.json").read_bytes()).hexdigest()[:16]
    image = "foc-phase2e-preflight:" + identity
    command(["docker", "build", "--platform", "linux/amd64", "--network", "none", "--no-cache",
             "--file", str(context / "Dockerfile.preflight"), "--tag", image, str(context)],
            raw / "build.log", timeout=2700)
    image_info, = json.loads(subprocess.check_output(["docker", "image", "inspect", image]))
    assert image_info["Architecture"] == "amd64" and image_info["Config"]["User"] == "10001:10001"
    container = "foc-qualification-" + identity
    try:
        command(["docker", "create", "--name", container, "--network", "none", "--read-only",
                 "--user", "10001:10001", "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true",
                 "--cpus", "2", "--memory", "1g", "--memory-swap", "1g", "--pids-limit", "64",
                 "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=64m,mode=1777", image], raw / "create.log", timeout=30)
        inspect, = json.loads(subprocess.check_output(["docker", "inspect", container]))
        restrictions = inspect["HostConfig"]
        assert restrictions["NetworkMode"] == "none" and restrictions["ReadonlyRootfs"] is True
        assert restrictions["CapDrop"] == ["ALL"] and restrictions["Memory"] == 1073741824
        assert restrictions["NanoCpus"] == 2000000000 and restrictions["PidsLimit"] == 64
        assert "no-new-privileges:true" in restrictions["SecurityOpt"]
        assert not inspect["Mounts"] and not restrictions.get("Devices") and not restrictions["Privileged"]
        command(["docker", "start", "--attach", container], raw / "native.log", timeout=60)
        finished, = json.loads(subprocess.check_output(["docker", "inspect", container]))
        assert finished["State"]["ExitCode"] == 0 and not finished["State"]["OOMKilled"]
        native = json.loads((raw / "native.log").read_text())
        assert native["native_transform_executed"] and native["inference_executed"] is False
        command(["docker", "cp", container + ":/opt/qualification/evidence/.", str(output)],
                raw / "copy.log", timeout=30)
        report = {"version": 1, "scope": "data_free_source_only_preflight",
                  "head_sha": os.environ.get("GITHUB_SHA"), "host_architecture": platform.machine(),
                  "image_id": image_info["Id"], "native": native,
                  "resource_limits": {"cpus": 2, "memory_bytes": 1073741824, "pids": 64, "timeout_seconds": 60},
                  "model_acquisition_authorized": False, "image_acquisition_authorized": False,
                  "independent_manifest_review": "pending", "E0_complete": False}
        (output / "source-only-result.json").write_text(json.dumps(report, indent=2) + "\n")
        checksums = {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sorted(output.rglob("*")) if p.is_file()}
        (output / "checksums.json").write_text(json.dumps(checksums, indent=2) + "\n")
        print(json.dumps({"source_only_preflight": "passed", "model_inference": "not_executed",
                          "independent_review": "pending", "E0_complete": False}))
    finally:
        subprocess.run(["docker", "rm", "--force", container], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work", type=Path)
    args = parser.parse_args()
    try:
        qualify(args.work.absolute())
    except (AssertionError, OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        # No environment, URLs, media, descriptors, receipts or secrets in summary.
        print(json.dumps({"source_only_preflight": "failed", "error_type": type(error).__name__,
                          "E0_complete": False}), file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
