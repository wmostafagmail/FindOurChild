import json
from uuid import uuid4

import psycopg
import pytest
from jsonschema import Draft202012Validator, FormatChecker

from tests.conftest import ROOT


def test_fnd_idempotency_scoped_uniqueness_and_default_deny(db):
    admin = db["admin"]
    key = uuid4()
    scope = b"s" * 32
    digest = b"d" * 32
    statement = "INSERT INTO app.idempotency_records(organization_id,principal_scope_hash,operation,idempotency_key,request_sha256,state,expires_at) VALUES(%s,%s,'synthetic.operation',%s,%s,'pending',now()+interval '1 hour')"
    admin.execute(statement, (db["org_a"], scope, key, digest))
    with pytest.raises(psycopg.errors.UniqueViolation):
        admin.execute(statement, (db["org_a"], scope, key, digest))
    admin.execute(statement, (db["org_b"], scope, key, digest))
    assert (
        admin.execute(
            "SELECT count(*) FROM app.idempotency_records WHERE idempotency_key=%s", (key,)
        ).fetchone()[0]
        == 2
    )
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        db["runtime"].execute("SELECT * FROM app.idempotency_records")
    db["runtime"].rollback()


def test_fnd_same_tenant_wrong_case_object_rejected(db):
    obj = uuid4()
    db["admin"].execute(
        "INSERT INTO app.objects(organization_id,id,case_id,bucket_class,opaque_key,object_version,content_sha256,bytes,detected_mime,encryption_key_ref) VALUES(%s,%s,%s,'quarantine',gen_random_uuid(),'synthetic-version',%s,1,'image/png','synthetic-key-reference')",
        (db["org_a"], obj, db["case_a"], b"h" * 32),
    )
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        db["admin"].execute(
            "INSERT INTO app.evidence_documents(organization_id,case_id,object_id,type,content_sha256) VALUES(%s,%s,%s,'synthetic',%s)",
            (db["org_a"], db["case_ungranted"], obj, b"h" * 32),
        )


def test_fnd_outbox_reconstructs_closed_envelope(db):
    event = uuid4()
    db["admin"].execute(
        "INSERT INTO app.outbox_events(organization_id,id,case_id,type,schema_version,aggregate_id,aggregate_revision,dedup_key) VALUES(%s,%s,%s,'report.submitted',1,%s,1,gen_random_uuid())",
        (db["org_a"], event, db["case_a"], db["case_a"]),
    )
    value = (
        db["admin"]
        .execute(
            "SELECT json_build_object('schema_version',schema_version::text,'event_id',id,'event_type',type,'organization_id',organization_id,'aggregate_type',aggregate_type,'aggregate_id',aggregate_id,'aggregate_revision',aggregate_revision,'occurred_at',occurred_at,'correlation_id',correlation_id,'policy_version',policy_version,'deletion_generation',deletion_generation) FROM app.outbox_events WHERE organization_id=%s AND id=%s",
            (db["org_a"], event),
        )
        .fetchone()[0]
    )
    Draft202012Validator(
        json.loads((ROOT / "docs/contracts/event-envelope.schema.json").read_text()),
        format_checker=FormatChecker(),
    ).validate(value)
    with pytest.raises(psycopg.errors.CheckViolation):
        db["admin"].execute(
            "UPDATE app.outbox_events SET type='unknown.payload' WHERE organization_id=%s AND id=%s",
            (db["org_a"], event),
        )
