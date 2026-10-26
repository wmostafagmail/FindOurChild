"""Disposable, separate synthetic qualification cluster; no case-service credentials/ports."""

import json
import os
import secrets
import shutil
import subprocess
from pathlib import Path

from scripts.fingerprint import fingerprint
from scripts.results_gate import python_gate

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts/raw/qualification-lab"
COMMAND = [
    "docker",
    "compose",
    "--project-name",
    "foc-qualification",
    "-f",
    str(ROOT / "compose.qualification.yaml"),
]


def run(args, data=None):
    result = subprocess.run(args, cwd=ROOT, input=data, capture_output=True, check=False)
    with (OUTPUT / "commands.log").open("ab") as log:
        log.write(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError("qualification command failed; inspect private lab diagnostics")
    return result.stdout


def sql(text, database="foc_qualification"):
    return run(
        COMMAND
        + ["exec", "-T", "labdb", "psql", "-XAt", "-v", "ON_ERROR_STOP=1", "-U", "postgres", "-d", database],
        text.encode(),
    )


def recovery():
    # Metadata-only sentinels: no photographs, vectors, identities or model binaries.
    seed = """
    INSERT INTO qualification.protocols VALUES('00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000002',repeat('a',64),'synthetic',now()+interval '1 hour',NULL);
    INSERT INTO qualification.datasets VALUES
    ('00000000-0000-0000-0000-000000000003','00000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000001',repeat('a',64),repeat('b',64),'synthetic','procedural-geometric-fixtures',now()+interval '1 hour',NULL),
    ('00000000-0000-0000-0000-000000000004','00000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000001',repeat('a',64),repeat('c',64),'synthetic','procedural-geometric-fixtures',now()+interval '1 hour',NULL);
    INSERT INTO qualification.grants VALUES
    ('00000000-0000-0000-0000-000000000005','00000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000003',repeat('a',64),'00000000-0000-0000-0000-000000000007','synthetic-qualification',now()+interval '1 hour',NULL),
    ('00000000-0000-0000-0000-000000000006','00000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000004',repeat('a',64),'00000000-0000-0000-0000-000000000007','synthetic-qualification',now()+interval '1 hour',now());
    """
    sql(seed)
    dump = run(
        COMMAND
        + [
            "exec",
            "-T",
            "labdb",
            "pg_dump",
            "-U",
            "postgres",
            "-d",
            "foc_qualification",
            "--no-owner",
            "--no-comments",
        ]
    )
    (OUTPUT / "metadata-backup.sql").write_bytes(dump)
    sql("CREATE DATABASE foc_qualification_restore;")
    run(
        COMMAND
        + [
            "exec",
            "-T",
            "labdb",
            "psql",
            "-X",
            "-v",
            "ON_ERROR_STOP=1",
            "-U",
            "postgres",
            "-d",
            "foc_qualification_restore",
        ],
        dump,
    )
    sql(
        "REVOKE CONNECT,TEMPORARY ON DATABASE foc_qualification_restore FROM PUBLIC; GRANT CONNECT ON DATABASE foc_qualification_restore TO foc_qualification;",
        "foc_qualification_restore",
    )
    sql(
        """
    DO $$ BEGIN
      IF (SELECT count(*) FROM qualification.datasets) <> 2 OR (SELECT count(*) FROM qualification.grants WHERE revoked_at IS NOT NULL) <> 1 THEN RAISE EXCEPTION 'metadata restore mismatch'; END IF;
      IF (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='qualification' AND c.relkind='r' AND c.relforcerowsecurity AND c.relrowsecurity) <> 4 THEN RAISE EXCEPTION 'restored RLS missing'; END IF;
    END $$;
    SET ROLE foc_qualification;
    SELECT set_config('foc.lab_organization','00000000-0000-0000-0000-000000000002',false),set_config('foc.lab_principal','00000000-0000-0000-0000-000000000007',false),set_config('foc.lab_purpose','synthetic-qualification',false);
    DO $$ BEGIN IF (SELECT count(*) FROM qualification.datasets) <> 1 THEN RAISE EXCEPTION 'restored authorization mismatch'; END IF; END $$;
    RESET ROLE;
    UPDATE qualification.grants SET revoked_at=now();
    SET ROLE foc_qualification;
    DO $$ BEGIN IF EXISTS(SELECT 1 FROM qualification.datasets) THEN RAISE EXCEPTION 'restored revocation bypass'; END IF; END $$;
    """,
        "foc_qualification_restore",
    )


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True, mode=0o700)
    before = fingerprint()
    secret_dir = ROOT / ".runtime/qualification"
    secret_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    # Never inherit application credentials into this independent Compose definition.
    for name in ["admin", "runtime"]:
        path = secret_dir / name
        path.write_text(secrets.token_hex(32))
        path.chmod(0o600)
    report_file = ROOT / "artifacts/raw/qualification-results.json"
    if report_file.exists():
        history = OUTPUT / ("previous-" + secrets.token_hex(8) + ".json")
        shutil.copyfile(report_file, history)
        report_file.unlink()
    try:
        cfg = json.loads(run(COMMAND + ["config", "--format", "json"]))
        assert cfg["name"] == "foc-qualification" and set(cfg["services"]) == {"labdb", "tester"}
        assert (
            set(cfg["networks"]) == {"qualification_only"}
            and cfg["networks"]["qualification_only"]["internal"] is True
        )
        for service in cfg["services"].values():
            assert not service.get("ports") and set(service["networks"]) == {"qualification_only"}
        tester = cfg["services"]["tester"]
        assert (
            set(cfg["volumes"]) == {"qualification_db"}
            and cfg["volumes"]["qualification_db"]["name"] == "foc-qualification_qualification_db"
            and not cfg["volumes"]["qualification_db"].get("external")
        )
        for name in ["admin", "runtime"]:
            assert Path(cfg["secrets"]["lab_" + name]["file"]).resolve() == (secret_dir / name).resolve()
        assert set(tester["environment"]) == {"FOC_LAB_HOST", "FOC_LAB_DATABASE", "COVERAGE_FILE"}
        assert {x["source"] for x in tester["secrets"]} == {"lab_admin", "lab_runtime"}
        assert tester["read_only"] is True and tester["cap_drop"] == ["ALL"]
        for volume in tester["volumes"]:
            source = Path(volume["source"]).resolve()
            assert source != ROOT and not source.is_relative_to(ROOT / ".runtime")
            if not volume.get("read_only", False):
                assert source == OUTPUT.resolve()
        # Recover reproducibly from an interrupted previous synthetic lab run.
        run(COMMAND + ["down", "--volumes", "--remove-orphans"])
        run(COMMAND + ["up", "-d", "--wait", "labdb"])
        network = json.loads(run(["docker", "network", "inspect", "foc-qualification_qualification_only"]))[0]
        assert network["Internal"] is True
        password = (secret_dir / "runtime").read_text()
        assert len(password) == 64 and all(c in "0123456789abcdef" for c in password)
        sql("ALTER ROLE foc_qualification PASSWORD '" + password + "';")
        run(COMMAND + ["run", "--rm", "--user", f"{os.getuid()}:{os.getgid()}", "tester"])
        report = json.loads((OUTPUT / "results.json").read_text())
        report["source_digest"] = before
        expected = json.loads((ROOT / "docs/phase2b/required-tests.json").read_text())["qualification"]
        python_gate(report, {"python": expected}, before)
        recovery()
        assert fingerprint() == before
        report["lab_isolation"] = {
            "separate_database": True,
            "network_internal": True,
            "published_ports": 0,
            "operational_credentials_mounted": False,
            "forced_rls_tables": 4,
            "metadata_backup_restore": "passed",
            "restored_revocation": "passed",
            "real_data_authorized": False,
        }
        report_file.write_text(json.dumps(report, indent=2) + "\n")
        report_file.chmod(0o600)
        shutil.copyfile(OUTPUT / ".coverage.qualification", ROOT / "artifacts/raw/.coverage.qualification")
        print(
            f"qualification: {len(expected)} required tests passed; isolated database, restored RLS and revocation verified"
        )
    finally:
        # Only this new disposable project is stopped/deleted; application volumes are untouched.
        run(COMMAND + ["down", "--volumes", "--remove-orphans"])
        for name in ["admin", "runtime"]:
            (secret_dir / name).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
