"""Synthetic test fixtures and independent privileged assertions; no application testing bypass."""

import hashlib
import io
import json
import os
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import psycopg
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from foc_api.config import Settings
from foc_api.main import create_app
from PIL import Image

ORIGIN = "https://127.0.0.1:3443"
ORG = "10000000-0000-4000-8000-000000000001"
from scripts.identity_setup import fixture_id

MODERATOR = fixture_id("synthetic-intake-moderator")


def make_client():
    return TestClient(create_app(Settings.load()), base_url=ORIGIN, client=(str(uuid4()), 50000))


def report_body(registry="missing"):
    unknown = {"lower": None, "upper": None, "precision": "unknown", "knowledge": "unknown"}
    body = {
        "names": [],
        "birth_date": unknown,
        "estimated_age": {"min_months": None, "max_months": None, "as_of": unknown},
        "general_location": {"country": "EG", "region": "unknown"},
        "reporter": {
            "relationship": "unknown",
            "encrypted_transport_contact": str(uuid4()) + "@synthetic.invalid",
        },
        "notice_version": "synthetic-1c-v1",
        "processing_purposes": ["intake"],
    }
    body["missing_at" if registry == "missing" else "discovered_at"] = {
        "lower": None,
        "upper": None,
        "timezone": "Africa/Cairo",
        "precision": "unknown",
    }
    if registry == "found":
        body["welfare"] = "unknown"
    return body


def public(client, path, body, key=None):
    challenge = client.post("/v1/public/intake-challenges", json={}, headers={"Origin": ORIGIN})
    assert challenge.status_code == 201
    return client.post(
        "/v1/public/" + path,
        json=body,
        headers={
            "Origin": ORIGIN,
            "X-Intake-Challenge": challenge.json()["challenge"],
            "Idempotency-Key": str(key or uuid4()),
        },
    )


def create_report(client, registry="missing", body=None):
    body = body or report_body(registry)
    response = public(client, "reports/" + registry, body)
    assert response.status_code == 202
    return response.json()["receipt"], body


def verify_reporter(client, receipt, contact):
    response = public(client, "access-requests", {"receipt": receipt, "contact": contact})
    assert response.status_code == 202
    encrypted = (Path("/delivery") / (hashlib.sha256(receipt.encode()).hexdigest() + ".json")).read_text()
    code = json.loads(Fernet(os.environ["FOC_CONTACT_KEY"].encode()).decrypt(encrypted.encode()))["code"]
    response = public(client, "access-exchanges", {"receipt": receipt, "code": code})
    assert response.status_code == 200
    return code


def headers(client, staff=False):
    name = "__Host-foc-csrf" if staff else "__Host-foc-reporter-csrf"
    return {"Origin": ORIGIN, "X-CSRF-Token": client.cookies.get(name, ""), "Idempotency-Key": str(uuid4())}


def png(metadata=False):
    from PIL.PngImagePlugin import PngInfo

    out = io.BytesIO()
    info = PngInfo()
    if metadata:
        info.add_text("Description", "SYNTHETIC_SECRET_CANARY")
    Image.new("RGB", (16, 16), "green").save(out, format="PNG", pnginfo=info)
    return out.getvalue()


def upload(client, data=None, mime="image/png"):
    data = data or png()
    sha = hashlib.sha256(data).hexdigest()
    response = client.post(
        "/v1/reporter/upload-intents",
        json={"mime": mime, "bytes": len(data), "sha256": sha},
        headers=headers(client),
    )
    assert response.status_code == 201
    iid = response.json()["id"]
    response = client.put(
        "/v1/reporter/upload-intents/" + iid + "/content",
        content=data,
        headers={**headers(client), "Content-Type": mime},
    )
    assert response.status_code == 200
    bound = response.json()
    response = client.post(
        "/v1/reporter/upload-intents/" + iid + "/complete", json=bound, headers=headers(client)
    )
    assert response.status_code == 202
    return iid, bound


@contextmanager
def admin():
    with psycopg.connect(os.environ["FOC_DATABASE_ADMIN_URL"], autocommit=True) as conn:
        assert conn.execute("SELECT data_class FROM platform.environment").fetchone()[0] == "synthetic"
        yield conn


def cid(receipt):
    with admin() as conn:
        return conn.execute(
            "SELECT case_id FROM platform.report_submissions WHERE receipt_hash=%s",
            (hashlib.sha256(receipt.encode()).digest(),),
        ).fetchone()[0]
