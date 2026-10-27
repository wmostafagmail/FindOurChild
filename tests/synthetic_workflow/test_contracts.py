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
