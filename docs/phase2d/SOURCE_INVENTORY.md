# Phase 2D source inventory

These are the explicit phase-change paths submitted for review; the Git PR diff and independently verified execution-source manifest are authoritative. Prior evidence and research are retained.

- `.github/workflows/phase1a.yml`
- `apps/web/app/[locale]/identity/session.tsx`
- `apps/web/app/[locale]/investigation/page.tsx`
- `apps/web/app/[locale]/investigation/workspace.tsx`
- `apps/web/app/style.css`
- `apps/web/app/v1/[...path]/route.ts`
- `apps/web/proxy.ts`
- `compose.yaml`
- `database/migrations/0025_synthetic_investigation.sql`
- `database/migrations/0026_synthetic_workflow_boundaries.sql`
- `database/migrations/0027_synthetic_commands_and_projection.sql`
- `database/migrations/0028_synthetic_definer_binding.sql`
- `database/migrations/0029_synthetic_denial_audit.sql`
- `database/migrations/0030_synthetic_decision_evidence.sql`
- `database/migrations/0031_synthetic_post_audit_authorization.sql`
- `database/migrations/0032_synthetic_ledger_guard.sql`
- `database/migrations/0033_synthetic_photo_projection_reauthorization.sql`
- `docs/TEST_MATRIX.md`
- `docs/contracts/event-envelope.schema.json`
- `docs/contracts/openapi.json`
- `docs/contracts/synthetic-candidate-source-v1.schema.json`
- `docs/phase1a/required-tests.json`
- `docs/phase2d/ARCHITECTURE.md`
- `docs/phase2d/ENTRY_GATE.md`
- `docs/phase2d/RUNBOOK.md`
- `docs/phase2d/TEST_TRACEABILITY.md`
- `docs/phase2d/VALIDATION_REPORT.md`
- `docs/phase2d/required-tests.json`
- `docs/phase2d/traceability.json`
- `docs/phase2d/test-to-feature.json`
- `docs/testing/test-matrix.json`
- `scripts/artifacts.py`
- `scripts/check_foundation.py`
- `scripts/dev.py`
- `scripts/fingerprint.py`
- `scripts/identity_setup.py`
- `scripts/recovery.py`
- `scripts/run-browser.mjs`
- `scripts/synthetic_workflow_setup.py`
- `scripts/workflow_fault.py`
- `scripts/workflow_http_environment.py`
- `scripts/workflow_test.py`
- `scripts/workflow_validate.py`
- `services/api/foc_api/main.py`
- `services/api/foc_api/synthetic_contracts.py`
- `services/api/foc_api/synthetic_workflow.py`
- `services/api/foc_api/worker.py`
- `tests/api/test_foundation.py`
- `tests/browser/synthetic_workflow.e2e.ts`
- `tests/database/test_rls.py`
- `tests/synthetic_workflow/__init__.py`
- `tests/synthetic_workflow/helpers.py`
- `tests/synthetic_workflow/test_boundaries.py`
- `tests/synthetic_workflow/test_capacity.py`
- `tests/synthetic_workflow/test_contracts.py`
- `tests/synthetic_workflow/test_transactions.py`
- `tests/synthetic_workflow/test_review_gaps.py`
- `tests/synthetic_workflow_http/__init__.py`
- `tests/synthetic_workflow_http/test_live.py`
- `tools/freeze_phase2d_contract.py`
- `tools/verify_phase2d_evidence.py`

No runtime or development dependency version/lock is changed. TesterArmy e2e 0.21.3, @e2e-dev/web 0.15.3 and its locked Playwright engine dependency remain pinned. No real recognition model or image dataset is acquired.

- `tests/identity/helpers.py` — supports an existing synthetic HTTP session for the real provider-sign-out / second-reviewer MFA handoff.

- `database/migrations/0034_synthetic_queue_projection.sql` — scenario-scoped projection preserving live paired authorization and unchanged direct-table RLS.
- `tests/synthetic_workflow_http/test_capacity.py` — actual 20-session /100-query /50-candidate TLS/BFF/API metadata measurement; no inference.

- `database/migrations/0035_synthetic_policy_lookup_indexes.sql` — expression indexes for unchanged policy predicates and sealed report-integrity lookups; no new grants or altered authorization functions.

- `database/migrations/0036_synthetic_live_expiry.sql` — real-time authority and pending-approval/worker deadlines after audit waits, preserving predicates, owners and grants.

- `apps/web/app/[locale]/identity/page.tsx` — corrects the stale pre-reporting notice in Arabic and English without changing authentication behavior.
