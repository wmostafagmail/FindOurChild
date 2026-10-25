import httpx
from foc_api.research.pipeline import capabilities

from tests.identity.helpers import real_login

ORIGIN = "https://127.0.0.1:3443"


def test_real_authenticated_capabilities_and_revoked_session():
    client, headers = real_login()
    try:
        r = client.get(ORIGIN + "/identity/research-capabilities", headers=headers)
        assert r.status_code == 200 and r.json() == capabilities()
        assert r.headers["cache-control"] == "no-store"
        assert client.post(ORIGIN + "/identity/logout", headers=headers).status_code == 200
        assert client.get(ORIGIN + "/identity/research-capabilities", headers=headers).status_code == 401
    finally:
        client.close()


def test_real_bff_denies_unauthenticated_research_and_activation():
    import ssl
    from pathlib import Path

    with httpx.Client(
        verify=ssl.create_default_context(cafile=str(Path(".runtime/tls/cert.pem"))), trust_env=False
    ) as client:
        assert client.get(ORIGIN + "/identity/research-capabilities").status_code == 401
        assert client.post(ORIGIN + "/v1/research/activate", json={"approved": True}).status_code == 404
