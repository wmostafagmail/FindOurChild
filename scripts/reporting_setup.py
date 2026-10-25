"""Private synthetic credentials and explicit intake routing; no production mode."""

import hashlib
import json
import secrets
from pathlib import Path

from cryptography.fernet import Fernet

ROOT = Path(__file__).resolve().parents[1]


def generate():
    path = ROOT / ".runtime/reporting.json"
    if path.exists():
        data = json.loads(path.read_text())
    else:
        data = {
            "FOC_REPORT_KEY": Fernet.generate_key().decode(),
            "FOC_CONTACT_KEY": Fernet.generate_key().decode(),
            "FOC_WORKER_PASSWORD": secrets.token_urlsafe(32),
            "FOC_S3_API_KEY": secrets.token_urlsafe(24),
            "FOC_S3_API_SECRET": secrets.token_urlsafe(32),
            "FOC_S3_WORKER_KEY": secrets.token_urlsafe(24),
            "FOC_S3_WORKER_SECRET": secrets.token_urlsafe(32),
            "FOC_S3_GATEWAY_KEY": secrets.token_urlsafe(24),
            "FOC_S3_GATEWAY_SECRET": secrets.token_urlsafe(32),
            "FOC_S3_ADMIN_KEY": secrets.token_urlsafe(24),
            "FOC_S3_ADMIN_SECRET": secrets.token_urlsafe(32),
        }
        path.write_text(json.dumps(data))
        path.chmod(0o600)
    identities = []
    for role, actions in {
        "API": ["Write:foc-quarantine", "Read:foc-quarantine"],
        "WORKER": [
            "Read:foc-quarantine",
            "Write:foc-quarantine",
            "List:foc-quarantine",
            "Write:foc-original",
            "Read:foc-original",
            "List:foc-original",
            "Write:foc-derivative",
            "Read:foc-derivative",
            "List:foc-derivative",
        ],
        "GATEWAY": ["Read:foc-derivative"],
        "ADMIN": ["Admin", "Read", "Write", "List", "Tagging"],
    }.items():
        identities.append(
            {
                "name": role.lower(),
                "credentials": [
                    {"accessKey": data[f"FOC_S3_{role}_KEY"], "secretKey": data[f"FOC_S3_{role}_SECRET"]}
                ],
                "actions": actions,
            }
        )
    config = ROOT / ".runtime/s3.json"
    config.write_text(json.dumps({"identities": identities}))
    config.chmod(0o644)  # credential file mounted only in private storage container
    sink = ROOT / ".runtime/delivery"
    sink.mkdir(exist_ok=True, mode=0o700)
    from scripts.identity_setup import EXTRA_USERS, fixture_id

    (ROOT / ".runtime/reporting-fixtures.json").write_text(
        json.dumps(
            {
                "staff_cases": {
                    name: fixture_id(name + "-case")
                    for name in EXTRA_USERS
                    if name.startswith("synthetic-reporting-")
                }
            }
        )
    )
    data["FOC_S3_CONFIG_SHA256"] = hashlib.sha256(config.read_bytes()).hexdigest()
    return data


def seed(conn):
    from scripts.identity_setup import EXTRA_USERS, ORG_A, STAFF_A, fixture_id

    moderator = fixture_id("synthetic-intake-moderator")
    conn.execute(
        "INSERT INTO platform.intake_route VALUES(%s,%s,now()+interval '30 days') ON CONFLICT(organization_id) DO UPDATE SET moderator=EXCLUDED.moderator,expires_at=EXCLUDED.expires_at",
        (ORG_A, moderator),
    )
    # Dedicated intake fixtures do not change the previously accepted staff-A/org-admin permissions.
    conn.execute(
        "UPDATE app.memberships SET revoked_at=now() WHERE organization_id=%s AND principal_id=%s AND role='supervisor'",
        (ORG_A, STAFF_A),
    )
    conn.execute(
        "INSERT INTO app.memberships(organization_id,principal_id,role,expires_at) VALUES(%s,%s,'supervisor',now()+interval '30 days') ON CONFLICT(organization_id,principal_id,role) DO UPDATE SET revoked_at=NULL,expires_at=EXCLUDED.expires_at",
        (ORG_A, moderator),
    )
    for name in EXTRA_USERS:
        if not name.startswith("synthetic-reporting-"):
            continue
        pid = fixture_id(name)
        case = fixture_id(name + "-case")
        conn.execute(
            "INSERT INTO app.cases(organization_id,id,registry) VALUES(%s,%s,'missing') ON CONFLICT DO NOTHING",
            (ORG_A, case),
        )
        for permission in ["case.read", "case.write", "media.read"]:
            conn.execute(
                "INSERT INTO app.case_grants(organization_id,case_id,principal_id,permission,purpose,granted_by,expires_at) VALUES(%s,%s,%s,%s,'case_management',%s,now()+interval '1 day') ON CONFLICT(organization_id,case_id,principal_id,permission,purpose) DO UPDATE SET revoked_at=NULL,expires_at=EXCLUDED.expires_at",
                (ORG_A, case, pid, permission, moderator),
            )


def provision_storage():
    import boto3
    from botocore.config import Config

    data = generate()
    client = boto3.client(
        "s3",
        endpoint_url="http://storage:8333",
        aws_access_key_id=data["FOC_S3_ADMIN_KEY"],
        aws_secret_access_key=data["FOC_S3_ADMIN_SECRET"],
        region_name="us-east-1",
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
            retries={"max_attempts": 0},
            connect_timeout=3,
            read_timeout=5,
        ),
    )
    import time
    from uuid import uuid4

    from botocore.exceptions import BotoCoreError, ClientError

    deadline = time.monotonic() + 60
    while True:
        try:
            for bucket in ["foc-quarantine", "foc-original", "foc-derivative"]:
                existing = [b["Name"] for b in client.list_buckets()["Buckets"]]
                if bucket not in existing:
                    client.create_bucket(Bucket=bucket)
                client.put_bucket_versioning(Bucket=bucket, VersioningConfiguration={"Status": "Enabled"})
                if client.get_bucket_versioning(Bucket=bucket)["Status"] != "Enabled":
                    raise RuntimeError("Versioned storage unavailable")
            key = str(uuid4())
            payload = secrets.token_bytes(32)
            result = client.put_object(Bucket="foc-quarantine", Key=key, Body=payload, IfNoneMatch="*")
            version = result.get("VersionId")
            if not version or version == "null":
                raise RuntimeError("Immutable storage version unavailable")
            response = client.get_object(Bucket="foc-quarantine", Key=key, VersionId=version)
            try:
                if response["Body"].read() != payload:
                    raise RuntimeError("Storage readiness integrity failed")
            finally:
                response["Body"].close()
            client.delete_object(Bucket="foc-quarantine", Key=key, VersionId=version)
            break
        except (BotoCoreError, ClientError):
            if time.monotonic() >= deadline:
                raise RuntimeError("Private storage not ready within deadline") from None
            time.sleep(1)


if __name__ == "__main__":
    provision_storage()
