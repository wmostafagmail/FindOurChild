# Phase 2E proposed contracts and data boundaries

**Design only. None of the operations, tables or migrations below exists from this packet.** Final executable OpenAPI, JSON Schema, SQL and test selectors are Phase 2E implementation deliverables after owner approval. Preserve existing operation IDs, v1 fixture contract, 0001–0036 migration bytes and [Phase 2D architecture](../phase2d/ARCHITECTURE.md).

## Fixed staff API proposal

Prefix: `/v1/staff/demo-recognition`. No public, reporter, operational-matching or arbitrary upstream equivalent. The BFF uses fixed method/path mappings with actual MFA/server-held sessions, exact Origin/CSRF/Fetch Metadata checks, bounded typed bodies and no browser token store. Default in every deployment is unavailable; only an approved isolated demo instance may enable these operations.

| Proposed operation ID | Method/path after prefix | Request / result | Required authority |
|---|---|---|---|
| `demoRecognitionStatus` | GET `/status` | Fixed availability/data-class/provider-capability descriptor; no model paths, gallery membership or asset inventory | Active staff organization, MFA and expiring demo-status purpose grant |
| `createDemoRecognitionJob` | POST `/cases/{case_id}/jobs` | Exact server-known query photo/version and allowlisted policy reference; 202 opaque job/revision. Server resolves the immutable gallery/split/space; no client model, gallery tenant, threshold, URL, vector or candidate JSON | Query case read/matching request/media grants, demo execute action and allowed policy/image/model authority |
| `getDemoRecognitionJob` | GET `/jobs/{job_id}` | Bounded state/error and authorized result references; no hidden total/candidate IDs for inaccessible cases | Current query case/media and demo-view grant; candidate projections separately check both cases |
| `cancelDemoRecognitionJob` | POST `/jobs/{job_id}/cancellations` | Closed reason code/current revision; 201 immutable cancellation event. Current lease fenced; no publication after effective cancellation | Current query write/demo-cancel authority; actor ownership/supervisor policy, never NGO role alone |
| `getDemoRecognitionDetections` | GET `/jobs/{job_id}/detections` | Current derivative revision, opaque detection IDs and bounded rectangle geometry needed for explicit selection; no raw landmarks/vectors or identity confidence | Current query case/media and demo-select/view authority; exact job/photo binding |
| `selectDemoRecognitionFace` | POST `/jobs/{job_id}/face-selections` | Opaque detection ID/current derivative revision; 201 selection event/revision and resumed job reference. Browser cannot submit arbitrary coordinates or change source bytes | Query write/media/demo-select; current detection, permission and model/image authority, no stale or foreign selection |

Every state-changing operation has required UUID `Idempotency-Key` and `If-Match` for its case/job aggregate. Bind replay to principal/organization/resource, canonical command digest and current authority. Reads return strong bounded ETags; versions/cursors are actor/org/instance/resource/filter-bound and short-lived. Terminal canceled/succeeded jobs do not gain another event from exact replay. Changed-body replay is 409; stale revision/selection is 412. No reissue of rights on an idempotent replay.

Status semantics: 401 missing/expired authentication; same minimized 404 for inaccessible/nonexistent case/job/photo/detection; 403 only for an already-authorized resource with forbidden action; 413 size ceiling; 422 invalid closed DTO; 409 incompatible state/changed command; 412 stale evidence; 429 bounded rate/capacity admission; 503 disabled provider, schema/epoch/manifest/IdP/audit/scanner/dependency unavailable. A terminal no-face/quality-hold/failed processing state is explicit and not a successful empty identity result. No internal exception/model path, guessed ID or private score is returned in an error. Unknown JSON fields, nonfinite numbers and nested overflows fail validation.

## Versioned candidate integration

New jobs publish into the existing authorized investigation experience through a separately reviewed provider-v2 boundary. Do not point old fixture import at arbitrary scores/images or activate generic operational routes. Existing fixture v1 remains fixture-only and its score stays null/scripted ordinal. Add generated v2 DTO/database validators and fixed dispatch together; unknown schema/provider combinations fail closed.

| Native demonstration source field group | Required semantics |
|---|---|
| Version/class | Explicit contract/provider/policy version; `kind=licensed_demo_model`, `data_class=synthetic`, `identity_determination=not_performed`, `operational_activation=false` |
| Artifact identity | Exact encoder/detector/aligner/build/preprocessing versions and hashes; reviewed acquisition/image-authority references. Full paths/store receipts remain private; browser sees minimized permitted identifiers only |
| Space | Canonical 64-hex digest and manifest version; dimension128, normalization `none`, metric `euclidean_distance`, recorded storage cast policy; no mixing with v1 `unit_l2` or old grid/research spaces |
| Pair score | Two exact authorized immutable photo versions, finite nonnegative native distance, lower-is-closer wording, no identity probability; `aggregation_version=single_photo_pair_v1` |
| Gallery | Server-bound immutable manifest/split/enrollment revision; only active current authorized opposite-registry members influence rank/counts; no absent/calibration-member leakage |
| Evidence | Photo-specific capture-date/age/reference intervals and uncertainty, clean-derivative/selection/quality versions, current case/media authority; no fabricated aging labels or demographics |
| Snapshot | Exact case/evidence/model/space/policy and authority generations; immutable event references and semantic rejection key. Job UUID/time alone cannot bypass a rejected unchanged snapshot |

A response containing multiple candidate leads is not multi-photo aggregation. For 2E, one selected query photo is compared to one preselected eligible gallery photo per case. Keep per-pair distances and provenance bound even if only a bounded visible rank is projected. Phase 2F's three-photo aggregation/open-set policy is not implemented here. No inherited 0.6 threshold or cosine conversion. Human holds/rejections/escalations/independent review remain the original guarded workflow, not identity/custody decisions.

## Proposed database relations and grants

Names are reserved design concepts; final names/DDL require implementation review. New migrations are forward-only after the actual complete ledger; do not edit historical 0001–0036 or invent applied-version evidence. Model/space records are private instance-scoped platform configuration; all tenant-bearing relations force RLS and use NOLOGIN ownership. API/worker roles cannot alter policy, authority or migration ledgers. Definers have fixed trusted search paths, no PUBLIC execution and explicit bounded arguments.

| Relation concept | Keys and immutable/versioned data | Runtime access boundary |
|---|---|---|
| `demo_component_manifests` | Instance+manifest digest, exact file hashes/size/notices, reviewed approval/revocation epoch, worker build and resource policy | Controlled provisioner; no browser/API inventory or arbitrary staff inserts; read-only approved projection to worker |
| `demo_embedding_spaces` | Instance+space digest, canonical component/preprocessing/dtype/normalization/metric manifest | Narrow private lookup, never editable in place; another build/space requires explicit backfill/review |
| `demo_gallery_memberships` | Instance/org/gallery/split/case/photo/version/space/enrollment revision; positive enrollment authority and tombstone | Provisioner records frozen members; caller cannot expand gallery. Unenrolled/absent images may be stage-tested but never silently enrolled |
| `demo_recognition_jobs` | Tenant/query case/photo/policy/gallery/space, requester/authority epoch, revision/state, deadlines, lease/fence, idempotency digest | Scoped submit/read/cancel/lease procedures; every lease/publication rechecks live authority and instance identity |
| `demo_face_selections` | Tenant/job/photo derivative/detection revision, selected rectangle reference, actor/server time and selection digest | Narrow authorized selection command only; source/selection change invalidates downstream descriptors/results |
| `demo_photo_embeddings` | Composite instance/org/case/photo/version/selection/space, `vector(128)`, input/authority/quality metadata, processing/tombstone state | Internal insert/retrieve procedures under current scope; no general API/reporter/public SELECT, vector dump or unbound SQL search |
| `demo_result_snapshots` | Tenant/job/pair/current photo versions/space/gallery/policy, native score/rank/provenance and authority generations | Atomic publish with minimized audit/outbox; projection checks both case/media permissions before and after audit; tombstone/cleanup on revocation |

Composite foreign keys prevent cross-tenant/instance case/photo/job/result references. Final uniqueness constraints enforce one output per exact input/space/selection plus fenced idempotency; changed inputs create a new version. Audit and current projection update in one transaction. Do not store vectors, chips or revocable detailed score payloads in append-only human journal events: journal keeps minimized person/reason/time/digest/references while separately protected result evidence can be withdrawn and cleaned.

Use exact L2 initially with selective tenant/space/gallery/enrollment indexes and authorization filters before ordering; no ANN index in this baseline. Confirm actual query plans under runtime RLS roles. Wrong dimensions, NaN/Inf, null authority, unknown manifest/space and incompatible source versions are denied. Shared-resource timing residuals must be measured/reported; do not claim perfect cross-tenant timing isolation from an RLS predicate.

## Upgrade, disablement and recovery

Migration review separates schema/ownership/constraints, least-privilege policies/functions, provider publication/projection and any measured supporting indexes. Apply to both an empty installation and a real upgrade copy; compare the complete ledger/checksums and actual role grants. A partial or mismatched ledger disables the provider.

Rollback first disables the new provider/jobs and uses a compatible prior application without dropping historical journal/migrations; no down-migration deletes review evidence. Reprocessing is explicit and same-space only. Revocation/tombstones fence running leases, suppress scores/derived projections, remove descriptor/chip/index rows and invalidate approvals. Restore into quarantine with a new independently held epoch, reconcile current model/image/person permissions and tombstones, then reissue rights only after review. No operational/research credentials enter this demo deployment; no production-erasure certification is inferred.

Every operation/relation maps to the planned [test matrix](TEST_MATRIX.md), especially FE-2E-10–21 and 23–27. Execute actual migrated PostgreSQL/RLS/concurrency/recovery, API authorization negatives and official three-browser regressions after implementation. This proposal creates no database or API behavior and passes none of those pending tests.
