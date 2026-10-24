import json

import pytest

from tests.conftest import ROOT

CONTRACT = json.loads((ROOT / "docs/contracts/openapi.json").read_text())
OPERATIONS = [
    (method, path) for path, item in CONTRACT["paths"].items() for method in item if path.startswith("/v1/")
]


@pytest.mark.parametrize("method,path", OPERATIONS, ids=[f"fnd_disabled_{i:02}" for i in range(1, 33)])
@pytest.mark.parametrize("credential", [None, "Bearer forged-synthetic-token"], ids=["anonymous", "forged"])
def test_fnd_domain_operations_fail_closed(client, method, path, credential):
    headers = {"Authorization": credential} if credential else {}
    response = client.request(
        method,
        path.replace("{id}", "00000000-0000-4000-8000-000000000001"),
        headers=headers,
        json={"secret": "SYNTHETIC_SECRET_CANARY"},
    )
    assert response.status_code == 503
    assert response.json()["code"] == "PHASE_DISABLED"
    assert set(response.json()) == {"code", "message_key", "request_id"}
    assert "CANARY" not in response.text
