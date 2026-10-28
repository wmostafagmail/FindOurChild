# Phase 2D validation report

Status: **final corrections pending exact-source hosted validation; not accepted**. Phase 2E has not begun. No pending, canceled, skipped or unexecuted result is counted as successful validation.

## Preserved scope and required inventory

The unchanged approved roadmap/licensing packet passed the entry gate before implementation; see [ENTRY_GATE.md](ENTRY_GATE.md). All prior research, 49 API operations, schemas, dependency locks, migrations 0001–0024 and the 190-feature / 1,216-case traceability baseline are preserved. Current required inventory: **738 Python** (554 preserved, 119 workflow unit/real-PostgreSQL, 65 real HTTP), **360 official TesterArmy executions** (120 Chromium, 120 Firefox, 120 WebKit), and **33 migrations**. The exact inventories and all 80 new logical scenarios remain pending final hosted verification. [Reverse mapping](test-to-feature.json) covers every new selector. No Playwright-only acceptance suite replaces official e2e 0.21.3 / web 0.15.3.

## Current local evidence

The corrected backend passed all 119 workflow unit/PostgreSQL/security tests and all 65 live TLS/Keycloak/BFF/API tests. The live lane includes revocation during actual audit waits, missing/corrupt migration ledger, private-storage restart, real bounded cgroup OOM with fenced recovery, and two denial-audit availability tests. These local results are recorded at their actual source digests and do not replace full exact-commit hosted regression. Type checking, production builds under pinned Node 24.18.0 and Ruff passed. Original logs remain private in `artifacts/raw/phase2d-local-history/` and `/private/tmp/foc-phase2d-*.log`.

A controlled local diagnostic reproduced TOTP replay rejection on Keycloak 26.7.0: first login completed, second same-account/code login in the same window was rejected. No MFA policy changed. A separate actual-database diagnostic reproduced synchronous denial auditing blocking unrelated health requests while the audit lock was held. The repair moves audit I/O off the event loop and applies bounded database waits; both real HTTP handler variants now pass. Diagnostics are not extra acceptance passes.

## Preserved hosted failures and corrective work

Original `302b727` push run 40534943176 failed: 225/360 browser executions passed and 135 failed at initial MFA completion; workflow HTTP was 2/55 passed. Distinct closed credentials per browser journey/HTTP scenario now preserve the IdP replay/brute-force policy without reusing one credential/code.

On `7adf29b26b3acf1b1846f763f31c910d1ca09497`, both runs 40602535242 and 40602541085 retain canceled/blocked outcomes and original digest-verified artifacts. Every browser engine executed 120 tests: **104 passed / 16 failed per engine; 312 passed / 48 failed total**, zero browser skips. Failures were SWB_05_INDEPENDENT at line 54 and SWB_06_REVOCATION at line 64 in that committed test file. A command busy guard could make sign out a no-op, while optimistic UI clearing advertised completion before server revocation. The correction makes logout independent of command busy state, clears private data immediately, confirms revocation before completion, blocks stale response restoration and supports explicit unconfirmed/retry states. The browser suite retains all original assertions and additionally exercises a real scoped logout-audit failure, Arabic failure text, page restoration and successful retry.

The push was canceled after browser failure when its later stage appeared stalled. Its original log confirms identity 58/58 executed successfully; a progress snapshot had lagged. Canceled aggregate runs and partial results remain excluded from acceptance. All prior canceled cce83d/3af7908/2f03202/302b727 runs, Linux private-report ownership correction and original failure logs are preserved. No canceled result is silently converted to a pass.

Forward migrations 0031–0033 repair the separately reproduced post-audit revocation race and enforce bundled migration-ledger integrity. Already-applied SQL bytes are unchanged. No critical repair is considered finally validated merely because it is implemented; the complete hosted rerun remains mandatory.

## Limits and review gate

Synthetic procedural images and scripted ranking demonstrate workflow software only. No real model or external image dataset was acquired. Neural recognition demonstration results and independently measured missing-child identification accuracy are absent. Operational recognition, public biometric search, identity confirmation, custody disclosure and child release remain disabled.

Manual native Arabic, screen-reader and long-journal browser usability reviews are unexecuted. History is paginated; load through the current first review before independent completion. The server rejects stale review IDs. Database retrieval measurements do not establish HTTP/browser capacity or model inference throughput. Recovery drills do not certify production erasure.

GitHub currently reports a **public** repository, strict/up-to-date Actions-app-bound `phase1a-required`, administrator enforcement and resolved conversations, with force push/deletion disabled. Required approving reviews: **zero**; no additional branch ruleset applies. This task changed neither visibility nor protection. Earlier private-repository records are historical observations, not current privacy assurance. Private runtime/raw data is excluded from Git, and published artifacts are sanitized. Draft PRs #8 and #9 remain unmerged. Stop after Phase 2D owner review; do not begin Phase 2E.
