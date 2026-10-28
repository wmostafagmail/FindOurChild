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

- `services/api/foc_api/identity.py` — bounded connection/TLS transport reuse with per-request cookie/client isolation, unchanged validation/introspection/timeout and zero retries.

## Verified evidence follow-up

The following documentation and sanitized evidence paths bind the completed implementation to both successful hosted runs. Raw artifacts remain ignored.

- `docs/phase2d/hosted-ci-verification.json`
- `docs/phase2d/hosted-artifact-verification.json`
- `artifacts/phase2d-sanitized/checksums.json`
- `artifacts/phase2d-sanitized/coverage.json`
- `artifacts/phase2d-sanitized/results.json`
- `artifacts/phase2d-sanitized/screenshots/101b464ada9e50d0c5b2f42a.png`
- `artifacts/phase2d-sanitized/screenshots/1165a08d1e669c0ac2e1f81c.png`
- `artifacts/phase2d-sanitized/screenshots/1b5ae5bfe75e5d95e9d42134.png`
- `artifacts/phase2d-sanitized/screenshots/1c9daf64f3b2aa34f436a07e.png`
- `artifacts/phase2d-sanitized/screenshots/224ef0a9ba66c7e6497e6e5a.png`
- `artifacts/phase2d-sanitized/screenshots/235613da95edbe7830ac3405.png`
- `artifacts/phase2d-sanitized/screenshots/24418c64649f0887ab7ea242.png`
- `artifacts/phase2d-sanitized/screenshots/24a0f72d9ff8b89e9209ca54.png`
- `artifacts/phase2d-sanitized/screenshots/2999987337565fd5887821da.png`
- `artifacts/phase2d-sanitized/screenshots/2a8913893054e7b7b74eeee4.png`
- `artifacts/phase2d-sanitized/screenshots/2cd73abe59808e8ef04589e0.png`
- `artifacts/phase2d-sanitized/screenshots/32f15078a1c4fd7c47c4bbe9.png`
- `artifacts/phase2d-sanitized/screenshots/4eb89fadf6562e3091f8ad30.png`
- `artifacts/phase2d-sanitized/screenshots/4f80e2b770a365692abf6a7d.png`
- `artifacts/phase2d-sanitized/screenshots/553ef84be7a12ea9455cf391.png`
- `artifacts/phase2d-sanitized/screenshots/557ca6b6e49b482317a64531.png`
- `artifacts/phase2d-sanitized/screenshots/5c9d7b05ddf5ce482252931e.png`
- `artifacts/phase2d-sanitized/screenshots/71ed094c090d68a8f57795dc.png`
- `artifacts/phase2d-sanitized/screenshots/740f21f34af4f1703f84d66f.png`
- `artifacts/phase2d-sanitized/screenshots/7bdc68b3b97e96d76e61a5dc.png`
- `artifacts/phase2d-sanitized/screenshots/7c5f31149c6247b6741c3368.png`
- `artifacts/phase2d-sanitized/screenshots/7f94c5e0367d3b27ada865ef.png`
- `artifacts/phase2d-sanitized/screenshots/84bf7bfc938b08f08ae9bd0b.png`
- `artifacts/phase2d-sanitized/screenshots/85adbac21bf4016ac3c3b0b1.png`
- `artifacts/phase2d-sanitized/screenshots/87abdf0044c02afc21878865.png`
- `artifacts/phase2d-sanitized/screenshots/8a753ade6f0e8102859f5228.png`
- `artifacts/phase2d-sanitized/screenshots/8efe0c8388b25e65209908cc.png`
- `artifacts/phase2d-sanitized/screenshots/90070ff5239c4d1934c76d0d.png`
- `artifacts/phase2d-sanitized/screenshots/90807f782b4d67c4c72ea68a.png`
- `artifacts/phase2d-sanitized/screenshots/96fa878d9dd7902b230addee.png`
- `artifacts/phase2d-sanitized/screenshots/9e5cdc969a8dbcdb4ecf8685.png`
- `artifacts/phase2d-sanitized/screenshots/9feededbecf84943688f7b2d.png`
- `artifacts/phase2d-sanitized/screenshots/a3409da405c636eb02741123.png`
- `artifacts/phase2d-sanitized/screenshots/a6e2e76926dd0b478bb2537f.png`
- `artifacts/phase2d-sanitized/screenshots/adf9920be2e446e1ef60585a.png`
- `artifacts/phase2d-sanitized/screenshots/b0dd258c76bda91bc9d77fd3.png`
- `artifacts/phase2d-sanitized/screenshots/bed623cf1f815caefb58e0b4.png`
- `artifacts/phase2d-sanitized/screenshots/c1517adc2657cb4775976de2.png`
- `artifacts/phase2d-sanitized/screenshots/c27715ff9eb2572bcc28b84f.png`
- `artifacts/phase2d-sanitized/screenshots/d13748565554379043d097f1.png`
- `artifacts/phase2d-sanitized/screenshots/d166b3dc2693f963598b32f1.png`
- `artifacts/phase2d-sanitized/screenshots/d38e731e788a530897f7c98a.png`
- `artifacts/phase2d-sanitized/screenshots/d7f585cefcbf8d93129ea2e3.png`
- `artifacts/phase2d-sanitized/screenshots/ea4b50c15036b3158f5d5453.png`
- `artifacts/phase2d-sanitized/screenshots/f1ba04bab5fbd730edc26f34.png`
- `artifacts/phase2d-sanitized/screenshots/f64eb9b3d07166d2b19a7095.png`
- `artifacts/phase2d-sanitized/screenshots/f8f0b344a276441411373b80.png`
- `artifacts/phase2d-sanitized/screenshots/fcee01e0daf9982eb697d429.png`
- `artifacts/phase2d-sanitized/source-manifest.json`
- `artifacts/phase2d-sanitized/traces.json`
- `artifacts/phase2d-sanitized/validation.log`
