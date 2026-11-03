"""Private V3 API, separate from operational reporting and V2 enrollment.

No deployment backend is provisioned. Tests compose a private synthetic backend
with the same handlers and the actual IdP/session boundary, not a header override.
"""

from fastapi import APIRouter, HTTPException, Request

from .identity import authenticate

router = APIRouter(prefix="/demo-authorization")


class OwnerBackend:
    """Privileged composition for ONE pinned owner/instance, never provisioned by an HTTP request."""

    def __init__(self, binding, engine):
        self.binding, self.engine = binding, engine

    def resolve(self, request, principal, session):
        import copy

        from tools.phase2e.owner_only_v3.identity import authenticate_token
        from tools.phase2e.owner_only_v3.records import require

        from .identity import configuration, connection, digest

        require(principal == self.binding.principal, "owner_principal")
        with connection(request) as conn:
            row = conn.execute("SELECT * FROM platform.session_get(%s)", (digest(session),)).fetchone()
        require(row is not None and str(row[0]) == principal, "owner_session_current")
        token = configuration()["cipher"].decrypt(row[1].encode(), ttl=1800).decode()

        def live(binding, value):
            actor, current = authenticate(request)
            return str(actor) == binding.principal and current == value

        owner = authenticate_token(token, self.binding, session, self.engine.clock.now(), live)
        # Revalidate this live request during store/audit waits, not only at entry.
        bound = copy.copy(self.engine)
        bound.live = lambda value: live(self.binding, session) and value.session_digest == owner.session_digest
        return bound, owner


def boundary(request, mutation=False):
    # Always existing live IdP/session/CSRF authentication, even when unprovisioned.
    principal, session = authenticate(request, mutation=mutation)
    if not session or request.query_params:
        raise HTTPException(403, "OWNER_SESSION_REQUIRED")
    backend = getattr(request.app.state, "owner_only_v3_backend", None)
    if backend is None:
        raise HTTPException(503, "OWNER_AUTHORITY_UNPROVISIONED")
    return backend.resolve(request, str(principal), session)


def private_call(operation):
    try:
        return operation()
    except ValueError:
        # No untrusted record, owner identity, token, URL, media or internal error in public errors.
        raise HTTPException(403, "OWNER_AUTHORIZATION_DENIED") from None


@router.get("/status")
def status(request: Request):
    def execute():
        engine, session = boundary(request)
        engine.current(session, engine.clock.now())
        from tools.phase2e.owner_only_v3.fixtures import lineage_key

        with engine.tx() as tx:
            exposure = tx.get("exposure", lineage_key(engine.fixture_plan))
            tx.audit("owner_status_read", engine.template["policy_digest"])
        return {"data_class": "synthetic_demo_only", "source_only": True, "execution_available": False,
                "record_template": engine.template, "fixture_plan": engine.fixture_plan,
                "provisioned_real_owner": False, "actual_assets": 0, "actual_inference": False,
                "permanent_fixture_history": exposure is not None}

    return private_call(execute)


@router.post("/prepare")
async def prepare(request: Request):
    raw = await request.body()

    def execute():
        engine, session = boundary(request, mutation=True)
        from tools.phase2e.owner_only_v3.records import decode, require

        require(decode(raw) == {}, "prepare_closed")
        return engine.prepare(session)

    return private_call(execute)


@router.post("/confirm")
async def confirm(request: Request):
    raw = await request.body()

    def execute():
        engine, session = boundary(request, mutation=True)
        from tools.phase2e.owner_only_v3.records import decode

        return engine.confirm(session, decode(raw))

    return private_call(execute)


@router.post("/revoke")
async def revoke(request: Request):
    raw = await request.body()

    def execute():
        engine, session = boundary(request, mutation=True)
        from tools.phase2e.owner_only_v3.records import decode, require

        body = decode(raw)
        require(type(body) is dict and set(body) == {"record_id"} and type(body["record_id"]) is str
                and len(body["record_id"]) == 36, "revoke_closed")
        return engine.revoke(session, body["record_id"])

    return private_call(execute)
