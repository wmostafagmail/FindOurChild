# Deployment-readiness validation

Status: implementation under validation; no actual owner deployment or campaign exists. Historical main verification is `exact-main-ci.json` on d6bb3cf869db9b578216295c5499fe93e32656f4, required run 41645205005 success.

Local validation: 52 new unit tests passed, Ruff checks passed, E2E TypeScript passed and 207 foundation/configuration checks passed. Docker daemon did not answer the bounded local probe; no local Docker startup or browser execution is claimed. Hosted Linux integration/complete regressions are pending this implementation head.

Frozen execution inventory: `../deployment-required-tests.json`: 77 selectors (61 unit + 16 actual-service integration/worker/recovery cases), zero mandatory skips allowed; one official TesterArmy scenario across 24 targets (8/engine). The mandatory foundation workflow requires the new readiness reusable job in addition to unchanged V2, V3 and identity preflights. The original full regression remains 747 Python, 360 official application browsers, 144 V3 owner browsers/16 synthetic lifecycle cycles, 76 V2, 136 E0, 52 source-only native and 36 migration/recovery checks. Inventories are separate; overlapping selectors are not unique additional coverage.

Source evidence: the new runner records exact checkout/tree, per-file SHA-256 source inventory, actual built image identities, structured per-test stage status, worker resource receipts, sanitized deterministic browser step traces and signed-out-only screenshots. Raw tokens, generated setup codes, private credentials, backup SQL, container/pytest logs stay in private runner storage and are not uploaded. Published payload hashes cover the sanitized files. Failure summaries contain fixed stages/types and private diagnostic hashes, never JWTs or DSNs.

Final exact-head hosted run IDs, results, failures/repairs and downloaded artifact integrity checks must be appended after execution. Pending/running/skipped tests never count as successful validation. Real hosting/DNS/TLS/IdP owner setup remains an external-resource boundary even if generated CI passes.

## Preserved first attempt — eaaf5f94320ee69257ada5566519783a3871f7d5

PR required run 41669863244, job 126036788225, checked out generated merge 4929c253cae82bb08608ab27f4294e7e113d19c0 (same implementation tree with main). Actual generated TLS/Keycloak/PostgreSQL/private enrollment/registration/recovery and benign worker tests reached 62/62 passed, zero skips. Browser result: 0/24 passed, 24 failed (8 per engine), all at initial browser.evaluate before app.open. Official web engine initializes its page on first app.open; the test now explicitly opens the private shell before querying locale. No production guard, browser, assertion or target was removed. The failure remains failed and is not replaced by the local unit pass.

Original data-free artifact 13247802847 archive SHA-256: 953fc7406a803f9dd56b65e3cb08fd9b88a5a36fcaf28efdf2cc847e149e6439; independently downloaded and verified. Original job log retained locally at /private/tmp/foc-deployment-first-job.log; the GitHub job preserves the original public log. Sanitized Python/browser/failure reports retained under /private/tmp/foc-deployment-evidence/eaaf5f94-pr. Subsequent source adds five real-storage denial scenarios and actual running-container profile checks, giving 68 frozen selectors. Additional reporting now records explicit failure stage, service image identities and strict cleanup failures.

Superseded b9e documentation-head required runs 41661939055 and 41661807680 were canceled to release current-head validation. They are never counted as successful current validation; their logs/evidence remain retained by GitHub.

## Additional source review repair

Review of the new readiness UI found that `default-src 'none'` also blocked its own same-origin authenticated fetch requests: the new CSP omitted `connect-src 'self'`. The repair permits only same-origin connections, adds an explicit header assertion and retains all other restrictive directives. This is a defect in the newly added readiness surface; original application/V1/V2/V3 policies are unchanged. Owner status also now measures the authorization journal count and denies unexpected campaign records instead of merely returning a constant zero. Generated-service tests explicitly query that no campaign records exist. Superseded f0b1d73e validation remains non-final; exact replacement-head validation is required.

## Source integrity and enrollment atomicity review

Two additional deployment boundaries are now checked before any trust mutation: runtime configuration must match the immutable baked source release, and a producer record must pass closed shape/key/hash/profile/stage validation before reserving an external registry head. Otherwise a stale container could claim a newer configuration, or malformed operator input could irreversibly consume a checkpoint reservation before rejection. Nine new executable negatives/positive release cases cover these boundaries. Current frozen total is 77 (61 unit, 16 actual-service cases), with all original inventories retained. A test-data key is never trusted as a real owner/asset identity. Final exact-head results will be recorded in the PR and source-bound hosted manifests; this committed report preserves the pre-validation state honestly.
