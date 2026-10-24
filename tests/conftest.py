import os
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from foc_api.config import Settings
from foc_api.main import create_app

from scripts.preflight import verify

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def client():
    with TestClient(create_app(Settings.load())) as value:
        yield value


@pytest.fixture
def db():
    verify()
    with psycopg.connect(os.environ["FOC_DATABASE_ADMIN_URL"], autocommit=True) as admin:
        # Guard was checked above against the private instance marker. Never run against an arbitrary URL.
        assert admin.execute("SELECT current_database()").fetchone()[0] == "foc_synthetic"
        a, b, p, q, c, d, e = [uuid4() for _ in range(7)]
        admin.execute(
            "INSERT INTO app.organizations(id,country_code,approved_status,policy_version) VALUES(%s,'EG','approved','synthetic-v1'),(%s,'EG','approved','synthetic-v1')",
            (a, b),
        )
        admin.execute(
            "INSERT INTO app.staff_principals(id,oidc_issuer,oidc_subject) VALUES(%s,'https://synthetic.invalid',%s),(%s,'https://synthetic.invalid',%s)",
            (p, str(p), q, str(q)),
        )
        admin.execute(
            "INSERT INTO app.memberships(organization_id,principal_id,role,starts_at,expires_at) VALUES(%s,%s,'reviewer',now()-interval '1 day',now()+interval '1 hour'),(%s,%s,'org_admin',now()-interval '1 day',now()+interval '1 hour')",
            (a, p, b, q),
        )
        admin.execute(
            "INSERT INTO app.cases(organization_id,id,registry) VALUES(%s,%s,'missing'),(%s,%s,'found'),(%s,%s,'found')",
            (a, c, a, d, b, e),
        )
        admin.execute(
            "INSERT INTO app.case_grants(organization_id,case_id,principal_id,permission,purpose,granted_by,expires_at) VALUES(%s,%s,%s,'case.read','case_management',%s,now()+interval '1 hour')",
            (a, c, p, p),
        )
        with psycopg.connect(os.environ["FOC_DATABASE_URL"]) as runtime:
            yield {
                "admin": admin,
                "runtime": runtime,
                "org_a": a,
                "org_b": b,
                "principal_a": p,
                "principal_b": q,
                "case_a": c,
                "case_ungranted": d,
                "case_b": e,
            }
        # Roll back runtime transactions before deleting the fixture, to avoid locks.
        admin.execute("DELETE FROM app.idempotency_records WHERE organization_id IN (%s,%s)", (a, b))
        admin.execute("DELETE FROM app.outbox_events WHERE organization_id IN (%s,%s)", (a, b))
        admin.execute("DELETE FROM app.objects WHERE organization_id IN (%s,%s)", (a, b))
        admin.execute("DELETE FROM app.case_grants WHERE organization_id IN (%s,%s)", (a, b))
        admin.execute("DELETE FROM app.cases WHERE organization_id IN (%s,%s)", (a, b))
        admin.execute("DELETE FROM app.memberships WHERE organization_id IN (%s,%s)", (a, b))
        admin.execute("DELETE FROM app.organizations WHERE id IN (%s,%s)", (a, b))
        admin.execute("DELETE FROM app.staff_principals WHERE id IN (%s,%s)", (p, q))


def context(db, org=None, principal=None, purpose="case_management"):
    conn = db["runtime"]
    for k, v in [
        ("organization", org or db["org_a"]),
        ("principal", principal or db["principal_a"]),
        ("purpose", purpose),
    ]:
        conn.execute("SELECT set_config(%s,%s,true)", ("foc." + k, str(v)))
    return conn
