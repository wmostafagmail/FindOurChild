import os
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest


@pytest.fixture
def lab():
    assert os.environ["FOC_LAB_HOST"] == "labdb" and os.environ["FOC_LAB_DATABASE"] == "foc_qualification"
    assert not any(
        k in os.environ
        for k in ["FOC_DATABASE_URL", "FOC_DATABASE_ADMIN_URL", "FOC_SESSION_KEY", "FOC_S3_API_SECRET"]
    )

    def conn(user, secret):
        return psycopg.connect(
            host="labdb",
            dbname="foc_qualification",
            user=user,
            password=Path("/run/secrets/" + secret).read_text(),
            autocommit=True,
        )

    with conn("postgres", "lab_admin") as a, conn("foc_qualification", "lab_runtime") as r:
        assert a.execute("SELECT current_database()").fetchone()[0] == "foc_qualification"
        org, other, person, outsider, p, d, g, e = [uuid4() for _ in range(8)]
        a.execute(
            "INSERT INTO qualification.protocols VALUES(%s,%s,repeat('a',64),'synthetic',now()+interval '1 hour',NULL)",
            (p, org),
        )
        a.execute(
            "INSERT INTO qualification.datasets VALUES(%s,%s,%s,repeat('a',64),repeat('b',64),'synthetic','procedural-geometric-fixtures',now()+interval '1 hour',NULL)",
            (d, org, p),
        )
        a.execute(
            "INSERT INTO qualification.grants VALUES(%s,%s,%s,repeat('a',64),%s,'synthetic-qualification',now()+interval '1 hour',NULL)",
            (g, org, d, person),
        )
        a.execute(
            "INSERT INTO qualification.evaluations VALUES(%s,%s,%s,repeat('a',64),repeat('c',64),true,false)",
            (e, org, d),
        )
        yield {
            "admin": a,
            "runtime": r,
            "org": org,
            "other": other,
            "person": person,
            "outsider": outsider,
            "protocol": p,
            "dataset": d,
            "grant": g,
        }
        r.close()
        a.execute("DELETE FROM qualification.protocols WHERE id=%s", (p,))


def context(lab, org=None, person=None, purpose="synthetic-qualification"):
    r = lab["runtime"]
    for key, value in [
        ("organization", org or lab["org"]),
        ("principal", person or lab["person"]),
        ("purpose", purpose),
    ]:
        r.execute("SELECT set_config(%s,%s,false)", ("foc.lab_" + key, str(value)))
    return r


def test_separate_cluster_has_no_operational_schema_roles_or_credentials(lab):
    a, r = lab["admin"], lab["runtime"]
    assert a.execute("SELECT to_regnamespace('app'),to_regnamespace('platform')").fetchone() == (None, None)
    assert not a.execute("SELECT 1 FROM pg_database WHERE datname='foc_synthetic'").fetchall()
    assert not a.execute("SELECT 1 FROM pg_roles WHERE rolname IN ('foc_api','foc_worker')").fetchall()
    assert r.execute(
        "SELECT rolsuper,rolbypassrls,rolcreatedb,rolcreaterole FROM pg_roles WHERE rolname=current_user"
    ).fetchone() == (False, False, False, False)
    assert r.execute("SHOW default_transaction_isolation").fetchone()[0] == "read committed"
    assert (
        a.execute(
            "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='qualification' AND c.relkind='r' AND c.relrowsecurity AND c.relforcerowsecurity"
        ).fetchone()[0]
        == 4
    )


def test_authorized_synthetic_metadata_is_visible(lab):
    r = context(lab)
    assert r.execute("SELECT count(*) FROM qualification.datasets").fetchone()[0] == 1
    assert r.execute("SELECT count(*) FROM qualification.evaluations").fetchone()[0] == 1


@pytest.mark.parametrize("change", ["absent", "organization", "principal", "purpose"])
def test_context_and_cross_tenant_denials(lab, change):
    r = (
        lab["runtime"]
        if change == "absent"
        else context(
            lab,
            org=lab["other"] if change == "organization" else None,
            person=lab["outsider"] if change == "principal" else None,
            purpose="case-management" if change == "purpose" else "synthetic-qualification",
        )
    )
    for table in ["datasets", "evaluations", "grants"]:
        assert r.execute("SELECT count(*) FROM qualification." + table).fetchone()[0] == 0


@pytest.mark.parametrize(
    "table,field",
    [
        ("grants", "revoked_at"),
        ("grants", "expires_at"),
        ("datasets", "revoked_at"),
        ("datasets", "expires_at"),
        ("protocols", "revoked_at"),
        ("protocols", "expires_at"),
    ],
)
def test_expiration_and_revocation_deny_next_statement(lab, table, field):
    r = context(lab)
    assert r.execute("SELECT count(*) FROM qualification.evaluations").fetchone()[0] == 1
    lab["admin"].execute(
        "UPDATE qualification." + table + " SET " + field + "=statement_timestamp()-interval '1 second'"
    )
    assert r.execute("SELECT count(*) FROM qualification.datasets").fetchone()[0] == 0
    assert r.execute("SELECT count(*) FROM qualification.evaluations").fetchone()[0] == 0


@pytest.mark.parametrize(
    "command",
    [
        "SET ROLE postgres",
        "CREATE SCHEMA unauthorized",
        "SELECT * FROM pg_authid",
        "INSERT INTO qualification.datasets DEFAULT VALUES",
        "UPDATE qualification.grants SET revoked_at=NULL",
        "DELETE FROM qualification.protocols",
    ],
)
def test_runtime_cannot_escalate_or_undo_revocation(lab, command):
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        lab["runtime"].execute(command)


@pytest.mark.parametrize("change", ["real", "cross-org", "protocol-swap"])
def test_owner_cannot_insert_real_class_or_cross_bound_metadata(lab, change):
    org = lab["other"] if change == "cross-org" else lab["org"]
    h = "d" if change == "protocol-swap" else "a"
    kind = "child-photographs" if change == "real" else "synthetic"
    with pytest.raises((psycopg.errors.CheckViolation, psycopg.errors.ForeignKeyViolation)):
        lab["admin"].execute(
            "INSERT INTO qualification.datasets VALUES(%s,%s,%s,%s,repeat('b',64),%s,'procedural-geometric-fixtures',now()+interval '1 hour',NULL)",
            (uuid4(), org, lab["protocol"], h * 64, kind),
        )


def test_no_accuracy_claim_and_no_stale_result_after_deletion(lab):
    with pytest.raises(psycopg.errors.CheckViolation):
        lab["admin"].execute("UPDATE qualification.evaluations SET recognition_accuracy_claim=true")
    r = context(lab)
    lab["admin"].execute("DELETE FROM qualification.datasets WHERE id=%s", (lab["dataset"],))
    assert r.execute("SELECT count(*) FROM qualification.evaluations").fetchone()[0] == 0
    assert r.execute("SELECT count(*) FROM qualification.grants").fetchone()[0] == 0
