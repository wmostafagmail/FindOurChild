"""Synthetic-only reporting and case management. DTOs are projected, never table serialization."""

import hashlib
import hmac
import json
import os
import secrets
from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from cryptography.fernet import Fernet
from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from jsonschema import Draft202012Validator, FormatChecker
from psycopg.types.json import Jsonb

from . import media
from .identity import authenticate, configuration, connection, digest, member, mutation_guard

router = APIRouter()
COOKIE = "__Host-foc-reporter"
BROWSER = "__Host-foc-intake"
ORG = UUID("10000000-0000-4000-8000-000000000001")
NOTICE = "synthetic-1c-v1"
CONTRACT = Path(__file__).resolve().parents[3] / "docs/contracts/openapi.json"


def cipher(contact=False):
    return Fernet(os.environ["FOC_CONTACT_KEY" if contact else "FOC_REPORT_KEY"].encode())


def seal(value, contact=False):
    return cipher(contact).encrypt(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).decode()


def unseal(value, contact=False):
    return json.loads(cipher(contact).decrypt(value.encode()))


def body_hash(value):
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")))


def contact_hash(value):
    return hmac.digest(os.environ["FOC_CONTACT_KEY"].encode(), value.strip().lower().encode(), "sha256")


def validate(schema, body):
    spec = json.loads(CONTRACT.read_text())
    validator = Draft202012Validator(
        {"$ref": "#/components/schemas/" + schema, **{k: v for k, v in spec.items() if k == "components"}},
        format_checker=FormatChecker(),
    )
    if not validator.is_valid(body):
        raise HTTPException(422, "INVALID_REQUEST")

    def intervals(obj):
        if isinstance(obj, dict):
            for a, b in [
                ("lower", "upper"),
                ("min_months", "max_months"),
                ("age_min_months", "age_max_months"),
            ]:
                if a in obj and b in obj:
                    lo, hi = obj[a], obj[b]
                    if (lo is None) != (hi is None):
                        raise HTTPException(422, "INVALID_INTERVAL")
                    if lo is not None:
                        left, right = lo, hi
                        if isinstance(lo, str) and "T" in lo:
                            left = datetime.fromisoformat(lo)
                            right = datetime.fromisoformat(hi)
                        if left > right:
                            raise HTTPException(422, "INVALID_INTERVAL")
            if obj.get("knowledge") == "unknown" and (
                obj.get("lower") is not None or obj.get("upper") is not None
            ):
                raise HTTPException(422, "INVALID_INTERVAL")
            if "knowledge" in obj and (
                (obj["knowledge"] == "unknown") != (obj.get("lower") is None)
                or (obj["knowledge"] == "unknown") != (obj.get("precision") == "unknown")
            ):
                raise HTTPException(422, "INVALID_INTERVAL")
            if "timezone" in obj:
                if obj.get("precision") == "unknown" and obj.get("lower") is not None:
                    raise HTTPException(422, "INVALID_INTERVAL")
                if (
                    obj.get("precision") != "unknown"
                    and obj.get("lower") is None
                    and "local_date_lower" not in obj
                ):
                    raise HTTPException(422, "INVALID_INTERVAL")
                try:
                    ZoneInfo(obj["timezone"])
                except ZoneInfoNotFoundError:
                    raise HTTPException(422, "INVALID_TIMEZONE") from None
            for value in obj.values():
                intervals(value)
        elif isinstance(obj, list):
            for value in obj:
                intervals(value)

    intervals(body)
    return body


def origin_guard(request):
    if request.headers.get("origin") != configuration()["origin"] or request.headers.get(
        "sec-fetch-site"
    ) not in (None, "same-origin"):
        raise HTTPException(403, "CSRF_DENIED")


def limited(request, scope, maximum=20):
    # Trusted peer only; ignore X-Forwarded-For. BFF aggregation is supplemented by contact/session quotas.
    peer = request.client.host if request.client else "unknown"
    hashed = hmac.digest(os.environ["FOC_CONTACT_KEY"].encode(), f"{scope}:{peer}".encode(), "sha256")
    with connection(request) as conn:
        allowed = conn.execute("SELECT platform.intake_limit(%s,%s)", (hashed, maximum)).fetchone()[0]
    if not allowed:
        raise HTTPException(429, "RATE_LIMITED", headers={"Retry-After": "600"})


def challenge_guard(request, command):
    origin_guard(request)
    token = request.headers.get("x-intake-challenge", "")
    browser = request.cookies.get(BROWSER, "")
    if len(token) != 43 or len(browser) != 43:
        raise HTTPException(401, "INTAKE_CHALLENGE_REQUIRED")
    with connection(request) as conn:
        valid = conn.execute(
            "SELECT platform.intake_authorize(%s,%s,%s)", (digest(token), digest(browser), command)
        ).fetchone()[0]
    if not valid:
        raise HTTPException(401, "INTAKE_CHALLENGE_REQUIRED")


def reporter(request, mutation=False):
    token = request.cookies.get(COOKIE, "")
    if len(token) != 43:
        raise HTTPException(401, "REPORTER_SESSION_REQUIRED")
    with connection(request) as conn:
        ctx = conn.execute("SELECT platform.reporter_context(%s)", (digest(token),)).fetchone()[0]
    if ctx is None:
        raise HTTPException(401, "REPORTER_SESSION_REQUIRED")
    if mutation:
        mutation_guard(request, bytes.fromhex(ctx["csrf_hash"]))
    return token, ctx


def accepted(request, extra=None):
    return {"request_id": request.state.request_id, "message_key": "report.received", **(extra or {})}


def delivery(payload, receipt):
    # Isolated encrypted operator sink; no application read route or artifact publication.
    name = Path("/delivery") / (hashlib.sha256(receipt.encode()).hexdigest() + ".json")
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as stream:
        stream.write(payload)


@router.post("/v1/public/intake-challenges", status_code=201)
def challenge(request: Request):
    origin_guard(request)
    limited(request, "challenge", 100)
    token = secrets.token_urlsafe(32)
    browser = request.cookies.get(BROWSER) or secrets.token_urlsafe(32)
    if len(browser) != 43:
        browser = secrets.token_urlsafe(32)
    with connection(request) as conn:
        conn.execute("SELECT platform.intake_challenge(%s,%s)", (digest(token), digest(browser)))
    response = JSONResponse({"challenge": token, "expires_in": 600}, status_code=201)
    response.set_cookie(
        BROWSER, browser, max_age=600, secure=True, httponly=True, samesite="strict", path="/"
    )
    return response


@router.post("/v1/public/reports/{registry}", status_code=202)
def submit(
    registry: str,
    body: dict,
    request: Request,
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
):
    if registry not in ("missing", "found"):
        raise HTTPException(404, "NOT_FOUND")
    challenge_guard(request, idempotency_key)
    limited(request, "submit", 100)
    validate("MissingReport" if registry == "missing" else "FoundReport", body)
    contact = body["reporter"]["encrypted_transport_contact"].strip().lower()
    if (
        not contact.endswith("@synthetic.invalid")
        or len(contact) > 320
        or body["notice_version"] != NOTICE
        or "intake" not in body["processing_purposes"]
    ):
        raise HTTPException(422, "SYNTHETIC_NOTICE_AND_CONTACT_REQUIRED")
    # Reporter relationship remains a claim. Neither contact possession nor this notice proves guardianship.
    receipt = secrets.token_urlsafe(32)
    claims = {k: v for k, v in body.items() if k not in ("reporter", "restricted_custody")}
    event_key = "missing_at" if registry == "missing" else "discovered_at"
    event = body[event_key]
    if "local_date_lower" in event or "local_date_upper" in event:
        if (
            not event.get("local_date_lower")
            or not event.get("local_date_upper")
            or event["local_date_lower"] > event["local_date_upper"]
            or event["lower"] is not None
            or event["upper"] is not None
            or event["precision"] != "day"
        ):
            raise HTTPException(422, "INVALID_INTERVAL")
        zone = ZoneInfo(event["timezone"])
        claims[event_key] = {
            **event,
            "lower": datetime.combine(date.fromisoformat(event["local_date_lower"]), time.min, zone)
            .astimezone(UTC)
            .isoformat(),
            "upper": datetime.combine(date.fromisoformat(event["local_date_upper"]), time.max, zone)
            .astimezone(UTC)
            .isoformat(),
        }
    claims["relationship_claim"] = body["reporter"]["relationship"]
    with connection(request) as conn:
        if not conn.execute(
            "SELECT platform.intake_limit(%s,10)", (contact_hash("submit:" + contact),)
        ).fetchone()[0]:
            raise HTTPException(429, "RATE_LIMITED")
        result = conn.execute(
            "SELECT platform.intake_command(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                digest(request.cookies.get(BROWSER, "")),
                ORG,
                registry,
                digest(receipt),
                contact_hash(contact),
                seal(contact, True),
                seal(receipt, True),
                seal(claims),
                idempotency_key,
                body_hash(body),
            ),
        ).fetchone()[0]
        # Exact location, if supplied, remains encrypted and excluded from normal staff/reporter projections.
        if body.get("restricted_custody"):
            conn.execute(
                "SELECT platform.restricted_intake_record(%s,%s)",
                (
                    digest(unseal(result["receipt_ciphertext"], True)),
                    seal(
                        {
                            "case_id": result["case_id"],
                            "restricted_custody": body["restricted_custody"],
                            "welfare": body.get("welfare"),
                        },
                        True,
                    ),
                ),
            )
        draft_token = request.cookies.get("__Host-foc-draft", "")
        if len(draft_token) == 43:
            conn.execute("SELECT platform.draft_delete(%s)", (digest(draft_token),))
    receipt = unseal(result["receipt_ciphertext"], True)
    response = JSONResponse(accepted(request, {"receipt": receipt}), status_code=202)
    response.delete_cookie("__Host-foc-draft", secure=True, httponly=True, samesite="strict", path="/")
    return response


@router.post("/v1/public/access-requests", status_code=202)
def access_request(
    body: dict, request: Request, idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")]
):
    challenge_guard(request, idempotency_key)
    limited(request, "access", 100)
    validate("AccessRequest", body)
    receipt = body["receipt"]
    code = secrets.token_urlsafe(24)
    with connection(request) as conn:
        if not conn.execute(
            "SELECT platform.intake_limit(%s,5)", (contact_hash("access:" + receipt),)
        ).fetchone()[0]:
            raise HTTPException(429, "RATE_LIMITED")
        result = conn.execute(
            "SELECT platform.access_request_command(%s,%s,%s,%s,%s,%s,%s)",
            (
                digest(request.cookies.get(BROWSER, "")),
                digest(receipt),
                contact_hash(body["contact"]),
                digest(code),
                seal(
                    {
                        "contact": body["contact"],
                        "receipt": receipt,
                        "code": code,
                        "message_key": "neutral.verification",
                    },
                    True,
                ),
                idempotency_key,
                body_hash(body),
            ),
        ).fetchone()[0]
    if result is not None and result["delivery_ciphertext"] is not None:
        try:
            delivery(result["delivery_ciphertext"], receipt)
        except OSError:
            raise HTTPException(503, "VERIFICATION_UNAVAILABLE") from None
    return accepted(request)


@router.post("/v1/public/access-exchanges")
def exchange(body: dict, request: Request, idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")]):
    challenge_guard(request, idempotency_key)
    limited(request, "exchange", 100)
    validate("AccessExchange", body)
    token = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(32)
    with connection(request) as conn:
        valid = conn.execute(
            "SELECT platform.reporting_exchange(%s,%s,%s,%s)",
            (digest(body["receipt"]), digest(body["code"]), digest(token), digest(csrf)),
        ).fetchone()[0]
    if not valid:
        raise HTTPException(401, "INVALID_VERIFICATION")
    response = JSONResponse({"status": "verified", "expires_in": 1800})
    response.set_cookie(COOKIE, token, max_age=1800, secure=True, httponly=True, samesite="strict", path="/")
    response.set_cookie(
        "__Host-foc-reporter-csrf",
        csrf,
        max_age=1800,
        secure=True,
        httponly=False,
        samesite="strict",
        path="/",
    )
    return response


def project_claims(versions):
    original = []
    supplements = []

    def claim(field, value, source, structured=False):
        return {
            "field": field,
            "value": json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            if structured
            else str(value),
            "source_id": source,
            "encoding": "json" if structured else "text",
        }

    for version in versions:
        if version["kind"] not in ("original", "supplement"):
            continue
        body = unseal(version["ciphertext"])
        if version["kind"] == "original":
            for key, value in body.items():
                if key in ("notice_version", "processing_purposes"):
                    continue
                if key == "names" and value:
                    original.extend(claim(key, [name], version["id"], True) for name in value)
                elif key == "distinguishing_marks" and value:
                    original.extend(claim(key, mark, version["id"]) for mark in value)
                elif key == "general_location":
                    original.append(
                        claim(
                            key, {k: v for k, v in value.items() if k != "description"}, version["id"], True
                        )
                    )
                    if value.get("description"):
                        original.append(
                            claim("general_location_description", value["description"], version["id"])
                        )
                else:
                    original.append(claim(key, value, version["id"], isinstance(value, (dict, list))))
        else:
            supplements.extend(claim(c["field"], c["value"], version["id"]) for c in body["claims"])
    # Originals remain visible alongside the most recent supplementary claims; stored revisions are never replaced.
    return original + supplements[-max(0, 100 - len(original)) :] if len(original) < 100 else original[:100]


@router.get("/v1/reporter/submission")
def submission(request: Request):
    token, _ = reporter(request)
    with connection(request) as conn:
        result = conn.execute("SELECT platform.reporter_versions(%s)", (digest(token),)).fetchone()[0]
        upload_states = conn.execute(
            "SELECT platform.reporter_upload_states(%s)", (digest(token),)
        ).fetchone()[0]
    return {
        "id": result["id"],
        "intake_status": result["lifecycle"],
        "submitted_claims": project_claims(result["versions"]),
        "upload_statuses": upload_states,
    }


@router.post("/v1/reporter/{action}", status_code=202)
def reporter_append(
    action: str,
    body: dict,
    request: Request,
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
):
    if action not in ("supplements", "contact"):
        raise HTTPException(404, "NOT_FOUND")
    token, _ = reporter(request, True)
    limited(request, "reporter-append", 100)
    validate("Supplement" if action == "supplements" else "RelayMessage", body)
    if action == "supplements" and body["evidence_refs"]:
        raise HTTPException(422, "EVIDENCE_MUST_BE_OWN_UPLOAD")
    with connection(request) as conn:
        conn.execute(
            "SELECT platform.reporter_append(%s,%s,%s,%s,%s)",
            (
                digest(token),
                "supplement" if action == "supplements" else "relay",
                seal(body),
                idempotency_key,
                body_hash(body),
            ),
        )
    return accepted(request)


@router.post("/v1/public/abuse-reports", status_code=202)
def concern(body: dict, request: Request, idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")]):
    challenge_guard(request, idempotency_key)
    limited(request, "concern", 20)
    validate("AbuseReport", body)
    with connection(request) as conn:
        conn.execute(
            "SELECT platform.concern_command(%s,%s,%s,%s)",
            (digest(request.cookies.get(BROWSER, "")), seal(body, True), idempotency_key, body_hash(body)),
        )
    return accepted(request)


@router.get("/v1/public/safety")
def safety(locale: str = "ar"):
    if locale not in ("ar", "en"):
        raise HTTPException(422, "INVALID_LOCALE")
    return {
        "locale": locale,
        "policy_version": NOTICE,
        "text": "بيئة اصطناعية فقط. لا تشارك مواقع الأطفال أو ترتب تسليم طفل. تأكيد وسيلة الاتصال لا يثبت الوصاية."
        if locale == "ar"
        else "Synthetic environment only. Do not share child locations or arrange a child handover. Contact verification does not establish guardianship.",
    }


@router.post("/v1/reporter/upload-intents", status_code=201)
def upload_intent(
    body: dict, request: Request, idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")]
):
    token, _ = reporter(request, True)
    validate("UploadIntent", body)
    iid, oid, qkey = uuid4(), uuid4(), uuid4()
    meta = {k: body.get(k) for k in ("capture_date", "capture_age", "purpose", "subject_statement")}
    with connection(request) as conn:
        result = conn.execute(
            "SELECT platform.upload_create(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                digest(token),
                iid,
                oid,
                qkey,
                bytes.fromhex(body["sha256"]),
                body["bytes"],
                body["mime"],
                media.new_key(),
                seal(meta),
                idempotency_key,
                body_hash(body),
            ),
        ).fetchone()[0]
    return {
        "id": result["id"],
        "expires_at": result["expires_at"],
        "upload_url": configuration()["origin"] + "/v1/reporter/upload-intents/" + result["id"] + "/content",
        "required_headers": {"Content-Type": body["mime"]},
    }


@router.put("/v1/reporter/upload-intents/{iid}/content")
async def upload_content(iid: UUID, request: Request):
    token, _ = reporter(request, True)
    with connection(request) as conn:
        intent = conn.execute("SELECT platform.upload_get(%s,%s)", (digest(token), iid)).fetchone()[0]
    if request.headers.get("content-type") != intent["expected_mime"]:
        raise HTTPException(415, "UNSUPPORTED_MEDIA")
    data = bytearray()
    async for block in request.stream():
        data.extend(block)
        if len(data) > min(media.MAX_BYTES, intent["expected_bytes"]):
            raise HTTPException(413, "TOO_LARGE")
    if len(data) != intent["expected_bytes"] or media.checksum(data) != intent["expected_hash"][2:]:
        raise HTTPException(422, "CHECKSUM_MISMATCH")
    if intent["state"] in ("uploaded", "scanning", "ready"):
        return {"object_version": intent["quarantine_version"], "sha256": media.checksum(data)}
    if intent["state"] != "pending":
        raise HTTPException(409, "UPLOAD_NOT_WRITABLE")
    try:
        version = media.put_once(
            "foc-quarantine", intent["quarantine_key"], bytes(data), intent["wrapped_key"], role="API"
        )
    except media.FAILURES:
        raise HTTPException(503, "STORAGE_UNAVAILABLE") from None
    with connection(request) as conn:
        conn.execute("SELECT platform.upload_bind(%s,%s,%s)", (digest(token), iid, version))
    return {"object_version": version, "sha256": media.checksum(data)}


@router.post("/v1/reporter/upload-intents/{iid}/complete", status_code=202)
def complete_upload(
    iid: UUID, body: dict, request: Request, idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")]
):
    token, _ = reporter(request, True)
    validate("UploadComplete", body)
    with connection(request) as conn:
        conn.execute(
            "SELECT platform.upload_complete_command(%s,%s,%s,%s,%s,%s)",
            (
                digest(token),
                iid,
                body["object_version"],
                bytes.fromhex(body["sha256"]),
                idempotency_key,
                body_hash(body),
            ),
        )
    return accepted(request)


def staff(request, organization_id, mutation=False):
    principal, _ = authenticate(request, mutation)
    return principal


@router.get("/v1/staff/cases")
def cases(request: Request, organization_id: UUID, limit: int = 25, cursor: UUID | None = None):
    principal = staff(request, organization_id)
    if not 1 <= limit <= 100:
        raise HTTPException(422, "INVALID_LIMIT")
    with connection(request, principal, organization_id) as conn:
        member(conn, organization_id)
        rows = conn.execute(
            "SELECT id,registry,lifecycle,revision,verification_status FROM app.cases WHERE (%s::uuid IS NULL OR id>%s) ORDER BY id LIMIT %s",
            (cursor, cursor, limit + 1),
        ).fetchall()
        conn.execute("SELECT platform.case_list_audit(%s)", (organization_id,))
    items = [
        dict(zip(["id", "registry", "lifecycle", "revision", "verification_status"], [str(r[0]), *r[1:]]))
        for r in rows[:limit]
    ]
    for item in items:
        item["organization_id"] = str(organization_id)
    return {"items": items, "next_cursor": str(rows[limit - 1][0]) if len(rows) > limit else None}


@router.get("/v1/staff/cases/{cid}")
def case_detail(cid: UUID, request: Request, organization_id: UUID):
    principal = staff(request, organization_id)
    with connection(request, principal, organization_id) as conn:
        member(conn, organization_id)
        result = conn.execute("SELECT platform.staff_versions(%s,%s)", (organization_id, cid)).fetchone()[0]
        evidence = conn.execute("SELECT platform.staff_evidence(%s,%s)", (organization_id, cid)).fetchone()[0]
        photos = conn.execute("SELECT platform.media_list(%s,%s)", (organization_id, cid)).fetchone()[0]
    assertions = [
        {**{k: v for k, v in row.items() if k != "ciphertext"}, **unseal(row["ciphertext"])}
        for row in evidence["assertions"]
    ]
    notes = [
        {**{k: v for k, v in row.items() if k != "ciphertext"}, **unseal(row["ciphertext"])}
        for row in evidence["notes"]
    ]
    for p in photos:
        p["capture"] = unseal(p.pop("metadata_ciphertext"))
    result["summary"]["organization_id"] = str(organization_id)
    dto = {
        "summary": result["summary"],
        "claims": project_claims(result["versions"]),
        "verified_assertions": [a for a in assertions if a["state"] == "verified"][-100:],
        "assertions": assertions[-100:],
        "reporter_messages": [
            {"id": v["id"], "message": unseal(v["ciphertext"])["message"]}
            for v in result["versions"][-100:]
            if v["kind"] == "relay"
        ],
        "evidence_refs": [e["id"] for e in evidence["evidence"]],
        "assignment": result["assignment"],
        "contact_verified": result["contact_verified"],
        "contact_paused": result["contact_paused"],
        "notes": notes[-100:],
        "photographs": photos,
    }
    return JSONResponse(dto, headers={"ETag": '"' + str(result["summary"]["revision"]) + '"'})


def case_command(
    cid: UUID,
    action: str,
    body: dict,
    request: Request,
    organization_id: UUID,
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
    if_match: Annotated[str, Header(alias="If-Match")],
):
    operations = {
        "transitions": ("transition", "Transition"),
        "assignments": ("assignment", "Assignment"),
        "notes": ("note", "Note"),
        "assertions": ("assertion", "Assertion"),
        "moderation": ("moderation", "Moderation"),
    }
    if action not in operations:
        raise HTTPException(503, "PHASE_DISABLED")
    principal = staff(request, organization_id, True)
    operation, schema = operations[action]
    validate(schema, body)
    try:
        expected = int(if_match.strip('"'))
    except ValueError:
        raise HTTPException(422, "INVALID_REVISION") from None
    with connection(request, principal, organization_id) as conn:
        member(conn, organization_id)
        result = conn.execute(
            "SELECT platform.staff_command(%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                organization_id,
                cid,
                operation,
                Jsonb(body),
                seal(body),
                expected,
                idempotency_key,
                body_hash(body),
            ),
        ).fetchone()[0]
    return result


def staff_action_endpoint(action_name):
    def endpoint(
        cid: UUID,
        body: dict,
        request: Request,
        organization_id: UUID,
        idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
        if_match: Annotated[str, Header(alias="If-Match")],
    ):
        return case_command(cid, action_name, body, request, organization_id, idempotency_key, if_match)

    return endpoint


for action_name in ["transitions", "assignments", "notes", "assertions", "moderation"]:
    router.add_api_route(
        "/v1/staff/cases/{cid}/" + action_name, staff_action_endpoint(action_name), methods=["POST"]
    )


@router.get("/v1/staff/media/{mid}/content")
def content(mid: UUID, request: Request, organization_id: UUID):
    principal = staff(request, organization_id)
    with connection(request, principal, organization_id) as conn:
        member(conn, organization_id)
        permitted = conn.execute("SELECT platform.media_read(%s,%s)", (organization_id, mid)).fetchone()[0]
        try:
            data = media.get(
                "GATEWAY", "foc-derivative", permitted["key"], permitted["version"], permitted["wrapped_key"]
            )
        except media.FAILURES:
            raise HTTPException(503, "MEDIA_UNAVAILABLE") from None
        if media.checksum(data) != permitted["sha256"]:
            raise HTTPException(503, "MEDIA_INTEGRITY_FAILURE")
        # Keep the transaction through the read, then recheck current grants before any bytes leave.
        conn.execute("SELECT platform.media_read(%s,%s)", (organization_id, mid))
    return Response(
        data,
        media_type="image/png",
        headers={
            "Content-Disposition": 'inline; filename="review.png"',
            "Cache-Control": "no-store",
            "Referrer-Policy": "no-referrer",
        },
    )


@router.get("/v1/public/drafts")
def read_draft(request: Request):
    token = request.cookies.get("__Host-foc-draft", "")
    if len(token) != 43:
        return {"draft": None, "revision": 0}
    with connection(request) as conn:
        result = conn.execute("SELECT platform.draft_read(%s)", (digest(token),)).fetchone()[0]
    return (
        {"draft": unseal(result["ciphertext"], True), "revision": result["revision"]}
        if result
        else {"draft": None, "revision": 0}
    )


@router.post("/v1/public/drafts")
def save_draft(
    body: dict, request: Request, idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")]
):
    challenge_guard(request, idempotency_key)
    limited(request, "draft", 100)
    validate("PrivateDraft", body)
    fields = body["fields"]
    contact = fields.get("contact", "")
    if contact and not contact.strip().lower().endswith("@synthetic.invalid"):
        raise HTTPException(422, "SYNTHETIC_CONTACT_REQUIRED")
    token = request.cookies.get("__Host-foc-draft", "")
    if len(token) != 43:
        token = secrets.token_urlsafe(32)
    with connection(request) as conn:
        revision = conn.execute(
            "SELECT platform.draft_command(%s,%s,%s,%s,%s)",
            (
                digest(token),
                seal({"registry": body["registry"], "fields": fields}, True),
                body["revision"],
                idempotency_key,
                body_hash(body),
            ),
        ).fetchone()[0]
    response = JSONResponse({"revision": revision})
    response.set_cookie(
        "__Host-foc-draft", token, max_age=604800, secure=True, httponly=True, samesite="strict", path="/"
    )
    return response


@router.post("/v1/reporter/logout")
def logout_reporter(body: dict, request: Request):
    if body:
        raise HTTPException(422, "INVALID_REQUEST")
    token, _ = reporter(request, True)
    with connection(request) as conn:
        conn.execute("SELECT platform.reporter_logout(%s)", (digest(token),))
    response = JSONResponse({"status": "signed_out"})
    for name in [COOKIE, "__Host-foc-reporter-csrf"]:
        response.delete_cookie(name, secure=True, path="/")
    return response
