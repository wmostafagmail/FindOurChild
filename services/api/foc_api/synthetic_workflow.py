"""Real staff workflow over sealed fictional fixtures. No inference or identity decisions."""

import hashlib
import json
import os
from functools import cache
from pathlib import Path
from typing import Annotated, Literal
from uuid import UUID

from cryptography.fernet import InvalidToken
from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from psycopg.types.json import Jsonb
from pydantic import AwareDatetime, Field

from . import media
from .identity import Closed, configuration, connection
from .identity import authenticate as identity_authenticate
from .synthetic_contracts import ComparisonDTO, LeadPageDTO, SnapshotDTO, StatusDTO, TaskDTO

router = APIRouter(prefix="/v1/staff/synthetic-workflow")


def authenticate(request, mutation=False):
    actor, session = identity_authenticate(request, mutation)
    request.state.workflow_actor = actor
    try:
        request.state.workflow_org = UUID(request.query_params.get("organization_id", ""))
    except ValueError:
        raise HTTPException(422, "INVALID_ORGANIZATION") from None
    return actor, session


def audit_denial(request):
    actor = getattr(request.state, "workflow_actor", None)
    org = getattr(request.state, "workflow_org", None)
    if actor and org:
        with connection(request, actor, org) as conn:
            epoch(conn)
            conn.execute("SELECT platform.sw_denial(%s)", (org,))


@cache
def migration_contract():
    folder = Path(__file__).resolve().parents[3] / "database/migrations"
    expected = {p.stem: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.glob("*.sql"))}
    if "0036_synthetic_live_expiry" not in expected:
        raise HTTPException(503, "WORKFLOW_UNAVAILABLE")
    return expected


def epoch(conn):
    value = os.environ.get("FOC_WORKFLOW_EPOCH", "")
    if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise HTTPException(503, "WORKFLOW_UNAVAILABLE")
    conn.execute("SELECT set_config('foc.workflow_epoch',%s,true)", (value,))
    conn.execute("SET LOCAL statement_timeout='8s'")
    conn.execute("SET LOCAL lock_timeout='3s'")
    conn.execute("SET LOCAL idle_in_transaction_session_timeout='10s'")
    if (
        dict(conn.execute("SELECT version,sha256 FROM platform.migrations").fetchall())
        != migration_contract()
    ):
        raise HTTPException(503, "WORKFLOW_UNAVAILABLE")


class RunCommand(Closed):
    scenario_id: UUID
    scenario_version: Literal["fixture-2d-v1"]


class EmptyCommand(Closed):
    pass


Reason = Literal[
    "INSUFFICIENT_AUTHORIZED_EVIDENCE",
    "SUPPORTING_FIXTURE_CLAIM",
    "CONTRADICTORY_FIXTURE_CLAIM",
    "REQUEST_EVIDENCE",
    "RECUSE_CONFLICT",
    "SYNTHETIC_WORKFLOW_ONLY",
]


class EvidenceCommand(Closed):
    snapshot_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    uncertainty_acknowledged: Literal[True]
    rationale_codes: list[Reason] = Field(min_length=1, max_length=5)
    evidence_refs: list[UUID] = Field(max_length=20)


class ReviewCommand(EvidenceCommand):
    outcome: Literal["hold", "reject", "escalate"]


class AssignmentCommand(EvidenceCommand):
    principal_id: UUID
    expires_at: AwareDatetime


class IndependentCommand(EvidenceCommand):
    first_review_id: UUID
    outcome: Literal["return_for_evidence", "disagree", "recuse", "workflow_review_complete"]


class EventDTO(Closed):
    id: UUID
    actor: UUID
    revision: int
    kind: Literal["reviews", "assignments", "notes", "peer-review-requests", "independent-reviews"]
    payload: ReviewCommand | AssignmentCommand | IndependentCommand | EvidenceCommand
    snapshot_hash: str
    occurred_at: str
    previous_hash: str
    event_hash: str


class EventPageDTO(Closed):
    items: list[EventDTO]
    next_cursor: str | None


class HistoryDTO(SnapshotDTO):
    events: EventPageDTO
    tasks: list[TaskDTO]


class CommandResult(Closed):
    id: UUID
    revision: int = Field(ge=1)


class RunResult(CommandResult):
    state: Literal["queued", "running", "completed", "held", "failed", "cancelled"]


def revision(value):
    if not value.startswith('"') or not value.endswith('"') or not value[1:-1].isdigit():
        raise HTTPException(422, "INVALID_REVISION")
    result = int(value[1:-1])
    if not 1 <= result <= 9223372036854775807:
        raise HTTPException(422, "INVALID_REVISION")
    return result


def response(value, status=200):
    headers = {"ETag": '"' + str(value["revision"]) + '"'} if "revision" in value else {}
    return JSONResponse(value, status_code=status, headers=headers)


@router.get("/status", response_model=StatusDTO)
def status(request: Request, organization_id: UUID):
    actor, _ = authenticate(request)
    with connection(request, actor, organization_id) as conn:
        epoch(conn)
        result = conn.execute("SELECT platform.sw_status(%s)", (organization_id,)).fetchone()[0]
        for scenario in result["scenarios"]:
            scenario["colleagues"] = conn.execute(
                "SELECT platform.sw_colleagues(%s,%s)", (organization_id, scenario["id"])
            ).fetchone()[0]
    return StatusDTO.model_validate(result).model_dump(mode="json")


@router.post("/cases/{cid}/runs", status_code=202, response_model=RunResult)
def start_run(
    cid: UUID,
    body: RunCommand,
    request: Request,
    organization_id: UUID,
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
    if_match: Annotated[str, Header(alias="If-Match")],
):
    return run_write(request, organization_id, cid, "runs", body, idempotency_key, if_match)


def run_write(request, org, aggregate, operation, body, key, match):
    actor, _ = authenticate(request, mutation=True)
    with connection(request, actor, org) as conn:
        epoch(conn)
        value = conn.execute(
            "SELECT platform.sw_run_command(%s,%s,%s,%s,%s,%s)",
            (org, aggregate, operation, Jsonb(body.model_dump(mode="json")), revision(match), key),
        ).fetchone()[0]
    return value


@router.get("/runs/{rid}", response_model=RunResult)
def run_status(rid: UUID, request: Request, organization_id: UUID):
    actor, _ = authenticate(request)
    with connection(request, actor, organization_id) as conn:
        epoch(conn)
        row = conn.execute(
            "SELECT id,revision,state FROM app.synthetic_matching_runs WHERE organization_id=%s AND id=%s",
            (organization_id, rid),
        ).fetchone()
        if row is None:
            raise HTTPException(404, "NOT_FOUND")
        conn.execute("SELECT platform.case_list_audit(%s)", (organization_id,))
        if not conn.execute(
            "SELECT id FROM app.synthetic_matching_runs WHERE organization_id=%s AND id=%s",
            (organization_id, rid),
        ).fetchone():
            raise HTTPException(404, "NOT_FOUND")
    return response({"id": str(row[0]), "revision": row[1], "state": row[2]})


@router.post("/runs/{rid}/cancellations", status_code=201, response_model=RunResult)
def cancel_run(
    rid: UUID,
    body: EmptyCommand,
    request: Request,
    organization_id: UUID,
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
    if_match: Annotated[str, Header(alias="If-Match")],
):
    return run_write(request, organization_id, rid, "cancellations", body, idempotency_key, if_match)


def cursor_offset(cursor, scope, stamp, limit):
    if not 1 <= limit <= 50:
        raise HTTPException(422, "INVALID_LIMIT")
    if not cursor:
        return 0
    try:
        value = json.loads(configuration()["cipher"].decrypt(cursor.encode(), ttl=300))
        if value["scope"] != scope or value["digest"] != stamp:
            raise HTTPException(412, "STALE_CURSOR")
        offset = value["offset"]
        if type(offset) is not int or not 0 <= offset <= 1000000000:
            raise ValueError()
        return offset
    except (InvalidToken, ValueError, KeyError, TypeError):
        raise HTTPException(422, "INVALID_CURSOR") from None


def next_cursor(scope, stamp, offset):
    return (
        configuration()["cipher"]
        .encrypt(json.dumps({"scope": scope, "digest": stamp, "offset": offset}).encode())
        .decode()
    )


def page(items, cursor, scope, limit):
    stamp = hashlib.sha256(json.dumps(items, sort_keys=True).encode()).hexdigest()
    offset = cursor_offset(cursor, scope, stamp, limit)
    end = offset + limit
    return {
        "items": items[offset:end],
        "next_cursor": next_cursor(scope, stamp, end) if end < len(items) else None,
    }


@router.get("/cases/{cid}/leads", response_model=LeadPageDTO)
def leads(
    cid: UUID,
    request: Request,
    organization_id: UUID,
    limit: int = 25,
    cursor: str | None = None,
    review_state: Literal["pending", "held", "rejected", "escalated"] | None = None,
    assigned_to_me: bool = False,
):
    actor, _ = authenticate(request)
    with connection(request, actor, organization_id) as conn:
        epoch(conn)
        if not conn.execute(
            "SELECT platform.case_permission(%s,%s,'case.read')", (organization_id, cid)
        ).fetchone()[0]:
            raise HTTPException(404, "NOT_FOUND")
        scope = [str(actor), str(organization_id), str(cid), "leads", str(review_state), str(assigned_to_me)]
        parameters = (organization_id, cid, review_state, assigned_to_me)
        stamp = conn.execute(
            "SELECT platform.sw_queue(%s,%s,%s,%s,0,0)", parameters
        ).fetchone()[0]["stamp"]
        offset = cursor_offset(cursor, scope, stamp, limit)
        page = conn.execute(
            "SELECT platform.sw_queue(%s,%s,%s,%s,%s,%s)", (*parameters, offset, limit + 1)
        ).fetchone()[0]
        if page["stamp"] != stamp:
            raise HTTPException(412, "STALE_CURSOR")
        conn.execute("SELECT platform.case_list_audit(%s)", (organization_id,))
        # Fresh statement after the real audit wait: no authorization cache.
        current = conn.execute(
            "SELECT platform.sw_queue(%s,%s,%s,%s,%s,%s)", (*parameters, offset, limit + 1)
        ).fetchone()[0]
        if current != page:
            raise HTTPException(404, "NOT_FOUND")
    rows = page["items"]
    items = rows[:limit]
    return {
        "items": items,
        "next_cursor": next_cursor(scope, stamp, offset + limit) if len(rows) > limit else None,
    }


def read(request, org, lid, view, cursor=None, limit=25):
    actor, _ = authenticate(request)
    with connection(request, actor, org) as conn:
        epoch(conn)
        value = conn.execute("SELECT platform.sw_read(%s,%s,%s)", (org, lid, view)).fetchone()[0]
        if view != "comparison":
            scope = [str(actor), str(org), str(lid), view]
            stamp = str(value["revision"])
            offset = cursor_offset(cursor, scope, stamp, limit)
            rows = conn.execute(
                "SELECT id,actor,revision,kind,payload,snapshot_hash,occurred_at,previous_hash,event_hash FROM app.synthetic_investigation_events WHERE organization_id=%s AND lead_id=%s ORDER BY revision LIMIT %s OFFSET %s",
                (org, lid, limit + 1, offset),
            ).fetchall()
            items = [
                {
                    "id": str(r[0]),
                    "actor": str(r[1]),
                    "revision": r[2],
                    "kind": r[3],
                    "payload": r[4],
                    "snapshot_hash": r[5],
                    "occurred_at": r[6].isoformat(),
                    "previous_hash": r[7],
                    "event_hash": r[8],
                }
                for r in rows[:limit]
            ]
            value["events"] = {
                "items": items,
                "next_cursor": next_cursor(scope, stamp, offset + limit) if len(rows) > limit else None,
            }
            tasks = conn.execute(
                "SELECT id,target,expires_at,state FROM app.synthetic_investigation_tasks WHERE organization_id=%s AND lead_id=%s ORDER BY expires_at DESC LIMIT 50",
                (org, lid),
            ).fetchall()
            value["tasks"] = [
                {"id": str(r[0]), "target": str(r[1]), "expires_at": r[2].isoformat(), "state": r[3]}
                for r in tasks
            ]
    model = ComparisonDTO if view == "comparison" else HistoryDTO
    return response(model.model_validate(value).model_dump(mode="json"))


@router.get("/leads/{lid}/comparison", response_model=ComparisonDTO)
def comparison(lid: UUID, request: Request, organization_id: UUID):
    return read(request, organization_id, lid, "comparison")


@router.get("/leads/{lid}/investigation", response_model=HistoryDTO)
def investigation(
    lid: UUID, request: Request, organization_id: UUID, cursor: str | None = None, limit: int = 25
):
    return read(request, organization_id, lid, "investigation", cursor, limit)


@router.get("/leads/{lid}/audit", response_model=HistoryDTO)
def audit(lid: UUID, request: Request, organization_id: UUID, cursor: str | None = None, limit: int = 25):
    return read(request, organization_id, lid, "audit", cursor, limit)


@router.get("/leads/{lid}/photos/{pid}/content")
def photograph(lid: UUID, pid: UUID, request: Request, organization_id: UUID):
    actor, _ = authenticate(request)
    with connection(request, actor, organization_id) as conn:
        epoch(conn)
        value = conn.execute(
            "SELECT platform.sw_read(%s,%s,'comparison')", (organization_id, lid)
        ).fetchone()[0]
        if not any(p["id"] == str(pid) for p in value["photos"]):
            raise HTTPException(404, "NOT_FOUND")
        permitted = conn.execute("SELECT platform.media_read(%s,%s)", (organization_id, pid)).fetchone()[0]
        try:
            data = media.get(
                "GATEWAY", "foc-derivative", permitted["key"], permitted["version"], permitted["wrapped_key"]
            )
        except media.FAILURES:
            raise HTTPException(503, "MEDIA_UNAVAILABLE") from None
        if media.checksum(data) != permitted["sha256"]:
            raise HTTPException(503, "MEDIA_INTEGRITY_FAILURE")
        conn.execute("SELECT platform.sw_read(%s,%s,'comparison')", (organization_id, lid))
        conn.execute("SELECT platform.media_read(%s,%s)", (organization_id, pid))
    return Response(
        data,
        media_type="image/png",
        headers={"Content-Disposition": 'inline; filename="synthetic-review.png"'},
    )


def event_write(request, org, lid, operation, body, key, match):
    actor, _ = authenticate(request, mutation=True)
    with connection(request, actor, org) as conn:
        epoch(conn)
        result = conn.execute(
            "SELECT platform.sw_event_command(%s,%s,%s,%s,%s,%s)",
            (org, lid, operation, Jsonb(body.model_dump(mode="json")), revision(match), key),
        ).fetchone()[0]
    return result


def event_endpoint(operation, model):
    def endpoint(
        lid: UUID,
        body: model,
        request: Request,
        organization_id: UUID,
        idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
        if_match: Annotated[str, Header(alias="If-Match")],
    ):
        return event_write(request, organization_id, lid, operation, body, idempotency_key, if_match)

    return endpoint


for operation, model in [
    ("reviews", ReviewCommand),
    ("notes", EvidenceCommand),
    ("assignments", AssignmentCommand),
    ("peer-review-requests", AssignmentCommand),
    ("independent-reviews", IndependentCommand),
]:
    router.add_api_route(
        "/leads/{lid}/" + operation,
        event_endpoint(operation, model),
        methods=["POST"],
        status_code=201,
        response_model=CommandResult,
    )


def worker_once(conn):
    epoch(conn)
    job = conn.execute("SELECT platform.sw_lease()").fetchone()[0]
    conn.commit()  # A crash after lease is recovered using the fenced deadline.
    if job is None:
        return False
    epoch(conn)
    conn.execute("SELECT platform.sw_finish(%s,%s,%s)", (job["organization_id"], job["id"], job["token"]))
    return True
