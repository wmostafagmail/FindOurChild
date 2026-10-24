"""Synthetic schema/data backup and restore drill. Never an operational erasure certification."""

import hashlib
import json
import subprocess
from pathlib import Path
from uuid import uuid4

from scripts.fingerprint import fingerprint

ROOT = Path(__file__).resolve().parents[1]
CONTAINER = "foc-phase1a-db-1"


def run(args, data=None):
    result = subprocess.run(
        ["docker", "exec", "-i", CONTAINER, *args], check=False, input=data, capture_output=True
    )
    if result.returncode:
        raise RuntimeError("Recovery subprocess failed; inspect private service logs")
    return result.stdout


def query(database, sql):
    return (
        run(["psql", "-X", "-U", "postgres", "-d", database, "-v", "ON_ERROR_STOP=1", "-tA", "-c", sql])
        .decode()
        .strip()
    )


def main():
    report = {
        "status": "failed",
        "scope": "synthetic foundation backup and restored schema/RLS only",
        "erasure_and_tombstone_replay": "pending",
    }
    name = "foc_restore_" + uuid4().hex
    created = False
    try:
        if (
            query("foc_synthetic", "SELECT data_class||':'||schema_version FROM platform.environment")
            != "synthetic:0001"
        ):
            raise RuntimeError("Untrusted source")
        dump = run(["pg_dump", "-U", "postgres", "-d", "foc_synthetic", "--format=custom"])
        run(["createdb", "-U", "postgres", name])
        created = True
        run(["pg_restore", "-U", "postgres", "-d", name, "--exit-on-error"], dump)
        evidence = json.loads(
            query(
                name,
                "SELECT json_build_object('tables',(SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='app' AND c.relkind IN ('r','p')),'forced_rls',(SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='app' AND c.relkind IN ('r','p') AND c.relrowsecurity AND c.relforcerowsecurity),'schema',(SELECT schema_version FROM platform.environment),'vector',(SELECT extversion FROM pg_extension WHERE extname='vector'),'migration_sha',(SELECT sha256 FROM platform.migrations WHERE version='0001_foundation'))",
            )
        )
        expected = hashlib.sha256((ROOT / "database/migrations/0001_foundation.sql").read_bytes()).hexdigest()
        if evidence != {
            "tables": 41,
            "forced_rls": 41,
            "schema": "0001",
            "vector": "0.8.7",
            "migration_sha": expected,
        }:
            raise RuntimeError("Restored schema differs")
        if query(name, "SET ROLE foc_api; SELECT count(*) FROM app.cases;").splitlines()[-1] != "0":
            raise RuntimeError("Restored RLS denied-default check failed")
        hardening = query(
            name, "SELECT sha256 FROM platform.migrations WHERE version='0002_contract_hardening'"
        )
        if (
            hardening
            != hashlib.sha256(
                (ROOT / "database/migrations/0002_contract_hardening.sql").read_bytes()
            ).hexdigest()
        ):
            raise RuntimeError("Hardening migration not restored")
        restored_migrations = json.loads(
            query(name, "SELECT json_object_agg(version,sha256) FROM platform.migrations")
        )
        expected_migrations = {
            p.stem: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (ROOT / "database/migrations").glob("*.sql")
        }
        if restored_migrations != expected_migrations:
            raise RuntimeError("Restored migrations differ")
        if (
            query(
                name,
                "SELECT relrowsecurity AND relforcerowsecurity FROM pg_class WHERE oid='platform.identity_sessions'::regclass",
            )
            != "t"
        ):
            raise RuntimeError("Restored session RLS disabled")
        report["all_migrations"] = restored_migrations
        if (
            query(
                name,
                "SELECT relrowsecurity AND relforcerowsecurity FROM pg_class WHERE oid='platform.identity_commands'::regclass",
            )
            != "t"
        ):
            raise RuntimeError("Restored command RLS disabled")
        report["identity_session_rls"] = "passed"
        report["hardening_sha256"] = hardening
        output = ROOT / "artifacts/raw"
        output.mkdir(parents=True, exist_ok=True)
        (output / "synthetic-backup.dump").write_bytes(dump)
        report.update(
            status="passed",
            database=evidence,
            backup_sha256=hashlib.sha256(dump).hexdigest(),
            source_digest=fingerprint(),
        )
    finally:
        if created:
            run(["dropdb", "-U", "postgres", name])
        output = ROOT / "artifacts/raw"
        output.mkdir(parents=True, exist_ok=True)
        (output / "recovery.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Synthetic backup restore and deny-default RLS verified; operational erasure remains pending")


if __name__ == "__main__":
    main()
