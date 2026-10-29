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
    sentinel = str(uuid4())
    seeded = False
    try:
        if (
            query("foc_synthetic", "SELECT data_class||':'||schema_version FROM platform.environment")
            != "synthetic:0001"
        ):
            raise RuntimeError("Untrusted source")
        # Private synthetic sentinel proves nonempty pgvector and per-photo metadata restoration.
        content_hash = hashlib.sha256((ROOT / "tests/fixtures/synthetic-green.png").read_bytes()).hexdigest()
        vector = "[1," + ",".join(["0"] * 127) + "]"
        space_sql = query(
            "foc_synthetic",
            "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='platform.research_vectors_synthetic_v1'::regclass AND contype='c' AND pg_get_constraintdef(oid) LIKE '%space_id%'",
        )
        import re

        spaces = re.findall(r"[a-f0-9]{64}", space_sql)
        if len(spaces) != 1:
            raise RuntimeError("Research space manifest missing")
        query(
            "foc_synthetic",
            f"BEGIN; INSERT INTO platform.research_datasets VALUES('{sentinel}','{sentinel}',true,'synthetic-2a-v1',now()+interval '1 hour',1,NULL); INSERT INTO platform.research_photographs(organization_id,dataset_id,generation,id,case_ref,subject_ref,family_ref,image_sha256,registry,partition,role,capture_precision,source,synthetic) VALUES('{sentinel}','{sentinel}',1,'{sentinel}','{sentinel}','{sentinel}','{sentinel}','{content_hash}','found','test','gallery','unknown','procedural-geometric-fixture-v1',true); INSERT INTO platform.research_vectors_synthetic_v1 VALUES('{sentinel}','{sentinel}','{sentinel}','{spaces[0]}','{vector}'::public.vector,1,now()); COMMIT;",
        )
        seeded = True
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
            "tables": 46,
            "forced_rls": 46,
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
        restored_vector = query(
            name,
            f"SELECT vector::text FROM platform.research_vectors_synthetic_v1 WHERE organization_id='{sentinel}' AND photo_id='{sentinel}'",
        )
        metadata = query(
            name,
            f"SELECT image_sha256||':'||capture_precision||':'||(capture_lower IS NULL AND capture_upper IS NULL AND age_min_months IS NULL AND age_max_months IS NULL)::text FROM platform.research_photographs WHERE organization_id='{sentinel}' AND id='{sentinel}'",
        )
        research_rls = query(
            name,
            "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='platform' AND c.relkind='r' AND c.relname LIKE 'research_%' AND c.relrowsecurity AND c.relforcerowsecurity",
        )
        denied = query(
            name,
            "SELECT NOT has_table_privilege('foc_api','platform.research_vectors_synthetic_v1','SELECT') AND NOT (SELECT rolcanlogin FROM pg_roles WHERE rolname='foc_research')",
        )
        if (
            restored_vector != vector
            or metadata != content_hash + ":unknown:true"
            or research_rls != "4"
            or denied != "t"
        ):
            raise RuntimeError("Synthetic vector/metadata/authorization restore differs")
        report["research_vector_restore"] = {
            "status": "passed",
            "vectors_verified": 1,
            "forced_research_tables": 4,
            "raw_vector_exported": False,
        }
        if (
            query(
                name,
                "SELECT relrowsecurity AND relforcerowsecurity FROM pg_class WHERE oid='platform.identity_commands'::regclass",
            )
            != "t"
        ):
            raise RuntimeError("Restored command RLS disabled")
        report["identity_session_rls"] = "passed"
        unsafe = int(
            query(
                name,
                "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='platform' AND c.relkind='r' AND c.relname NOT IN ('environment','migrations') AND NOT(c.relrowsecurity AND c.relforcerowsecurity)",
            )
        )
        if unsafe:
            raise RuntimeError("Restored private metadata RLS disabled")
        report["reporting_metadata_rls"] = "passed"
        workflow_rls = query(name, "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('platform','app') AND c.relkind='r' AND c.relname LIKE 'synthetic_%' AND c.relrowsecurity AND c.relforcerowsecurity")
        # A restored copy has no synthetic activation: independent database name + epoch gates.
        workflow_denied = query(name, "SET ROLE foc_api; SELECT count(*) FROM app.synthetic_candidate_leads;").splitlines()[-1]
        if workflow_rls != '8' or workflow_denied != '0':
            raise RuntimeError('Restored workflow isolation differs')
        report['synthetic_workflow_restore'] = {'forced_rls_tables':8,'quarantined_restore_denies_access':True,'activation_epoch_reissue_required':True,'operational_erasure':'pending'}

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
        if seeded:
            query(
                "foc_synthetic",
                f"DELETE FROM platform.research_datasets WHERE organization_id='{sentinel}' AND id='{sentinel}'",
            )
        if created:
            run(["dropdb", "-U", "postgres", name])
        output = ROOT / "artifacts/raw"
        output.mkdir(parents=True, exist_ok=True)
        (output / "recovery.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Synthetic backup restore and deny-default RLS verified; operational erasure remains pending")


if __name__ == "__main__":
    main()
