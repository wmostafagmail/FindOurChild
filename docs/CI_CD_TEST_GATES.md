# CI/CD test gates — Find Our Child

Phase 0 specification only. No active CI workflows, required GitHub checks, deployment automation or application tests have been implemented/configured. Human phase approvals and all original safeguarding/legal/model gates remain required.

## Required lanes

| Gate name (planned) | Pull request requirement | Phase/release requirement | Evidence |
|---|---|---|---|
| phase0-docs-config | Every documentation/tool/config PR | Current review package | Integrity checks, source pins, complete traceability inventory, configuration type/load/telemetry results |
| unit-component | All changed behavior plus dependents | Full regression | Unit/domain/component results and changed-line/branch coverage report |
| api-contract-integration | Every affected API/module; baseline contract compatibility always | All operations and projections | OpenAPI diff, request/response/schema/authorization tests on real API |
| database-migration-rls | Every schema/persistence/grant/job change plus permanent critical subset | Clean+upgrade+restore on real PostgreSQL | Migration ledger, role/RLS/composite FK/transaction and race reports |
| authentication-authorization | Every auth/session/role/scope change plus permanent critical subset | Actual test Keycloak and full grant matrix | Issuer/audience/MFA/revocation/CSRF/session evidence |
| security-safeguarding | Permanent critical catalogue on every app PR; all affected threats | Full catalogue plus independent pen test before pilot/release | Deterministic denial and no-side-effect oracles; independent review |
| browser-e2e | TesterArmy/e2e critical synthetic journeys and affected regression | Full accepted browser/locale/width regression | e2e report.json, JUnit, sanitized screenshots/traces and side-effect checks |
| accessibility-responsive | Changed UI ar/en plus critical journey sample | 3 browsers × 2 locales × 4 widths, keyboard/zoom and manual screen reader | Automated DOM/layout/a11y results, approved manual evidence |
| worker-events | All affected consumers, orchestration, permissions and cancellation | Full event/job matrix | Duplicate/order/lease/crash/deletion race and delivery reports |
| ml-evaluation-regression | Model/weights/preprocessing/ranking/index/data changes | Phase 2/3 activation or any model release | Lawful frozen manifest, split/leakage checks, metrics/CIs and approval |
| performance-resilience | Affected cost/latency/concurrency/storage/retry behavior | Full load/soak/recovery before pilot and major release | Observed latencies/error/resources, controlled failures, RPO/RTO |
| supply-chain-deploy-rollback | Dependency/build/migration/release changes | Every immutable release candidate | Lock/SBOM/license/scan/digest verification, install/upgrade/rollback/restore evidence |
| required-results | Always, including failed/cancelled prerequisite lanes | Every phase exit/release | Exact expected ID×target×fixture inventory vs all shard results and artifact manifest |

A required gate may be inapplicable only through a reviewed, explicit applicability rule in the phase/test inventory. Inapplicable future features remain pending, not passed. Phase 1 still requires denial of every unavailable sensitive capability; inability to perform a future positive handover is never a reason to weaken release-denial tests. No repository-host setting is claimed enforced until required checks/merge queue rules are actually configured and tested.

## Per-PR selection and full regression

Maintain the full versioned test inventory from TEST_MATRIX. Every behavior change updates requirement/API/job/table/permission traceability and adds or revises regression cases in the same PR. Run all directly affected cases and transitive consumers; uncertain selection expands to the full suite. Human-readable AI impact advice may help reviewers, but no AI selector may omit mandatory security/safeguarding cases.

Permanent critical cases run on every app PR: unauthorized image/biometric access, tenant isolation, current permissions, bogus claimant/location disclosure, independent approval, release denial, deletion race and notification leakage. Full accepted regression runs on main/merge queue, phase exit and release candidate; nightly broad runs supplement PR gates and do not replace them. Changes to config/selection/report parsing themselves require full gate-policy checks.

Approved phase applicability distinguishes disabled/not-yet-implemented capability from a skipped required case. Phase 0 has only documentation/tooling checks. No application lane can pass before executable suites and services exist.

The registry's per-case required_from_phase defines the earliest applicable phase. Future SAF capabilities carry explicit Phase 1 disabled-capability denial cases; later positive/browser/state journeys are not included in earlier expected result sets and remain pending. Required-results must freeze this reviewed expected set before execution, never reinterpret a skipped test after seeing a result.

## Result accounting and failure rules

Gate success = every applicable mandatory expected test ID/target/fixture exists, ran, passed deterministically and has required accepted artifacts, and every required tool/setup/migration/sanitization lane succeeded. A zero CLI exit alone is insufficient. Reject missing/extra/unmapped mandatory results, absent shards, duplicate/conflicting results, stale commit/digest/fixture evidence, zero discovery, mandatory skipped/interrupted/blocked tests, failed attempts and flaky critical tests.

Do not use `--pass-with-no-tests`, `.only`, unreviewed exclusions, AI filters, `continue-on-error`, missing-secret skips, quarantine exemptions or “run || rerun” to make a gate green. Diagnostic reruns retain the original failure and do not replace full acceptance. retries=0 for mandatory browser runs; a later successful rerun alone does not clear a critical failure. `failOnSkippedFailure` does not reject clean skips: required-results must explicitly reject them.

Start with a fresh per-run evidence directory before setup. If install/startup/migration fails, publish a safe startup failure manifest and fail the gate; never upload stale reports. Preserve exit codes without a logging pipe swallowing failure. Collect artifacts with an always-run finalizer, while treating missing finalizer/runner-loss evidence as incomplete and blocking promotion. Cancelled runs are not success.

## Isolated execution order

1. Verify trusted source revision, reviewed dependency locks and runner/container/action digests. No production secrets for untrusted PR code; separate sandbox execution from privileged publishing.
2. Provision per-run/shard disposable DB/realm/buckets/queues and private network. Inspect actual identities, allowed hosts and synthetic markers; forbid production fallback.
3. Apply actual migrations and grants/RLS using separate migrator; seed synthetic fixtures; start actual web/API/IdP/media/worker services.
4. Readiness checks verify build versions, database identity and permission posture, not merely an HTTP 200 from any process on the port.
5. Discover tests and freeze expected applicable inventory. Run coordinated suites and deterministic side-effect oracles.
6. Export raw diagnostics to restricted ephemeral storage; sanitize and scan. Produce sanitized result/log/screenshot/trace/migration/coverage artifacts with checksums.
7. required-results reconciles all lanes/shards with expected IDs and verdicts; critical failures block merging, phase progression and promotion.
8. Destroy disposable resources and verify cleanup using a separate finalizer; cleanup failures are operational failures, never silent success.

No pipeline YAML that pretends to start nonexistent app services is committed during Phase 0. Phase 1 must implement these jobs and demonstrate both pass and deliberate-failure paths.

## Artifacts and privacy

| Artifact | Safe published content | Required safeguards |
|---|---|---|
| Test results/JUnit/coverage | Test IDs, targets, statuses, counts, source coverage and versions | No literal child data/tokens/secret URLs in titles, errors or source snapshots |
| Logs/service output | Allowlisted synthetic IDs, errors/codes/timing | Redact request bodies, cookies, contacts, signed URLs and credential transformations; command.log not assumed safe |
| Browser screenshots | Synthetic drawings/data and permitted UI state | Mask secrets and private canaries before upload; no real child photographs |
| Traces/HTTP | Synthetic steps; sanitized URLs/headers/statuses | Remove authorization/cookies/bodies/downloads/model transcripts unless specifically safe; no generic raw .e2e upload |
| DB migration/RLS results | Schema versions, roles, assertions, counts and transaction outcomes | No SQL credentials, row dumps, contacts, vectors or restricted values |
| ML evaluation | Approved aggregate metrics, CIs and pseudonymous run references | Restricted failure examples/data remain in authorized ML store; no external testing model |
| Artifact manifest | Run/commit/build/lock/model/fixture IDs, hashes, times, tools, verdicts and reviewer | Access-controlled store; signed phase/release decision references |

Persist reviewable sanitized screenshots/traces even when browser assertions fail; capture failure evidence in synthetic environments. If a sensitive run ever cannot safely capture an artifact, leave it restricted and mark required evidence blocked until an approved safe equivalent exists. Never publish raw evidence to satisfy a completeness checkbox.

Proposed synthetic artifact retention: raw quarantine ≤24 hours; sanitized PR artifacts 7 days, failure/phase-review artifacts 30 days; signed decision summaries according to the organization's approved audit schedule. These are proposed operational policies, not child-record legal retention decisions. All artifacts need scoped access and deletion workflow. Missing sanitizer/canary scan fails publication and acceptance.

## Phase gates and owners

Phase 1: engineering/security verifies real-stack reporting/manual operations, migrations/RLS/auth and Arabic/English E2E; privacy/safeguarding accepts safe intake. Phase 2: ML/security/safeguarding verifies scoped model pipeline, lawful evaluation and no automatic identity/release. Phase 3: independent validator accepts longitudinal/subgroup results and explicit supported scope. Phase 4: NGO operations and both federation parties accept alerts/bilateral approvals and supervised custody workflows. Phase 5: release board accepts independent penetration test, full regression, deployment/rollback/recovery and NGO pilot.

All original legal/retention/model/hosting and human approval blockers remain. Security/safeguarding critical failures have no ordinary engineering waiver; the affected capability remains disabled until corrected and independently revalidated.
