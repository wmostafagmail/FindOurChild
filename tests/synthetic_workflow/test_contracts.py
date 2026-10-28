from uuid import uuid4

import pytest
from fastapi import HTTPException
from foc_api.synthetic_contracts import AgeInterval, CaptureInterval, FixtureSource, ReferenceInterval
from foc_api.synthetic_workflow import EvidenceCommand, ReviewCommand, page, revision
from pydantic import ValidationError


@pytest.mark.parametrize(
    "bounds",
    [
        {"lower": None, "upper": "2018-12-31", "precision": "interval"},
        {"lower": "2019-01-01", "upper": "2018-12-31", "precision": "interval"},
        {"lower": "2018-01-01", "upper": "2018-12-31", "precision": "day"},
        {"lower": "2018-01-01", "upper": "2018-12-31", "precision": "unknown"},
    ],
)
def test_capture_bounds_reject_incomplete_inverted_or_false_precision(bounds):
    with pytest.raises(ValidationError):
        CaptureInterval.model_validate(bounds)


@pytest.mark.parametrize(
    "bounds",
    [
        {"lower": None, "upper": 24, "knowledge": "estimated"},
        {"lower": 30, "upper": 24, "knowledge": "estimated"},
        {"lower": -1, "upper": 24, "knowledge": "estimated"},
        {"lower": 0, "upper": 0, "knowledge": "unknown"},
    ],
)
def test_age_bounds_reject_inferred_zero_and_incoherence(bounds):
    with pytest.raises(ValidationError):
        AgeInterval.model_validate(bounds)


def test_unknowns_are_null_and_reference_dates_are_not_capture_age_inference():
    assert CaptureInterval(lower=None, upper=None, precision="unknown").lower is None
    assert AgeInterval(lower=None, upper=None, knowledge="unknown").lower is None
    with pytest.raises(ValidationError):
        ReferenceInterval(lower="2018-01-01", upper=None)


@pytest.mark.parametrize(
    "extra", ["model_url", "custody", "text", "photograph", "automatic_identity_confirmation"]
)
def test_closed_review_input_cannot_admit_data_or_activation(extra):
    data = {
        "snapshot_hash": "a" * 64,
        "uncertainty_acknowledged": True,
        "rationale_codes": ["SYNTHETIC_WORKFLOW_ONLY"],
        "evidence_refs": [],
        "outcome": "hold",
        extra: "SYNTHETIC_SECRET_CANARY",
    }
    with pytest.raises(ValidationError):
        ReviewCommand.model_validate(data)


def test_future_model_source_is_not_accepted_as_fixture_provenance():
    with pytest.raises(ValidationError):
        FixtureSource.model_validate({"kind": "licensed_demo_model", "model_version": "uncleared"})


@pytest.mark.parametrize(
    "value", ["1", '"0"', '"-1"', '"1.5"', '"9223372036854775808"', '"nan"', '"<script>"']
)
def test_strong_revision_header_is_bounded(value):
    with pytest.raises(HTTPException):
        revision(value)


def test_cursor_is_authenticated_expiring_actor_scoped_and_detects_changes():
    items = [{"id": str(uuid4())} for _ in range(3)]
    scope = ["actor", "org", "query", "leads"]
    first = page(items, None, scope, 1)
    cursor = first["next_cursor"]
    assert cursor
    assert page(items, cursor, scope, 1)["items"] == [items[1]]
    for altered in [cursor + "x", "forged"]:
        with pytest.raises(HTTPException):
            page(items, altered, scope, 1)
    with pytest.raises(HTTPException):
        page(items, cursor, ["other", *scope[1:]], 1)
    with pytest.raises(HTTPException):
        page(items[:2], cursor, scope, 1)
    for limit in [0, 51]:
        with pytest.raises(HTTPException):
            page(items, None, scope, limit)


def test_structured_collaboration_has_no_free_form_channel():
    with pytest.raises(ValidationError):
        EvidenceCommand.model_validate(
            {
                "snapshot_hash": "a" * 64,
                "uncertainty_acknowledged": True,
                "rationale_codes": ["SYNTHETIC_WORKFLOW_ONLY"],
                "evidence_refs": [],
                "note": "fictional but unbounded text",
            }
        )


def test_api_capacity_publication_denies_private_stale_and_incomplete_evidence():
    import copy

    from scripts.artifacts import http_capacity_record

    source = "1" * 64
    value = {"source_digest": source, "scope": "actual_synthetic_tls_bff_api_metadata",
             "sessions": 20, "queries": 100, "candidates_per_query": 50, "requests": 200,
             "failed_requests": 0, "model_inference": False, "status": "measured",
             "host_logical_cpus": 4, "host_memory_bytes": 16 * 1024**3, "host_architecture": "x86_64"}
    for name, target in [("queue", 1000), ("comparison", 1500)]:
        value[name] = {"samples": 100, "p50_ms": 500, "p95_ms": 1100, "p99_ms": 1700,
                       "planning_target_ms": target, "planning_target_met": 1100 <= target}
    published = http_capacity_record(value, source)
    assert "source_digest" not in published and published["queue"]["planning_target_met"] is False
    assert published["comparison"]["planning_target_met"] is True
    changes = [{"cookie": "SYNTHETIC_SECRET_CANARY"}, {"source_digest": "stale"},
               {"requests": 199}, {"failed_requests": 1}, {"model_inference": 0}, {"host_architecture": "private-hostname"},
               {"host_logical_cpus": True}, {"queue": {**value["queue"], "p95_ms": float("nan")}},
               {"queue": {**value["queue"], "planning_target_met": True}}]
    for change in changes:
        candidate = copy.deepcopy(value)
        candidate.update(change)
        with pytest.raises((ValueError, TypeError)):
            http_capacity_record(candidate, source)
