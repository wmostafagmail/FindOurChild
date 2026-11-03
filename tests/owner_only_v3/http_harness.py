"""Explicit CI-only composition, not imported by the application deployment factory.

Each fictional account has a separate private instance with one pinned owner.
No test principal or key is enrolled in a real registry or deployed authority.
"""

import os
import time
from uuid import uuid4

import jwt
import psycopg
from cryptography.hazmat.primitives import serialization
from fastapi import HTTPException
from foc_api import identity
from foc_api.main import create_app
from foc_api.owner_only_demo import OwnerBackend

from scripts.identity_setup import OWNER_V3_USERS, fixture_id
from tests.owner_only_v3.helpers import SHARED_CHECKPOINT, fixture_plan, postgres_store, template
from tools.phase2e.owner_only_v3.confirmation import Clock, Confirmation
from tools.phase2e.owner_only_v3.identity import Binding
from tools.phase2e.owner_only_v3.records import require


class SyntheticInstances:
    def __init__(self):
        self.denial_codes = {}
        config = identity.configuration()
        jwks = identity.idp("/protocol/openid-connect/certs")["keys"]
        keys = [k for k in jwks if k.get("kty") == "RSA" and k.get("use") == "sig"]
        require(len(keys) == 1, "synthetic_idp_key")
        key = jwt.PyJWK.from_dict(keys[0]).key.public_bytes(serialization.Encoding.PEM,
                                                         serialization.PublicFormat.SubjectPublicKeyInfo)
        self.backends = {}
        for name in OWNER_V3_USERS:
            principal, instance, tenant = fixture_id(name), str(uuid4()), str(uuid4())
            binding = Binding(config["issuer"], "foc-api", principal, principal, key,
                              token_audiences=("foc-api", "foc-bff"))
            store = postgres_store(instance, tenant, SHARED_CHECKPOINT)
            engine = Confirmation(store, template(binding, instance, tenant), Clock(), lambda _: False)
            engine.fixture_plan = fixture_plan()
            self.backends[principal] = OwnerBackend(binding, engine)
        # Explicit simulated exposure fixture. No photograph/model is acquired or called.
        from tools.phase2e.owner_only_v3.fixtures import freeze, validate_plan
        from tools.phase2e.owner_only_v3.records import canonical, digest

        first = next(iter(self.backends.values())).engine
        plan = validate_plan(canonical(first.fixture_plan))
        derivatives = {row["image_ref"]: digest("generated-browser-fixture:" + row["image_ref"])
                       for row in plan["images"]}
        with first.tx() as tx:
            freeze(tx, plan, derivatives)

    def resolve(self, request, principal, session):
        if principal not in self.backends:
            raise HTTPException(403, "OWNER_REQUIRED")
        from tools.phase2e.owner_only_v3.records import Denied

        try:
            return self.backends[principal].resolve(request, principal, session)
        except Denied as exc:
            allowed = {"owner_principal", "owner_session_current", "owner_unprovisioned", "owner_algorithm",
                       "owner_signature", "owner_session", "owner_claim_type", "owner_mfa", "owner_audience_type",
                       "owner_audience_binding", "owner_binding", "owner_freshness", "owner_event", "owner_live_status"}
            code = str(exc) if str(exc) in allowed else "other_owner_denial"
            self.denial_codes[code] = self.denial_codes.get(code, 0) + 1
            raise


def safe_claim_shape():
    """CI-only diagnostics from a synthetic session; never emits token, owner subject, SID or secrets.

    Unverified decoding is ONLY a diagnostic shape report, never authentication.
    Actual admission still uses the normal pinned signature/MFA/live-status verifier.
    """
    from uuid import UUID

    from cryptography.fernet import Fernet

    with psycopg.connect(os.environ["FOC_DATABASE_ADMIN_URL"]) as conn:
        require(conn.execute("SELECT data_class FROM platform.environment").fetchone() == ("synthetic",),
                "synthetic_claim_diagnostics_only")
        row = conn.execute("SELECT encrypted_token FROM platform.identity_sessions WHERE principal_id=%s "
                           "AND revoked_at IS NULL ORDER BY expires_at DESC LIMIT 1",
                           (fixture_id("synthetic-owner-v3-smoke"),)).fetchone()
    require(row is not None, "smoke_session_missing")
    token = Fernet(os.environ["FOC_SESSION_KEY"].encode()).decrypt(row[0].encode(), ttl=1800).decode()
    claims = jwt.decode(token, options={"verify_signature": False})
    audiences = claims.get("aud")
    audiences = [audiences] if type(audiences) is str else audiences
    safe_audiences = [v if type(v) is str and v in {"foc-api", "foc-bff", "account"} else "other"
                      for v in audiences] if type(audiences) is list else []
    sid_uuid = False
    try:
        sid_uuid = str(UUID(claims.get("sid", ""))) == claims.get("sid")
    except (ValueError, TypeError, AttributeError):
        pass
    return {"synthetic_only": True, "audience_type": type(claims.get("aud")).__name__,
            "public_service_audiences": sorted(safe_audiences), "sid_present": "sid" in claims,
            "sid_is_uuid": sid_uuid, "auth_time_integer": type(claims.get("auth_time")) is int,
            "iat_integer": type(claims.get("iat")) is int, "exp_integer": type(claims.get("exp")) is int,
            "subject_matches_synthetic_fixture": claims.get("sub") == fixture_id("synthetic-owner-v3-smoke"),
            "amr_list": type(claims.get("amr")) is list,
            "password_and_otp": type(claims.get("amr")) is list
            and all(type(v) is str for v in claims["amr"]) and {"pwd", "otp"}.issubset(claims["amr"])}


def app():
    require(os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("FOC_V3_TEST_MODE")
            == "hosted-real-postgres" and os.environ.get("FOC_E2E_DATA_CLASS") == "synthetic",
            "ci_only_harness")
    with psycopg.connect(os.environ["FOC_DATABASE_ADMIN_URL"]) as conn:
        require(conn.execute("SELECT data_class FROM platform.environment").fetchone() == ("synthetic",),
                "synthetic_application_database")
    # API health does not prove the asynchronously imported Keycloak realm is ready.
    # Wait for the actual pinned discovery/JWKS endpoints; never accept a fallback key.
    deadline = time.monotonic() + 180
    while True:
        try:
            discovery = identity.idp("/.well-known/openid-configuration")
            keys = identity.idp("/protocol/openid-connect/certs")
            require(discovery.get("issuer") == identity.configuration()["issuer"]
                    and type(keys.get("keys")) is list and bool(keys["keys"]), "pinned_idp_discovery")
            break
        except HTTPException:
            require(time.monotonic() < deadline, "synthetic_idp_readiness_timeout")
            time.sleep(.5)
    result = create_app()
    result.state.owner_only_v3_backend = SyntheticInstances()
    return result
