# Test strategy and evidence

> Phase 1A execution update (2026-10-24): the [review](phase1a/REVIEW.md) and [current matrix](TEST_MATRIX.md) supersede preimplementation status statements below. The checked-in required inventory selects foundation tests plus four disabled-feature guards; it does not drop the original whole-Phase-1 regression obligation. All unimplemented operational tests remain pending. Actual browser runs use the real web/API and private migrated database, deterministic assertions, no model, no retries, both telemetry flags and the root patched lock. Current API/migration coverage is 94.81%; no broader coverage claim is made. Artifact export is foundation-only and must be reviewed before any page can contain photos/contact data. Manual accessibility, penetration, ML, load and operational safeguarding validation remain separate pending suites.

Phase 0 is documentation and research tooling only. No application unit, API, database, authorization, browser E2E, model-accuracy or load tests have run. Future requirements below are acceptance gates, not successful-test claims. This correction selects **TesterArmy/e2e as the principal browser functional runner**, using its Playwright-based web engine. Original product, model, security and safeguarding decisions remain unchanged.

## Phase 0 checks performed/retained

Reviewed-source SHAs and selected source contents, research npm package lock, REA registration/doctor results, static analysis with original stderr/exit codes, exact inline extraction provenance and document/contract integrity checks. See [validation report](research/VALIDATION_REPORT.md) for actual results.

A successful REA process can have partial coverage. A source tree/README review cannot prove an installed application's behavior. Upstream test inventories are not upstream passing-test evidence.

## Phase-by-phase gate matrix

| Phase | Unit + contract | Integration + migration | Authorization + adversarial | E2E / RTL / performance | Exit owner |
|---|---|---|---|---|---|
| 0 | Evidence manifest/schema/link consistency | REA clean installation and diagnostic | Confirm research targets public and no child data | Document RTL specification review; no runtime UI | Technical + safeguarding/legal review |
| 1 | Claim uncertainty, transitions, DTO allowlists, upload contracts | Clean PostgreSQL migration, object-version scan pipeline, IdP/BFF | Tenant/case grants, restricted custody, reporter token replay, unsafe uploads, CSRF/XSS/rate limits | TesterArmy/e2e missing/found/access/supplement flows in ar/en; keyboard/RTL; initial metadata/load targets | Engineering + privacy + NGO intake |
| 2 | Model compatibility, aggregation, retrieval union, event idempotency | Reprocessing/index versions, vector migration, job crash/retry | No public search, cross-tenant vectors, poison/corrupt models, deleted-case races | Staff lead review, no-face/multiface flows, queue latency, exact-vs-ANN benchmark | ML + security + safeguarding |
| 3 | Age/date interval fusion and frozen evaluation transforms | Independent-model/export parity, calibration artifacts | Leakage/incorrect chronology/synthetic contamination and subgroup harms | Longitudinal holdout, quality/age-gap strata and workload usability | Independent validation + NGO owners |
| 4 | Notification dedup/retry and approval scopes | Durable jobs/federation, replay and opt-out migration | Self-approval, stale evidence, revoked grants, counterpart inference and fraud scenarios | NGO operations/approval journeys, RTL dashboards and staff pilot/load | Operations + safeguarding |
| 5 | Full regression and release contract diff | Clean reproducible install, upgrade/rollback/backup restore | Independent penetration test and incident/erasure exercise | Accessibility audit, soak/capacity test, NGO acceptance | Release board named in review log |

Every phase requires regression coverage for all previously accepted invariants, a clean-install record and evidence of reviewed fixtures/provenance. A phase cannot pass on skipped tests or unavailable infrastructure.

## Important test design

- Unit tests verify behavior/invariants, not line-for-line implementation. Use generated uncertain intervals and malformed dimensions where useful.
- API contracts validate request and response shapes, error redaction, pagination and access-dependent projection; full route OpenAPI coverage is a preimplementation contract milestone.
- Migrations test empty install, upgrade from prior accepted schema, representative synthetic data, resumable backfill, rollback/restore and no cross-tenant FK association.
- Integration uses real PostgreSQL/pgvector and a private test object store, with a scanner fixture plus controlled malware-test sample only under safe test protocol; scanner outages must fail closed.
- Authorization tests every route and worker under own tenant, other tenant, no grant, revoked/expired grant, suspended org, restricted custody and federated scopes. Exercise API and SQL with the actual non-owner database role.
- Abuse cases include guessed receipts, repeated access exchange, altered MIME/header, image bombs, document HTML payloads, path traversal, duplicate reports, multi-face confusion, timing/count leaks, stale idempotency replay and brute-force claimant attempts.
- Concurrency tests revoke case/consent while matching, delete during index insertion, change evidence during approval, retry handover and deliver duplicate/out-of-order events.
- TesterArmy/e2e checks full public/staff journeys through its Playwright web engine in Arabic/English, 320px layout, browser back/refresh, interrupted upload/retry, expiry, focus/error announcements and masked private data. Add automated accessibility checks plus manual screen-reader review.
- Performance uses the declared synthetic pilot workload and realistic tenant/grant selectivity. Measure p50/p95/p99, error rates, storage growth and resource budgets; security controls remain enabled. No real child records in CI.

## Fixture and output rules

Synthetic names/cases only in repository. Do not commit actual missing-child images, biometrics, contacts or authority documents. Consented evaluation data lives in restricted encrypted stores; screenshots/traces/video/HTTP logs are disabled for sensitive runs unless explicitly approved and redacted. CI artifacts must not contain reporter capabilities, signed media URLs or full request payloads.

Each test report records commit, environment/lock/digests, setup command, fixture manifest, start/end, exit code, passed/failed/skipped counts and blockers. No live-data acceptance inferred from synthetic fixtures. Production go/no-go requires the independent model and safeguarding evidence in [MODEL_EVALUATION_PLAN](MODEL_EVALUATION_PLAN.md).

## Coordinated suites — mandatory architecture

| Suite | Principal mechanism and independent oracle | Boundary |
|---|---|---|
| Unit and component | Pytest domain tests and Vitest rendered React component tests, property/interval cases | Fast isolated behavior; mocks allowed here; versions require Phase 1 locks |
| API contract and integration | Request/response validation against complete frozen OpenAPI; real FastAPI and dependencies | Every declared operation, error projection, idempotency and revision |
| Database schema/migration/RLS/transaction | Actual PostgreSQL/pgvector and actual non-owner roles, SQL/FK assertions, controlled fault/race barriers | Empty install, upgrade, pool context, atomic audit/outbox, approval/deletion races |
| Authentication and authorization | Actual test Keycloak realm, BFF/session/MFA lifecycle and role×org×case×purpose matrix | JWT validation alone cannot establish case access |
| Security and adversarial | [Security catalogue](SECURITY_TEST_CATALOG.md), HTTP/SQL/worker/media attacks and independent penetration testing | All T01–T19 and safeguarding critical invariants |
| Browser E2E | **TesterArmy/e2e 0.21.3 + @e2e-dev/web 0.15.3**, deterministic locator/HTTP/state assertions | Actual application services and isolated migrated test database; no mocked app backend |
| Arabic/English accessibility/responsive | TesterArmy browser journeys plus dedicated accessibility checks and manual screen-reader/keyboard review | Chromium/Firefox/WebKit × ar-EG/en-GB × 320/360/390/1280px, zoom and bidi |
| AI/model evaluation and regression | Separate restricted reproducible ML harness, lawful ground truth and subject-disjoint data | Synthetic vectors test workflows only; no recognition-accuracy claim from browser tests |
| Background workers/events | Actual leased jobs/outbox with controlled clock, duplicates/reordering/crashes and provider sink | At-least-once delivery, current grants, deletion generation, dead letters |
| Performance/concurrency/recovery/resilience | Load harness, deterministic barriers, isolated dependency/process/network failure injection and restore drills | Measure proposed targets with controls enabled; no production fault injection |
| Deployment and rollback | Locked immutable full-stack install/upgrade/downgrade-compatibility/restore validation | No revoked approval/model/deleted-case resurrection; signed promotion decision |

These suites coordinate through a per-run synthetic fixture manifest and stable case IDs. Browser E2E does **not** replace DB/RLS testing, security/adversarial analysis, independent penetration testing or ML evaluation. Expected outcomes include actual persisted/absent effects, not just UI text. Tools for non-browser suites remain to be version-locked and validated before implementation.

## Traceability and acceptance

[TEST_MATRIX](TEST_MATRIX.md) and [its JSON registry](testing/test-matrix.json) map every declared FR/API/event/job/database boundary/safeguarding workflow to planned executable paths, exact test IDs/selectors, positive/negative/security/edge scenarios, fixtures, expected outcomes and evidence/status. All application tests are **pending**. Planned selectors are not existing executables. The generator and Phase 0 checks validate coverage of the current declared inventory; newly added contracts require new mappings.

Follow [E2E_FRAMEWORK_INTEGRATION](E2E_FRAMEWORK_INTEGRATION.md) and [CI_CD_TEST_GATES](CI_CD_TEST_GATES.md). Real-service browser setup requires actual isolated DB identity/preflight, not an environment assertion or a mock server. Phase applicability is explicit; future positive cases stay pending while unavailable sensitive capabilities require denial tests in earlier phases.

Every AI-assisted action, if later approved for synthetic testing, must end in deterministic assertions. No real child data may go to any external testing model, including a model-backed coding-agent MCP client. Default required suites have no model configured, no model credentials and no outbound provider access. Cache-only replay does not guarantee no model traffic on a miss.

All test/MCP/helper processes set E2E_TELEMETRY_DISABLED=1 and DO_NOT_TRACK=1. Verify opt-out and enforce network policy. Preserve sanitized results/logs/screenshots/traces/migration/coverage reports with version/hash evidence; do not rely on built-in redaction. Failed sanitization blocks publication and gate acceptance. Original sensitive-data restrictions remain applicable.

Critical security/safeguarding failures block PR/phase/release progression. Required-results must reconcile exact expected test×target×fixture results across all shards; missing, zero, skipped, interrupted, blocked or flaky mandatory tests cannot count as passed. failOnSkippedFailure only handles skip-after-failure, so clean skips need an independent result gate. Retain original failure evidence; no rerun/continue-on-error shortcut can turn it green.

Current corrections' actual documentation/configuration evidence is in [the correction validation report](research/e2e/VALIDATION_REPORT.md). Application suites and CI enforcement remain unimplemented.
