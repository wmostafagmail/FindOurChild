"""Private PostgreSQL serialization, immutable records, audit and atomic outbox.

Requires an externally current durable checkpoint. A database hash chain alone
cannot defend against the privileged host. Restore starts inactive and must be
reconciled administratively; no reconciliation/provisioning endpoint is supplied.
"""

from contextlib import contextmanager
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb

from .records import digest, require


class Transaction:
    def __init__(self, conn, instance, tenant, revision, checkpoint, external):
        self.conn, self.instance, self.tenant = conn, instance, tenant
        self.revision, self.checkpoint = revision, checkpoint
        self.changed = False
        self.external = external

    def get(self, kind, key):
        if kind == "exposure":
            self.conn.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,271828))", (key,))
            row = self.conn.execute("SELECT value,digest FROM owner_only_demo.fixture_exposure WHERE key=%s",
                                    (key,)).fetchone()
            if row:
                require(digest(row[0]) == row[1] and self.external.frozen(key) == row[1], "exposure_checkpoint")
                return row[0]
            return None
        row = self.conn.execute(
            "SELECT value,digest FROM owner_only_demo.journal WHERE instance=%s AND kind=%s AND key=%s",
            (self.instance, kind, key),
        ).fetchone()
        if row:
            require(digest(row[0]) == row[1], "journal_corrupt")
            return row[0]
        return None

    def put(self, kind, key, value):
        prior = self.get(kind, key)
        require(prior is None or prior == value, "immutable_record_conflict")
        if prior is not None:
            return
        if kind == "exposure":
            self.external.seal(key, digest(value))
            self.conn.execute("INSERT INTO owner_only_demo.fixture_exposure(key,value,digest) VALUES(%s,%s,%s)",
                              (key, Jsonb(value), digest(value)))
            self.changed = True
            self.checkpoint = digest({"previous": self.checkpoint, "exposure": key, "value": digest(value)})
            return
        self.conn.execute(
            "INSERT INTO owner_only_demo.journal(instance,tenant,kind,key,value,digest) VALUES(%s,%s,%s,%s,%s,%s)",
            (self.instance, self.tenant, kind, key, Jsonb(value), digest(value)),
        )
        self.checkpoint = digest({"previous": self.checkpoint, "kind": kind, "key": key, "value": digest(value)})
        self.changed = True

    def audit(self, action, object_digest):
        row = {"action": action, "object_digest": object_digest, "previous": self.checkpoint}
        event = str(uuid4())
        self.put("event", event, row)
        self.put("outbox", event, {"event_digest": digest(row)})


class Store:
    def __init__(self, dsn, instance, tenant, checkpoint):
        # All arguments are privileged composition inputs, never request parameters.
        self.dsn, self.instance, self.tenant = dsn, instance, tenant
        self.external = checkpoint

    @contextmanager
    def transaction(self, activation_epoch, authority_epoch):
        with psycopg.connect(self.dsn, connect_timeout=3) as conn:
            conn.execute("SET LOCAL statement_timeout='5s'")
            conn.execute("SET LOCAL lock_timeout='3s'")
            role = conn.execute("SELECT rolsuper,rolbypassrls FROM pg_roles WHERE rolname=current_user").fetchone()
            require(role == (False, False), "private_role_required")
            conn.execute("SELECT set_config('foc.v3_instance',%s,true)", (self.instance,))
            conn.execute("SELECT set_config('foc.v3_tenant',%s,true)", (self.tenant,))
            row = conn.execute(
                "SELECT enabled,activation_epoch,authority_epoch,revision,checkpoint FROM owner_only_demo.authority "
                "WHERE instance=%s AND tenant=%s FOR UPDATE", (self.instance, self.tenant),
            ).fetchone()
            require(row is not None and row[0] is True and row[1:3] == (activation_epoch, authority_epoch),
                    "authority_inactive_or_epoch")
            require(self.external.current(self.instance) == tuple(row[1:]), "external_checkpoint")
            tx = Transaction(conn, self.instance, self.tenant, row[3], row[4], self.external)
            yield tx
            # External fence recheck after any audit/row-lock wait, before commit.
            require(self.external.current(self.instance) == tuple(row[1:]), "external_checkpoint_changed")
            if tx.changed:
                conn.execute("UPDATE owner_only_demo.authority SET revision=revision+1,checkpoint=%s WHERE instance=%s",
                             (tx.checkpoint, self.instance))
                # Reserve-before-commit: crash between this and PG commit fences both old/new
                # states until privileged reconciliation; never falls back to an older epoch.
                self.external.advance(self.instance, tuple(row[1:]),
                                      (row[1], row[2], row[3] + 1, tx.checkpoint))
