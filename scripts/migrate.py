"""Atomic, checksum-verified forward migrations. Admin credentials never enter the API process."""

import hashlib
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]


def migrate(url):
    with psycopg.connect(url) as conn:
        conn.execute("SELECT pg_advisory_xact_lock(8201601)")
        for path in sorted((ROOT / "database/migrations").glob("*.sql")):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            exists = conn.execute("SELECT to_regclass('platform.migrations')").fetchone()[0]
            if exists:
                prior = conn.execute(
                    "SELECT sha256 FROM platform.migrations WHERE version=%s", (path.stem,)
                ).fetchone()
                if prior:
                    if prior[0] != digest:
                        raise RuntimeError("Applied migration checksum differs: " + path.name)
                    continue
            conn.execute(path.read_text(), prepare=False)
            conn.execute("INSERT INTO platform.migrations(version,sha256) VALUES(%s,%s)", (path.stem, digest))
