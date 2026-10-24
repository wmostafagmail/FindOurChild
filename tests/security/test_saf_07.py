def test_tc_saf_07_disabled_p1(client):
    response = client.post(
        "/v1/staff/disclosure-requests/00000000-0000-4000-8000-000000000001/approvals",
        json={"override": True},
        headers={"Authorization": "Bearer forged-synthetic"},
    )
    assert response.status_code == 503
    assert response.json()["code"] == "PHASE_DISABLED"
