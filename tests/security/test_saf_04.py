def test_tc_saf_04_disabled_p1(client):
    response = client.post(
        "/v1/staff/cases/00000000-0000-4000-8000-000000000001/matching-runs",
        json={"override": True},
        headers={"Authorization": "Bearer forged-synthetic"},
    )
    assert response.status_code == 503
    assert response.json()["code"] == "PHASE_DISABLED"
