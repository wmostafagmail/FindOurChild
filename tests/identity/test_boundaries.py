import json
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from foc_api.identity import COOKIE, digest
from foc_api.main import create_app

from scripts.identity_setup import ADMIN_A, CASE_A, CASE_B, ORG_A, ORG_B, STAFF_A, STAFF_B
from tests.identity.helpers import real_login


@pytest.mark.integration
def test_real_keycloak_mfa_session_case_and_tenant_boundary():
    client, headers = real_login()
    try:
        me = client.get("https://127.0.0.1:3443/identity/me", headers=headers)
        assert me.status_code == 200
        assert me.json() == {"principal_id": STAFF_A, "organizations": [{"id": ORG_A, "role": "reviewer"}]}
        base = "https://127.0.0.1:3443/identity/organizations/"
        assert (
            client.get(base + ORG_A + "/cases/" + CASE_A + "/permission", headers=headers).status_code == 200
        )
        for org, case in [(ORG_B, CASE_B), (ORG_A, CASE_B), (ORG_A, str(uuid4()))]:
            response = client.get(base + org + "/cases/" + case + "/permission", headers=headers)
            assert response.status_code == 404
            assert response.json()["code"] == "NOT_FOUND"
            assert set(response.json()) == {"code", "message_key", "request_id"}
        assert client.get(base + ORG_A + "/audit", headers=headers).status_code == 404
        assert (
            client.post(
                base + ORG_A + "/memberships",
                headers={**headers, "Idempotency-Key": str(uuid4())},
                json={
                    "principal_id": STAFF_B,
                    "role": "reviewer",
                    "expires_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
                },
            ).status_code
            == 404
        )
        assert (
            client.post(
                "https://127.0.0.1:3443/identity/logout",
                headers={**headers, "origin": "https://evil.invalid"},
            ).status_code
            == 403
        )
        assert (
            client.post(
                "https://127.0.0.1:3443/identity/logout",
                headers={k: v for k, v in headers.items() if k != "x-csrf-token"},
            ).status_code
            == 403
        )
        assert client.post("https://127.0.0.1:3443/identity/logout", headers=headers).status_code == 200
        assert client.get("https://127.0.0.1:3443/identity/me", headers=headers).status_code == 401
    finally:
        client.close()


@pytest.mark.integration
def test_real_admin_membership_enforcement_and_audit():
    client, headers = real_login("synthetic-admin-a")
    base = "https://127.0.0.1:3443/identity/organizations/" + ORG_A
    expiry = (datetime.now(UTC) + timedelta(hours=1)).isoformat()
    try:
        for pid, role in [
            (ADMIN_A, "reviewer"),
            (STAFF_B, "org_admin"),
            (STAFF_B, "safeguarding"),
            (STAFF_B, "authority"),
            (STAFF_B, "privacy"),
        ]:
            assert (
                client.post(
                    base + "/memberships",
                    headers={**headers, "Idempotency-Key": str(uuid4())},
                    json={"principal_id": pid, "role": role, "expires_at": expiry},
                ).status_code
                == 403
            )
        command_headers = {**headers, "Idempotency-Key": str(uuid4())}
        command_body = {"principal_id": STAFF_B, "role": "reviewer", "expires_at": expiry}
        assert client.post(base + "/memberships", headers=headers, json=command_body).status_code == 422
        assert (
            client.post(base + "/memberships", headers=command_headers, json=command_body).status_code == 200
        )
        assert (
            client.post(base + "/memberships", headers=command_headers, json=command_body).status_code == 200
        )
        assert (
            client.post(
                base + "/memberships", headers=command_headers, json={**command_body, "role": "supervisor"}
            ).status_code
            == 409
        )
        assert (
            client.post(
                base + "/memberships",
                headers={**headers, "Idempotency-Key": str(uuid4())},
                json={"principal_id": STAFF_B, "role": "reviewer", "expires_at": expiry, "revoke": True},
            ).status_code
            == 200
        )
        assert client.get(base + "/cases/" + CASE_A + "/permission", headers=headers).status_code == 404
        report = client.get(base + "/audit", headers=headers)
        assert report.status_code == 200
        actions = [e["action"] for e in report.json()["events"]]
        assert "membership.grant" in actions and "membership.revoke" in actions
        assert "encrypted_token" not in report.text and "principal_id" not in report.text
        assert (
            client.get(
                "https://127.0.0.1:3443/identity/organizations/" + ORG_B + "/audit", headers=headers
            ).status_code
            == 404
        )
    finally:
        client.post("https://127.0.0.1:3443/identity/logout", headers=headers)
        client.close()


@pytest.mark.integration
@pytest.mark.parametrize(
    "condition",
    [
        "session_expired",
        "session_idle",
        "session_revoked",
        "principal_disabled",
        "membership_revoked",
        "membership_expired",
        "org_suspended",
        "grant_revoked",
        "grant_expired",
    ],
)
def test_live_revocation(condition):
    from scripts.identity_setup import fixture_id

    principal = fixture_id("synthetic-revoke-" + condition)
    client, headers = real_login("synthetic-revoke-" + condition)
    session = headers["cookie"].split("=", 1)[1]
    mutations = {
        "session_expired": (
            "UPDATE platform.identity_sessions SET expires_at=now()-interval '1 second' WHERE token_hash=%s",
            (digest(session),),
        ),
        "session_idle": (
            "UPDATE platform.identity_sessions SET last_seen=now()-interval '11 minutes' WHERE token_hash=%s",
            (digest(session),),
        ),
        "session_revoked": (
            "UPDATE platform.identity_sessions SET revoked_at=now() WHERE token_hash=%s",
            (digest(session),),
        ),
        "principal_disabled": ("UPDATE app.staff_principals SET disabled_at=now() WHERE id=%s", (principal,)),
        "membership_revoked": (
            "UPDATE app.memberships SET revoked_at=now() WHERE organization_id=%s AND principal_id=%s",
            (ORG_A, principal),
        ),
        "membership_expired": (
            "UPDATE app.memberships SET expires_at=now()-interval '1 second', starts_at=now()-interval '1 day' WHERE organization_id=%s AND principal_id=%s",
            (ORG_A, principal),
        ),
        "org_suspended": ("UPDATE app.organizations SET suspended_at=now() WHERE id=%s", (ORG_A,)),
        "grant_revoked": (
            "UPDATE app.case_grants SET revoked_at=now() WHERE organization_id=%s AND principal_id=%s",
            (ORG_A, principal),
        ),
        "grant_expired": (
            "UPDATE app.case_grants SET expires_at=now()-interval '1 second' WHERE organization_id=%s AND principal_id=%s",
            (ORG_A, principal),
        ),
    }
    from psycopg import sql as query

    from scripts.identity_setup import seed

    class DockerDatabase:
        def execute(self, statement, args=()):
            # Reviewed synthetic UUID/hash values only; psycopg literal quoting, no shell.
            parts = statement.split("%s")
            assembled = query.SQL(parts[0])
            for arg, part in zip(args, parts[1:]):
                assembled += query.Literal(arg) + query.SQL(part)
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "-i",
                    "foc-phase1a-db-1",
                    "psql",
                    "-X",
                    "-U",
                    "postgres",
                    "-d",
                    "foc_synthetic",
                    "-v",
                    "ON_ERROR_STOP=1",
                    "-tA",
                ],
                input=assembled.as_string().encode(),
                capture_output=True,
                check=True,
            )
            self.value = result.stdout.decode().strip()
            return self

        def fetchone(self):
            return (self.value,)

    conn = DockerDatabase()
    if True:
        try:
            sql, args = mutations[condition]
            conn.execute(sql, args)
            response = client.get(
                "https://127.0.0.1:3443/identity/organizations/" + ORG_A + "/cases/" + CASE_A + "/permission",
                headers=headers,
            )
            assert response.status_code == (
                401 if condition.startswith("session_") or condition == "principal_disabled" else 404
            )
        finally:
            conn.execute("UPDATE app.staff_principals SET disabled_at=NULL WHERE id=%s", (principal,))
            conn.execute("UPDATE app.organizations SET suspended_at=NULL WHERE id=%s", (ORG_A,))
            seed(conn)
            client.close()


@pytest.mark.parametrize(
    "path",
    [
        "me",
        "organizations/" + ORG_A + "/audit",
        "organizations/" + ORG_A + "/cases/" + CASE_A + "/permission",
    ],
)
@pytest.mark.parametrize("credential", ["", "Bearer forged", "Basic forged"])
def test_anonymous_or_forged_identity_denied(path, credential):
    with TestClient(create_app()) as client:
        assert client.get("/identity/" + path, headers={"authorization": credential}).status_code == 401


@pytest.mark.parametrize("params", [{}, {"state": "forged", "code": "forged"}, {"error": "access_denied"}])
def test_login_callback_fail_closed(params):
    with TestClient(create_app()) as client:
        assert client.get("/identity/callback", params=params).status_code == 401


def test_session_cipher_and_cookie_flags():
    with TestClient(create_app()) as client:
        response = client.get("/identity/login", follow_redirects=False)
        cookie = response.headers["set-cookie"]
        assert response.status_code == 302
        assert "HttpOnly" in cookie and "Secure" in cookie and "SameSite=lax" in cookie and "Path=/" in cookie
        assert "code_challenge_method=S256" in response.headers["location"]
        private = json.loads((Path(__file__).resolve().parents[2] / ".runtime/identity.json").read_text())
        assert private["FOC_IDP_SECRET"] not in response.text + cookie + response.headers["location"]
        assert COOKIE not in cookie


@pytest.mark.integration
def test_real_oidc_code_replay_cannot_create_another_session():
    client, headers = real_login("synthetic-reviewer-b")
    try:
        callback_url, flow = client._synthetic_callback
        replay = client.get(callback_url, headers={"cookie": "__Host-foc-flow=" + flow})
        assert replay.status_code in [401, 503]
        assert "__Host-foc-session" not in replay.cookies
        assert "access_token" not in replay.text and "id_token" not in replay.text
    finally:
        client.post("https://127.0.0.1:3443/identity/logout", headers=headers)
        client.close()


@pytest.mark.integration
def test_api_cannot_modify_validation_reports():
    result = subprocess.run(
        [
            "docker",
            "exec",
            "foc-phase1a-api-1",
            "python",
            "-c",
            "import json,os; print(json.dumps({'coverage':os.access('/coverage',os.W_OK),'reports':os.access('/workspace/artifacts/raw',os.W_OK)}))",
        ],
        capture_output=True,
        check=True,
        text=True,
    )
    assert json.loads(result.stdout) == {"coverage": True, "reports": False}
