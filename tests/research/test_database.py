import hashlib
import os
from uuid import uuid4

import psycopg
import pytest
from foc_api.research.pipeline import SYNTHETIC_SPACE


def vec(index):
    return "[" + ",".join("1" if i == index else "0" for i in range(128)) + "]"


@pytest.fixture
def research_db(db):
    admin = db["admin"]
    org = db["org_a"]
    principal = db["principal_a"]
    ds = uuid4()
    probe = uuid4()
    gallery = uuid4()
    case = uuid4()
    admin.execute(
        "INSERT INTO platform.research_grants VALUES(%s,%s,'synthetic-2a-v1',now()+interval '1 hour',NULL)",
        (org, principal),
    )
    admin.execute(
        "INSERT INTO platform.research_datasets VALUES(%s,%s,true,'synthetic-2a-v1',now()+interval '1 hour',1,NULL)",
        (org, ds),
    )
    for photo, role, registry in [(probe, "probe", "missing"), (gallery, "gallery", "found")]:
        admin.execute(
            "INSERT INTO platform.research_photographs(organization_id,dataset_id,generation,id,case_ref,subject_ref,family_ref,image_sha256,registry,partition,role,capture_precision,source,synthetic) VALUES(%s,%s,1,%s,%s,%s,%s,%s,%s,'test',%s,'unknown','procedural-geometric-fixture-v1',true)",
            (
                org,
                ds,
                photo,
                case if role == "gallery" else uuid4(),
                principal,
                principal,
                hashlib.sha256(photo.bytes).hexdigest(),
                registry,
                role,
            ),
        )
        admin.execute(
            "INSERT INTO platform.research_vectors_synthetic_v1(organization_id,dataset_id,photo_id,space_id,vector,source_revision) VALUES(%s,%s,%s,%s,%s::public.vector,1)",
            (org, ds, photo, SYNTHETIC_SPACE.id, vec(0)),
        )
    with psycopg.connect(os.environ["FOC_DATABASE_ADMIN_URL"]) as conn:

        def context(purpose="research_evaluation", tenant=None):
            conn.execute("SET LOCAL ROLE foc_research")
            for key, value in [
                ("organization", tenant or org),
                ("principal", principal),
                ("purpose", purpose),
            ]:
                conn.execute("SELECT set_config(%s,%s,true)", ("foc." + key, str(value)))
            return conn

        yield {
            "conn": conn,
            "context": context,
            "admin": admin,
            "org": org,
            "ds": ds,
            "probe": probe,
            "gallery": gallery,
            "case": case,
            "principal": principal,
            "runtime": db["runtime"],
        }
        conn.rollback()
    admin.execute("DELETE FROM platform.research_datasets WHERE organization_id=%s", (org,))
    admin.execute("DELETE FROM platform.research_grants WHERE organization_id=%s", (org,))


def search(r, conn=None):
    return (
        (conn or r["context"]())
        .execute(
            "SELECT * FROM platform.research_exact_candidates(%s,%s,%s,10)", (r["org"], r["ds"], r["probe"])
        )
        .fetchall()
    )


def test_exact_pgvector_retrieval_and_unknown_per_photo_metadata(research_db):
    r = research_db
    assert search(r) == [(r["case"], 1.0)]
    rows = (
        r["conn"]
        .execute(
            "SELECT capture_lower,capture_upper,age_min_months,age_max_months FROM platform.research_photographs ORDER BY id"
        )
        .fetchall()
    )
    assert rows == [(None, None, None, None)] * 2


@pytest.mark.parametrize(
    "target",
    ["research_grants", "research_datasets", "research_photographs", "research_vectors_synthetic_v1"],
)
def test_app_runtime_has_no_research_access(research_db, target):
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        research_db["runtime"].execute("SELECT * FROM platform." + target)
    research_db["runtime"].rollback()


def test_app_runtime_cannot_become_research_role(research_db):
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        research_db["runtime"].execute("SET ROLE foc_research")
    research_db["runtime"].rollback()


@pytest.mark.parametrize(
    "table",
    [
        "app.photographs",
        "app.embeddings",
        "app.restricted_custody",
        "platform.upload_metadata",
        "platform.research_grants",
    ],
)
def test_research_cannot_access_operational_or_approval_data(research_db, table):
    conn = research_db["context"]()
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        conn.execute("SELECT * FROM " + table)


def test_missing_context_and_cross_organization_are_empty(research_db):
    r = research_db
    conn = r["conn"]
    conn.execute("SET LOCAL ROLE foc_research")
    assert search(r, conn) == []
    conn.rollback()
    assert search(r, r["context"](tenant=uuid4())) == []
    conn.rollback()
    assert search(r, r["context"](purpose="biometric_search")) == []


@pytest.mark.parametrize(
    "mutation",
    [
        "UPDATE platform.research_grants SET revoked_at=now() WHERE organization_id=%s",
        "UPDATE platform.research_grants SET expires_at=now()-interval '1 second' WHERE organization_id=%s",
        "UPDATE platform.research_datasets SET revoked_at=now() WHERE organization_id=%s",
        "UPDATE platform.research_datasets SET expires_at=now()-interval '1 second' WHERE organization_id=%s",
    ],
)
def test_expired_revoked_authorization_or_data_invalidates_retrieval(research_db, mutation):
    r = research_db
    assert search(r)
    r["conn"].rollback()
    r["admin"].execute(mutation, (r["org"],))
    assert search(r) == []


def test_deletion_cleans_exact_vector_index_and_prevents_stale_write(research_db):
    r = research_db
    assert search(r)
    r["conn"].rollback()
    r["admin"].execute(
        "DELETE FROM platform.research_photographs WHERE organization_id=%s AND id=%s",
        (r["org"], r["gallery"]),
    )
    assert search(r) == []
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        r["conn"].execute(
            "INSERT INTO platform.research_vectors_synthetic_v1 VALUES(%s,%s,%s,%s,%s::public.vector,1,now())",
            (r["org"], r["ds"], r["gallery"], SYNTHETIC_SPACE.id, vec(0)),
        )


@pytest.mark.parametrize(
    "space,vector,revision",
    [
        ("wrong", vec(0), 1),
        (SYNTHETIC_SPACE.id, "[1,0]", 1),
        (SYNTHETIC_SPACE.id, "[" + ",".join(["0"] * 128) + "]", 1),
        (SYNTHETIC_SPACE.id, vec(0), 2),
    ],
)
def test_incompatible_dimension_space_normalization_revision_rejected(research_db, space, vector, revision):
    r = research_db
    conn = r["context"]()
    conn.execute("DELETE FROM platform.research_vectors_synthetic_v1 WHERE photo_id=%s", (r["gallery"],))
    with pytest.raises(psycopg.Error):
        conn.execute(
            "INSERT INTO platform.research_vectors_synthetic_v1 VALUES(%s,%s,%s,%s,%s::public.vector,%s,now())",
            (r["org"], r["ds"], r["gallery"], space, vector, revision),
        )


@pytest.mark.parametrize(
    "assignment",
    [
        "capture_lower='2021-01-01',capture_upper='2020-01-01',capture_precision='interval'",
        "age_min_months=-1,age_max_months=2",
        "synthetic=false",
        "capture_lower='2020-01-01'",
        "age_min_months=2",
    ],
)
def test_historical_photo_constraints(research_db, assignment):
    r = research_db
    with pytest.raises(psycopg.errors.CheckViolation):
        r["admin"].execute(
            "UPDATE platform.research_photographs SET " + assignment + " WHERE id=%s", (r["gallery"],)
        )


def test_every_research_table_forces_rls_and_role_is_no_login(research_db):
    r = research_db
    rows = (
        r["admin"]
        .execute(
            "SELECT relrowsecurity,relforcerowsecurity FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='platform' AND c.relname LIKE 'research_%' AND c.relkind='r'"
        )
        .fetchall()
    )
    assert len(rows) == 4 and all(x == (True, True) for x in rows)
    assert r["admin"].execute(
        "SELECT rolcanlogin,rolsuper,rolbypassrls FROM pg_roles WHERE rolname='foc_research'"
    ).fetchone() == (False, False, False)


def test_authorized_research_write_preserves_independent_photo_history(research_db):
    r = research_db
    conn = r["context"]()
    photo = uuid4()
    case = uuid4()
    conn.execute(
        "INSERT INTO platform.research_photographs(organization_id,dataset_id,generation,id,case_ref,subject_ref,family_ref,image_sha256,registry,partition,role,capture_lower,capture_upper,capture_precision,age_min_months,age_max_months,age_reference_lower,age_reference_upper,source,synthetic) VALUES(%s,%s,1,%s,%s,%s,%s,%s,'found','test','gallery','2011-01-01','2013-01-01','interval',12,36,'2011-01-01','2013-01-01','procedural-geometric-fixture-v1',true)",
        (r["org"], r["ds"], photo, case, uuid4(), uuid4(), hashlib.sha256(photo.bytes).hexdigest()),
    )
    conn.execute(
        "INSERT INTO platform.research_vectors_synthetic_v1 VALUES(%s,%s,%s,%s,%s::public.vector,1,now())",
        (r["org"], r["ds"], photo, SYNTHETIC_SPACE.id, vec(1)),
    )
    assert search(r, conn) == [(r["case"], 1.0), (case, 0.0)]
    assert conn.execute(
        "SELECT capture_lower::text,capture_upper::text,age_min_months,age_max_months FROM platform.research_photographs WHERE id=%s",
        (photo,),
    ).fetchone() == ("2011-01-01", "2013-01-01", 12, 36)
    assert conn.execute(
        "SELECT capture_lower,age_min_months FROM platform.research_photographs WHERE id=%s", (r["gallery"],)
    ).fetchone() == (None, None)


def test_cross_tenant_mutations_and_unversioned_updates_are_denied(research_db):
    r = research_db
    conn = r["context"](tenant=uuid4())
    assert (
        conn.execute("DELETE FROM platform.research_photographs WHERE id=%s", (r["gallery"],)).rowcount == 0
    )
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        conn.execute(
            "INSERT INTO platform.research_vectors_synthetic_v1 VALUES(%s,%s,%s,%s,%s::public.vector,1,now())",
            (r["org"], r["ds"], r["gallery"], SYNTHETIC_SPACE.id, vec(1)),
        )
    conn.rollback()
    conn = r["context"]()
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        conn.execute("UPDATE platform.research_vectors_synthetic_v1 SET vector=%s::public.vector", (vec(1),))


@pytest.mark.parametrize(
    "mutation",
    [
        "UPDATE app.memberships SET revoked_at=now() WHERE organization_id=%s",
        "UPDATE app.memberships SET expires_at=now()-interval '1 second' WHERE organization_id=%s",
        "UPDATE app.organizations SET suspended_at=now() WHERE id=%s",
        "UPDATE app.staff_principals SET disabled_at=now() WHERE id IN (SELECT principal_id FROM app.memberships WHERE organization_id=%s)",
    ],
)
def test_identity_revocation_also_revokes_research(research_db, mutation):
    r = research_db
    assert search(r)
    r["conn"].rollback()
    r["admin"].execute(mutation, (r["org"],))
    assert search(r) == []


def test_read_committed_rechecks_research_revocation_without_pool_reset(research_db):
    r = research_db
    conn = r["context"]()
    assert search(r, conn)
    r["admin"].execute(
        "UPDATE platform.research_grants SET revoked_at=now() WHERE organization_id=%s", (r["org"],)
    )
    assert search(r, conn) == []


def test_pgvector_matches_independent_python_exact_search_with_photo_caps(research_db):
    import math

    from foc_api.research.evaluation import Record, retrieve

    r = research_db
    conn = r["context"]()
    gallery = []
    for c in range(6):
        case = uuid4()
        for j in range(4):
            photo = uuid4()
            sha = hashlib.sha256(photo.bytes).hexdigest()
            v = [0.0] * 128
            v[0] = 1
            v[c + 1] = (c + 1) * 0.1 + j * 0.04
            norm = math.sqrt(sum(x * x for x in v))
            v = [x / norm for x in v]
            conn.execute(
                "INSERT INTO platform.research_photographs(organization_id,dataset_id,generation,id,case_ref,subject_ref,family_ref,image_sha256,registry,partition,role,capture_precision,source,synthetic) VALUES(%s,%s,1,%s,%s,%s,%s,%s,'found','test','gallery','unknown','procedural-geometric-fixture-v1',true)",
                (r["org"], r["ds"], photo, case, case, case, sha),
            )
            conn.execute(
                "INSERT INTO platform.research_vectors_synthetic_v1 VALUES(%s,%s,%s,%s,%s::public.vector,1,now())",
                (r["org"], r["ds"], photo, SYNTHETIC_SPACE.id, "[" + ",".join(map(str, v)) + "]"),
            )
            gallery.append(Record(sha, str(case), str(case), str(case), "found", "gallery", "test", tuple(v)))
    original = Record(
        hashlib.sha256(r["gallery"].bytes).hexdigest(),
        "original",
        "original",
        str(r["case"]),
        "found",
        "gallery",
        "test",
        tuple(1.0 if i == 0 else 0.0 for i in range(128)),
    )
    probe = Record(
        hashlib.sha256(r["probe"].bytes).hexdigest(),
        "probe",
        "probe",
        "probe",
        "missing",
        "probe",
        "test",
        original.vector,
    )
    expected = retrieve(probe, [original, *gallery], k=10)
    observed = search(r, conn)
    assert [str(row[0]) for row in observed] == [row["case"] for row in expected]
    assert all(abs(a[1] - b["score"]) < 1e-5 for a, b in zip(observed, expected, strict=True))
