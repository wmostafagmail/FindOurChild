# Phase 0 validation evidence

Prepared 23 October 2026. Scope: research tooling and artifact integrity only. **Final workspace checker: passed, 225 checks, 16 required documents, 14 pinned repositories, 65 inspected source files.** Actual output is recorded in [validation-result.json](validation-result.json).

## Executed checks

- Fresh isolated `npm ci --ignore-scripts` for rea-agents 6.7.0 completed successfully; 174 packages installed; version smoke check returned 6.7.0. See [clean-install.log](rea/clean-install.log). Optional platform packages in the lock need not all be installed. npm's audit output is not an independent security assessment.
- Documented Codex setup preview/apply and scoped doctor completed. Final launcher: `/Users/waleedmostafa/.codex/tools/find-our-child-rea-6.7.0/node_modules/.bin/rea mcp`. Scoped healthy=true; optional providers and bundled skill absent; live MCP discovery still needs Codex restart. See [setup summary](rea/codex-setup-summary.json) and [doctor summary](rea/codex-doctor-summary.json).
- Three static analyses completed with recorded exit 0, source identity, statistics, stderr and coverage. Original HTML and extracted-script coverage remain partial. Selected Immich files have complete supplied-file graph coverage, not whole-repository/runtime verification.
- Snapshot comparison detected and corrected an extra trailing newline before the final analysis refresh. A workspace read-integrity failure is retained; final outputs use byte-identical temporary targets without weakening REA integrity policy. See [failure](rea/workspace-integrity-failure.json) and REA_RESEARCH_REPORT for details.
- `python3 tools/validate_phase0.py` checks all 16 documents, fourteen source pins, fetched-text hashes/URLs, byte-exact snapshots/extraction, documented Evidence IDs, observed exit/parse statuses, local links, four sequence diagrams, closed event envelope and exact research package pin. These are structural/integrity checks.

## Not executed / not established

No application unit/API/integration/migration/RLS/tenant/Playwright/RTL/load/regression tests, model inference, child-image processing, production release, penetration test or operational restore. No upstream test suite was run. Full OpenAPI/JSON Schema standards conformance was not checked with an external validator; the current outline is intentionally representative and must be completed before implementation. Mermaid diagram presence is checked; renderer output was not visually tested.

Source hashes attest retained-text consistency, not upstream signing, artifact entitlement, complete license compliance or runtime correctness. No model accuracy, calibrated threshold, model weight/data permission, legal compliance or child-safeguarding approval is implied by successful tooling checks. Phase 0 acceptance and all later phase gates remain pending review.
