"""Generate private synthetic-only IdP realm and bootstrap explicit ACLs. Never real identities."""

import base64
import json
import secrets
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from cryptography.fernet import Fernet

ROOT = Path(__file__).resolve().parents[1]
ORG_A = "10000000-0000-4000-8000-000000000001"
ORG_B = "10000000-0000-4000-8000-000000000002"
STAFF_A = "20000000-0000-4000-8000-000000000001"
STAFF_B = "20000000-0000-4000-8000-000000000002"
ADMIN_A = "20000000-0000-4000-8000-000000000003"
CASE_A = "30000000-0000-4000-8000-000000000001"
CASE_B = "30000000-0000-4000-8000-000000000002"


REVOCATIONS = [
    "session_expired",
    "session_idle",
    "session_revoked",
    "principal_disabled",
    "membership_revoked",
    "membership_expired",
    "org_suspended",
    "grant_revoked",
    "grant_expired",
]
EXTRA_USERS = [
    f"synthetic-{b}-{l}-{w}"
    for b in ["chromium", "firefox", "webkit"]
    for l in ["ar-EG", "en-GB"]
    for w in [320, 360, 390, 1280]
] + ["synthetic-revoke-" + name for name in REVOCATIONS]


def fixture_id(name):
    return str(uuid5(NAMESPACE_URL, "https://synthetic.invalid/foc/" + name))


def users():
    return [
        (STAFF_A, "synthetic-reviewer-a"),
        (STAFF_B, "synthetic-reviewer-b"),
        (ADMIN_A, "synthetic-admin-a"),
    ] + [(fixture_id(name), name) for name in EXTRA_USERS]


def generate():
    state = ROOT / ".runtime"
    private = state / "identity.json"
    if private.exists():
        data = json.loads(private.read_text())
    else:
        data = {
            "FOC_IDP_SECRET": secrets.token_urlsafe(32),
            "FOC_SESSION_KEY": Fernet.generate_key().decode(),
            "password": secrets.token_urlsafe(24),
            "otp": base64.b32encode(secrets.token_bytes(20)).decode(),
        }
    data["users"] = {name: pid for pid, name in users()}
    private.write_text(json.dumps(data))
    private.chmod(0o600)
    realm = json.loads((ROOT / "config/keycloak/realm-template.json").read_text())
    realm["clients"][0]["secret"] = data["FOC_IDP_SECRET"]
    for pid, name in users():
        realm.setdefault("users", []).append(
            {
                "id": pid,
                "username": name,
                "enabled": True,
                "emailVerified": True,
                "email": name + "@synthetic.invalid",
                "firstName": "Synthetic",
                "lastName": "Fixture",
                "credentials": [
                    {"type": "password", "value": data["password"], "temporary": False},
                    {
                        "type": "otp",
                        "secretData": json.dumps({"value": data["otp"]}),
                        "credentialData": json.dumps(
                            {
                                "subType": "totp",
                                "digits": 6,
                                "counter": 0,
                                "period": 30,
                                "algorithm": "HmacSHA1",
                                "secretEncoding": "BASE32",
                            }
                        ),
                    },
                ],
            }
        )
    target = state / "keycloak"
    target.mkdir(mode=0o700, exist_ok=True)
    # Container user must be able to traverse/read the synthetic realm; parent .runtime stays private to host.
    target.chmod(0o755)
    (target / "foc-synthetic-realm.json").write_text(json.dumps(realm))
    (target / "foc-synthetic-realm.json").chmod(0o644)


if __name__ == "__main__":
    generate()


def seed(conn):
    if conn.execute("SELECT data_class FROM platform.environment").fetchone() != ("synthetic",):
        raise RuntimeError("Synthetic identity fixtures only")
    for org in [ORG_A, ORG_B]:
        conn.execute(
            "INSERT INTO app.organizations(id,country_code,approved_status,policy_version) VALUES(%s,'EG','approved','synthetic-identity-v1') ON CONFLICT DO NOTHING",
            (org,),
        )
    for pid, _ in users():
        conn.execute(
            "INSERT INTO app.staff_principals(id,oidc_issuer,oidc_subject) VALUES(%s,'https://127.0.0.1:8443/realms/foc-synthetic',%s) ON CONFLICT(id) DO UPDATE SET oidc_issuer=excluded.oidc_issuer,oidc_subject=excluded.oidc_subject",
            (pid, pid),
        )
    for org, pid, role in [
        (ORG_A, STAFF_A, "reviewer"),
        (ORG_B, STAFF_B, "reviewer"),
        (ORG_A, ADMIN_A, "org_admin"),
    ] + [(ORG_A, fixture_id(name), "reviewer") for name in EXTRA_USERS]:
        conn.execute(
            "INSERT INTO app.memberships(organization_id,principal_id,role,expires_at) VALUES(%s,%s,%s,now()+interval '1 day') ON CONFLICT(organization_id,principal_id,role) DO UPDATE SET expires_at=excluded.expires_at,revoked_at=NULL",
            (org, pid, role),
        )
    for org, case in [(ORG_A, CASE_A), (ORG_B, CASE_B)]:
        conn.execute(
            "INSERT INTO app.cases(organization_id,id,registry) VALUES(%s,%s,'missing') ON CONFLICT DO NOTHING",
            (org, case),
        )
    for pid in [STAFF_A] + [fixture_id(name) for name in EXTRA_USERS]:
        conn.execute(
            "INSERT INTO app.case_grants(organization_id,case_id,principal_id,permission,purpose,granted_by,expires_at) VALUES(%s,%s,%s,'case.read','case_management',%s,now()+interval '1 day') ON CONFLICT(organization_id,case_id,principal_id,permission,purpose) DO UPDATE SET expires_at=excluded.expires_at,revoked_at=NULL",
            (ORG_A, CASE_A, pid, ADMIN_A),
        )
