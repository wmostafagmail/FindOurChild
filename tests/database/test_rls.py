import psycopg
import pytest

from tests.conftest import context

pytestmark = pytest.mark.database


def case_ids(conn):
    return [r[0] for r in conn.execute("SELECT id FROM app.cases").fetchall()]


def test_fnd_no_context_denied(db):
    assert case_ids(db["runtime"]) == []


def test_fnd_authorized_case_only(db):
    conn = context(db)
    assert case_ids(conn) == [db["case_a"]]


def test_fnd_cross_tenant_denied(db):
    conn = context(db, org=db["org_b"])
    assert case_ids(conn) == []


def test_fnd_org_admin_without_case_grant_denied(db):
    conn = context(db, org=db["org_b"], principal=db["principal_b"])
    assert case_ids(conn) == []


@pytest.mark.parametrize(
    "mutation",
    [
        "UPDATE app.case_grants SET revoked_at=now() WHERE organization_id=%s",
        "UPDATE app.case_grants SET expires_at=now()-interval '1 second' WHERE organization_id=%s",
        "UPDATE app.memberships SET revoked_at=now() WHERE organization_id=%s",
        "UPDATE app.memberships SET expires_at=now()-interval '1 second' WHERE organization_id=%s",
        "UPDATE app.organizations SET suspended_at=now() WHERE id=%s",
        "UPDATE app.cases SET deleted_at=now() WHERE organization_id=%s",
    ],
    ids=[
        "revoked-grant",
        "expired-grant",
        "revoked-member",
        "expired-member",
        "suspended-org",
        "deleted-case",
    ],
)
def test_fnd_revocation_and_expiry(db, mutation):
    conn = context(db)
    assert case_ids(conn) == [db["case_a"]]
    # End read transaction before rechecking current authorization in a new transaction.
    conn.rollback()
    db["admin"].execute(mutation, (db["org_a"],))
    conn = context(db)
    assert case_ids(conn) == []


def test_fnd_disabled_principal_denied(db):
    db["admin"].execute("UPDATE app.staff_principals SET disabled_at=now() WHERE id=%s", (db["principal_a"],))
    assert case_ids(context(db)) == []


def test_fnd_wrong_purpose_denied(db):
    assert case_ids(context(db, purpose="biometric_search")) == []


def test_fnd_context_does_not_survive_pool_reuse(db):
    conn = context(db)
    assert case_ids(conn) == [db["case_a"]]
    conn.commit()
    assert case_ids(conn) == []


@pytest.mark.parametrize(
    "table",
    [
        "restricted_custody",
        "photographs",
        "objects",
        "embeddings",
        "broker_candidate_edges",
        "approvals",
        "handovers",
        "memberships",
        "case_grants",
        "audit_events",
        "idempotency_records",
    ],
)
def test_fnd_sensitive_boundaries_deny_runtime(db, table):
    conn = context(db)
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        conn.execute("SELECT * FROM app." + table)
    conn.rollback()


def test_fnd_runtime_cannot_write_or_elevate(db):
    conn = context(db)
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        conn.execute("UPDATE app.cases SET lifecycle='active'")
    conn.rollback()
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        conn.execute("SET ROLE foc_policy")
    conn.rollback()


def test_fnd_all_domain_relations_force_rls(db):
    rows = (
        db["admin"]
        .execute(
            "SELECT c.relname,c.relrowsecurity,c.relforcerowsecurity,r.rolname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_roles r ON r.oid=c.relowner WHERE n.nspname='app' AND c.relkind IN ('r','p')"
        )
        .fetchall()
    )
    assert len(rows) == 41
    assert all(enabled and forced and owner == "foc_owner" for _, enabled, forced, owner in rows)


def test_fnd_non_owner_runtime_role(db):
    assert db["runtime"].execute(
        "SELECT rolsuper,rolbypassrls,rolcreaterole,rolcreatedb FROM pg_roles WHERE rolname=current_user"
    ).fetchone() == (False, False, False, False)


def test_fnd_composite_foreign_key_rejects_tenant_mix(db):
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        db["admin"].execute(
            "INSERT INTO app.registry_events(organization_id,case_id,precision,original_timezone) VALUES(%s,%s,'unknown','Africa/Cairo')",
            (db["org_a"], db["case_b"]),
        )


def test_fnd_invalid_age_interval_rejected(db):
    with pytest.raises(psycopg.errors.CheckViolation):
        db["admin"].execute(
            "INSERT INTO app.child_profiles(organization_id,case_id,birth_knowledge,age_min_months,age_max_months) VALUES(%s,%s,'estimated',90,20)",
            (db["org_a"], db["case_a"]),
        )


def test_fnd_runtime_cannot_insert_handover(db):
    conn = context(db)
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        conn.execute("INSERT INTO app.handovers DEFAULT VALUES")
    conn.rollback()


def test_fnd_outbox_atomic_rollback(db):
    admin = db["admin"]
    with pytest.raises(RuntimeError), admin.transaction():
        admin.execute(
            "UPDATE app.cases SET revision=revision+1 WHERE organization_id=%s AND id=%s",
            (db["org_a"], db["case_a"]),
        )
        admin.execute(
            "INSERT INTO app.outbox_events(organization_id,case_id,type,schema_version,aggregate_id,aggregate_revision,dedup_key) VALUES(%s,%s,'report.submitted',1,%s,2,gen_random_uuid())",
            (db["org_a"], db["case_a"], db["case_a"]),
        )
        raise RuntimeError("synthetic rollback")
    assert (
        admin.execute(
            "SELECT revision FROM app.cases WHERE organization_id=%s AND id=%s", (db["org_a"], db["case_a"])
        ).fetchone()[0]
        == 1
    )
    assert (
        admin.execute(
            "SELECT count(*) FROM app.outbox_events WHERE organization_id=%s", (db["org_a"],)
        ).fetchone()[0]
        == 0
    )
