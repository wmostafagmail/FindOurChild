import hashlib
import json
import logging
from pathlib import Path
from uuid import uuid4

import psycopg
from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .config import Settings

CONTRACT = Path(__file__).resolve().parents[3] / "docs/contracts/openapi.json"
logger = logging.getLogger("foc")


def create_app(settings: Settings | None = None):
    settings = settings or Settings.load()
    app = FastAPI(title="Find Our Child", docs_url=None, redoc_url=None, openapi_url=None)

    app.state.settings = settings
    from .identity import router

    app.include_router(router)
    from .reporting import router as reporting_router

    # Prefer concrete routes over generic action paths.
    reporting_router.routes.sort(key=lambda route: route.path.count("{"))
    app.include_router(reporting_router)
    from .synthetic_workflow import router as workflow_router

    app.include_router(workflow_router)

    @app.exception_handler(HTTPException)
    async def identity_error(request: Request, exc: HTTPException):
        if exc.status_code in {401, 403, 404} and getattr(request.state, "workflow_actor", None):
            from .synthetic_workflow import audit_denial

            try:
                await run_in_threadpool(audit_denial, request)
            except (psycopg.Error, HTTPException):
                return JSONResponse(
                    {
                        "code": "SERVICE_UNAVAILABLE",
                        "message_key": "errors.service_unavailable",
                        "request_id": request.state.request_id,
                    },
                    status_code=503,
                )
        return JSONResponse(
            {
                "code": str(exc.detail),
                "message_key": "errors.identity_denied",
                "request_id": request.state.request_id,
            },
            status_code=exc.status_code,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, exc: RequestValidationError):
        return JSONResponse(
            {
                "code": "INVALID_REQUEST",
                "message_key": "errors.invalid_request",
                "request_id": request.state.request_id,
            },
            status_code=422,
        )

    @app.exception_handler(psycopg.errors.InsufficientPrivilege)
    async def denied_database(request: Request, exc):
        from .synthetic_workflow import audit_denial

        try:
            await run_in_threadpool(audit_denial, request)
        except (psycopg.Error, HTTPException):
            return JSONResponse(
                {
                    "code": "SERVICE_UNAVAILABLE",
                    "message_key": "errors.service_unavailable",
                    "request_id": request.state.request_id,
                },
                status_code=503,
            )
        return JSONResponse(
            {"code": "NOT_FOUND", "message_key": "errors.not_found", "request_id": request.state.request_id},
            status_code=404,
        )

    @app.exception_handler(psycopg.errors.UniqueViolation)
    async def conflict_database(request: Request, exc):
        return JSONResponse(
            {
                "code": "IDEMPOTENCY_CONFLICT",
                "message_key": "errors.conflict",
                "request_id": request.state.request_id,
            },
            status_code=409,
        )

    @app.exception_handler(psycopg.Error)
    async def database_error(request: Request, exc: psycopg.Error):
        if exc.sqlstate in {"P0412", "P0409", "P0422", "P0429"}:
            status = {"P0412": 412, "P0409": 409, "P0422": 422, "P0429": 429}[exc.sqlstate]
            return JSONResponse(
                {
                    "code": "REQUEST_CONFLICT",
                    "message_key": "errors.conflict",
                    "request_id": request.state.request_id,
                },
                status_code=status,
            )
        return JSONResponse(
            {
                "code": "SERVICE_UNAVAILABLE",
                "message_key": "errors.service_unavailable",
                "request_id": request.state.request_id,
            },
            status_code=503,
        )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        request_id = str(uuid4())  # Never trust an inbound correlation string in reports.
        request.state.request_id = request_id
        if request.method in {"POST", "PUT", "PATCH"}:
            ceiling = 5242880 if request.url.path.endswith("/content") else 65536
            chunks = bytearray()
            async for chunk in request.stream():
                chunks.extend(chunk)
                if len(chunks) > ceiling:
                    return JSONResponse(
                        {"code": "TOO_LARGE", "message_key": "errors.too_large", "request_id": request_id},
                        status_code=413,
                        headers={"Cache-Control": "no-store"},
                    )
            request._body = bytes(chunks)
        response = await call_next(request)
        response.headers.update(
            {
                "Cache-Control": "no-store",
                "Referrer-Policy": "no-referrer",
                "X-Content-Type-Options": "nosniff",
                "X-Request-ID": request_id,
                "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
            }
        )
        return response

    @app.get("/health/live")
    def live():
        return {"status": "alive", "service": "find-our-child-api", "phase": "1A"}

    @app.get("/health/ready")
    def ready():
        try:
            with psycopg.connect(settings.database_url, connect_timeout=2) as conn:
                row = conn.execute(
                    "SELECT data_class, schema_version, instance_id::text FROM platform.environment WHERE singleton AND EXISTS (SELECT 1 FROM platform.migrations WHERE version='0002_contract_hardening')"
                ).fetchone()
                role = conn.execute(
                    "SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user"
                ).fetchone()
                if row is None or row[:2] != ("synthetic", "0001") or role != (False, False):
                    raise RuntimeError("Untrusted database identity")
                required = {
                    p.stem: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in (Path(__file__).resolve().parents[3] / "database/migrations").glob("*.sql")
                }
                applied = dict(conn.execute("SELECT version,sha256 FROM platform.migrations").fetchall())
                if not required or any(applied.get(k) != v for k, v in required.items()):
                    raise RuntimeError("Required migration not applied")

            return {
                "status": "ready",
                "data_class": "synthetic",
                "schema_version": "0001",
                "instance_id": row[2],
            }
        except (psycopg.Error, RuntimeError):
            # Do not log connection strings, SQL parameters, or exception contents.
            return JSONResponse({"status": "unavailable"}, status_code=503)

    @app.get("/openapi.json")
    def contract():
        return JSONResponse(json.loads(CONTRACT.read_text()))

    @app.api_route("/v1/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
    def disabled(path: str, request: Request):
        # No authentication, report intake, media, search, or safeguarding action exists in 1A.
        return JSONResponse(
            {
                "code": "PHASE_DISABLED",
                "message_key": "errors.phase_disabled",
                "request_id": request.state.request_id,
            },
            status_code=503,
        )

    return app
