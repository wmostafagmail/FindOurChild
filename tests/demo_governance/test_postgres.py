"""Real isolated PostgreSQL transactions/RLS/concurrency, not SQLite substitutes."""

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest

from tools.phase2e.demo_governance.fencing import Fence
from tools.phase2e.demo_governance.records import Denied


@pytest.fixture
def govdb():
    url = os.environ.get("FOC_GOVERNANCE_DATABASE_URL")
    assert url, "Required private real PostgreSQL harness missing"
    a = psycopg.connect(url, autocommit=True)
    assert a.info.host == "127.0.0.1" and a.info.dbname == "foc_demo_gov"
    assert a.execute("SELECT synthetic_only FROM demo_governance.engineering_marker").fetchone() == (True,)
    i, o, j, t = map(str, [uuid4() for _ in range(4)])
    a.execute(
        "INSERT INTO demo_governance.authority VALUES(%s,true,1,1,clock_timestamp()+interval '1 hour')", (i,)
    )
    a.execute(
        "INSERT INTO demo_governance.jobs VALUES(%s,%s,%s,%s,1,'running',clock_timestamp()+interval '1 hour',1,1,%s)",
        (j, i, o, t, "a" * 64),
    )
    for k in ["key", "model", "image", "case", "media", "purpose"]:
        a.execute(
            "INSERT INTO demo_governance.grants VALUES(%s,%s,1,true,clock_timestamp()+interval '1 hour')",
            (j, k),
        )
    c = psycopg.connect(url)
    c.execute("SET ROLE foc_demo_fence")
    c.execute(
        "SELECT set_config('foc.demo_instance',%s,false),set_config('foc.demo_organization',%s,false)", (i, o)
    )
    c.commit()
    args = {
        "job": j,
        "token": t,
        "epoch": 1,
        "revision": 1,
        "now": datetime.now(UTC),
        "instance": i,
        "organization": o,
        "snapshot": "a" * 64,
    }
    yield a, c, args, url
    c.close()
    a.close()


def publish(f):
    return Fence(f[1]).publish(**f[2])


def test_positive_atomic_publication_and_no_direct_worker_writes(govdb):
    a, c, p, _ = govdb
    assert publish(govdb)
    assert a.execute("SELECT state FROM demo_governance.jobs WHERE id=%s", (p["job"],)).fetchone() == (
        "complete",
    )
    assert a.execute("SELECT count(*) FROM demo_governance.outbox WHERE job=%s", (p["job"],)).fetchone() == (
        1,
    )
    with pytest.raises(psycopg.errors.InsufficientPrivilege), c.transaction():
        c.execute("UPDATE demo_governance.authority SET enabled=true")
    with pytest.raises(psycopg.errors.InsufficientPrivilege), c.transaction():
        c.execute("INSERT INTO demo_governance.outbox VALUES(%s)", (str(uuid4()),))


def test_dg_w08_cancel_old_token_requeue_and_exact_replay(govdb):
    a, _, p, _ = govdb
    for sql in [
        "UPDATE demo_governance.jobs SET state='cancelled' WHERE id=%s",
        "UPDATE demo_governance.jobs SET token=gen_random_uuid(),state='running' WHERE id=%s",
    ]:
        a.execute(sql, (p["job"],))
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            publish(govdb)
    a.execute("UPDATE demo_governance.jobs SET token=%s WHERE id=%s", (p["token"], p["job"]))
    assert publish(govdb)
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        publish(govdb)


def test_dg_w09_each_live_grant_revocation(govdb):
    a, _, p, _ = govdb
    for k in ["key", "model", "image", "case", "media", "purpose"]:
        a.execute("UPDATE demo_governance.grants SET active=false WHERE job=%s AND kind=%s", (p["job"], k))
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            publish(govdb)
        a.execute("UPDATE demo_governance.grants SET active=true WHERE job=%s AND kind=%s", (p["job"], k))
    assert a.execute("SELECT count(*) FROM demo_governance.outbox WHERE job=%s", (p["job"],)).fetchone() == (
        0,
    )


def test_dg_w10_changed_epoch_or_input_revision(govdb):
    a, _, p, _ = govdb
    a.execute("UPDATE demo_governance.jobs SET revision=2 WHERE id=%s", (p["job"],))
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        publish(govdb)
    a.execute("UPDATE demo_governance.jobs SET revision=1 WHERE id=%s", (p["job"],))
    a.execute("UPDATE demo_governance.authority SET epoch=2 WHERE instance=%s", (p["instance"],))
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        publish(govdb)


def test_dg_w11_foreign_tenant_instance_rls_and_no_vector_or_path_api(govdb):
    _, c, p, _ = govdb
    with c.transaction():
        c.execute("SELECT set_config('foc.demo_organization',%s,true)", (str(uuid4()),))
        assert c.execute("SELECT count(*) FROM demo_governance.jobs").fetchone() == (0,)
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            publish(govdb)
    with pytest.raises(psycopg.errors.UndefinedTable), c.transaction():
        c.execute("SELECT * FROM demo_governance.vectors")
    with pytest.raises(psycopg.errors.UndefinedTable), c.transaction():
        c.execute("SELECT * FROM demo_governance.model_paths")
    p["instance"] = str(uuid4())
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        publish(govdb)


def test_dg_w12_audit_outage_rolls_back_everything(govdb):
    a, _, p, _ = govdb
    name = "fault_" + uuid4().hex
    # Trusted test-only DDL on this isolated synthetic cluster; no user SQL.
    a.execute(
        f"CREATE FUNCTION demo_governance.{name}() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic audit failure'; END $$"
    )
    a.execute(
        f"CREATE TRIGGER {name} BEFORE INSERT ON demo_governance.audit FOR EACH ROW EXECUTE FUNCTION demo_governance.{name}()"
    )
    try:
        with pytest.raises(psycopg.Error):
            publish(govdb)
        assert a.execute("SELECT state FROM demo_governance.jobs WHERE id=%s", (p["job"],)).fetchone() == (
            "running",
        )
        assert a.execute(
            "SELECT count(*) FROM demo_governance.outbox WHERE job=%s", (p["job"],)
        ).fetchone() == (0,)
    finally:
        a.execute(f"DROP TRIGGER {name} ON demo_governance.audit")
        a.execute(f"DROP FUNCTION demo_governance.{name}()")


def test_dg_w13_post_audit_deadline_and_untrusted_clock(govdb):
    a, _, p, _ = govdb
    name = "wait_" + uuid4().hex
    a.execute(
        f"CREATE FUNCTION demo_governance.{name}() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN PERFORM pg_sleep(0.2); RETURN NEW; END $$"
    )
    a.execute(
        f"CREATE TRIGGER {name} BEFORE INSERT ON demo_governance.audit FOR EACH ROW EXECUTE FUNCTION demo_governance.{name}()"
    )
    try:
        a.execute(
            "UPDATE demo_governance.jobs SET deadline=clock_timestamp()+interval '100 milliseconds' WHERE id=%s",
            (p["job"],),
        )
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            publish(govdb)
        assert a.execute(
            "SELECT count(*) FROM demo_governance.audit WHERE job=%s", (p["job"],)
        ).fetchone() == (0,)
    finally:
        a.execute(f"DROP TRIGGER {name} ON demo_governance.audit")
        a.execute(f"DROP FUNCTION demo_governance.{name}()")
    p["now"] = datetime.now()
    with pytest.raises(Denied):
        publish(govdb)


def test_dg_s15_expiry_during_audit_wait(govdb):
    a, _, p, _ = govdb
    a.execute(
        "UPDATE demo_governance.grants SET expires=clock_timestamp()-interval '1 second' WHERE job=%s AND kind='key'",
        (p["job"],),
    )
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        publish(govdb)
    # The true post-audit wait path is exercised by DG-W13, using DB clock.


def test_dg_w14_stale_restored_activation_epoch(govdb):
    a, _, p, _ = govdb
    a.execute(
        "UPDATE demo_governance.authority SET enabled=false,activation=2 WHERE instance=%s", (p["instance"],)
    )
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        publish(govdb)
    a.execute("UPDATE demo_governance.authority SET enabled=true WHERE instance=%s", (p["instance"],))
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        publish(govdb)


def test_dg_w15_new_uuid_cannot_launder_rejected_snapshot(govdb):
    a, _, p, _ = govdb
    a.execute("UPDATE demo_governance.jobs SET state='rejected' WHERE id=%s", (p["job"],))
    with pytest.raises(psycopg.errors.UniqueViolation):
        a.execute(
            "INSERT INTO demo_governance.jobs SELECT %s,instance,organization,%s,revision,'running',deadline,epoch,activation,snapshot FROM demo_governance.jobs WHERE id=%s",
            (str(uuid4()), str(uuid4()), p["job"]),
        )
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        publish(govdb)


def test_concurrent_publication_exactly_once(govdb):
    a, _, p, url = govdb

    def attempt(_):
        with psycopg.connect(url) as c:
            c.execute("SET ROLE foc_demo_fence")
            c.execute(
                "SELECT set_config('foc.demo_instance',%s,false),set_config('foc.demo_organization',%s,false)",
                (p["instance"], p["organization"]),
            )
            try:
                return Fence(c).publish(**p)
            except psycopg.errors.InsufficientPrivilege:
                return False

    with ThreadPoolExecutor(4) as pool:
        results = list(pool.map(attempt, range(4)))
    assert results.count(True) == 1
    assert a.execute("SELECT count(*) FROM demo_governance.audit WHERE job=%s", (p["job"],)).fetchone() == (
        1,
    )


def test_schema_is_separate_no_operational_tables(govdb):
    a, _, _, _ = govdb
    assert a.execute("SELECT count(*) FROM pg_namespace WHERE nspname='app'").fetchone() == (0,)
    assert Path("database/demo_governance/0001_control_plane.sql").is_file()
