# Deployment and operations specification

> Phase 1A execution update: [local environment](phase1a/ENVIRONMENT.md) and [review](phase1a/REVIEW.md). Both migrations and a real synthetic database backup/restore drill executed. Restored migration checksums, pgvector and forced RLS were verified; production restoration, tombstone replay, data erasure, load/recovery SLOs, KMS and provider integrations are still pending. The local foundation/test image is not a production release image. GitHub workflow/action pins, a passing Ubuntu hosted regression and sanitized artifact publication are verified. Main protection is bound to GitHub Actions; a disposable failing-test PR received an actual HTTP 405 merge rejection. See [hosted validation](phase1a/HOSTED_VALIDATION.md). Local raw artifact expiry/CI retention policy must not be confused with an operational retention approval.

Proposed deployment; no app containers, production services or infrastructure provisioned in Phase 0.

## Environments and topology

Development uses Docker-based isolated Next.js, FastAPI, PostgreSQL/pgvector, Keycloak, media/job workers and a private S3-compatible test provider. Use synthetic fixtures and bind admin services to local/private interfaces. Optional GPU inference profile is introduced only when a cleared model/runtime exists. Do not substitute floating legacy MinIO images for a reviewed maintained object provider.

Staging reproduces production auth/storage/network policies with synthetic or separately consented data. Production hosting region and subprocessors require legal approval. Initial architecture is a modest set of processes around one transactional database; no Kubernetes requirement. Private DB/object/KMS/inference networks, TLS ingress and restricted operator jump access.

Secrets from an approved secret manager; distinct API, worker, broker, migration, backup and audit roles. No default credentials. Identity administration and object administration are separate from caseworker access.

## Version and supply chain policy

Research tooling: exact rea-agents 6.7.0 and full package-lock retained. Reviewed source SHAs are evidence pins, not production release pins. Phase 1 must select supported released versions of Node/Next.js/React/TypeScript/Python/FastAPI/PostgreSQL/pgvector/Keycloak, media/scanning libraries and infrastructure; verify compatibility/security and record transitive locks plus OCI platform/digests. No “latest” deployment tags.

Model manifest separately records detector/recognizer weights, hashes, code/data/weight licenses and validation release. Disable auto-downloads and verify artifacts at startup. Lock scanner engine and signature-update policy; stale signatures surface an operational hold according to approved policy. Generate SBOM and license inventory for every deployable artifact, preserving notices. No absence-of-CVE assertion from a successful installation.

## CI/CD plan

Contract and source validation → unit/integration/RLS/migration/abuse tests → TesterArmy/e2e ar/en browser and accessibility checks → deterministic artifact build/SBOM/license/security checks → synthetic staging → independent phase gate approval → signed immutable deployment → health/readiness checks and monitored rollout.

Treat untrusted PRs without production secrets/privileged execution. Never run external source setup scripts with access to real case data. Release/deployment are separate explicitly authorized actions.

## Backup, recovery and deletion

PostgreSQL encrypted base backups + WAL point-in-time recovery, object version/replication plan, identity configuration backup and independent KMS recovery custody. Proposed pilot targets: RPO ≤15 minutes, RTO ≤4 hours, pending measured drills and NGO acceptance. Object/media recovery must be coherent with DB references; document inconsistent-cut detection.

Restore in network-isolated recovery environment → restore database/object versions and keys → verify checksums/audit roots → replay deletion/revocation ledger → reconcile object/vector references → exercise read-only synthetic checks → obtain incident/operations approval → reopen. Recovery tests must demonstrate erased cases stay inaccessible.

Backups do not replace source originals or a signed authority record. Replication is not independent backup. Legal holds/WORM are scoped to lawful records and must not silently block erasure of unrelated cases.

## Observability and alerts

Metrics: neutral request counts/latencies, denied access counts, intake backlog, scan failures/signature age, ready-media lag, inference/quality failures, processing queue age, model-space mismatch, stale jobs/dead letters, notification retries, deleted-data reconciliation, audit export/root freshness and backup/restore freshness. No image/vector/name/contact/location values in metrics labels, traces or errors.

Operational alerts reach named authorized responders, carry neutral service/task IDs and deduplicate; no child details on lock screens. Proposed triage targets and staffing must be agreed before launch. Bounded job retry, rate-limit and notification rules are configuration with versions/audit.

## Failure modes and runbooks

| Failure | Immediate behavior | Recovery evidence |
|---|---|---|
| Scanner unavailable | Keep media quarantined; public intake can continue within quota | Re-scan queued objects with current signatures before any serve/embed |
| Model missing/license revoked/tampered | Disable affected inference space; manual case work continues | Reapprove manifest and reprocess versioned jobs; no incompatible fallback |
| Identity provider unavailable | Existing sessions obey expiry; no emergency anonymous staff login | Verify restored session/revocation state |
| Database unavailable | Fail closed for grants/media; bounded neutral error | Restore transactional consistency and outbox dedup |
| Storage/KMS outage | Deny media read; do not export plaintext fallback | Verify restored encryption/versions/checksums |
| Disclosure concern/incident | Freeze contact/disclosure, revoke affected grants, preserve restricted evidence | Safeguarding/legal clearance with audit review |
| Audit sink outage | Queue bounded exports; sensitive actions hold if safe durable audit cannot be assured | Verify chain/roots, gap reconciliation and approved resumption |
| Notification provider outage | Retry bounded neutral messages; retain task in staff queue | Delivery reconciliation; no duplicate sensitive content |
| Federation opt-out/deletion | Invalidate broker edges/approvals and cancel stale jobs | Negative retrieval/disclosure checks across both parties |

Reprocessing is resumable, idempotent and tied to original evidence revisions; job restarts recheck current authority and deletion generation. Rollback must not reactivate a revoked model, deleted case or outdated approval. Database rollbacks use compatible schema or verified restore; never destructively downgrade without an approved plan.

## Operational release checklist

Named owners for child safety, security, privacy, infrastructure, model validation and incident command; current policies and vendor contracts; tested MFA/access reviews; patched locked artifacts; actual restore/erasure drill; valid model license/evaluation; no sensitive telemetry; NGO pilot support and safe handover protocol. Every item requires evidence, not a checkbox inferred from this document.

## Testing environment and delivery gates — correction

Apply [CI_CD_TEST_GATES](CI_CD_TEST_GATES.md) to every PR, phase and release; [E2E_FRAMEWORK_INTEGRATION](E2E_FRAMEWORK_INTEGRATION.md) pins the principal browser runner. Exact testing packages/lock are reviewed separately from still-pending application releases. Do not run upstream unpinned init/CI examples unchanged or introduce a second floating Playwright installation.

Provision one disposable DB/realm/bucket/queue namespace per run/shard, validate actual database identity/roles/build versions, apply real migrations/RLS and seed synthetic cases before actual application services start. Fail on any production/default-DB fallback, unavailable service or unsafe destination. Browser E2E must reach real Next.js/FastAPI/Keycloak/media/workers and PostgreSQL, with a local sink replacing only outside delivery. Document and demonstrate teardown/rollback with deletion/revocation replay.

Separate trusted dependency/browser preparation from network-restricted test execution. Every runner/MCP/helper gets E2E_TELEMETRY_DISABLED=1 and DO_NOT_TRACK=1. Mandatory runs have no model/provider/hosted-browser credentials or public artifact reporter. External testing models never receive real child information, irrespective of whether a separate ML protocol permits lawful local evaluation.

Retain test results, service logs, sanitized screenshots/traces, migration/RLS reports, coverage and artifact manifests in an access-controlled store. Raw .e2e output, command.log, caches, videos/downloads and session files are not automatically safe; sanitize/scan before upload. Missing evidence, sanitization failure or any critical security/safeguarding failure blocks progression. No skipped mandatory result, missing shard or successful-only rerun can satisfy the gate. Proposed synthetic artifact retention and failure handling are in CI_CD_TEST_GATES; original child-data legal retention/backup decisions remain unchanged.

Actual pipeline jobs, result reconciler, sanitizer, required-check hosting settings, browser compatibility and app startup/release/rollback tests remain pending. This Phase 0 correction configures none of those live services and performs no deployment.
