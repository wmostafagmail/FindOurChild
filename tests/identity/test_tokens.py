"""Cryptographic negative unit cases. Network double here is not IdP integration evidence."""

import json
import time
from unittest.mock import Mock

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from foc_api import identity


@pytest.fixture
def signed(monkeypatch):
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private.public_key()))
    public.update(kid="synthetic-key", use="sig")
    monkeypatch.setattr(identity, "idp", lambda *args, **kwargs: {"keys": [public]})
    claims = {
        "iss": identity.configuration()["issuer"],
        "aud": "foc-api",
        "sub": "synthetic-subject",
        "azp": "foc-bff",
        "exp": int(time.time()) + 300,
        "iat": int(time.time()),
        "auth_time": int(time.time()),
        "amr": ["pwd", "otp"],
    }
    return private, claims


def test_valid_signed_mfa(signed):
    private, claims = signed
    token = jwt.encode(claims, private, algorithm="RS256", headers={"kid": "synthetic-key"})
    assert identity.validate_token(token)["sub"] == "synthetic-subject"


@pytest.mark.parametrize(
    "change",
    [
        {"iss": "https://evil.invalid"},
        {"aud": "other-api"},
        {"azp": "other-client"},
        {"exp": 1},
        {"iat": 9999999999},
        {"auth_time": 1},
        {"auth_time": 9999999999},
        {"amr": ["pwd"]},
        {"amr": []},
        {"amr": None},
        {"sub": None},
    ],
)
def test_invalid_signed_claims_rejected(signed, change):
    private, claims = signed
    token = jwt.encode({**claims, **change}, private, algorithm="RS256", headers={"kid": "synthetic-key"})
    with pytest.raises(HTTPException) as error:
        identity.validate_token(token)
    assert error.value.status_code == 401


@pytest.mark.parametrize("missing", ["exp", "iat", "sub", "iss", "aud", "auth_time", "amr"])
def test_missing_required_claim(signed, missing):
    private, claims = signed
    del claims[missing]
    token = jwt.encode(claims, private, algorithm="RS256", headers={"kid": "synthetic-key"})
    with pytest.raises(HTTPException):
        identity.validate_token(token)


def test_wrong_signature_and_unknown_key(signed):
    private, claims = signed
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    for key, kid in [(other, "synthetic-key"), (private, "unknown")]:
        token = jwt.encode(claims, key, algorithm="RS256", headers={"kid": kid})
        with pytest.raises(HTTPException):
            identity.validate_token(token)


@pytest.mark.parametrize(
    "token",
    [
        "invalid",
        "",
        jwt.encode({"sub": "forged"}, "synthetic-secret-which-is-long-enough", algorithm="HS256"),
        jwt.encode({"sub": "forged"}, key="", algorithm="none"),
    ],
    ids=["malformed", "empty", "hmac-confusion", "unsigned"],
)
def test_algorithm_confusion_and_malformed_tokens(token):
    with pytest.raises(HTTPException):
        identity.validate_token(token)


def test_nonce_bound_to_flow(signed):
    private, claims = signed
    token = jwt.encode(
        {**claims, "aud": "foc-bff", "nonce": "expected"},
        private,
        algorithm="RS256",
        headers={"kid": "synthetic-key"},
    )
    assert identity.validate_token(token, "foc-bff", "expected")
    with pytest.raises(HTTPException):
        identity.validate_token(token, "foc-bff", "wrong")


@pytest.mark.parametrize("origin", ["https://evil.invalid", "null", "", None])
def test_csrf_origin_fail_closed(origin):
    request = Mock(headers={} if origin is None else {"origin": origin, "x-csrf-token": "correct"})
    with pytest.raises(HTTPException) as error:
        identity.mutation_guard(request, identity.digest("correct"))
    assert error.value.status_code == 403


@pytest.mark.parametrize("failure", ["unreachable", "invalid-json", "error-status"])
def test_idp_failure_denies_access(monkeypatch, failure):
    response = Mock()
    if failure == "invalid-json":
        response.json.side_effect = ValueError()
    elif failure == "error-status":
        response.raise_for_status.side_effect = httpx.HTTPError("synthetic")
    fake = Mock()
    if failure == "unreachable":
        fake.get.side_effect = httpx.ConnectError("synthetic")
    else:
        fake.get.return_value = response
    context = Mock()
    context.__enter__ = Mock(return_value=fake)
    context.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: context)
    with pytest.raises(HTTPException) as error:
        identity.idp("/protocol/openid-connect/certs")
    assert error.value.status_code == 503
