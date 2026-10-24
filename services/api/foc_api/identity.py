"""Synthetic staff identity boundary. No bearer tokens or IdP responses enter browser reports."""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Literal
from urllib.parse import urlencode
from uuid import UUID

import httpx
import jwt
import psycopg
from cryptography.fernet import Fernet, InvalidToken
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, ConfigDict

COOKIE = "__Host-foc-session"
FLOW = "__Host-foc-flow"
router = APIRouter()


class Closed(BaseModel):
    model_config = ConfigDict(extra="forbid")


class OrganizationDTO(Closed):
    id: UUID
    role: Literal["reviewer", "supervisor", "safeguarding", "authority", "privacy", "org_admin"]


class IdentityDTO(Closed):
    principal_id: UUID
    organizations: list[OrganizationDTO]


class PermissionDTO(Closed):
    permission: Literal["case.read"]
    allowed: Literal[True]


class MembershipDTO(Closed):
    status: Literal["granted", "revoked"]


class LogoutDTO(Closed):
    status: Literal["signed_out"]


class AuditEventDTO(Closed):
    sequence: int
    event_id: UUID
    action: str
    outcome: Literal["allowed", "denied"]
    previous_hash: str
    event_hash: str
    occurred_at: str


class AuditDTO(Closed):
    events: list[AuditEventDTO]


def digest(value):
    return hashlib.sha256(value.encode()).digest()


def configuration():
    # No request header can choose the issuer, upstream, audience, redirect URI or origin.
    return {
        "issuer": "https://127.0.0.1:8443/realms/foc-synthetic",
        "upstream": os.environ.get("FOC_IDP_UPSTREAM", "http://keycloak:8080/realms/foc-synthetic"),
        "client": "foc-bff",
        "origin": "https://127.0.0.1:3443",
        "redirect": "https://127.0.0.1:3443/identity/callback",
        "secret": os.environ["FOC_IDP_SECRET"],
        "cipher": Fernet(os.environ["FOC_SESSION_KEY"].encode()),
    }


def idp(path, data=None):
    config = configuration()
    url = config["upstream"] + path
    try:
        with httpx.Client(timeout=5, follow_redirects=False, trust_env=False) as client:
            if data is None:
                response = client.get(url)
            else:
                response = client.post(
                    url, data={**data, "client_id": config["client"], "client_secret": config["secret"]}
                )
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, ValueError):
        raise HTTPException(503, "IDENTITY_UNAVAILABLE") from None


def validate_token(token, audience="foc-api", nonce=None):
    config = configuration()
    try:
        header = jwt.get_unverified_header(token)
        if header.get("alg") != "RS256" or not isinstance(header.get("kid"), str):
            raise ValueError()
        keys = idp("/protocol/openid-connect/certs")["keys"]
        matches = [
            key
            for key in keys
            if key.get("kid") == header["kid"] and key.get("kty") == "RSA" and key.get("use") == "sig"
        ]
        if len(matches) != 1:
            raise ValueError()
        claims = jwt.decode(
            token,
            jwt.PyJWK.from_dict(matches[0]).key,
            algorithms=["RS256"],
            audience=audience,
            issuer=config["issuer"],
            options={"require": ["exp", "iat", "sub", "iss", "aud", "auth_time", "amr"]},
        )
        now = time.time()
        if (
            claims.get("azp") != config["client"]
            or not {"pwd", "otp"}.issubset(set(claims["amr"]))
            or not 0 <= now - claims["auth_time"] <= 1800
        ):
            raise ValueError()
        if nonce is not None and not hmac.compare_digest(str(claims.get("nonce", "")), nonce):
            raise ValueError()
        return claims
    except (jwt.PyJWTError, ValueError, KeyError, TypeError):
        raise HTTPException(401, "INVALID_IDENTITY") from None


@contextmanager
def connection(request, principal=None, org=None):
    with psycopg.connect(request.app.state.settings.database_url, connect_timeout=3) as conn:
        if principal:
            conn.execute("SELECT set_config('foc.principal',%s,true)", (str(principal),))
        if org:
            conn.execute("SELECT set_config('foc.organization',%s,true)", (str(org),))
        conn.execute("SELECT set_config('foc.purpose','case_management',true)")
        yield conn


def mutation_guard(request, expected):
    if request.headers.get("origin") != configuration()["origin"] or request.headers.get(
        "sec-fetch-site"
    ) not in (None, "same-origin"):
        raise HTTPException(403, "CSRF_DENIED")
    supplied = request.headers.get("x-csrf-token", "")
    if not supplied or not hmac.compare_digest(digest(supplied), bytes(expected)):
        raise HTTPException(403, "CSRF_DENIED")


def authenticate(request, mutation=False):
    token = None
    session = request.cookies.get(COOKIE)
    bearer = request.headers.get("authorization", "")
    if session and bearer:
        raise HTTPException(401, "AMBIGUOUS_IDENTITY")
    if session:
        if len(session) != 43:
            raise HTTPException(401, "INVALID_SESSION")
        with connection(request) as conn:
            row = conn.execute("SELECT * FROM platform.session_get(%s)", (digest(session),)).fetchone()
        if row is None:
            raise HTTPException(401, "INVALID_SESSION")
        if mutation:
            mutation_guard(request, row[2])
        try:
            token = configuration()["cipher"].decrypt(row[1].encode(), ttl=1800).decode()
        except InvalidToken:
            raise HTTPException(401, "INVALID_SESSION") from None
    elif bearer.startswith("Bearer ") and not mutation:
        token = bearer[7:]
    if not token:
        raise HTTPException(401, "AUTHENTICATION_REQUIRED")
    claims = validate_token(token)
    active = idp("/protocol/openid-connect/token/introspect", {"token": token})
    if active.get("active") is not True or active.get("sub") != claims["sub"]:
        raise HTTPException(401, "REVOKED_IDENTITY")
    with connection(request) as conn:
        principal = conn.execute(
            "SELECT platform.identity_lookup(%s,%s)", (claims["iss"], claims["sub"])
        ).fetchone()[0]
    if principal is None or (session and principal != row[0]):
        raise HTTPException(401, "UNPROVISIONED_IDENTITY")
    return principal, session


def member(conn, org, role=None):
    if not conn.execute("SELECT platform.active_member(%s,%s)", (org, role)).fetchone()[0]:
        raise HTTPException(404, "NOT_FOUND")


@router.get("/identity/login")
def login():
    config = configuration()
    flow = {
        "state": secrets.token_urlsafe(32),
        "nonce": secrets.token_urlsafe(32),
        "verifier": secrets.token_urlsafe(48),
        "created": time.time(),
    }
    challenge = base64.urlsafe_b64encode(digest(flow["verifier"])).rstrip(b"=").decode()
    query = urlencode(
        {
            "client_id": config["client"],
            "redirect_uri": config["redirect"],
            "response_type": "code",
            "scope": "openid",
            "state": flow["state"],
            "nonce": flow["nonce"],
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "prompt": "login",
            "max_age": "0",
        }
    )
    response = RedirectResponse(config["issuer"] + "/protocol/openid-connect/auth?" + query, status_code=302)
    response.set_cookie(
        FLOW,
        config["cipher"].encrypt(json.dumps(flow).encode()).decode(),
        max_age=300,
        secure=True,
        httponly=True,
        samesite="lax",
        path="/",
    )
    return response


@router.get("/identity/callback")
def callback(request: Request):
    config = configuration()
    try:
        flow = json.loads(config["cipher"].decrypt(request.cookies.get(FLOW, "").encode(), ttl=300))
        if not hmac.compare_digest(
            request.query_params.get("state", ""), flow["state"]
        ) or not request.query_params.get("code"):
            raise ValueError()
    except (InvalidToken, ValueError, KeyError):
        raise HTTPException(401, "INVALID_LOGIN_STATE") from None
    tokens = idp(
        "/protocol/openid-connect/token",
        {
            "grant_type": "authorization_code",
            "code": request.query_params["code"],
            "redirect_uri": config["redirect"],
            "code_verifier": flow["verifier"],
        },
    )
    identity = validate_token(tokens.get("id_token", ""), config["client"], flow["nonce"])
    access = validate_token(tokens.get("access_token", ""))
    if identity["sub"] != access["sub"]:
        raise HTTPException(401, "INVALID_IDENTITY")
    session, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    with connection(request) as conn:
        principal = conn.execute(
            "SELECT platform.identity_lookup(%s,%s)", (access["iss"], access["sub"])
        ).fetchone()[0]
        if principal is None:
            raise HTTPException(401, "UNPROVISIONED_IDENTITY")
        conn.execute("SELECT set_config('foc.principal',%s,true)", (str(principal),))
        conn.execute(
            "SELECT platform.session_create(%s,%s,%s,%s,%s)",
            (
                digest(session),
                principal,
                config["cipher"].encrypt(tokens["access_token"].encode()).decode(),
                digest(csrf),
                datetime.fromtimestamp(access["exp"], UTC),
            ),
        )
    # CSRF is exposed to same-origin JavaScript, never as an authentication credential.
    response = RedirectResponse("/en/identity", status_code=302)
    response.set_cookie(COOKIE, session, max_age=1800, secure=True, httponly=True, samesite="lax", path="/")
    response.set_cookie(
        "__Host-foc-csrf", csrf, max_age=1800, secure=True, httponly=False, samesite="strict", path="/"
    )
    response.delete_cookie(FLOW, secure=True, httponly=True, samesite="lax", path="/")
    return response


@router.get("/identity/me", response_model=IdentityDTO)
def me(request: Request):
    principal, _ = authenticate(request)
    with connection(request, principal) as conn:
        organizations = conn.execute("SELECT * FROM platform.identity_orgs()").fetchall()
    return {
        "principal_id": str(principal),
        "organizations": [{"id": str(o), "role": r} for o, r in organizations],
    }


@router.post("/identity/logout", response_model=LogoutDTO)
def logout(request: Request):
    principal, session = authenticate(request, mutation=True)
    with connection(request, principal) as conn:
        for org, _ in conn.execute("SELECT * FROM platform.identity_orgs()").fetchall():
            conn.execute("SELECT set_config('foc.organization',%s,true)", (str(org),))
            conn.execute("SELECT platform.audit_append(%s,'session.logout',%s,'allowed')", (org, principal))
        conn.execute("SELECT platform.session_revoke(%s)", (digest(session),))
    response = JSONResponse({"status": "signed_out"})
    for cookie in [COOKIE, "__Host-foc-csrf", FLOW]:
        response.delete_cookie(cookie, secure=True, path="/")
    return response


class MembershipChange(BaseModel):
    model_config = ConfigDict(extra="forbid")
    principal_id: UUID
    role: str
    expires_at: datetime
    revoke: bool = False


@router.post("/identity/organizations/{org}/memberships", response_model=MembershipDTO)
def membership(org: UUID, body: MembershipChange, request: Request):
    principal, _ = authenticate(request, mutation=True)
    try:
        with connection(request, principal, org) as conn:
            member(conn, org, "org_admin")
            conn.execute(
                "SELECT platform.membership_change(%s,%s,%s,%s,%s)",
                (org, body.principal_id, body.role, body.expires_at, body.revoke),
            )
    except psycopg.errors.InsufficientPrivilege:
        raise HTTPException(403, "PERMISSION_DENIED") from None
    return {"status": "revoked" if body.revoke else "granted"}


@router.get("/identity/organizations/{org}/cases/{case}/permission", response_model=PermissionDTO)
def permission(org: UUID, case: UUID, request: Request):
    principal, _ = authenticate(request)
    with connection(request, principal, org) as conn:
        member(conn, org)
        allowed = conn.execute("SELECT platform.case_permission(%s,%s,'case.read')", (org, case)).fetchone()[
            0
        ]
        conn.execute(
            "SELECT platform.audit_append(%s,%s,%s,%s)",
            (
                org,
                "case.permission.allowed" if allowed else "case.permission.denied",
                case,
                "allowed" if allowed else "denied",
            ),
        )
    if not allowed:
        raise HTTPException(404, "NOT_FOUND")
    return {"permission": "case.read", "allowed": True}


@router.get("/identity/organizations/{org}/audit", response_model=AuditDTO)
def audit(org: UUID, request: Request):
    principal, _ = authenticate(request)
    with connection(request, principal, org) as conn:
        member(conn, org, "org_admin")
        conn.execute("SELECT platform.audit_append(%s,'audit.read',%s,'allowed')", (org, org))
        rows = conn.execute("SELECT * FROM platform.audit_read(%s)", (org,)).fetchall()
    return {
        "events": [
            {
                "sequence": row[0],
                "event_id": str(row[1]),
                "action": row[2],
                "outcome": row[3],
                "previous_hash": bytes(row[4]).hex(),
                "event_hash": bytes(row[5]).hex(),
                "occurred_at": row[6].isoformat(),
            }
            for row in rows
        ]
    }
