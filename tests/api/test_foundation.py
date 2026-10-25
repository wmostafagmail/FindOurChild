import json
from uuid import UUID

from fastapi.testclient import TestClient
from foc_api.config import Settings
from foc_api.main import create_app
from jsonschema import Draft202012Validator, FormatChecker
from openapi_spec_validator import validate

from tests.conftest import ROOT

CONTRACT = json.loads((ROOT / "docs/contracts/openapi.json").read_text())


def test_fnd_live(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive", "service": "find-our-child-api", "phase": "1A"}


def test_fnd_real_database_readiness(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["data_class"] == "synthetic"
    assert (
        response.json()["instance_id"]
        == json.loads((ROOT / ".runtime/instance.json").read_text())["instance_id"]
    )


def test_fnd_unavailable_database_fails_safely():
    with TestClient(create_app(Settings("postgresql://foc_api@127.0.0.1:1/foc_synthetic"))) as client:
        response = client.get("/health/ready")
        assert response.status_code == 503
        assert response.json() == {"status": "unavailable"}
        assert "postgresql" not in response.text


def test_fnd_full_openapi(client):
    validate(CONTRACT)
    assert sum(len(v) for v in CONTRACT["paths"].values()) == 49
    assert client.get("/openapi.json").json() == CONTRACT
    assert len({o["operationId"] for p in CONTRACT["paths"].values() for o in p.values()}) == 49


def test_fnd_closed_report_schema():
    schema = {"$ref": "#/components/schemas/MissingReport", "components": CONTRACT["components"]}
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    invalid = {"names": [], "child_location": "SYNTHETIC_SECRET_CANARY"}
    assert list(validator.iter_errors(invalid))


def test_fnd_security_headers_and_request_id(client):
    response = client.get("/health/live", headers={"X-Request-ID": "SYNTHETIC_SECRET_CANARY"})
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["x-content-type-options"] == "nosniff"
    UUID(response.headers["x-request-id"])
    assert "CANARY" not in str(response.headers)
