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

## Initial hosted checkpoint and subsequent review

PR head `8d82e8ac34899792392080321e70308a7fbff52d` passed the V3 hosted run
[41534881277](https://github.com/wmostafagmail/FindOurChild/actions/runs/41534881277).
Artifact `13183118502` has ZIP SHA-256
`7d413a446f5da7c9db64783554161269b0a0c5e532260d54a945cb169bdd2614`.
It contains 98 passing selectors, 15 actual non-neural isolation receipts,
compiled benign source outputs, and an inactive restore with three forced-RLS
relations. This includes unit tests/doubles alongside actual database/native tests;
it is not 98 real network-authentication tests or neural qualification.

The PR checkout was GitHub's merge candidate
`8fa6bbbb5a041dc7dce80a2e544b1457197a964a`; its source tree
`6786186e665a720b16aabfe84388e1f79632b48c` was independently verified equal to
the exact head tree. Source-manifest digest:
`f14414d94f3e17c45abf0b2e5e8b2e77d2ecaba238ad2fc5350d2f0277dda81c`.
Private backup SHA-256:
`6eaec299293a61bea9963193609246de3fa1975184dfbf376b971b6a56ed73c4`.

Additional review probes then reproduced two failures despite that passing
inventory: V3-FIX-01 and V3-FIX-02, retained verbatim as data-free failure evidence.
Both were repaired with additional assertions inside the existing mandatory
selectors. A focused local repair run passed four selected cases; all other
94 selectors were deselected in that focused run and are not counted as passed
there. The protected checkpoint constructor also now closes rejected file
descriptors, with an eight-attempt leak-negative test. Actual build-output hashes
are included in subsequent V3 manifests. Existing targets and controls are unchanged.

A source integration check identified the existing realm's exact API+BFF audience
set and pinned it explicitly, with duplicate/foreign/type negatives. Browser
journeys were strengthened for real nonowner MFA denial, concurrent confirmation,
simulated permanent history and actual session expiry. Final hosted validation
on the subsequent repair head is **pending**; the initial success is not final
acceptance and the 144 browser executions are not yet claimed passed.

On 2026-11-03, stale local FileProvider reads and expired temporary dependency
files blocked Git/validation tooling. Locked dependencies were restored without
changing manifests. Original saved source files were preserved privately under
`.runtime/owner-v3-file-preservation/`, and identical verified snapshot bytes
were rematerialized. Git objects were strictly verified in a complete temporary
mirror before import; the source branch advanced normally, without history rewrite.
No application failure was reclassified as an environment pass.

## Controller environment hardening

The V3 controller initially inherited synthetic private database DSNs in the
TesterArmy child environment because their names do not end in `_PASSWORD`.
No credential exposure in a public artifact or external-model request was
observed; the isolated credentials were still unnecessarily forwarded. The
controller now uses the existing strict application environment allowlist,
retaining only public synthetic-loopback/preflight flags. OD3-W16/X16 assert
that admin/runtime DSNs and tokens are stripped. The closed CI-only expiry
fixture reads its existing private synthetic state file rather than inheriting
those credentials through the browser runner. Final exact-head validation must
include this additional hardening; no previous pass is promoted to that head.

Source review also strengthened internal campaign-input and resource-ceiling
bindings before final validation. Earlier source-only admission interfaces
accepted generic privileged-caller input maps and compared measurements only
against reported ceilings; they had no enabled actual-asset consumer. The
source-only interfaces now derive exact campaign digests from protected scope,
check authority before reading sealed bytes, and require pinned producer limit
ceilings. The same frozen selectors gained negative variants and an actual
generated-buffer receipt-ingestion control. This is a documented source-review
finding; no executed real-asset exploitation, human assessment or inference is
claimed. Subsequent CI must execute all 98 selectors and 144 browser cases again.
