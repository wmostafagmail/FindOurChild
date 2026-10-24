"""Real PostgreSQL identity privilege and audit-chain boundaries."""

import hashlib
from datetime import UTC, datetime, timedelta

import psycopg
import pytest

from tests.conftest import context


@pytest.mark.database
def test_identity_sessions_direct_access_denied(db):
    for statement in [
        "SELECT * FROM platform.identity_sessions",
        "DELETE FROM platform.identity_sessions",
        "UPDATE platform.identity_sessions SET revoked_at=now()",
    ]:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            db["runtime"].execute(statement)
        db["runtime"].rollback()


@pytest.mark.database
def test_membership_admin_cannot_grant_sensitive_or_self_roles(db):
    conn = context(db, db["org_b"], db["principal_b"])
    expiry = datetime.now(UTC) + timedelta(hours=1)
    for target, role in [
        (db["principal_b"], "reviewer"),
        (db["principal_a"], "org_admin"),
        (db["principal_a"], "safeguarding"),
        (db["principal_a"], "authority"),
        (db["principal_a"], "privacy"),
    ]:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            conn.execute(
                "SELECT platform.membership_change(%s,%s,%s,%s,false)",
                (db["org_b"], target, role, expiry),
            )
    assert conn.execute("SELECT count(*) FROM app.cases").fetchone()[0] == 0


@pytest.mark.database
def test_identity_missing_context_and_revocation(db):
    conn = context(db)
    assert conn.execute("SELECT platform.active_member(%s,NULL)", (db["org_a"],)).fetchone()[0]
    assert not conn.execute("SELECT platform.active_member(%s,NULL)", (db["org_b"],)).fetchone()[0]
    conn.rollback()
    assert not conn.execute("SELECT platform.active_member(%s,NULL)", (db["org_a"],)).fetchone()[0]
    assert conn.execute("SELECT * FROM platform.identity_orgs()").fetchall() == []


@pytest.mark.database
def test_audit_chain_and_runtime_append_only(db):
    conn = context(db)
    for _ in range(2):
        conn.execute(
            "SELECT platform.audit_append(%s,'case.permission.allowed',%s,'allowed')",
            (db["org_a"], db["case_a"]),
        )
    conn.commit()
    rows = (
        db["admin"]
        .execute(
            "SELECT previous_hash,event_hash FROM app.audit_events WHERE organization_id=%s ORDER BY sequence",
            (db["org_a"],),
        )
        .fetchall()
    )
    assert bytes(rows[0][0]) == bytes(32)
    assert bytes(rows[1][0]) == bytes(rows[0][1])
    verified = (
        db["admin"]
        .execute(
            "SELECT bool_and(event_hash=public.digest(previous_hash||convert_to(jsonb_build_array(event_id,actor_ref,action,target_ref,purpose,outcome,occurred_at)::text,'UTF8'),'sha256')) FROM app.audit_events WHERE organization_id=%s",
            (db["org_a"],),
        )
        .fetchone()[0]
    )
    assert verified is True
    for statement in ["UPDATE app.audit_events SET outcome='denied'", "DELETE FROM app.audit_events"]:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            conn.execute(statement)
        conn.rollback()


@pytest.mark.database
def test_session_token_is_hashed_and_expiry_enforced(db):
    conn = context(db)
    token = hashlib.sha256(b"synthetic-session-only").digest()
    csrf = hashlib.sha256(b"synthetic-csrf-only").digest()
    conn.execute(
        "SELECT platform.session_create(%s,%s,%s,%s,now()+interval '1 hour')",
        (token, db["principal_a"], "synthetic-encrypted-placeholder", csrf),
    )
    conn.commit()
    assert (
        db["admin"]
        .execute(
            "SELECT expires_at<=created_at+interval '30 minutes 1 second' FROM platform.identity_sessions WHERE token_hash=%s",
            (token,),
        )
        .fetchone()[0]
    )
    assert conn.execute("SELECT * FROM platform.session_get(%s)", (bytes(32),)).fetchall() == []
    assert conn.execute("SELECT * FROM platform.session_get(%s)", (token,)).fetchone()[0] == db["principal_a"]
    conn.execute("SELECT platform.session_revoke(%s)", (token,))
    assert conn.execute("SELECT * FROM platform.session_get(%s)", (token,)).fetchall() == []


@pytest.mark.database
def test_membership_change_rolls_back_when_audit_unavailable(db):
    conn = context(db, db["org_b"], db["principal_b"])
    admin = db["admin"]
    admin.execute("REVOKE INSERT ON app.audit_events FROM foc_policy")
    try:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            conn.execute(
                "SELECT platform.membership_change(%s,%s,'reviewer',now()+interval '1 hour',false)",
                (db["org_b"], db["principal_a"]),
            )
        assert (
            admin.execute(
                "SELECT count(*) FROM app.memberships WHERE organization_id=%s AND principal_id=%s",
                (db["org_b"], db["principal_a"]),
            ).fetchone()[0]
            == 0
        )
    finally:
        conn.rollback()
        admin.execute("GRANT INSERT ON app.audit_events TO foc_policy")
