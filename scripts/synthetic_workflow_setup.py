"""Operator-only, closed procedural fixtures. No browser import or external acquisition."""

import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb

from scripts.identity_setup import ORG_A, WORKFLOW_USERS, fixture_id, workflow_person_name

QUERY = fixture_id("workflow-missing")
CANDIDATE = fixture_id("workflow-found")
SCENARIO = fixture_id("workflow-ranked-scenario-v1")
REVERSE = fixture_id("workflow-ranked-reverse-v1")
SECOND = fixture_id("workflow-found-contradictory")
THIRD = fixture_id("workflow-found-insufficient")
CASES = [QUERY, CANDIDATE, SECOND, THIRD]
USERS = WORKFLOW_USERS


def seed(conn):
    if conn.execute("SELECT data_class FROM platform.environment").fetchone() != ("synthetic",):
        raise RuntimeError("Synthetic environment required")
    for cid, registry in [(QUERY, "missing"), (CANDIDATE, "found"), (SECOND, "found"), (THIRD, "found")]:
        conn.execute(
            "INSERT INTO app.cases(organization_id,id,registry,lifecycle) VALUES(%s,%s,%s,'review') ON CONFLICT DO NOTHING",
            (ORG_A, cid, registry),
        )
        # Fictional metadata only. Reporter access is a pipeline fixture, not guardian verification.
        conn.execute(
            "INSERT INTO platform.report_submissions(organization_id,case_id,receipt_hash,contact_hash,contact_ciphertext,receipt_ciphertext,contact_verified) VALUES(%s,%s,%s,%s,'fixture','fixture',true) ON CONFLICT DO NOTHING",
            (
                ORG_A,
                cid,
                hashlib.sha256(cid.encode()).digest(),
                hashlib.sha256(b"fictional-contact").digest(),
            ),
        )
        conn.execute(
            "INSERT INTO app.legal_bases(organization_id,case_id,processing_purpose,authority_type,notice_version,effective_from,effective_until) SELECT %s,%s,'intake','synthetic_only','synthetic-2d-v1',now(),now()+interval '1 day' WHERE NOT EXISTS(SELECT 1 FROM app.legal_bases WHERE organization_id=%s AND case_id=%s)",
            (ORG_A, cid, ORG_A, cid),
        )
    for name in USERS:
        pid = fixture_id(name)
        role = "safeguarding" if name.startswith("synthetic-workflow-peer-") else "supervisor"
        conn.execute(
            "INSERT INTO app.memberships(organization_id,principal_id,role,expires_at) VALUES(%s,%s,%s,now()+interval '1 day') ON CONFLICT(organization_id,principal_id,role) DO UPDATE SET expires_at=excluded.expires_at,revoked_at=NULL",
            (ORG_A, pid, role),
        )
        for cid in CASES:
            for permission in ["case.read", "case.write", "media.read", "matching.request", "audit.read"]:
                conn.execute(
                    "INSERT INTO app.case_grants(organization_id,case_id,principal_id,permission,purpose,granted_by,expires_at) VALUES(%s,%s,%s,%s,'case_management',%s,now()+interval '1 day') ON CONFLICT(organization_id,case_id,principal_id,permission,purpose) DO UPDATE SET expires_at=excluded.expires_at,revoked_at=NULL",
                    (ORG_A, cid, pid, permission, pid),
                )


def prepare_media(conn):
    from foc_api import media, worker
    from foc_api.reporting import seal
    from foc_api.research.pipeline import fixture

    for side, cid, count in [("query", QUERY, 3), ("candidate", CANDIDATE, 2)]:
        if (
            conn.execute(
                "SELECT count(*) FROM app.photo_derivatives WHERE organization_id=%s AND case_id=%s",
                (ORG_A, cid),
            ).fetchone()[0]
            == count
        ):
            continue
        token = hashlib.sha256(("workflow-pipeline:" + cid).encode()).digest()
        access = fixture_id(cid + "-pipeline")
        conn.execute(
            "INSERT INTO app.report_access(organization_id,id,case_id,capability_hash,expires_at) VALUES(%s,%s,%s,%s,now()+interval '1 day') ON CONFLICT DO NOTHING",
            (ORG_A, access, cid, token),
        )
        conn.execute(
            "INSERT INTO platform.report_sessions(hash,organization_id,case_id,csrf_hash,expires_at,access_id) VALUES(%s,%s,%s,%s,now()+interval '1 day',%s) ON CONFLICT DO NOTHING",
            (token, ORG_A, cid, token, access),
        )
        conn.commit()
        existing = conn.execute(
            "SELECT count(*) FROM app.upload_intents WHERE organization_id=%s AND case_id=%s", (ORG_A, cid)
        ).fetchone()[0]
        for index in range(existing, count):
            data = fixture(index + (0 if side == "query" else 8))
            key = media.new_key()
            iid, oid, qkey = uuid4(), uuid4(), uuid4()
            sha = hashlib.sha256(data).digest()
            conn.execute(
                "SELECT platform.upload_create(%s,%s,%s,%s,%s,%s,'image/png',%s,%s,%s,%s)",
                (
                    token,
                    iid,
                    oid,
                    qkey,
                    sha,
                    len(data),
                    key,
                    seal({"source": "procedural-fixture-2d-v1"}),
                    uuid4(),
                    sha,
                ),
            )
            conn.commit()
            version = media.put_once("foc-quarantine", str(qkey), data, key, role="API")
            conn.execute("SELECT platform.upload_bind(%s,%s,%s)", (token, iid, version))
            conn.execute("SELECT platform.upload_complete(%s,%s,%s,%s)", (token, iid, version, sha))
            conn.commit()
    for _ in range(100):
        if not worker.once():
            break
    if (
        conn.execute(
            "SELECT count(*) FROM app.photo_derivatives WHERE organization_id=%s AND case_id IN (%s,%s)",
            (ORG_A, QUERY, CANDIDATE),
        ).fetchone()[0]
        != 5
    ):
        raise RuntimeError("Actual scan/derivative pipeline incomplete")


def provision(conn):
    from foc_api.research.pipeline import fixture

    epoch = os.environ["FOC_WORKFLOW_EPOCH"]
    instance = conn.execute("SELECT instance_id FROM platform.environment").fetchone()[0]
    cases = []
    photos = []
    allowed = {hashlib.sha256(fixture(i)).hexdigest() for i in range(32)}
    for side, cid in [
        ("query", QUERY),
        ("candidate", CANDIDATE),
        ("candidate", SECOND),
        ("candidate", THIRD),
    ]:
        row = conn.execute(
            "SELECT revision,deletion_generation,registry FROM app.cases WHERE organization_id=%s AND id=%s",
            (ORG_A, cid),
        ).fetchone()
        claims = conn.execute(
            "SELECT encode(public.digest(coalesce(string_agg(id::text||body_ciphertext,'' ORDER BY id),''),'sha256'),'hex') FROM platform.report_versions WHERE organization_id=%s AND case_id=%s",
            (ORG_A, cid),
        ).fetchone()[0]
        cases.append(
            {"id": cid, "revision": row[0], "generation": row[1], "registry": row[2], "claims_digest": claims}
        )
        rows = conn.execute(
            "SELECT o.id,o.content_sha256,o.object_version,m.expected_hash FROM app.objects o JOIN platform.upload_metadata m ON m.organization_id=o.organization_id AND m.derivative_key=o.opaque_key WHERE o.organization_id=%s AND o.case_id=%s AND o.bucket_class='derivative' ORDER BY m.intent_id",
            (ORG_A, cid),
        ).fetchall()
        for i, (pid, sha, version, original) in enumerate(rows):
            if bytes(original).hex() not in allowed:
                raise RuntimeError("Unapproved media cannot enter closed scenario")
            photos.append(
                {
                    "id": str(pid),
                    "case_id": cid,
                    "side": side,
                    "sha256": bytes(sha).hex(),
                    "object_version": version,
                    "source_kind": "procedural_fixture",
                    "synthetic": True,
                    "capture_date": {
                        "lower": "2018-01-01" if i == 0 else None,
                        "upper": "2018-12-31" if i == 0 else None,
                        "precision": "interval" if i == 0 else "unknown",
                    },
                    "capture_age_months": {
                        "lower": 18 if i == 0 else None,
                        "upper": 30 if i == 0 else None,
                        "knowledge": "estimated" if i == 0 else "unknown",
                    },
                    "age_reference": {
                        "lower": "2018-01-01" if i == 0 else None,
                        "upper": "2018-12-31" if i == 0 else None,
                    },
                    "quality": "face_quality_not_measured",
                }
            )
    explanations = [
        {"code": code, "case_id": cid, "source_ref": fixture_id(code + cid), "kind": kind}
        for code, kind, cid in [
            ("SUPPORTING_FIXTURE_CLAIM", "supporting", QUERY),
            ("CONTRADICTORY_FIXTURE_CLAIM", "contradictory", CANDIDATE),
            ("CAPTURE_DATE_UNCERTAIN", "uncertain", QUERY),
            ("CONTRADICTORY_FIXTURE_CLAIM", "contradictory", SECOND),
            ("CAPTURE_DATE_UNCERTAIN", "uncertain", THIRD),
        ]
    ]
    for sid, query, candidate in [(SCENARIO, QUERY, CANDIDATE), (REVERSE, CANDIDATE, QUERY)]:
        selected = [{**p, "side": "query" if p["case_id"] == query else "candidate"} for p in photos]
        manifest = {
            "data_class": "synthetic",
            "provider": "fixture-scenario-v1",
            "query_case_id": query,
            "query_revision": 1,
            "cases": cases,
            "photos": selected,
            "candidates": [
                {"case_id": c} for c in ([CANDIDATE, SECOND, THIRD] if query == QUERY else [candidate])
            ],
            "result_source": {
                "kind": "fixture_scenario",
                "provider_version": "fixture-scenario-v1",
                "model_version": None,
                "embedding_space_id": None,
                "score": {
                    "metric": "scripted_ordinal",
                    "value": None,
                    "semantics": "fixture_order_only_not_identity_probability",
                },
                "photo_refs": [p["id"] for p in selected],
                "provenance": "closed_procedural_fixture",
                "policy_version": "synthetic-2d-v1",
                "calibration_status": "not_applicable_synthetic_demo",
            },
            "explanations": explanations,
        }
        conn.execute(
            "INSERT INTO platform.synthetic_workflow_scenarios VALUES(%s,%s,'fixture-2d-v1',%s,%s,%s,encode(public.digest(%s::jsonb::text,'sha256'),'hex'),now()+interval '1 day',NULL) ON CONFLICT(organization_id,id) DO NOTHING",
            (ORG_A, sid, instance, epoch, Jsonb(manifest), Jsonb(manifest)),
        )
        for name in USERS:
            person_name = workflow_person_name(name)
            conn.execute(
                "INSERT INTO platform.synthetic_workflow_grants VALUES(%s,%s,%s,%s,true,'synthetic_investigation',%s,now()+interval '1 day',NULL) ON CONFLICT DO NOTHING",
                (
                    ORG_A,
                    sid,
                    fixture_id(name),
                    fixture_id(person_name + "-person"),
                    [
                        "view",
                        "run",
                        "cancel",
                        "review",
                        "collaborate",
                        "assign",
                        "peer",
                        "independent",
                        "audit",
                    ],
                ),
            )
    conn.execute(
        "UPDATE platform.synthetic_workflow_scenarios SET revoked_at=now() WHERE id IN (%s,%s)",
        (fixture_id("workflow-scenario"), fixture_id("workflow-reverse")),
    )
    conn.commit()
    Path(".runtime/workflow-fixtures.json").write_text(
        json.dumps(
            {
                "organization_id": ORG_A,
                "query_case_id": QUERY,
                "candidate_case_id": CANDIDATE,
                "scenario_id": SCENARIO,
                "users": {name: fixture_id(name) for name in USERS},
            }
        )
    )


def main():
    with psycopg.connect(os.environ["FOC_DATABASE_ADMIN_URL"]) as conn:
        seed(conn)
        conn.commit()
        prepare_media(conn)
        provision(conn)
    print("Closed fictional workflow fixtures provisioned through actual scanner and private storage")


if __name__ == "__main__":
    main()
