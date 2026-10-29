"""Versioned result provenance. Future model contracts are descriptive, never executable."""

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import Field, model_validator

from .identity import Closed


class CaptureInterval(Closed):
    lower: date | None
    upper: date | None
    precision: Literal["interval", "day", "unknown"]

    @model_validator(mode="after")
    def coherent(self):
        if (self.lower is None) != (self.upper is None) or (self.lower is None) != (
            self.precision == "unknown"
        ):
            raise ValueError("incomplete capture interval")
        if self.lower is not None and (
            self.lower > self.upper or self.precision == "day" and self.lower != self.upper
        ):
            raise ValueError("inverted capture interval")
        return self


class AgeInterval(Closed):
    lower: int | None = Field(ge=0, le=240)
    upper: int | None = Field(ge=0, le=240)
    knowledge: Literal["estimated", "known", "unknown"]

    @model_validator(mode="after")
    def coherent(self):
        if (
            (self.lower is None) != (self.upper is None)
            or (self.lower is None) != (self.knowledge == "unknown")
            or self.lower is not None
            and self.lower > self.upper
        ):
            raise ValueError("incomplete age interval")
        return self


class ReferenceInterval(Closed):
    lower: date | None
    upper: date | None

    @model_validator(mode="after")
    def coherent(self):
        if (self.lower is None) != (self.upper is None) or self.lower is not None and self.lower > self.upper:
            raise ValueError("incomplete reference interval")
        return self


class PhotoDTO(Closed):
    id: UUID
    case_id: UUID
    side: Literal["query", "candidate"]
    source_kind: Literal["procedural_fixture"]
    synthetic: Literal[True]
    capture_date: CaptureInterval
    capture_age_months: AgeInterval
    age_reference: ReferenceInterval
    quality: Literal["face_quality_not_measured"]


class FixtureScore(Closed):
    metric: Literal["scripted_ordinal"]
    value: None
    semantics: Literal["fixture_order_only_not_identity_probability"]


class FixtureSource(Closed):
    kind: Literal["fixture_scenario"]
    provider_version: Literal["fixture-scenario-v1"]
    model_version: None
    embedding_space_id: None
    score: FixtureScore
    photo_refs: list[UUID] = Field(max_length=6)
    provenance: Literal["closed_procedural_fixture"]
    policy_version: Literal["synthetic-2d-v1"]
    calibration_status: Literal["not_applicable_synthetic_demo"]


class FutureModelSource(Closed):
    """Phase 2E compatibility specification ONLY; no current route/provider accepts it."""

    kind: Literal["licensed_demo_model"]
    model_version: str = Field(min_length=1, max_length=100)
    embedding_space_id: str = Field(pattern=r"^[a-f0-9]{64}$")
    weight_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    detector_version: str = Field(min_length=1, max_length=100)
    alignment_version: str = Field(min_length=1, max_length=100)
    preprocessing_version: str = Field(min_length=1, max_length=100)
    photo_refs: list[UUID] = Field(min_length=2, max_length=6)
    embedding_dimension: Literal[128, 512]
    normalization: Literal["unit_l2"]
    raw_score: float = Field(allow_inf_nan=False)
    aggregation_version: str = Field(min_length=1, max_length=100)
    pair_scores: list["FuturePhotoScore"] = Field(min_length=1, max_length=9)
    metric: Literal["cosine_similarity", "euclidean_distance"]
    score_semantics: Literal["raw_similarity_not_identity_probability"]
    acquisition_authorization_ref: UUID
    dataset_authorization_ref: UUID
    operational_activation: Literal[False]


class FuturePhotoScore(Closed):
    query_photo_id: UUID
    candidate_photo_id: UUID
    metric: Literal["cosine_similarity", "euclidean_distance"]
    value: float = Field(allow_inf_nan=False)
    model_version: str = Field(min_length=1, max_length=100)
    embedding_space_id: str = Field(pattern=r"^[a-f0-9]{64}$")


class ExplanationDTO(Closed):
    code: Literal["SUPPORTING_FIXTURE_CLAIM", "CONTRADICTORY_FIXTURE_CLAIM", "CAPTURE_DATE_UNCERTAIN"]
    case_id: UUID
    source_ref: UUID
    kind: Literal["supporting", "contradictory", "uncertain"]


class SnapshotDTO(Closed):
    lead_id: UUID
    revision: int = Field(ge=1)
    snapshot_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    data_class: Literal["synthetic"]
    identity_determination: Literal["not_performed"]
    review_state: Literal["pending", "held", "rejected", "escalated"]
    investigation_state: Literal[
        "open",
        "awaiting_independent_review",
        "returned_for_evidence",
        "workflow_reviewed",
        "closed_without_conclusion",
    ]
    usability: Literal["current"]


class ComparisonDTO(SnapshotDTO):
    query_case_id: UUID
    candidate_case_id: UUID
    query_registry: Literal["missing", "found"]
    candidate_registry: Literal["missing", "found"]
    result_source: FixtureSource
    photos: list[PhotoDTO] = Field(max_length=6)
    explanations: list[ExplanationDTO] = Field(max_length=20)
    prior_reviews: list["PriorReviewDTO"] = Field(max_length=20)


class PriorReviewDTO(Closed):
    event_id: UUID
    outcome: Literal["hold", "reject", "escalate"]
    rationale_codes: list[str]
    occurred_at: datetime
    same_snapshot: bool


class ColleagueDTO(Closed):
    id: UUID
    role: Literal["reviewer", "safeguarding"]


class ScenarioDTO(Closed):
    id: UUID
    version: Literal["fixture-2d-v1"]
    query_case_id: UUID
    case_revision: str = Field(pattern=r"^[1-9][0-9]*$")
    colleagues: list[ColleagueDTO]


class StatusDTO(Closed):
    data_class: Literal["synthetic"]
    provider: Literal["fixture-scenario-v1"]
    operational_activation: Literal[False]
    scenarios: list[ScenarioDTO]


class LeadDTO(Closed):
    id: UUID
    revision: int = Field(ge=1)
    visible_rank: int = Field(ge=1)
    review_state: str
    investigation_state: str
    run_id: UUID
    data_class: Literal["synthetic"]


class LeadPageDTO(Closed):
    items: list[LeadDTO]
    next_cursor: str | None


class TaskDTO(Closed):
    id: UUID
    target: UUID
    expires_at: datetime
    state: Literal["pending", "completed", "cancelled"]
