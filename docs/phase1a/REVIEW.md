# Find Our Child — Phase 1A review

**Assessment: all local Phase 1A validation passes; acceptance remains blocked by hosted CI and branch-protection verification. Stop before Phase 1B.** Firefox remediation and the complete regression are documented in [REMEDIATION_REPORT.md](REMEDIATION_REPORT.md). No GitHub remote is configured. The owner intends to provide a repository URL and has not accepted these external blockers. Hosted controls are not claimed as active. This package authorizes no production data or later-phase implementation.

## Delivered source and environment

Git was initialized with the approved Phase 0 package preserved at `40231be73ab9a5eb577ccf5308c86f6b7282976b`. Work is isolated on `codex/phase-1a-foundation`; `main` retains the research baseline. [Source inventory](SOURCE_INVENTORY.md), [locked dependency manifest](LOCKED_DEPENDENCIES.md), [observed environment evidence](environment-evidence.json) and [local commands](ENVIRONMENT.md) make the foundation reviewable. No remote repository or pull request was created.

The application skeleton is Next.js/React/TypeScript with an Arabic-first, English-switchable, input-free foundation shell, nonce-based CSP and accessible responsive layout. FastAPI implements liveness, dependency/identity readiness and OpenAPI serving. Readiness reaches the actual private PostgreSQL service. All 32 domain operations return a no-store 503, including intake, reporter access, media, matching, approvals and handover. Identity/MFA, reporting, uploads, scanning, notifications and workers have not been implemented or claimed as working.

The executable local environment includes an immutable PostgreSQL/pgvector image, locked Python image, synthetic-only startup guards and private generated credentials. The database has no published host port; migrations/tests run inside its internal-only network. The API runs as an unprivileged non-owner database role and receives no provisioner credentials. Web/browser processes receive neither database/provisioner nor testing-model credentials. Filesystem stalls in Documents required a byte-equivalent temporary runtime; dependency symlinks and hashes are documented. Bootstrap recreates dependencies from locks rather than relying on temporary storage.

## API and database contract status

OpenAPI **0.2.0** now has **35 operations**: 32 typed future domain contracts and three implemented foundation operations. Request/response DTOs, UUIDs, nullable uncertainty, authentication declarations, idempotency/revision/CSRF headers and errors are machine-readable and standards-validated. The `x-implementation-status` fields identify unavailable operations. A declared success response is not an available application feature. NGO policy review of engineering DTO bounds/enums, notices and operational workflow rules remains required before reporting is enabled.

Two forward-only, checksum-verified migrations execute and replay. Migration 0001 was not rewritten after application; 0002 adds scoped idempotency storage, complete closed-event outbox metadata and same-case object/plan/event foreign keys. Schema release `0001` comprises both ledger entries. There are **41 domain relations**, all with enabled and forced RLS. Trusted active membership, organization, principal, case grant, purpose, expiry/revocation and deletion state constrain the foundation case-read policy. All writes and other classified reads remain denied. Phase 1B must add reviewed live identity and action-specific policies; the current schema is not proof of completed staff authorization or operational release controls.

The policy reader is NOLOGIN and is not granted to the runtime role. Missing transaction context denies reads and transaction-local context does not survive connection reuse. This assumes the service protects its SQL credentials and sets context only after future server-side identity validation; arbitrary SQL with stolen runtime credentials is outside that boundary. No embedding-space partition, inference worker, facial weights or production matching is enabled. Explicit cross-case original-object sharing is deferred to a separately tested grant/link migration.

## Actual validation

| Check | Execution outcome |
|---|---|
| Required Python unit/API/integration/database/security inventory | **151 passed**, no skips; real isolated PostgreSQL |
| API and migration Python line coverage | **94.81%**; this is not whole-repository or frontend coverage |
| Browser matrix | **72 passed / 0 failed**, 72 executed, zero skipped/flaky/retried |
| Chromium | 24 passed |
| WebKit | 24 passed |
| Firefox | 24 passed after isolated macOS app-data repair; original launch failures preserved |
| Arabic/English automated accessibility/layout/keyboard checks | Passed in Chromium/Firefox/WebKit; manual assistive-technology review pending |
| Current npm/Python dependency audits | No known vulnerabilities at recorded execution time |
| Clean final npm lock install / TypeScript / production web build | Completed; private logs retained |
| Real backup/restore drill | Passed for both migration checksums, pgvector, 41 forced-RLS relations and default-denied runtime reads |
| Source-bound required-results/export gate | **Passed** for the remediated source; hosted acceptance is separate |
| Hosted GitHub workflow / branch protection | **Pending**, not executed or enforced remotely |

[Sanitized results](../../artifacts/sanitized/results.json), [coverage](../../artifacts/sanitized/coverage.json), [normalized traces](../../artifacts/sanitized/traces.json), [source manifest](../../artifacts/sanitized/source-manifest.json), [artifact checksums](../../artifacts/sanitized/checksums.json) and [configuration checks](configuration-checks.json) are reviewable artifacts. Forty-eight allowlisted synthetic-shell screenshots are retained under `artifacts/sanitized/screenshots`. Raw browser attempts/logs, JUnit, coverage and synthetic backup remain private under ignored local artifact paths. Original evidence is preserved under `artifacts/raw/baseline-add5cf7/`; the byte-equivalent runtime archive has a full preservation checksum manifest. The final raw browser report is `.e2e/report.json`. [Remediation evidence](remediation-evidence.json) binds exact counts, raw report hashes and commands to committed source `ec99ac0c5200f83fffcb1bbbee9db1c8cfeaa89d` and the exported source digest. Prior browser failures were retained before later runs; no retry was used to turn a failing mandatory case green.

The original Phase 0 validators run against the preserved commit because their assertions intentionally require a preimplementation tree. Their success certifies that historical research/configuration package, not application functionality. The current checker additionally validates complete OpenAPI, exact package/lock agreement, private database topology and immutable action pins. Current documentation links and matrix references are checked separately.

## Testing and safeguarding status

The [current matrix](../TEST_MATRIX.md) retains the original **151-feature / 630-case** baseline and adds foundation traceability, including the new idempotency boundary. Only four original disabled-feature safeguards have executed evidence; the unimplemented operational scenarios remain pending. The numerical coincidence between 151 baseline features and 151 executed Python tests does not mean the original feature baseline has passed.

Negative tests cover forged/anonymous domain requests, missing/expired/revoked/wrong-purpose grants, disabled principals, suspended organizations, cross-tenant and same-tenant cross-case references, role escalation, forbidden sensitive-table access, wrong model/runner/origin result evidence, metadata canaries and artifact path traversal. The enforced disabled matching/disclosure/approval/handover guards fail safely. These are not operational fraud investigations, claimant verification, two-person approvals, media erasure, human match rejection or notification-safety acceptance. Those original safeguarding tests remain pending and the relevant operations remain disabled.

TesterArmy runner **0.21.3**, web **0.15.3** and Playwright core **1.64.1** remain pinned. The active lock applies Zod **4.6.6** to remove the reported high-severity transitive advisory; original research locks are preserved and not used as the active test environment. Browser runs use deterministic assertions against actual services and the isolated database, no model/provider, cache or retries. Both telemetry opt-outs are enforced, Next telemetry is disabled, and recorded model calls/tokens are zero. No packet capture or process-wide egress-firewall certification was performed. No real child data or photographs entered testing.

## CI configuration and enforcement

The checked-in [workflow](../../.github/workflows/phase1a.yml) runs on pull requests, main/engineering branches, merge queue and manual dispatch. It installs locked dependencies, runs structural checks, real database regression, backup/restore, security audits, web build and the complete browser matrix. An independent inventory/result gate rejects zero/missing/duplicate, skipped, retried, stale, wrong-engine/origin or model-assisted mandatory results. Sanitization occurs before artifact upload; raw reports/screenshots are never directly published.

The exporter publishes allowlisted IDs/statuses, code coverage line numbers, step names and metadata-stripped PNGs from fully passed tests of the input-free synthetic shell. It is **not a general PII detector**. Before any reporting/contact/photo page exists, its screenshot/trace policy must be reviewed and extended; unknown page content must not inherit this allowance. Local raw expiry, operational artifact access and final retention require implementation/approval for those later environments.

No hosted run has been observed and no remote required check or branch rule is asserted. Repository ownership/selection and protected-branch configuration remain required. A locally passing workflow file cannot establish those controls.

## Remaining blockers and limits

1. **Resolved locally:** the unchanged Firefox 157.0/revision 1555 binary launches with disposable CoreFoundation app data on macOS 27. `scripts/run-browser.mjs` applies this automatically and cleans up the created directory. A/B launch diagnostics and all 72 TesterArmy executions are recorded in the remediation report. No engine, target, assertion or retry policy was removed.
2. Select the GitHub repository, execute the workflow on its target runner and enforce/verify required checks and branch protection. Linux browser/OS compatibility and hosted artifact enforcement are pending.
3. The local environment is synthetic foundation tooling, not a production deployment. Keycloak/MFA, S3 quarantine/scanner integrations, secure sessions/CSRF enforcement, staff actions and worker implementations belong to the separately gated next phases. SDK/version presence is not a completed service integration.
4. Manual accessibility, independent penetration/adversarial testing, performance/concurrency/soak, operational recovery and tombstone replay, deletion/index cleanup, legal/retention/KMS/provider approvals and all model evaluation remain pending. The baseline B01–B11 decisions still govern their relevant scopes; explicit authorization cleared only entry to synthetic Phase 1A work.
5. Hosted OS libraries, production image hardening/SBOM and bit-for-bit build provenance are not certified by package locks. Research-source licensing and lawful model/data use remain independent approvals.

No Phase 1B/1C work may start from this review. Resolve the Phase 1A acceptance blockers and obtain explicit review/approval first.
