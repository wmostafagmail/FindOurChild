"""Pinned owner, strict claims and live session status. Never trusts a caller owner claim."""

from dataclasses import dataclass
from uuid import UUID

import jwt

from .records import Denied, require, sha


@dataclass(frozen=True)
class Binding:
    issuer: str
    audience: str
    subject: str
    principal: str
    public_key: bytes


@dataclass(frozen=True)
class OwnerSession:
    issuer: str
    audience: str
    subject: str
    principal: str
    authentication_event_id: str
    authenticated_at: int
    expires_at: int
    session_digest: str


def claims_session(claims, binding, session, now, live):
    require(type(claims) is dict and binding is not None and type(session) is str
            and len(session) >= 32, "owner_session")
    for key in ["auth_time", "iat", "exp"]:
        require(type(claims.get(key)) is int, "owner_claim_type")
    require(type(claims.get("amr")) is list and all(type(v) is str for v in claims["amr"])
            and {"pwd", "otp"}.issubset(claims["amr"]), "owner_mfa")
    require(claims.get("iss") == binding.issuer and claims.get("aud") == binding.audience
            and claims.get("sub") == binding.subject, "owner_binding")
    require(0 <= now - claims["auth_time"] <= 300 and claims["auth_time"] <= claims["iat"] <= now
            < claims["exp"], "owner_freshness")
    try:
        event = str(UUID(claims["sid"]))
        require(event == claims["sid"], "owner_event")
    except (ValueError, TypeError, KeyError, AttributeError):
        raise Denied("owner_event") from None
    # The privileged adapter must introspect the token AND check the local current session/account.
    require(live(binding, session) is True, "owner_live_status")
    return OwnerSession(binding.issuer, binding.audience, binding.subject, binding.principal,
                        event, claims["auth_time"], claims["exp"], sha(session.encode()))


def authenticate_token(token, binding, session, now, live):
    require(binding is not None, "owner_unprovisioned")
    try:
        require(jwt.get_unverified_header(token).get("alg") == "RS256", "owner_algorithm")
        claims = jwt.decode(token, binding.public_key, algorithms=["RS256"], audience=binding.audience,
                            issuer=binding.issuer, options={"require": ["exp", "iat", "sub", "iss", "aud",
                                                                        "auth_time", "amr", "sid"]})
    except jwt.PyJWTError:
        raise Denied("owner_signature") from None
    return claims_session(claims, binding, session, now, live)
