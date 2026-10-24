"""Environment markers alone never prove database or service isolation."""

import json
import os
from pathlib import Path

import httpx
import psycopg

ROOT = Path(__file__).resolve().parents[1]


def verify(services=False):
    if os.environ.get("FOC_DATA_CLASS") != "synthetic":
        raise RuntimeError("Synthetic data required")
    expected = json.loads((ROOT / ".runtime/instance.json").read_text())
    with psycopg.connect(os.environ["FOC_DATABASE_URL"]) as conn:
        row = conn.execute(
            "SELECT current_database(),data_class,instance_id::text,schema_version FROM platform.environment WHERE EXISTS (SELECT 1 FROM platform.migrations WHERE version='0002_contract_hardening')"
        ).fetchone()
        role = conn.execute(
            "SELECT rolsuper,rolbypassrls FROM pg_roles WHERE rolname=current_user"
        ).fetchone()
        if row != ("foc_synthetic", "synthetic", expected["instance_id"], "0001") or role != (False, False):
            raise RuntimeError("Database identity or runtime privileges invalid")
        if conn.execute("SELECT count(*) FROM app.cases").fetchone()[0] != 0:
            raise RuntimeError("Missing context must deny all case reads")
    print("Verified synthetic database identity, migrations, non-owner role and deny-default reads")
    if services:
        verify_services()


def verify_services():
    expected = json.loads((ROOT / ".runtime/instance.json").read_text())
    response = httpx.get("http://127.0.0.1:8000/health/ready", timeout=5)
    if response.status_code != 200 or response.json().get("instance_id") != expected["instance_id"]:
        raise RuntimeError("API must use this isolated migrated database")
    page = httpx.get("http://127.0.0.1:3000/en", timeout=30)
    if page.status_code != 200 or 'data-ready="true"' not in page.text:
        raise RuntimeError("Actual web service must reach the actual API")
    print("Verified actual web/API services against the isolated database instance")


if __name__ == "__main__":
    import sys

    verify("--services" in sys.argv)
