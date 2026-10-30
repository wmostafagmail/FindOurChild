# Phase 2E demo governance validation

Scope: **source-only engineering; Phase2E incomplete; owner review required**. No actual human appointments, trusted keys, issued permits, acquired assets, unpacked/scanned assets, model parsing or neural inference. Original A1b review remains unmet with demo waiver; all actual acquisition/execution locks remain false. No Phase2F/3 or merge authorization.

## Verified starting point and preservation

PR #11 merged into main `f1de81728efff491c2ecb964104dcd50e9f8a085`. GitHub required `phase1a-required` succeeded on that exact revision: [run41083456269/job124158334906](https://github.com/wmostafagmail/FindOurChild/actions/runs/41083456269/job/124158334906). Its tree `1b26efbaa32ba66995c8bf0522c249d5280f9082` equals approved policy checkpoint797d940. New branch `codex/phase-2e-demo-governance` preserves history. First commit `4e78844c2c9ccba53920a84f5caf3d6fcd1ad605` adds only the four unchanged planning files.

| Historical file | Preserved SHA-256 |
|---|---|
| DEMO_GOVERNANCE_IMPLEMENTATION_CHECKLIST.md | c0b589657ade0183c154c273eeb64333639d4c9624dd547dadf9b1baa35aa618 |
| DEMO_GOVERNANCE_NEGATIVE_TEST_PLAN.md | 7929e2666c4b05988a035b6b119fe487606774da2b5ccf993f4e401430104db2 |
| DEMO_POLICY_DESIGN_APPROVAL.md | 830abb2b5fa4f6458e5f6e530b5a74f62560db4aa85c096b91a84916c01047e5 |
| DEMO_GOVERNANCE_PLAN_STATUS.json | 33c8f39419c39ce7996b51bb285f99114b9be4ce434efdb99cd3d39db10f2950 |

The original approved policy, source projection, native fixed model identities/guard, v1 approval verifier and all prior native/source findings remain unchanged. Build retention is additive: new CI builds retain actual new wheels/extensions/contract binaries. This does not recover the missing original binaries from older CI archives.

## Commands and evidence contract

- `python -m ruff check tools/phase2e services/demo_recognition tests/phase2e tests/demo_governance`
- `python -m pytest --confcutdir=tests/demo_governance tests/demo_governance/test_records.py tests/demo_governance/test_registry.py tests/demo_governance/test_enrollment.py tests/demo_governance/test_evidence.py -q --tb=short`: **39 passed, zero skipped**, local CPython3.13.13. Includes positive chains/enrollment, actual cryptography, transactional SQLite enrollment/revocation, fixture immutability and negative evidence inventory checks.
- `python -m pytest --confcutdir=tests/phase2e tests/phase2e -q --tb=short`: **136 passed, zero skipped**, local source-only controls. This is not the native Linux qualification or original application regression.
- `python -m tools.phase2e.demo_governance.run_checks`: mandatory Linux x86_64 source-only probe/container build, sealed-descriptor tests, **76 exact tests covering64 mapped DG IDs**, private real PostgreSQL/forced RLS/concurrency/audit/restore checks. Missing Linux/PG/image fixtures fail rather than skip.
- Existing `phase2e-source-preflight`: all136 E0 controls, unchanged52 source-only native tests, closed six-interface build, dependency audit and source projection. No model is loaded.
- Existing `phase1a-required`: all747 Python/API/database/security/integration tests,36 migrations/recovery,360 official TesterArmy/e2e0.21.3/web0.15.3 browser executions:120 Chromium,120 Firefox,120 WebKit. Actual services/isolated database, Arabic/English, responsive/accessibility, deterministic assertions. New governance prerequisite must succeed; failure/cancellation is an explicit red required check.

Hosted execution results are generated on the exact checked-out revision, not inferred from local tests or earlier commits. `artifacts/phase2e-governance/results.json` contains every selector's setup/call/teardown and a no-skip/no-missing inventory gate; `manifest.json` contains exact source-file hashes, GitHub checkout SHA, build/image identities, benign binary digests and actual restore results. `phase2e-source-only-*` retains source/native build evidence; `phase1a-sanitized-*` retains application/browser/migration evidence. PR versus push checkout commits must be distinguished. Final run URLs, exact head and artifact identities are recorded with the draft PR review report after execution. No unexecuted hosted suite is counted as passed by this document.

## Verified governance checkpoint (not a claim about a later head)

At implementation `65b88a64ce12ce2a06ac864124319948ea63ebae`, both [push41097299211](https://github.com/wmostafagmail/FindOurChild/actions/runs/41097299211) and [PR41097310358](https://github.com/wmostafagmail/FindOurChild/actions/runs/41097310358) passed76/76 tests, zero skips, all64 DG families. Independently downloaded artifacts verified every setup/call/teardown outcome, all7 retained build-source/binary/compiler/dependency files against their hashes, inactive restore and forced RLS. Both source manifests equal `da5d8f5e5fa40efc0c1adea49d94cf99d0919d790a4678a73b9c23fc5bb6b1a7`. Push checkout is65b88a6; PR synthetic merge checkout is884b5c3ac64edc424357ee3d2ce8b1fb0d070544. These are distinct Git revisions with identical tested governance inputs.

See [current checkpoint inventory](DEMO_GOVERNANCE_IMPLEMENTATION_STATUS.json) and [remaining blockers](DEMO_GOVERNANCE_BLOCKERS.md). The final exact-head full/native/browser result table and artifact identities are published in the [PR12 validation report](https://github.com/wmostafagmail/FindOurChild/pull/12). This committed document freezes the named checkpoint evidence; it never extrapolates a pass to a subsequent commit. Missing, running, failed or cancelled checks do not count as successful validation.

## Failed attempts retained

Private local attempt logs under `artifacts/raw/governance-local/` retain initial failures and repairs: unknown-action test-helper dispatch, RFC8032 vector transcription, test clock construction across a second boundary, missing enrollment-scope fields during development, lint/import corrections, the hosted standalone-Python sealed-memory binding, an overbroad artifact-name scan, and a positive fixture under unsafe hosted /opt ancestry. The latter moved to protected /var/lib; ownership/sealing rules remain unchanged. These were engineering defects corrected before final execution, not waived mandatory checks. No dependent asset work occurred. Failed hosted attempts, if any, remain available in GitHub and are recorded in the final review report rather than overwritten or relabeled.

## Limits and owner checkpoint

See [implementation and residual risks](DEMO_GOVERNANCE_IMPLEMENTATION.md) and [selector traceability](governance-required-tests.json). The64 DG IDs are test families: scanning/decoder-failure scenarios validate rejection of synthetic receipts; they do not claim an actual asset scan. Control-plane-loss tests use owned synthetic helpers and client loss, not destruction of the shared Docker daemon. Future actual parser/load/inference, real O/T/F decisions and live operational-case permission integration remain unqualified and disabled. Source-only results establish neither model safety on hostile model bytes nor missing-child recognition accuracy.

Frozen database p95:1,149.158629ms push /1,126.882086ms PR, target1,000ms unchanged; **missed, owner-accepted demo exception**. Actual-head regression measurements must be reported separately. Phase3 manual Arabic/screen-reader/long-history gates and the later additional192 official model-workflow browser executions remain pending. This PR is not full Phase2E acceptance or permission to enroll/acquire/parse/infer/merge.

Source-review hardening after65b88a6 removed unused runtime `SELECT` on the private authority table and added an actual PostgreSQL denial assertion. Only RLS-filtered jobs are readable by that role; publication uses the fixed guarded function. This is a new tested input and must pass final-head CI; the65b88a6 source hash is not relabeled as this revision.

## Author source-review finding DG-FIX-01

An isolated synthetic reproduction against4a654c2 showed that the old A6 check accepted a changed-link attestation with a backdated claimed review time. No actual key, fixture or model was active. This finding is preserved privately at `artifacts/raw/governance-local/blinding-before-repair.json`; previous passing inventories are not a completed security assessment. The repair binds renewal to the exact original reviewer/fixture/review-time/evidence identity sealed in the owner's signed score-access epoch transition. The original A6 must have been durably accepted before any score access. A new or changed post-score review by that person is denied even when backdated; an unchanged authentic original can renew, and an actually unexposed newly appointed F remains a separate later path. DG-R09 now exercises the negative and authentic-renewal outcomes. All affected suites must rerun on the new exact head. This is author-led engineering review, not the waived independent human assessment.
