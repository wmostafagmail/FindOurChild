import hashlib
import json
import os

from jsonschema import Draft202012Validator

from scripts.migrate import migrate
from tests.conftest import ROOT


def test_fnd_migration_replay_and_checksum(db):
    migrate(os.environ["FOC_DATABASE_ADMIN_URL"])
    expected = hashlib.sha256((ROOT / "database/migrations/0001_foundation.sql").read_bytes()).hexdigest()
    assert (
        db["admin"]
        .execute("SELECT sha256 FROM platform.migrations WHERE version='0001_foundation'")
        .fetchone()[0]
        == expected
    )
    assert (
        db["admin"].execute("SELECT extversion FROM pg_extension WHERE extname='vector'").fetchone()[0]
        == "0.8.7"
    )


def test_fnd_event_envelope_rejects_child_payload():
    schema = json.loads((ROOT / "docs/contracts/event-envelope.schema.json").read_text())
    validator = Draft202012Validator(schema)
    event = {
        "schema_version": "1",
        "event_id": "00000000-0000-4000-8000-000000000001",
        "event_type": "media.ready",
        "organization_id": "00000000-0000-4000-8000-000000000002",
        "aggregate_type": "photograph",
        "aggregate_id": "00000000-0000-4000-8000-000000000003",
        "aggregate_revision": 1,
        "occurred_at": "2026-10-24T00:00:00Z",
        "correlation_id": "00000000-0000-4000-8000-000000000004",
        "policy_version": "synthetic-v1",
        "deletion_generation": 0,
    }
    assert not list(validator.iter_errors(event))
    assert list(validator.iter_errors({**event, "child_name": "SYNTHETIC_SECRET_CANARY"}))
    assert list(validator.iter_errors({**event, "schema_version": "2"}))
