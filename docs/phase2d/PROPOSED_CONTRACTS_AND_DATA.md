# Phase 2D proposed contracts, data and authorization

Status: design only; **all operations, tables, migrations and tests below are unimplemented/pending**. This is not an executable OpenAPI or SQL change. Follow [the implementation specification](IMPLEMENTATION_SPEC.md) and existing [OpenAPI](../contracts/openapi.json). No existing operation ID or response is silently repurposed.

## HTTP boundary

Proposed common prefix: `/v1/staff/synthetic-workflow`. Next forwards only each fixed method/path below to the existing API, using server-held sessions, exact Origin/CSRF/Fetch Metadata checks, no arbitrary upstream URL and no browser bearer-token storage. Existing `/v1/staff/cases/{id}/matching-runs`, `/leads` and generic review/biometric/disclosure/release operations stay disabled. No public/reporter equivalent is added.

All DTOs are closed (`additionalProperties: false`), UUIDs/cursors bounded and parsed, text rendered as text and responses allowlisted. Body ceiling remains within the existing 64 KiB ordinary command budget; no upload endpoint is introduced. Proposed operation IDs below are names to reserve during authorized implementation, not implemented API IDs.

| ID | Method/path after prefix | Purpose / authorization beyond live MFA | Success |
|---|---|---|---|
| SW-01 | GET `/status` | Current synthetic environment and explicit workspace-view grant; no case/model inventory | 200 fixed synthetic descriptor |
| SW-02 | POST `/cases/{case_id}/runs` | Query read/write plus matching-request grant, scenario entitlement and workflow-run action | 202 opaque run ref |
| SW-03 | GET `/runs/{run_id}` | Query read + workflow view; no hidden candidate totals or IDs | 200 bounded run state |
| SW-04 | POST `/runs/{run_id}/cancellations` | Live run-cancel grant and query write; ownership/supervisor policy | 201 cancellation event ref |
| SW-05 | GET `/cases/{case_id}/leads` | Query read + workflow view; candidate read filters applied before ordering/pagination | 200 visible lead page |
| SW-06 | GET `/leads/{lead_id}/comparison` | Both case reads and workflow view; media/source projections independently scoped | 200 permitted snapshot |
| SW-07 | GET `/leads/{lead_id}/photos/{photo_id}/content` | Both case reads, relevant media read and photo belongs to this exact sealed pair/snapshot | 200 clean fixture derivative stream |
| SW-08 | POST `/leads/{lead_id}/reviews` | Both case writes and workflow review; current evidence + canonical reviewer/conflict checks | 201 immutable review ref |
| SW-09 | GET `/leads/{lead_id}/investigation` | Both case reads + workflow view; authorized events/tasks only | 200 paginated investigation |
| SW-10 | POST `/leads/{lead_id}/assignments` | Both case writes, supervisor/workflow-assign action; target already has both reads and valid workflow action grants | 201 assignment event ref |
| SW-11 | POST `/leads/{lead_id}/notes` | Both case writes + workflow collaborate; closed note codes/fixture refs | 201 append-only note ref |
| SW-12 | POST `/leads/{lead_id}/peer-review-requests` | Both case writes + workflow review; lead escalated, evidence current, independent target eligible | 201 neutral private task ref |
| SW-13 | POST `/leads/{lead_id}/independent-reviews` | Both case writes + supervisor/second-review action; distinct canonical person and no conflict | 201 independent event ref |
| SW-14 | GET `/leads/{lead_id}/audit` | Both case reads, both scoped audit grants and workspace view | 200 minimized permitted audit page |

Every write requires a UUID `Idempotency-Key` and `If-Match` for its aggregate revision (case for run creation; run for cancellation; lead/investigation for review/collaboration). Typed references and response shape are frozen in machine-readable OpenAPI only after approval. Reads issue strong aggregate ETags; no sensitive body or stable cross-tenant hash is placed in an error.

Authentication failure is 401. Inaccessible/nonexistent case/run/lead/photo is the same minimized 404 with no counterpart IDs/counts. A forbidden action may return 403 only after the resource is already authorized. Invalid DTO is 422; oversized body 413; changed idempotency body/state conflict 409; stale revision/snapshot 412; rate budget 429. Unavailable environment/IdP/audit/fixture verification returns safe 503, never partial sensitive data or a successful empty match. Globally disabled operations remain static 503 without revealing existence. Tests must bind errors to actual DTO/state effects, not only status text.

## Request and response semantics

Run creation accepts only an allowlisted `scenario_id` and `scenario_version`; the server resolves a closed manifest already bound to the query case. Reject fields selecting a real model, URL, weights, embedding space, gallery organization, dynamic threshold, arbitrary candidate list, custody or approval override. It does not take the existing `MatchingRequest.manifest_ids` list. Scenario permission and all data hashes must hold before a job is queued.

Proposed comparison shape (illustrative fields; IDs and values are fictional):

```json
{
  "lead_id": "00000000-0000-4000-8000-000000000101",
  "data_class": "synthetic",
  "result_source": "fixture_scenario",
  "identity_determination": "not_performed",
  "revision": 3,
  "snapshot_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "query": {"case_ref": "fictional-missing-A", "registry": "missing"},
  "candidate": {"case_ref": "fictional-found-B", "registry": "found"},
  "photos": [{
    "side": "query",
    "photo_id": "00000000-0000-4000-8000-000000000201",
    "source_kind": "procedural_fixture",
    "capture_date": {"lower": "2018-01-01", "upper": "2018-12-31", "precision": "interval"},
    "capture_age_months": {"lower": 18, "upper": 30, "knowledge": "estimated"},
    "age_reference": {"lower": "2018-01-01", "upper": "2018-12-31"},
    "quality": "face_quality_not_measured"
  }],
  "explanations": [{"code": "CAPTURE_DATE_UNCERTAIN", "source_refs": ["fixture-claim-A"]}],
  "review_state": "pending",
  "usability": "current",
  "calibration_status": "not_applicable_synthetic_demo"
}
```

The hash above is a placeholder, not a valid server snapshot. No embedded image bytes, vectors, storage URLs, original EXIF, reporter contact, exact location, weight registry or probability/confidence percentage is returned. Authorized synthetic metric fields may be an explicitly labeled optional extension with metric/space/source versions; fixture-scenario ordering cannot be misrepresented as measured neural similarity.

Photo records are independent: content/version, source event, date interval, precision/knowledge, age interval and reference interval, provenance state, fixture marker and warnings. `null` bounds mean unknown, not absent zeros. Derived gap intervals retain both source photo IDs and the derivation/version; contradictions remain warnings. Do not replace old encrypted capture metadata with these projections.

Review command fields: `outcome` = hold/reject/escalate; nonempty bounded `rationale_codes` from a fixed list; up to 20 typed evidence refs bound to this pair; `snapshot_hash`; and a required uncertainty acknowledgement when specified. Hold may cite `INSUFFICIENT_AUTHORIZED_EVIDENCE` with an empty reference list. Reject/escalate require the scenario-defined visible supporting/contradictory evidence; no forced invented facts. Rationale is not free-form child information. Server computes the signed snapshot from both cases/revisions/deletion generations, run/provider/scenario/policy and exact authorized evidence versions.

Independent review outcomes are `return_for_evidence`, `disagree`, `recuse`, or `workflow_review_complete`; no identity outcome exists. A returned/disagreed event makes no automatic new lead or case transition. Second review is valid only for the exact first-review event and current snapshot. If either changes, require another independent review. Person identity is mapped by controlled synthetic provisioning; two principals mapped to one person fail independence. Missing/ambiguous identity/conflict records fail closed.

Assignment references a provisioned principal and expiry bounded by current memberships, workflow grants and case grants. It does not issue or renew any of them. Notes contain template code, fixture refs and optional bounded structured values allowed by that code. No email, mention delivery, rich HTML, attachment, arbitrary URL, unrestricted narrative or cross-organization sharing is supported. Notifications remain neutral events in the private test sink.

Pagination uses opaque authenticated cursors bound to actor, organization, fixed purpose, query/run/filter/revision and expiry; limit defaults 25, max 50. Reauthorize on every page. Never return raw offsets, hidden totals, denied candidate placeholders, global rank gaps or cursor contents from another principal. Photo projection exposes only permitted records. A record withheld through access denial is not counted as a matching failure in scientific evaluation—no such evaluation runs here.

## Proposed data model

Use additive forward-only migrations beginning after current `0024`; actual numbers and names must be reserved after approval. Keep all 24 existing migration bytes and disabled generic matching/review tables intact. The names below are proposed, not provisioned objects.

| Proposed relation | Contents and keys | Boundary |
|---|---|---|
| `platform.synthetic_workflow_scenarios` | Versioned closed manifest, fixture/source digest, organization, approved fictional case/revision/evidence set and activation epoch | Provisioner-only changes; API/worker cannot label arbitrary records synthetic |
| `platform.synthetic_workflow_grants` | Organization/principal/scenario scope, fixed purpose, closed actions, expiry/revocation and canonical synthetic person binding | Controlled provisioning only; not issued by ordinary org-admin/assignment APIs |
| `app.synthetic_matching_runs` | Query case, scenario/version, request actor/scope/revision, source fingerprint, state, completeness/failure and bounded provider identity | No model-manifest or embedding payload; query-bound tenant FK and known fixture gate |
| `app.synthetic_candidate_leads` | Run, both case refs/revisions/generations, deterministic internal rank, typed explanation/uncertainty refs, current projection revision | Composite tenant FKs; query equals owner case; opposite registries; unique pair/run; no cross-tenant links |
| `app.synthetic_investigation_events` | Immutable review/note/request/second-review/recusal events, actor/person, encrypted structured payload, both snapshot refs, superseded event and timestamp | Append-only; no UPDATE/DELETE by runtime; event refs cannot bind another pair/tenant |
| `app.synthetic_investigation_tasks` | Current owner/status/expiry, lead/review dependency, independent reviewer target and optimistic revision | Assignment is not an ACL; event history remains authoritative |
| `app.synthetic_investigation_assignments` | Task/principal, starts/expiry/revocation and assignment event | Composite task/tenant linkage; active membership/action constraints |
| `platform.synthetic_workflow_commands` | Principal/org/aggregate/action/key scope, canonical body digest, safe outcome ref/revision, timestamp | Replay checks live rights before lookup outcome; no stale response disclosure or duplicate event |

Use the existing job/outbox machinery through new bounded functions and a closed synthetic job/event type. Do not give the worker arbitrary table, research-role, media-original or model-registry access. Queue messages carry minimal opaque run/task refs and versions; no evidence payload or explanatory narrative.

Every new table enables and forces RLS. API/worker roles remain non-owner/NOBYPASSRLS; no broad direct writes or `GRANT ALL`. Definer functions have fixed search paths, parameterized inputs, explicit ACLs, PUBLIC execution revoked and live checks for both cases. RLS on child rows must check the candidate as well as the query; a query-case FK alone is insufficient. Commands and outbox writes share the review transaction. Test direct SQL privileges as the actual non-owner runtime roles, not just HTTP behavior.

Current case grants are purpose-bound to `case_management`. Synthetic-workflow rights add a second explicit purpose gate; no caller-supplied session setting, URL organization or JWT role is trusted. Underlying SQL context remains a trusted server boundary, not protection against stolen arbitrary privileged SQL credentials. A compromised Docker/root operator is outside the synthetic-host isolation claim.

The separate Phase 2B qualification cluster stays separate: no network, credentials or implicit join/import from it. The Phase 2A research role is not granted to API/worker. New application relations contain no vectors, real weight artifacts or unapproved dataset. Future cleared neural demonstration integration must define a separate provider/asset boundary and explicit approval; changing a string flag is insufficient.

## Transactions, audit, recovery and limits

Lock both case rows in canonical ID order, then the lead/task/command key; freeze and compare revisions/generations before mutation. This is a proposed lock order to verify with deterministic race tests. Audit append, event/current projection update, command result and neutral outbox insert either all commit or all roll back. Actor attribution, chained audit events and timestamps are server-generated. Include denied probes without recording guessed child details; write no request body, rationale plaintext, score list, identity/contact/location, token or image into logs.

Audit the successful sensitive read before releasing its projection. An audit outage fails the read/action. Per-tenant sequencing avoids global activity gaps. Hash chaining is tamper evidence under ordinary roles, not immutable against DB administrators; independent write-once export remains a future operational requirement and must not be claimed done by this demo.

Bound runs to 50 distinct candidates and three pre-score selected fixture photos per case; output pages to 50; rationale codes to five; evidence refs to 20; narrative templates to bounded reviewed schema. Event/audit history is cursor-paginated rather than deleted to meet UI limits. Scope rate limits to the live principal/org/command; anonymous-cookie rotation never confers a workspace bucket or grants.

Forward deployment first creates deny-by-default tables/functions, seeds only the closed synthetic manifest and controlled grants, then enables the synthetic workspace only in the verified demo environment. A missing required migration/hash or wrong data class keeps it disabled. Rollback disables entry and new leases first; preserve encrypted event history and use a compatible prior binary or isolated restore. Do not rewrite applied migrations or replay old commands to recreate effects.

Restoring a backup must not reactivate stale sessions, grants, tasks or worker leases. Restore into a quarantined fresh environment with workflow activation disabled and a new environment/activation epoch. A controlled provisioner reconciles the latest synthetic revocation/tombstone fixture ledger and reissues fresh approved synthetic activation only after checks; unavailable control evidence leaves it disabled. Test a post-backup revocation before restoring an older backup. This is a demonstration recovery design, not certification of real-data erasure or a production tombstone service.

No patient/child research, actual face matching, original-file serving, approval bypass or institutional activation is part of this proposed schema. All future executable test evidence remains pending until Phase 2D is explicitly authorized and implemented.
