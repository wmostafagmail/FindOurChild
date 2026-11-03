"""Pinned owner, strict claims and live session status. Never trusts a caller owner claim."""

from dataclasses import dataclass
from uuid import NAMESPACE_URL, uuid5

import jwt

from .records import Denied, digest, require, sha


@dataclass(frozen=True)
class Binding:
    issuer: str
    audience: str
    subject: str
    principal: str
    public_key: bytes
    token_audiences: tuple[str, ...] = ()


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
    aud = claims.get("aud")
    if type(aud) is str:
        audiences = (aud,)
    else:
        require(type(aud) is list and 0 < len(aud) <= 4 and all(type(v) is str for v in aud)
                and len(aud) == len(set(aud)), "owner_audience_type")
        audiences = tuple(sorted(aud))
    expected = tuple(sorted(binding.token_audiences or (binding.audience,)))
    require(binding.audience in expected and audiences == expected, "owner_audience_binding")
    require(claims.get("iss") == binding.issuer
            and claims.get("sub") == binding.subject, "owner_binding")
    require(0 <= now - claims["auth_time"] <= 300 and claims["auth_time"] <= claims["iat"] <= now
            < claims["exp"], "owner_freshness")
    # OIDC sid is opaque, not a UUID. Never coerce it into a person/event identity.
    sid = claims.get("sid")
    require(type(sid) is str and 0 < len(sid) <= 256 and sid.isascii()
            and all(33 <= ord(c) <= 126 for c in sid), "owner_event")
    session_digest = sha(session.encode())
    # Correlation identifier only, not an approval or bearer capability. The actual
    # trust comes from the pinned signature, MFA, live session and explicit consent.
    material = {"issuer": binding.issuer, "audiences": list(expected), "subject": binding.subject,
                "sid": sid, "auth_time": claims["auth_time"], "session_sha256": session_digest}
    event = str(uuid5(NAMESPACE_URL, "foc-phase2e-v3-authentication-event/" + digest(material)))
    # The privileged adapter must introspect the token AND check the local current session/account.
    require(live(binding, session) is True, "owner_live_status")
    return OwnerSession(binding.issuer, binding.audience, binding.subject, binding.principal,
                        event, claims["auth_time"], claims["exp"], session_digest)


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
