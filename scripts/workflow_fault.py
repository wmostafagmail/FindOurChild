"""Private test operator: actual scoped revocation/audit failure; never an HTTP endpoint."""

import hashlib
import os
import sys

import psycopg
from psycopg import sql

from scripts.identity_setup import fixture_id
from scripts.synthetic_workflow_setup import CANDIDATE, USERS


def main():
    name, kind, state = sys.argv[1:4]
    if name not in USERS or kind not in {"grant", "audit", "logout"} or state not in {"on", "off"}:
        raise RuntimeError("Invalid synthetic fixture operation")
    if "--inside" not in sys.argv:
        from scripts.dev import compose

        compose(
            "run",
            "--rm",
            "--user",
            "0:0",
            "tester",
            "python",
            "-m",
            "scripts.workflow_fault",
            name,
            kind,
            state,
            "--inside",
        )
        return
    with psycopg.connect(os.environ["FOC_DATABASE_ADMIN_URL"]) as conn:
        if conn.execute("SELECT current_database(),data_class FROM platform.environment").fetchone() != (
            "foc_synthetic",
            "synthetic",
        ):
            raise RuntimeError("Synthetic database required")
        actor = fixture_id(name)
        if kind == "grant":
            conn.execute(
                "UPDATE app.case_grants SET revoked_at=CASE WHEN %s THEN now() ELSE NULL END WHERE principal_id=%s AND case_id=%s AND permission='case.read' AND purpose='case_management'",
                (state == "on", actor, CANDIDATE),
            )
        else:
            identifier = sql.Identifier("sw_fault_" + hashlib.sha256(name.encode()).hexdigest()[:12])
            if state == "on":
                action = (
                    sql.SQL("NEW.action = 'session.logout'")
                    if kind == "logout"
                    else sql.SQL("NEW.action LIKE 'synthetic.%'")
                )
                conn.execute(
                    sql.SQL(
                        "CREATE FUNCTION platform.{}() RETURNS trigger LANGUAGE plpgsql AS $body$ BEGIN IF NEW.actor_ref={}::uuid AND ({}) THEN RAISE EXCEPTION 'synthetic audit unavailable'; END IF; RETURN NEW; END $body$"
                    ).format(identifier, sql.Literal(actor), action)
                )
                conn.execute(
                    sql.SQL(
                        "CREATE TRIGGER {} BEFORE INSERT ON app.audit_events FOR EACH ROW EXECUTE FUNCTION platform.{}()"
                    ).format(identifier, identifier)
                )
            else:
                conn.execute(sql.SQL("DROP TRIGGER IF EXISTS {} ON app.audit_events").format(identifier))
                conn.execute(sql.SQL("DROP FUNCTION IF EXISTS platform.{}()").format(identifier))


if __name__ == "__main__":
    main()
