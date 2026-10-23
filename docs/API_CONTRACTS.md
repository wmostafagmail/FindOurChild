# API and asynchronous contracts

Proposed API v1 / design revision 0.1. This is a preimplementation contract, not an available endpoint. The [OpenAPI outline](contracts/openapi.json) covers representative intake, staff case and approval operations; remaining routes below must be expanded into full machine-readable contracts before phase 1 implementation.

## Transport, authentication and errors

TLS only. JSON UTF-8; UTC RFC3339 instants with separate original timezone/precision. UUIDs are opaque identifiers, never authorization credentials. Staff authorization is OIDC bearer at the backend/BFF boundary with verified issuer/audience/expiry/signature, MFA context and current memberships. Browser BFF uses Secure HttpOnly cookies and CSRF protection. Reporter updates use a short-lived, hashed-at-rest capability bound to a verified contact and one submission.

Idempotency-Key required for create/action POSTs; scope by principal/organization/operation and reject reuse with a different body (409). Expected case/plan revision via If-Match; stale writes return 412, lifecycle conflict 409. Success replay returns the original permitted response, rechecking current access. Store idempotency records under approved retention.

Errors: `{code,message_key,request_id,field_errors?}`. Do not echo uploaded bytes, contact values, face vectors or exact locations. 401 for invalid session, 404 for inaccessible/nonexistent resources alike, 403 for a known permitted resource but forbidden action, 413 size limit, 415 unsupported media, 422 structural validation, 429 with Retry-After. Existence-safe access recovery always returns a neutral 202 independent of contact existence. Request IDs cannot encode child identity.

## Route outline

| Route | Authorization | Request / response and invariant |
|---|---|---|
| POST /v1/public/reports/missing | Scoped intake challenge + rate limits | MissingReport claims/legal notice/contact → 202 neutral receipt; no child search |
| POST /v1/public/reports/found | Scoped intake challenge + rate limits | FoundReport claims/welfare/safe contact → 202; individuals accepted into quarantine |
| POST /v1/public/access-requests | Anti-abuse and contact verification | Contact/receipt → neutral 202; out-of-band code only if authorized |
| POST /v1/public/access-exchanges | Short-lived one-time code | Code+receipt → own-report session; bounded attempts, replay denied |
| GET /v1/reporter/submission | Own-report session | Redacted submitted facts and intake status only |
| POST /v1/reporter/supplements | Own-report session | Additional claims/evidence refs → 202; never mutates verified facts directly |
| POST /v1/reporter/contact | Own-report session | Relay message → 202; no direct shelter/staff personal contacts |
| POST /v1/public/abuse-reports | Anti-abuse challenge | Concern/report reference → neutral 202; no case lookup |
| GET /v1/public/safety | Public, cacheable | Locale-specific approved safety text, policy version |
| POST /v1/reporter/upload-intents | Own-report upload permission | Mime/size/hash claim → intent ID and constrained quarantine upload permission |
| POST /v1/reporter/upload-intents/{id}/complete | Bound capability | Object version/hash → 202 scan job; cannot retarget case/key |
| GET /v1/staff/cases | Active org + case grants | Cursor/filter → permitted summaries only, no inaccessible counts |
| GET /v1/staff/cases/{id} | Case read grant | CaseDTO, ETag, permitted assertions; custody excluded |
| POST /v1/staff/cases/{id}/transitions | Case action + revision | Transition/reason/evidence → new state; legal guards server-side |
| POST /v1/staff/cases/{id}/assignments | Supervisor permission | Staff/team assignment plus valid case grant → audited assignment |
| POST /v1/staff/cases/{id}/assertions | Evidence review grant | Field/value/source/verification → immutable assertion revision |
| POST /v1/staff/photos/{id}/subject-selection | Case media/review grant | Face region IDs/reason → approved selection with revision |
| GET /v1/staff/media/{id}/content | Media grant + purpose | Stream sanitized permitted media with no-store; audit access |
| POST /v1/staff/cases/{id}/matching-runs | Matching purpose grant | Approved model/policy/scope IDs → 202 job reference |
| GET /v1/staff/cases/{id}/leads | Lead grant for both cases | CandidateDTO[] with channels/scores/warnings; federation redaction applies |
| POST /v1/staff/leads/{id}/reviews | Assigned reviewer | Hold/reject/escalate, rationale/evidence, revision → review record |
| POST /v1/staff/cases/{id}/notes | Investigation grant | Text/evidence refs → immutable note revision |
| POST /v1/staff/duplicate-links | Both case grants + supervisor for confirmation | Case pair/reason/status → reversible link |
| POST /v1/staff/disclosure-requests | Safeguarding request permission | Recipient/field mask/purpose/expiry/snapshot → pending request |
| POST /v1/staff/disclosure-requests/{id}/approvals | Independent authorized approver; bilateral if federated | Signed decision → approval, no automatic claimant message |
| POST /v1/staff/reunification-plans | Identity investigation complete | Claimant/evidence/plan → pending plan |
| POST /v1/staff/reunification-plans/{id}/approvals | Distinct safeguarding/authority permissions + recent MFA | Typed approval, snapshot hash, evidence → approval record |
| POST /v1/staff/reunification-plans/{id}/handover | Current complete approvals + witness authority | Handover evidence → supervised completion review |
| POST /v1/staff/cases/{id}/deletion-requests | Privacy authority | Basis/scope → purge workflow or legal-hold review |
| GET /v1/staff/audit-events | Minimized audit mandate | Cursor → redacted, scoped event metadata |
| GET /v1/staff/analytics | Approved aggregate purpose | Suppressed small cells, no child/location drill-through |
| POST /v1/staff/organizations/{id}/memberships | Org administration | Approved principal/role → membership; no automatic sensitive grants |

## Representative DTOs

MissingReport: registry implied by route; `names[] {original,language,variant_kind}`, `birth_date {lower,upper,precision,knowledge}`, `estimated_age {min_months,max_months,as_of}`, `missing_at {lower,upper,timezone,precision}`, `general_location {country,region,description?}`, `description?`, `distinguishing_marks[]`, `clothing?`, `reporter {relationship,encrypted_transport_contact}`, `authority_reference?`, `notice_version`, `processing_purposes[]`. Unknown arrays/values allowed; contact cannot be omitted without selecting an approved assisted-reporting route. FoundReport substitutes discovery/custody/welfare fields, with restricted details collected separately.

CaseDTO: case ID, own organization, registry, lifecycle, revision, claims and verified assertions (separate collections), permitted evidence references and assignment. A generic database serialization is forbidden.

CandidateDTO: lead/run IDs, permitted case refs, rank, `retrieval_channels[]`, `model_scores[] {manifest_id,metric,value,calibration_status}`, `evidence_pairs[]`, `quality_warnings[]`, `age_gap {interval,source}`, `metadata {supports,contradicts,unknown}`, `review_state`. No embedding arrays or identity-probability property.

## Job and event contracts

[Event schema](contracts/event-envelope.schema.json) is a closed envelope:

```json
{
  "schema_version": "1",
  "event_id": "00000000-0000-4000-8000-000000000001",
  "event_type": "media.ready",
  "organization_id": "00000000-0000-4000-8000-000000000002",
  "aggregate_type": "photograph",
  "aggregate_id": "00000000-0000-4000-8000-000000000003",
  "aggregate_revision": 3,
  "occurred_at": "2026-10-23T19:00:00Z",
  "correlation_id": "00000000-0000-4000-8000-000000000004",
  "policy_version": "design-v0.1",
  "deletion_generation": 0
}
```

Allowlisted types: report.submitted, media.uploaded, media.ready, media.quarantined, subject.selected, embedding.ready, matching.requested, matching.completed, lead.reviewed, disclosure.approved, approval.revoked, reunification.recorded, deletion.requested, deletion.completed, notification.requested.

Events carry IDs, revisions and policy versions only. Consumers load permitted data under their own least-privilege credentials. The transactional outbox belongs to the domain commit; leased jobs reference events and record attempts/lease/dedup. No public webhook can inject internal events.

Versioning: additive optional field changes remain v1; meaning changes require a new version and coexistence/migration plan. Unknown event versions go to dead letters. Dedup per consumer+event ID and business operation key. Retry transient errors with bounded exponential backoff/jitter; permanent validation/license/authorization failures do not retry blindly. Proposed maximum five delivery attempts before staff review; exact intervals await NGO operations approval.

## Media authorization

Signed upload permissions bind exact quarantine object key, max bytes, expected content types and expiry (proposed 10 minutes), never public ACL. Finalize verifies actual immutable object version and checksum rather than trusting client claims. Enforce orphan upload quota/expiry.

Default media reads go through a gateway that reauthorizes every request, supports revocation and sets Cache-Control: no-store, Referrer-Policy: no-referrer and restrictive content type/disposition. If operational requirements demand direct presigned reads, proposed TTL ≤60 seconds with explicit residual bearer-link exposure documented; TTL is not immediate revocation. Originals/EXIF require stronger evidence access. No signed URLs in logs, emails or analytics.

