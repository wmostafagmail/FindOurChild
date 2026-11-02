"""Explicit CI-only composition, not imported by the application deployment factory.

Each fictional account has a separate private instance with one pinned owner.
No test principal or key is enrolled in a real registry or deployed authority.
"""

import os
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
        return self.backends[principal].resolve(request, principal, session)


def app():
    require(os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("FOC_V3_TEST_MODE")
            == "hosted-real-postgres" and os.environ.get("FOC_E2E_DATA_CLASS") == "synthetic",
            "ci_only_harness")
    with psycopg.connect(os.environ["FOC_DATABASE_ADMIN_URL"]) as conn:
        require(conn.execute("SELECT data_class FROM platform.environment").fetchone() == ("synthetic",),
                "synthetic_application_database")
    result = create_app()
    result.state.owner_only_v3_backend = SyntheticInstances()
    return result
