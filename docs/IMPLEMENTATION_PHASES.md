# Implementation phases and validation gates

> Current authorization is **Phase 1A only**. Original Phase 0 stop statements below describe the historical run and are superseded solely by the explicit Phase 1A authorization. Phase 1A covers repository/locks/environment/contracts/schema/skeleton/tests. Stop for review after 1A; implement identity/security only after separate Phase 1B approval; stop again before Phase 1C reporting. No production facial matching or real child information is permitted. The [current review](phase1a/REVIEW.md) records passing technical gates and readiness for owner acceptance review; no approval for 1B is inferred.

Status: **stop after Phase 0**. This file plans later work; it does not authorize it.

## Phase 0 — research and architecture (this package)

Deliverables: all 16 requested documents, repository source/commit evidence and licensing decisions, REA Codex setup and bounded static investigations, data/API/event design, four sequence diagrams, child-safeguarding/privacy assessment, model evaluation plan, blockers and named approval decisions.

Correction deliverables: [TesterArmy integration](E2E_FRAMEWORK_INTEGRATION.md), [feature/test matrix](TEST_MATRIX.md), [CI/CD gates](CI_CD_TEST_GATES.md) and [security test catalogue](SECURITY_TEST_CATALOG.md), plus updated testing/deployment architecture. Original research and safeguarding decisions are preserved. Configuration/tooling checks cannot satisfy any application phase gate.

Completed research does not clear production licenses, establish legal authority, measure model accuracy or approve policy. Phase 0 package is ready for review only after file/contract/evidence checks. Entry to phase 1 requires explicit user/NGO review and resolution or documented scope-limited deferral of each relevant blocker.

## Phase 1 — reporting MVP

Suggested order: freeze complete OpenAPI/DDL/event contracts and release dependency locks → authentication/organizations/case grants/RLS → independent missing/found claims → private upload quarantine/scanning → moderation/assignment/evidence/notes → secure reporter access and supplements → bilingual RTL flows → manual safeguarding transitions.

Deliver a modular API, database migrations, private object adapter, staff MFA, append-only audit/export, rate limits, notices/retention/deletion jobs and a synthetic seeded environment. No biometric matching yet.

Gate: all phase 1 test classes in TEST_STRATEGY pass, clean install recorded, legal/retention and hosting/vendor approvals signed, threat controls demonstrated, accessibility review and NGO manual workflow acceptance complete.

Testing architecture entry work, after explicit Phase 1 authorization: complete executable API/DDL contracts; reproduce the exact TesterArmy runner/web/Playwright lock; validate actual browser binaries/OS compatibility; implement the isolated real-service/test-DB provisioner, synthetic fixture registry, all applicable matrix executables, artifact sanitizer and independent required-results gate. Make actual CI required checks enforce them. Keep model-free deterministic browser runs as the principal functional suite; Codex e2e MCP integration may see only the synthetic environment. No app scaffolding or active e2e MCP registration is part of this Phase 0 correction.

## Phase 2 — AI matching MVP

Only cleared artifacts enter the pipeline. Implement versioned detection/alignment/quality/subject selection, embeddings/space partitions, exact vector retrieval, multi-image case aggregation, independently retrieved metadata leads, review UI, reprocessing and deletion/cancellation. AI remains disabled operationally until model release gate passes.

Gate: artifact licenses/provenance, lawful evaluation data and independently measured open-set/Recall@K/error/workload results accepted; model compatibility/tenant tests pass; staff false-lead exercise and rollback succeed. ANN optional only after exact comparison.

## Phase 3 — age-gap and multimodal matching

Implement frozen age/date uncertainty features, independent model comparisons, calibrated ranking where evidence supports it, longitudinal/subgroup evaluation and optional isolated progression experiments.

Gate: sufficient lawful longitudinal coverage and subject-disjoint tests, documented age/quality/demographic limits and confidence intervals, measurable benefit at fixed review burden, no unjustified production probability claims. Synthetic production use requires a separate signed decision; absence of validation leaves it off.

## Phase 4 — NGO operations

Verified organizational onboarding, staff supervision, configurable deduplicated alerts, restricted investigations, bilateral federation and scoped disclosure/reunion approvals. Evaluate Temporal only if durable workflow metrics and operations ownership justify replacing leased jobs.

Gate: actual fraud/unsafe-family/custody scenarios, bilateral revocation/race tests, delivery audit, operator training, authority liaison protocol and supervised pilot sign-off.

## Phase 5 — production readiness

Independent security testing, restore/erasure/incident exercises, reproducible locked builds, SBOM/license/CVE review, load/soak testing, monitored NGO pilot and final release review. Establish support owner, on-call, data protection officer where required and processor agreements.

Gate: no unresolved critical child-safety/privacy vulnerabilities; measurable SLO/capacity and recovery evidence; model release and safeguarding approvals current; pilot acceptance and rollback authority signed. “Demo works” is not a release gate.

## Dependencies, ownership and estimates

No calendar promise until NGO staffing, lawful data and procurement decisions are known. Phase 1 engineering can begin only after review; operational biometric use depends on licensing/data, not merely implementation time. Privacy/legal owns lawful authority/retention; safeguarding owns claimant/disclosure/reunion policy; ML owns evidence quality; engineering/security owns technical controls; operations owns recovery.

Any phase gate can return the system to manual review mode. Scope-limited approval must specify what remains disabled and who accepts the residual risk. The assistant must not continue into application building in this run.

## Regression obligations for every phase

Use TEST_MATRIX phase applicability plus CI_CD_TEST_GATES; all affected/transitively affected tests run whenever behavior changes, and the permanent critical safeguarding subset runs on every app PR. Run the full accepted regression on main/merge queue, phase exit and release. Every phase retains unit/component, API/integration, actual DB/migration/RLS/transaction, auth, adversarial, TesterArmy browser, ar/en a11y/layout, worker, performance/resilience and deployment evidence as applicable. ML changes additionally require independent evaluation, not browser assertions.

Future unimplemented features stay pending, never passed; mandatory skips, empty discovery, incomplete shards and unavailable required services block acceptance. Sensitive verification/approval failure always leaves disclosure/release denied. B01–B11 and all model/legal/NGO approvals remain unchanged; this correction does not grant permission to begin Phase 1.
