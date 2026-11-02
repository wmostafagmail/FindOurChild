# V3 source-only validation checkpoint

Design checkpoint: `51c29c0e39424db243f30ce4d6d5ee8900ee122f`.
This report is written before the first implementation CI push. Final hosted
results must be verified against the subsequent exact implementation head and
published in the draft PR/evidence package. Nothing pending here is a pass.

| Check | Actual checkpoint result |
|---|---|
| Local source unit scenarios | 78 passed, 12 explicitly deselected Linux/infrastructure cases; unit doubles only, not complete validation |
| Focused first-run/domain/renewal rerun | 3 passed after repair |
| Additional local boundary tests | 4 passed, 4 infrastructure cases deselected; not a real-PostgreSQL or full API validation claim |
| Locked TypeScript source-copy checks | Web and E2E compiler checks passed with pinned temporary dependencies |
| Locked dependency install | 74 packages installed from original lock, 0 npm audit findings reported by install |
| Ruff source checks | Passed before source checkpoint; rerun in hosted CI |
| 98 V3 Python tests, actual PostgreSQL/native/recovery | Pending hosted execution |
| 144 new official TesterArmy browser executions | Pending hosted execution |
| Original 747 Python/API/security/RLS, 360 official browsers, 36 migrations/recovery | Pending exact-head regression |
| Original 76 V2 governance, 136 E0, 52 source-only native | Pending exact-head regression |
| Independent human A1b review | Unmet, original demo waiver retained |
| Database p95 performance | Unresolved owner-accepted demo exception; target remains 1,000 ms |
| Actual owner provisioning/authorizations, assets, neural inference | None; disabled |
| Full Phase 2E acceptance | Incomplete; no automatic merge |

## Failure and repair history

1. First local collection failed on a missing closing list bracket in the new
   scenario inventory. Corrected the source; no test was removed.
2. First focused run: 9 passed, 3 failed. The failures exposed the fixture catalog
   `sealed_demo_test` versus schema `evaluation` label mismatch, and a test using
   JSON-object digest on raw bytes in the V1/V2 rejection control. The synthetic
   fixture label mapping is explicit; the frozen design is unchanged. The V2
   rejection test now calls the actual V2 chain verifier with a raw-byte digest.
   All three focused tests subsequently passed.
3. Initial root type-check could not locate `tsc` because local dependencies were
   incomplete. Installed the exact existing lock into a temporary directory and
   compiled exact source copies. An attempted compile before copying completed
   failed dependency resolution; sequential reruns passed for both configurations.
4. Ruff found syntax/import/sorting/loop-capture/explicit subprocess-check issues;
   corrected those without relaxing lint or test gates.

Private local logs are retained under `/private/tmp/foc-v3-*.log` and are not
published as sanitized execution evidence. Subsequent hosted failures and repairs
must be added with run IDs and source identities. No earlier failure is erased
or reclassified as a pass. Synthetic engineering does not establish image rights,
model compatibility, neural inference, independent blinding or identification accuracy.
