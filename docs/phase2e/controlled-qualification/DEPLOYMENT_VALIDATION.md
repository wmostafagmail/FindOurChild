# Deployment-readiness validation

Status: implementation under validation; no actual owner deployment or campaign exists. Historical main verification is `exact-main-ci.json` on d6bb3cf869db9b578216295c5499fe93e32656f4, required run 41645205005 success.

Local validation: 52 new unit tests passed, Ruff checks passed, E2E TypeScript passed and 207 foundation/configuration checks passed. Docker daemon did not answer the bounded local probe; no local Docker startup or browser execution is claimed. Hosted Linux integration/complete regressions are pending this implementation head.

Frozen execution inventory: `../deployment-required-tests.json`: 67 selectors (52 unit + 15 actual-service integration/worker/recovery cases), zero mandatory skips allowed; one official TesterArmy scenario across 24 targets (8/engine). The mandatory foundation workflow requires the new readiness reusable job in addition to unchanged V2, V3 and identity preflights. The original full regression remains 747 Python, 360 official application browsers, 144 V3 owner browsers/16 synthetic lifecycle cycles, 76 V2, 136 E0, 52 source-only native and 36 migration/recovery checks. Inventories are separate; overlapping selectors are not unique additional coverage.

Source evidence: the new runner records exact checkout/tree, per-file SHA-256 source inventory, actual built image identities, structured per-test stage status, worker resource receipts, sanitized deterministic browser step traces and signed-out-only screenshots. Raw tokens, generated setup codes, private credentials, backup SQL, container/pytest logs stay in private runner storage and are not uploaded. Published payload hashes cover the sanitized files. Failure summaries contain fixed stages/types and private diagnostic hashes, never JWTs or DSNs.

Final exact-head hosted run IDs, results, failures/repairs and downloaded artifact integrity checks must be appended after execution. Pending/running/skipped tests never count as successful validation. Real hosting/DNS/TLS/IdP owner setup remains an external-resource boundary even if generated CI passes.
