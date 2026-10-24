import json
import os
from pathlib import Path

import psycopg
from psycopg import sql

from scripts.migrate import migrate


def main():
    url = os.environ["FOC_DATABASE_ADMIN_URL"]
    migrate(url)
    with psycopg.connect(url) as conn:
        conn.execute(
            sql.SQL("ALTER ROLE foc_api PASSWORD {}").format(sql.Literal(os.environ["FOC_DB_API_PASSWORD"]))
        )
        from scripts.identity_setup import seed
        seed(conn)
        row = conn.execute("SELECT instance_id::text FROM platform.environment").fetchone()
    Path(".runtime/instance.json").write_text(
        json.dumps({"database": "foc_synthetic", "instance_id": row[0], "data_class": "synthetic"})
    )
    print("Applied checksum-verified migration to isolated synthetic PostgreSQL")


if __name__ == "__main__":
    main()
