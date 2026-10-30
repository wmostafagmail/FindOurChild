"""Exact-source, zero-skip governance runner; no human authority or assets."""

import hashlib
import io
import json
import os
import platform
import secrets
import shutil
import subprocess
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import psycopg
import pytest

from .evidence import enforce, sanitized
from .records import require

ROOT = Path(__file__).resolve().parents[3]


def source_manifest():
    paths = []
    for base in [
        "tools/phase2e/demo_governance",
        "tests/demo_governance",
        "services/demo_governance",
        "database/demo_governance",
    ]:
        paths += [p for p in (ROOT / base).rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    paths += [
        ROOT / p
        for p in [
            "config/phase2e/demo-governance.json",
            "docs/phase2e/governance-required-tests.json",
            ".github/workflows/phase2e-demo-governance.yml",
            "pyproject.toml",
            "uv.lock",
        ]
    ]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


class Results:
    def __init__(self):
        self.nodes = []
        self.stages = {}
        self.diagnostics = []

    def pytest_collection_modifyitems(self, items):
        self.nodes = [i.nodeid for i in items]

    def pytest_runtest_logreport(self, report):
        self.stages.setdefault(report.nodeid, {})[report.when] = report.outcome
        if report.failed:
            import re

            match = re.search(r"(?:Denied|IntegrityError): ([a-z_]{1,64})", report.longreprtext)
            types = re.findall(
                r"E\s+(?:[a-zA-Z_.]+\.)?([A-Z][A-Za-z]+(?:Error|Exception)):", report.longreprtext
            )
            self.diagnostics.append(
                {
                    "id": report.nodeid,
                    "stage": report.when,
                    "fixed_code": match[1] if match else None,
                    "error_type": types[-1] if types else "AssertionError",
                    "private_diagnostic_sha256": hashlib.sha256(report.longreprtext.encode()).hexdigest(),
                }
            )


def command(args, **kwargs):
    return subprocess.check_output(args, timeout=kwargs.pop("timeout", 60), **kwargs)


def prepare(work):
    require(platform.system() == "Linux" and platform.machine() == "x86_64", "linux_x86_required")
    native = work / "native"
    native.mkdir()
    for name in ["supervisor.cpp", "synthetic_probe.cpp", "Dockerfile"]:
        shutil.copyfile(ROOT / "services/demo_governance" / name, native / name)
    tag = "foc-governance-synthetic:" + secrets.token_hex(8)
    command(["docker", "build", "--network", "none", "--tag", tag, str(native)], timeout=600)
    image = command(["docker", "image", "inspect", "--format", "{{.Id}}", tag]).decode().strip()
    cid = command(["docker", "create", image, "ok"]).decode().strip()
    try:
        for path, name in [("/opt/foc-demo/bin", "container-binaries"), ("/evidence", "container-build")]:
            command(["docker", "cp", cid + ":" + path, str(native / name)])
    finally:
        command(["docker", "rm", cid])
    rooted = Path("/var/lib/foc-governance-synthetic") / secrets.token_hex(8)
    # Disposable, root-owned benign files exercise the actual deployed path
    # boundary; no relaxed-owner shortcut is accepted as a positive test.
    command(
        [
            "sudo",
            sys.executable,
            "-c",
            """import os,sys
from pathlib import Path
p=Path(sys.argv[1]);p.mkdir(parents=True,mode=0o755)
for name in ['cnn_detector','five_point_predictor','resnet_128_encoder']:
 f=p/name;f.write_bytes(b'benign-interface-buffer');f.chmod(0o444)
(p/'symlink').symlink_to(p/'cnn_detector')
os.link(p/'five_point_predictor',p/'hardlink')
os.mkfifo(p/'fifo')
(p/'writable').write_bytes(b'x')
(p/'directory').mkdir()
""",
            str(rooted),
        ]
    )
    os.environ["FOC_GOVERNANCE_ROOTED_FIXTURE"] = str(rooted)
    password = secrets.token_hex(24)
    env = os.environ.copy()
    env["POSTGRES_PASSWORD"] = password
    pg = (
        command(
            [
                "docker",
                "run",
                "-d",
                "--label",
                "foc.scope=demo-governance-synthetic",
                "-e",
                "POSTGRES_PASSWORD",
                "-e",
                "POSTGRES_DB=foc_demo_gov",
                "-p",
                "127.0.0.1::5432",
                "--memory",
                "256m",
                "--pids-limit",
                "128",
                "pgvector/pgvector:0.8.7-pg17-bookworm@sha256:ac08538c6f8b9904c33c8224c5e5706dbe760aca29db1d096972b4052c22a75d",
            ],
            env=env,
        )
        .decode()
        .strip()
    )
    try:
        port = json.loads(command(["docker", "inspect", pg]))[0]["NetworkSettings"]["Ports"]["5432/tcp"][0][
            "HostPort"
        ]
        url = f"postgresql://postgres:{password}@127.0.0.1:{port}/foc_demo_gov"
        until = time.monotonic() + 60
        while True:
            try:
                with psycopg.connect(url, autocommit=True, connect_timeout=2) as c:
                    c.execute((ROOT / "database/demo_governance/0001_control_plane.sql").read_text())
                    c.execute(
                        "CREATE TABLE demo_governance.engineering_marker(synthetic_only boolean NOT NULL CHECK(synthetic_only))"
                    )
                    c.execute("INSERT INTO demo_governance.engineering_marker VALUES(true)")
                break
            except psycopg.OperationalError:
                require(time.monotonic() < until, "postgres_start")
                time.sleep(0.2)
        os.environ["FOC_GOVERNANCE_PROBE_IMAGE"] = image
        os.environ["FOC_GOVERNANCE_DATABASE_URL"] = url
        return pg, url, image
    except BaseException:
        command(["docker", "rm", "--force", pg])
        raise


def recovery(pg):
    dump = command(["docker", "exec", pg, "pg_dump", "-U", "postgres", "-d", "foc_demo_gov", "--no-owner"])
    command(["docker", "exec", pg, "createdb", "-U", "postgres", "foc_demo_gov_restore"])
    subprocess.run(
        [
            "docker",
            "exec",
            "-i",
            pg,
            "psql",
            "-U",
            "postgres",
            "-d",
            "foc_demo_gov_restore",
            "-v",
            "ON_ERROR_STOP=1",
        ],
        input=dump,
        capture_output=True,
        check=True,
        timeout=30,
    )
    receipt = command(
        [
            "docker",
            "exec",
            pg,
            "psql",
            "-XAt",
            "-U",
            "postgres",
            "-d",
            "foc_demo_gov_restore",
            "-v",
            "ON_ERROR_STOP=1",
            "-c",
            "UPDATE demo_governance.authority SET enabled=false; SELECT count(*) FROM demo_governance.authority WHERE enabled; SELECT relrowsecurity AND relforcerowsecurity FROM pg_class WHERE oid='demo_governance.jobs'::regclass;",
        ]
    )
    require(receipt.decode().splitlines()[-2:] == ["0", "t"], "restore_inactive_rls")
    return {"backup_sha256": hashlib.sha256(dump).hexdigest(), "restore_inactive": True, "forced_rls": True}


def main():
    required = json.loads((ROOT / "docs/phase2e/governance-required-tests.json").read_text())["selectors"]
    before = source_manifest()
    source = hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest()
    work = ROOT / "artifacts/raw/governance" / str(time.time_ns())
    work.mkdir(parents=True, mode=0o700)
    output = ROOT / "artifacts/phase2e-governance"
    output.mkdir(parents=True, exist_ok=True)
    result = Results()
    capture = io.StringIO()
    pg = None
    try:
        probe_output = work / "probe-receipts"
        probe_output.mkdir(mode=0o700)
        os.environ["FOC_GOVERNANCE_PROBE_EVIDENCE"] = str(probe_output)
        pg, _, image = prepare(work)
        with redirect_stdout(capture), redirect_stderr(capture):
            code = pytest.main(
                ["--confcutdir=tests/demo_governance", "tests/demo_governance", "-q", "--tb=short"],
                plugins=[result],
            )
        report = {"source": source, "exit": int(code), "tests": result.stages}
        (work / "pytest.log").write_text(capture.getvalue())
        (work / "pytest.log").chmod(0o600)
        (output / "results.json").write_text(json.dumps(sanitized(report, required), indent=2) + "\n")
        require(result.nodes == required, "exact_collection")
        require(before == source_manifest(), "source_changed")
        enforce(report, required, source)
        restored = recovery(pg)
        receipts = list(probe_output.glob("*.json"))
        require(len(receipts) == 14, "exact_probe_receipts")
        shutil.copytree(probe_output, output / "probe-receipts")
        binaries = {
            str(p.relative_to(work)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((work / "native").rglob("*"))
            if p.is_file()
        }
        # All inputs/results are data-free sources and benign binaries. Never
        # copy private database files, permits, authority keys or raw logs.
        shutil.copytree(work / "native", output / "source-only-build")
        manifest = {
            "checkout": os.environ.get("GITHUB_SHA"),
            "event": os.environ.get("GITHUB_EVENT_NAME"),
            "source_manifest": before,
            "source": source,
            "tests": len(required),
            "probe_receipts": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in receipts},
            "negative_ids": 64,
            "image": image,
            "build_outputs": binaries,
            "recovery": restored,
            "actual_keys": 0,
            "actual_permits": 0,
            "assets_acquired": 0,
            "neural_inference": False,
            "independent_human_review": "unmet_demo_waiver",
            "phase2e_complete": False,
        }
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(json.dumps({"governance_tests": len(required), "mandatory_skips": 0, "inference": False}))
    except BaseException as error:
        failure = {
            "checkout": os.environ.get("GITHUB_SHA"),
            "source": source,
            "error_class": type(error).__name__,
            "diagnostics": result.diagnostics,
            "tests": result.stages,
            "scope": "source_only_failed_no_assets_no_inference",
        }
        (output / "failure.json").write_text(json.dumps(failure, indent=2) + "\n")
        print(
            json.dumps(
                {
                    "failed_selectors": [
                        n
                        for n in result.nodes
                        if result.stages.get(n) != {"setup": "passed", "call": "passed", "teardown": "passed"}
                    ],
                    "error_class": type(error).__name__,
                }
            )
        )
        raise
    finally:
        (work / "pytest.log").write_text(capture.getvalue())
        (work / "pytest.log").chmod(0o600)
        rooted = os.environ.get("FOC_GOVERNANCE_ROOTED_FIXTURE")
        if rooted:
            command(
                [
                    "sudo",
                    sys.executable,
                    "-c",
                    "import shutil,sys; from pathlib import Path; p=Path(sys.argv[1]); assert p.parent == Path('/var/lib/foc-governance-synthetic'); shutil.rmtree(p)",
                    rooted,
                ]
            )
        if pg:
            command(["docker", "rm", "--force", pg])


if __name__ == "__main__":
    main()
