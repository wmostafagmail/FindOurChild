"""Closed host-side CI fault fixture. Not a deployed API or authorization issuer."""

import json
import os
import sys
from pathlib import Path

import psycopg

from scripts.identity_setup import OWNER_V3_USERS, fixture_id


def main():
    if (os.environ.get("GITHUB_ACTIONS") != "true" or os.environ.get("FOC_E2E_ISOLATED") != "1"
            or len(sys.argv) != 3 or sys.argv[1] != "expire_session" or sys.argv[2] not in OWNER_V3_USERS
            or not sys.argv[2].endswith("-05")):
        raise SystemExit("Closed synthetic CI fixture required")
    data = json.loads((Path(__file__).resolve().parents[1] / ".runtime/local.json").read_bytes())
    with psycopg.connect(data["FOC_DATABASE_ADMIN_URL"], connect_timeout=3) as conn:
        assert conn.execute("SELECT data_class FROM platform.environment").fetchone() == ("synthetic",)
        result = conn.execute("UPDATE platform.identity_sessions SET expires_at=now()-interval '1 second' "
                              "WHERE principal_id=%s AND revoked_at IS NULL RETURNING principal_id",
                              (fixture_id(sys.argv[2]),)).fetchall()
        assert len(result) == 1
    print('{"fault":"session_expired","synthetic_only":true}')


if __name__ == "__main__":
    main()
