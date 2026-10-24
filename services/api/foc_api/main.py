import json
import logging
from pathlib import Path
from uuid import uuid4

import psycopg
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .config import Settings

CONTRACT = Path(__file__).resolve().parents[3] / "docs/contracts/openapi.json"
logger = logging.getLogger("foc")


def create_app(settings: Settings | None = None):
    settings = settings or Settings.load()
    app = FastAPI(title="Find Our Child", docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        request_id = str(uuid4())  # Never trust an inbound correlation string in reports.
        request.state.request_id = request_id
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
