# Phase 0 review and decisions

> Phase 1A update: the user explicitly authorized foundation implementation only after this Phase 0 review. The immutable preimplementation package is Git commit `40231be73ab9a5eb577ccf5308c86f6b7282976b`; its original validators still run against that commit. Current findings/evidence are in [Phase 1A review](phase1a/REVIEW.md). Research, licensing, legal authority, safeguarding, retention and model-evaluation approvals have not been inferred from engineering progress. Phase 1B remains unapproved; Phase 1A technical gates now pass and await owner acceptance review.

Prepared 23 October 2026; corrected testing architecture 23 October 2026. **Research/specification package ready for review; human Phase 0 acceptance remains pending. No application built and no application tests passed.**

## Recommended architecture

Arabic-first Next.js/React/TypeScript frontend, FastAPI modular domain backend, PostgreSQL/pgvector, private S3-compatible storage with separate quarantine/original/derivative access, Keycloak staff MFA, restricted image/ML workers and transactional outbox/leased jobs. Audit is append-only to application roles with independently retained tamper evidence.

Reports remain independently owned cases with attributed claims and verified assertions. Missing/found comparison is scoped by organization and case permission; cross-NGO matching is disabled until bilateral legal/safeguarding agreements and case grants exist. No public biometric search or identity/location lookup.

Matching combines independently retrieved face and structured leads, preserves multiple image ages/model spaces, and exposes uncertainty to trained reviewers. Identity confirmation, limited disclosure, custody authorization and witnessed reunion are separate human decisions.

## Adoption recommendations

| Category | Recommendation |
|---|---|
| Adopt | FastAPI; PostgreSQL + pgvector; Keycloak subject to operations owner; REA for bounded research |
| Adopt for Phase 1 testing | TesterArmy/e2e as principal browser runner with its Playwright-based web engine, model-free deterministic assertions and separate coordinated specialist suites |
| Adapt for lawful evaluation | InsightFace adapter and DeepFace comparison wrappers; AdaFace quality-aware baseline after checkpoint/data rights review |
| Study only | CompreFace services; Immich photo/ML boundaries; PhotoPrism provenance, compatibility and license gates |
| Defer | Qdrant scale-out; Temporal durable workflows; MinIO production provider selection pending maintenance/license/support assessment |
| Reject production base | FindTrace: unsuitable trust boundaries, no identified reuse license, unverified aging/accuracy/privacy claims |

All required repos have reviewed SHA pins and all ten requested assessment dimensions in OPEN_SOURCE_CAPABILITY_MATRIX. Code licenses do not clear pretrained weights/data. Exact installed research dependency: rea-agents 6.7.0; production application releases/digests remain a gated phase 1 selection, since no app dependencies were installed.

## Evidence highlights

REA Codex configuration applied with backup and scoped diagnostic healthy. Restart Codex to load the new MCP registration; static CLI use already verified. Three retained analyses cover original FindTrace HTML, its provenance-mapped extracted script and two selected Immich TypeScript interfaces. Partial coverage is explicitly preserved. Clean research-tool installation and document/evidence checks are recorded in [validation](research/VALIDATION_REPORT.md).

FindTrace source includes localStorage, a distance-to-percentage match label, procedural canvas aging, IP geolocation and an external descriptive-prediction request; the latter makes its blanket local-only privacy claim unsupported by source. No application was executed and no data transmission/recognition performance was measured.

Independent research supports investigating longitudinal degradation; it does not establish a safe operational model here. See AGE_GAP_RECOGNITION_RESEARCH for papers and access limitations.

## Blockers and required owners

| ID | Blocker / decision | Owner | Blocks |
|---|---|---|---|
| B01 | Lawful basis and current Egyptian regulator/children/biometric obligations; controller/processor allocation | Qualified Egyptian counsel + NGO privacy owner | Real-data collection/pilot |
| B02 | Safeguarding SOP, authority liaison, claimant risk assessment and distinct reunion/disclosure approvers | NGO safeguarding + competent authority liaison | Operational case decisions |
| B03 | Approved maximum retention, rights handling, legal holds and backup erasure | Counsel + privacy + operations | Real-data ingestion |
| B04 | Exact detector/recognizer weight and training-data permissions; artifact hashes | Counsel + ML/procurement | Model installation/evaluation/operational use according to license |
| B05 | Lawful, independently verified longitudinal population data and subject-disjoint protocol | Data custodian + ML + safeguarding | Meaningful phase 2/3 model validation |
| B06 | Measured open-set thresholds, subgroup/age-gap coverage and acceptable review burden | Independent validation + NGO technical/safeguarding owners | AI activation |
| B07 | Hosting region/provider agreements, KMS owner, backup/recovery/support | Privacy + infrastructure + NGO procurement | Deployment |
| B08 | Supported released application dependencies, full lock/SBOM, complete OpenAPI/DDL and compatibility baseline | Engineering + security | Phase 1 implementation |
| B09 | Bilateral matching/legal agreement, purpose grants and recipient disclosure policy | Both NGOs + counsel + safeguarding | Cross-NGO matching (can remain disabled) |
| B10 | Capacity/SLOs, on-call staffing, notification templates/channel/provider and escalation ownership | NGO operations + engineering | Pilot readiness |
| B11 | Explicit review of this Phase 0 package and authorization for next phase | User + NGO technical/safeguarding sponsors | Phase 1 start |

These are concrete review decisions; no approval is presumed. Architecture can support a manual single-NGO pilot before AI/federation, but even that needs legal basis, secure reporting and safeguarding acceptance. Numeric retention/SLO suggestions are proposals, not law or measured commitments.

## Age-gap gaps and experimental boundary

Infant/young-child performance, large actual photo gaps, poor historical images, relatives/lookalikes, intended Egyptian population, training-data overlap and probability calibration remain unresolved. Evaluate independent model families, real photographs and age intervals first. Synthetic progression stays research-only and never becomes identity evidence or a production feature without separate measured validation and signed approval.

## Data/API summary and build plan

Data model: organizations/memberships/grants; missing/found cases; attributed assertions; reporter access; private originals/derivatives/selected faces; immutable model manifests/spaces/embeddings; runs/leads/reviews; restricted custody; scope-bound approvals/handovers; outbox/jobs; audit/deletion ledger.

API separates public intake, secure own-submission access, staff case/evidence work, internal matching and safeguarded disclosure/reunion commands. Events contain opaque references and revisions, not child data. Representative OpenAPI and closed event-envelope schema accompany the full route outline.

Next phases: (1) reporting/manual case management, (2) versioned AI retrieval and review, (3) longitudinal/multimodal validation, (4) NGO operations and optional federation, (5) security/model/recovery pilot acceptance. Each requires its own unit/component/contract/integration/migration/RLS/authorization/adversarial/TesterArmy browser/RTL/worker/performance/resilience/deployment/regression evidence and clean installation. Browser E2E does not replace specialist database/security/penetration/ML validation. See IMPLEMENTATION_PHASES and TEST_STRATEGY.

## Correction readiness assessment

Added [TEST_MATRIX](TEST_MATRIX.md), [E2E_FRAMEWORK_INTEGRATION](E2E_FRAMEWORK_INTEGRATION.md), [CI_CD_TEST_GATES](CI_CD_TEST_GATES.md) and [SECURITY_TEST_CATALOG](SECURITY_TEST_CATALOG.md); updated the five requested architecture/phase/testing/operations/review documents. The matrix registers every currently declared FR, API operation, event, additional job, database relation boundary, transaction race and safeguarding workflow with planned executable IDs/paths, scenarios, fixtures, outcomes, evidence and pending status. Matrix generation is documentation work, not implemented application tests.

TesterArmy source commit 69e123b17e04ed624df16d32f3b1ef95ce22c083 is recorded separately from the original fourteen repository pins. Exact selected packages: e2e 0.21.3, @e2e-dev/web 0.15.3, playwright-core 1.64.1; the installed Node 24.18.0/npm 11.16.0 and specimen compiler/lock are recorded. Type/load/telemetry command evidence and limits are in [the correction validation report](research/e2e/VALIDATION_REPORT.md). Browser binaries/full-stack behavior remain untested. Discovery returning NO_TESTS is an expected non-success because no application tests exist; it must never satisfy a phase gate.

Original research/product/API/data/model/security/privacy/safeguarding documents and REA locks are protected by a [baseline hash manifest](research/e2e/protected-baseline.json). B01–B11 and original human/NGO/legal/model approval decisions remain unchanged. Mandatory telemetry opt-out, model-free regression, actual isolated services/DB, deterministic outcomes, no real child data to external testing models, sanitized artifacts and no-skips reconciliation are now explicit design gates.

### Missing evidence, unsupported assumptions and conflicts

- No application services/database/suites exist; all application test cases are pending. No E2E result substitutes for database/RLS, penetration or model evaluation.
- Existing OpenAPI is a representative four-operation outline, while the declared route inventory has 32 operations. Exact complete DTO/status contracts, executable migrations, additional administrative grant/alert/federation operations and their tests must be finalized before implementation. Matrix completeness is measured against the current declared inventory, not an assertion that all future product contracts are frozen.
- Upstream documents model-free testing and Codex integration, but no plugin/MCP activation or browser execution is performed here. Type compatibility/peer metadata is verified; app integration/browser/OS and hosted CI required-check behavior are not.
- Upstream default telemetry, optional model/cache fallback, CI retry/clean-skip/no-test behavior and unredacted artifacts conflict with our sensitive testing policy. The selected model-free specimen opts out of telemetry, disables cache/retries and requires a separate expected-result/sanitization gate; those application CI gates remain to be implemented and tested.
- Other suite-tool releases/runner images/action digests, complete fixture seeders, artifact sanitizer, independent result reconciler, active CI required checks and release/rollback evidence remain Phase 1+ deliverables. No fabricated workflow YAML or success report stands in for those missing components.
- The current workspace is not a Git repository and has no configured PR/merge protection. Required CI check names are specifications until a project repository/CI host is established and enforcement is demonstrated.

Readiness: corrected **Phase 0 documentation and configuration package for review**, with explicit production/implementation blockers retained. Phase 1 remains stopped until the user authorizes it and relevant owners accept its entry gates.

## Review outcome to record

For each decision: named accountable signer, approved/rejected/deferred status, evidence references, scope/conditions, date and review expiry. Phase 1 starts only after explicit next-phase instruction and relevant gate acceptance. This run stops after Phase 0 as requested.
