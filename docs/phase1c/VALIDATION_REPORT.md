# Phase 1C validation report

**Assessment: Phase 1C technical validation passed; submitted for owner review in [draft PR #4](https://github.com/wmostafagmail/FindOurChild/pull/4). Phase 1C is not owner-accepted or production-approved. Stop here; Phase 2 has not begun and requires explicit approval.**

Phase 1B was accepted only after PR #3 merged to exact main `9fcb6ef52057a9b46826c8ad7e03e8cb13276431` and required hosted run [40144238603](https://github.com/wmostafagmail/FindOurChild/actions/runs/40144238603) passed on that main commit. [Acceptance](../phase1b/ACCEPTANCE.md) preserves the independently verified main artifact and branch-protection observation.

## Delivered behavior and boundaries

On `codex/phase-1c-reporting-case-management`, missing/found reports retain uncertain information as attributed, unverified claims. Contact-code verification grants restricted access to the reporter's own submission; it never establishes guardianship or grants NGO access. Private drafts, supplements, safe relay, contact revocation and logout are implemented. Intake remains restricted to synthetic contacts/data.

Multiple photographs and supporting image documents enter private encrypted/versioned quarantine. The actual pinned ClamAV service scans input, Pillow strips metadata into a safe review derivative, and the leased background worker checks current authority before publication. Original files are excluded from reporter previews and the normal media gateway. Tampering, invalid files, scanner failure, stale leases, revoked access and incomplete verification fail closed. Quarantine/orphan cleanup acknowledges actual version erasure before success.

Authorized NGO staff can review scoped cases, moderate or hold suspicious claims, add immutable notes, assign cases and record evidence-backed assertions under role/case/purpose restrictions and revision checks. Case updates, audit and outbox records commit together. Arabic/English interfaces include RTL, uncertainty labels, keyboard/language focus, responsive layout and automated accessibility checks. Found-child custody details remain encrypted and outside ordinary case/reporter projections. Confidential concerns enter a separate restricted inbox.

No production facial recognition, automated identity decision, public child search, custody disclosure or child-release capability is implemented. Existing disabled-capability safeguards remain mandatory. Earlier research/specifications and applied migrations 0001–0006 are preserved; 15 additive migrations bring the total to 21.

## Exact validation evidence

Implementation source: `c23f414c7bd52823cb8ae7534a20c3d4e4a7f40b`. Required [PR run 40168908791](https://github.com/wmostafagmail/FindOurChild/actions/runs/40168908791) and [push run 40168906338](https://github.com/wmostafagmail/FindOurChild/actions/runs/40168906338) completed successfully; every job step succeeded. [CI evidence](hosted-ci-verification.json) records the exact head and all step conclusions. A later evidence-only handoff commit must also pass hosted CI; its link is recorded in the draft PR after verification.

The downloaded artifact `12589803879` has SHA-256 `91cb6c26d85cfdb73855fe46484404f58187ec002dff289cec8cdddef9a83b15`. Its 53 payload checksums, all 126 execution files against committed Git blobs, complete result inventories, migration hashes, PNG structures and minimized traces were independently verified. The execution-source digest is `1c15c86da0fe7972c0358b91c074c9d42f3851bf7ba914449cdd57724b59f3b7`. The PR checkout is synthetic merge `a199366549de9f7a5f0962e337b6beb31977d172`; its executed source exactly matches the committed head. [Verification proof](hosted-artifact-verification.json), [artifact metadata](hosted-artifact-metadata.json) and [versioned sanitized results](../../artifacts/phase1c-sanitized/results.json) permit independent review after the hosted artifact expires.

| Suite | Executed / passed | Result |
|---|---:|---|
| Preserved baseline unit/API/database/security/integration | 158 / 158 | Passed |
| Preserved identity/cryptography/boundary/real Keycloak HTTP | 58 / 58 | Passed |
| Reporting/API/real PostgreSQL/storage/scanner/worker regression | 109 / 109 | Passed |
| Actual scanner service outage | 1 / 1 | Passed; unsafe publication denied |
| Actual TLS Next BFF/API/Keycloak/PostgreSQL/media/worker integration | 6 / 6 | Passed |
| **Total Python tests** | **332 / 332** | **Zero mandatory skips** |
| Official TesterArmy Chromium | 56 / 56 | Passed |
| Official TesterArmy Firefox | 56 / 56 | Passed |
| Official TesterArmy WebKit | 56 / 56 | Passed |
| **Total official browser executions** | **168 / 168** | **Zero failed, skipped, interrupted, flaky or retried cases** |
| Checksum-verified migrations and restore drill | 21 / 21 | Passed; 41 app relations FORCE RLS and private identity/reporting metadata RLS restored |
| Structural/configuration and historical evidence | 175 checks | Passed |
| Ruff, TypeScript and production build | Required checks | Passed |
| Known-vulnerability dependency audits | Python and npm | Passed; zero known vulnerabilities reported |
| Combined Python API/migration line coverage | 902 / 965 statements | **93.47%**; 75% gate passed |

Python counts include explicitly scoped unit/boundary tests. The 58-case identity suite comprises 32 cryptographic/unit cases, 14 boundary/filesystem cases and 12 actual IdP/HTTP cases. Reporting case tests that substitute authentication are API/SQL boundary tests against real non-owner PostgreSQL, not proof of real MFA. The independently mandatory real identity, six reporting HTTP and 168 browser executions use actual running services. Browser testing does not replace database, penetration or ML evaluation.

Browser coverage is seven logical titles across 24 configured targets: three engines × two browser locales (`ar-EG`, `en-GB`) × four widths (320, 360, 390, 1280). The principal runner is official `e2e` **0.21.3**, web engine `@e2e-dev/web` **0.15.3**, with its locked Playwright core **1.64.1**; no ordinary Playwright-only tests count toward acceptance. Deterministic assertions validate draft restoration/removal, missing/found intake, code exchange, immutable/literal supplements, prototype-name rendering, two ready photographs, safe relay, logout, NGO review/notes, tenant/authorization denials, ar/en axe checks, focus, RTL and 200% text reflow. No model/provider or AI filter is configured. Telemetry is disabled and all data are synthetic. Native macOS TLS browsers were not rerun after the user's hosted-only instruction; no certificate trust was added.

[Traceability](TEST_TRACEABILITY.md) maps every implemented API operation to exact executable selectors, with worker, database, security and safeguarding crosswalks. The master registry preserves the immutable 151-feature/630-test Phase 0 baseline and accepted Phase 1A–1B records. It now has **178 features / 972 logical cases: 346 passed and 626 future cases pending**. The 119 new Phase 1C logical cases are passed only after current-source hosted artifact verification. Logical mappings are distinct from executions.

## Corrections and retained failures

| Finding | Correction and evidence |
|---|---|
| Prototype-named claim fields/values could resolve inherited label-object properties and crash a view | Own-property lookups; literal/unverified API regression and both reporter browser journeys across all targets |
| TesterArmy interprets plain selection strings as option labels | Select by explicit `{value: registry}`; retained all engines, locales and widths |
| Previous case mutation could clear a newly typed note | Disable reason input while busy and assert the preceding command cleared it before entering the next note |
| Root fixture reader without Linux DAC capabilities could not read API UID-10001 mode-0600 delivery files | Read using the existing unprivileged API user; preserve dropped capabilities and file permissions. [Actual API-owned-file diagnostic](operator-fixture-diagnostic.json) reproduced root denial and owner success |
| Shared BFF socket peer pooled distinct reporters into one rate bucket | Signed, canonical, expiring anonymous scopes plus peer admission control; retain existing per-command, contact and receipt limits. New regression denies forged/expired/alias tokens and forwarded-IP spoofing, while preserving independent valid reporter-session access |
| Earlier storage/scanner/provisioning faults | Official multi-arch Debian scanner, non-root storage startup, bounded allocation/readiness, scoped IAM config hashing/reload, fixed SQL search paths and typed contracts; actual media/cleanup/restore regression passed |

[Run 40150941664](hosted-attempts/40150941664.json) is preserved as failed: 113/168 browser passes, 55 failures and six HTTP fixture-setup failures. [Run 40167531882](hosted-attempts/40167531882.json) is preserved as failed: all 24 NGO journeys passed, while 48 reporter journeys and six HTTP setups failed the delivery-owner fixture. Both archives' hashes and payload checksums were verified. Private original logs and ZIP locations are recorded in those summaries; raw diagnostics are not published. Superseded canceled runs do not count as success. The temporary approval-review usage-limit failure cleared before final validation. No failure was converted to a skip or hidden by retries.

## Reproduction and independent checks

Use the exact runtimes/locks and commands in [environment instructions](ENVIRONMENT.md) and [dependency manifest](LOCKED_DEPENDENCIES.md). Executed validation commands were:

```sh
uv sync --locked
npm ci --ignore-scripts
.venv/bin/ruff check services/api scripts tests
.venv/bin/python -m scripts.check_foundation
.venv/bin/python -m scripts.dev init
.venv/bin/python -m scripts.dev db
.venv/bin/python -m scripts.dev api
.venv/bin/python -m scripts.dev test
.venv/bin/python -m scripts.reporting_validate
.venv/bin/python -m scripts.recovery
.venv/bin/python -m scripts.audit
npm run typecheck
npm run build
./node_modules/.bin/e2e-web install chromium firefox webkit --with-deps
# Ephemeral Ubuntu TLS trust/startup: exact steps in .github/workflows/phase1a.yml
.venv/bin/python -m scripts.dev browser
.venv/bin/python -m scripts.identity_test
.venv/bin/python -m scripts.reporting_http_test
.venv/bin/python -m scripts.coverage_finish
.venv/bin/python -m scripts.artifacts
python3 tools/update_phase1c_matrix.py
```

`reporting_validate` stops the real worker for deterministic component tests, stops the actual scanner for the outage test, and restores both services in `finally` blocks. No Docker socket is mounted into the application or tests. Local execution used a byte-equivalent temporary directory because macOS Documents I/O stalled; root/temporary source bytes were compared and fingerprinted. A temporary Git index avoided a macOS `index.lock` write timeout without changing history. Local 268-test/restore evidence remains [separately scoped](local-regression-evidence.json).

For an independently downloaded GitHub ZIP and its single artifact metadata object:

```sh
python3 tools/verify_phase1c_evidence.py ARTIFACT_METADATA_JSON ARCHIVE_ZIP c23f414c7bd52823cb8ae7534a20c3d4e4a7f40b --no-copy
```

This verifier imports no application validation helper. The committed checksum manifest also permits review of each sanitized file without network access. [Source inventory](SOURCE_INVENTORY.md) lists changed source, configuration, tests, tools and evidence.

## Protection, artifact privacy and remaining release gates

Main protection was actually rechecked; [the observed API response](main-protection.observed.json) requires `phase1a-required` from GitHub Actions app 15368, an up-to-date branch and resolved conversations, enforces administrators, and disallows force pushes/deletion. **Independent review is not enforced: zero approving reviews are required; code-owner and last-push approval requirements are disabled.** No settings were changed. PR #4 remains draft and must not be merged by this task.

Published artifacts contain reviewed test IDs/statuses, source/checksum manifests, migration/coverage results, 168 input-free action/status traces, and 48 input-free foundation screenshots with ancillary PNG metadata removed. Reporter/staff DOM, raw errors/logs, photos, receipts, verification codes, tokens and contact-bearing screenshots are excluded. No real child information or external testing model was used. No unresolved critical finding remains from this implementation/validation; this is not an independent security certification.

Production release still requires NGO/legal/safeguarding/data-protection approvals; production IdP, KMS, hosting, edge abuse controls and signature-update operations; external messaging integration; independent penetration testing, manual accessibility/Arabic review and load/recovery acceptance; operational WORM audit export, retention/legal-hold and whole-case/backup erasure. Confidential inbox/custody review is an operator/legal workflow, not a general staff lookup. Evidence documents are image-only; PDF/Office/SVG imports are rejected. The UI applies capture-year metadata to a batch; API metadata can be set per upload. Journal/upload quotas are explicit. Synthetic backup/restore and orphan erasure do not certify operational erasure. Future matching, federation and child handover tests remain pending and fail-closed capabilities stay disabled.
