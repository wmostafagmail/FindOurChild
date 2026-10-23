# Find Our Child — Phase 0 review package

Prepared 23 October 2026 (Africa/Cairo). **Phase 0 only. No application, inference service, database or production deployment has been built.**

Start with [Phase 0 findings and decisions](docs/PHASE_0_REVIEW.md). All architecture, policies, targets and contracts are proposals awaiting the named owners' approval. Research observations are distinguished from design decisions; no child-identification accuracy has been measured here.

## Required documents

- [Product requirements](docs/PRODUCT_REQUIREMENTS.md)
- [REA research report](docs/REA_RESEARCH_REPORT.md)
- [Open-source capability matrix](docs/OPEN_SOURCE_CAPABILITY_MATRIX.md)
- [Engineering architecture and four sequence diagrams](docs/ENGINEERING_ARCHITECTURE.md)
- [Database schema](docs/DATABASE_SCHEMA.md)
- [API and event contracts](docs/API_CONTRACTS.md)
- [AI matching specification](docs/AI_MATCHING_SPEC.md)
- [Age-gap recognition research](docs/AGE_GAP_RECOGNITION_RESEARCH.md)
- [Model evaluation plan](docs/MODEL_EVALUATION_PLAN.md)
- [Security threat model](docs/SECURITY_THREAT_MODEL.md)
- [Child safeguarding policy](docs/CHILD_SAFEGUARDING_POLICY.md)
- [Privacy and retention](docs/PRIVACY_AND_RETENTION.md)
- [UI/UX specification](docs/UI_UX_SPECIFICATION.md)
- [Test strategy](docs/TEST_STRATEGY.md)
- [Implementation phases](docs/IMPLEMENTATION_PHASES.md)
- [Deployment operations](docs/DEPLOYMENT_OPERATIONS.md)

Phase 0 testing corrections:

- [TesterArmy/e2e framework integration](docs/E2E_FRAMEWORK_INTEGRATION.md)
- [Complete planned test matrix](docs/TEST_MATRIX.md)
- [CI/CD test gates](docs/CI_CD_TEST_GATES.md)
- [Security and safeguarding test catalogue](docs/SECURITY_TEST_CATALOG.md)
- [Correction validation evidence and limitations](docs/research/e2e/VALIDATION_REPORT.md)

TesterArmy/e2e is the principal planned browser functional runner. All application test cases are pending; documentation/configuration checks do not establish application behavior. Original research and child-protection decisions remain unchanged.

The [research manifest](docs/research/repository-lock.json) pins reviewed commits. Source snapshots and REA outputs are research evidence, not approved dependencies or application assets. The FindTrace snapshot lacks an identified reuse license; do not incorporate it into product code or redistribute it as a licensed component.

REA 6.7.0 is installed under `tools/rea`, with an exact npm lockfile. Its Codex registration uses the durable runtime under ~/.codex/tools/find-our-child-rea-6.7.0; the workspace retains reproducible package/lock files. Restart Codex to load newly registered tools. CLI analysis has already been performed independently of that restart.

## Review boundary

Phase 1 remains **not authorized by this package**. The original instruction requires stopping after Phase 0. NGO, legal, safeguarding and technical owners must review the decisions and phase gates before implementation begins.
