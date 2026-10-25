import dataclasses
import hashlib
import math
import socket

import pytest
from fastapi.testclient import TestClient
from foc_api.main import create_app
from foc_api.research.pipeline import (
    SYNTHETIC_SPACE,
    QualificationError,
    Space,
    SyntheticAdapter,
    capabilities,
    fixture,
    load_recognition_backend,
    validate_vector,
)


def test_procedural_pipeline_has_complete_stage_provenance():
    adapter = SyntheticAdapter()
    data = fixture(7)
    assert adapter.detect(data).value == ((8, 8, 24, 24),)
    aligned = adapter.align(data, (8, 8, 24, 24), subject_approved=True)
    quality = adapter.quality(data)
    embedded = adapter.embed(data, subject_approved=True)
    for stage in [aligned, quality, embedded]:
        assert stage.schema_version == "stage-1"
        assert stage.input_sha256 == hashlib.sha256(data).hexdigest()
        assert stage.warnings == ("synthetic_only_not_face_recognition",)
    assert quality.value["face_quality"] == "not_measured"
    assert len(embedded.value["vector"]) == 128
    assert embedded.value["space_id"] == SYNTHETIC_SPACE.id
    assert adapter.embed(data, subject_approved=True) == embedded


@pytest.mark.parametrize("data", [b"", b"not-an-image", b"x" * 5000])
def test_unapproved_bytes_are_rejected(data):
    with pytest.raises(QualificationError):
        SyntheticAdapter().embed(data, subject_approved=True)


@pytest.mark.parametrize("approval", [False, None, 1, "approved"])
def test_sensitive_subject_selection_fails_closed(approval):
    with pytest.raises(QualificationError):
        SyntheticAdapter().embed(fixture(1), subject_approved=approval)


def test_unknown_region_cannot_silently_align():
    with pytest.raises(QualificationError):
        SyntheticAdapter().align(fixture(1), (0, 0, 1, 1), subject_approved=True)


@pytest.mark.parametrize("index", [-1, 32, True, "1"])
def test_fixture_factory_is_bounded(index):
    with pytest.raises(QualificationError):
        fixture(index)


@pytest.mark.parametrize(
    "value",
    [
        [0.0] * 128,
        [1.0] * 127,
        [float("nan")] + [0.0] * 127,
        [float("inf")] + [0.0] * 127,
        [True] + [0.0] * 127,
    ],
)
def test_invalid_embeddings_are_rejected(value):
    with pytest.raises(QualificationError):
        validate_vector(value)


@pytest.mark.parametrize(
    "field",
    [
        "code_revision",
        "detector_version",
        "alignment_version",
        "quality_version",
        "preprocessing_version",
        "schema_version",
        "weights_sha256",
    ],
)
def test_equal_dimensions_do_not_imply_compatible_spaces(field):
    replacement = "0" * 64 if field == "weights_sha256" else "changed-v2"
    assert dataclasses.replace(SYNTHETIC_SPACE, **{field: replacement}).id != SYNTHETIC_SPACE.id


@pytest.mark.parametrize(
    "kwargs",
    [
        {"dimension": 512},
        {"metric": "l2"},
        {"data_class": "real"},
        {"normalization": "none"},
        {"weights_sha256": "x" * 64},
        {"code_revision": ""},
    ],
)
def test_unqualified_space_is_rejected(kwargs):
    with pytest.raises(QualificationError):
        Space(**{**dataclasses.asdict(SYNTHETIC_SPACE), **kwargs})


def test_operational_model_loading_cannot_be_activated(monkeypatch):
    for name in ["FOC_AI_ENABLED", "FOC_MODEL_APPROVED", "FOC_PUBLIC_BIOMETRIC_SEARCH", "FOC_MODEL_PATH"]:
        monkeypatch.setenv(name, "true")
    for source in ["https://synthetic.invalid/model.onnx", "/tmp/model.pkl", {"approved": True}]:
        with pytest.raises(QualificationError):
            load_recognition_backend(source)
    assert capabilities()["operational_activation"] is False


def test_pipeline_has_no_network_dependency(monkeypatch):
    def reject(*args, **kwargs):
        raise AssertionError("network forbidden")

    monkeypatch.setattr(socket, "create_connection", reject)
    assert math.isclose(
        sum(x * x for x in SyntheticAdapter().embed(fixture(3), subject_approved=True).value["vector"]), 1
    )


@pytest.mark.parametrize(
    "headers", [{}, {"Authorization": "Bearer forged"}, {"Cookie": "__Host-foc-session=forged"}]
)
def test_capability_api_rejects_unauthorized_access(headers):
    with TestClient(create_app()) as client:
        response = client.get("/identity/research-capabilities", headers=headers)
        assert response.status_code == 401
        assert "vector" not in response.text and "forged" not in response.text


@pytest.mark.parametrize(
    "path",
    ["/v1/public/biometric-search", "/v1/research/activate", "/v1/custody/disclose", "/v1/identity/confirm"],
)
def test_operational_routes_remain_disabled(path):
    with TestClient(create_app()) as client:
        assert client.post(path, json={"approved": True, "synthetic": False}).status_code == 503
