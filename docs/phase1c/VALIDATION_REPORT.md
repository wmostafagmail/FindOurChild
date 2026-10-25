# Phase 1C validation report — hosted validation pending

Phase 1B is accepted: PR #3 merged into main `9fcb6ef52057a9b46826c8ad7e03e8cb13276431`; required hosted run [40144238603](https://github.com/wmostafagmail/FindOurChild/actions/runs/40144238603) passed on that exact main commit. The downloaded acceptance archive and all 53 payload hashes were verified. See [Phase 1B acceptance](../phase1b/ACCEPTANCE.md).

Phase 1C is implemented on `codex/phase-1c-reporting-case-management`. [Draft PR #4](https://github.com/wmostafagmail/FindOurChild/pull/4) contains implementation commit `afc97a71d35287940c63f507c7cd61d3e1cfabad`. A subsequent claim-rendering security fix and its additional regression are currently local; the draft does not yet contain that fix. Phase 1C is not accepted or fully validated. Phase 2 has not begun.

## Delivered scope

Missing/found reports retain uncertain information as attributed, unverified claims. Reporter access uses scoped receipts, contact-code verification, secure cookies and CSRF protection; it does not establish guardianship. Private drafts, supplements, neutral relay, multiple photographs, private encrypted/versioned quarantine, actual ClamAV scanning, metadata-stripped review derivatives, worker leases/retries/fencing, NGO moderation, case revisions, assignments, notes and evidence assertions are implemented. Arabic/English interfaces include RTL and deterministic accessibility/reflow assertions. Actual PostgreSQL functions, non-owner runtime roles, FORCE RLS and same-transaction audit/outbox boundaries protect these operations. Original migrations 0001–0006 and approved research are preserved; 15 additive reporting migrations bring the total to 21.

## Current validation

The corrected execution-source digest is `df4590562d75150e703fd03f4bca47843519961bc0b36854797fcb1eb2d534b8`. Detailed local evidence is in [local validation](local-validation.json). New traceability remains pending until the entire current-source hosted artifact passes and is independently verified.

| Required lane | Inventory | Current-source result |
|---|---:|---|
| Baseline unit/API/PostgreSQL/RLS/security/integration | 158 | Passed locally; no skips |
| Reporting/API/real PostgreSQL/storage/scanner/worker regression | 108 | Passed locally; no skips |
| Actual scanner service outage | 1 | Passed locally; no skips |
| Preserved identity/real Keycloak HTTP regression | 58 | Pending hosted validation |
| Actual reporting TLS/BFF/API/worker integration | 6 | Pending hosted validation |
| Official TesterArmy/e2e browser regression | 168 | Pending hosted validation; 56 each Chromium, Firefox and WebKit |
| Structural/configuration and historical evidence checks | 175 checks | Passed locally |
| Ruff, TypeScript and production build | Required | Passed locally |
| Migration/restore/RLS drill and dependency audit | Required | Previous source passed; current-source hosted evidence pending |

The required Python total is **331**. Browser coverage is seven logical titles across 24 targets: three engines × two browser locales × four widths. The principal runner is pinned `e2e` 0.21.3 with `@e2e-dev/web` 0.15.3 and its pinned Playwright engine. There are no ordinary Playwright-only acceptance tests. Browser assertions execute against the actual application/backend and isolated synthetic database. API tests that substitute an identity boundary are explicitly unit/boundary tests; the independent real MFA, HTTP, browser and database lanes remain mandatory.

The security review found that prototype-named supplementary claim fields/values could resolve inherited label-object properties and crash reporter or staff rendering. Label lookups now require own properties. The new API regression verifies literal, unverified claim storage; both missing/found browser journeys include prototype-key/value rendering checks across all configured targets. Only the local regression has executed on this fix so far.

## Hosted evidence and blockers

Implementation commit `afc97a7` started [PR run 40150941664](https://github.com/wmostafagmail/FindOurChild/actions/runs/40150941664) and [push run 40150913837](https://github.com/wmostafagmail/FindOurChild/actions/runs/40150913837). Last observed, provisioning, migrations, baseline/reporting/outage/recovery/audit/build/browser installation/TLS setup succeeded and browser regression was running. Their final conclusions and sanitized artifacts have not been verified. Even a successful result on that commit cannot validate the subsequent security fix.

A GitHub status command was not executed because automatic approval review hit a usage limit and could not complete. This was a review-service failure, not an unsafe-action finding. Hosted status verification, pushing the correction, downloading/checking its artifacts and verifying the final committed revision remain outstanding. Local certificate trust has not been changed; the user's hosted-only TLS validation instruction remains in force.

Main protection was actually observed and saved in [protection evidence](main-protection.observed.json): required `phase1a-required` check (GitHub Actions app 15368), strict/up-to-date checks, administrator enforcement, resolved conversations, no force push/deletion. **Independent approval is not enforced: required approving review count is zero**; code-owner and last-push approval requirements are disabled. These settings have not been changed. A fresh observation remains pending with final hosted verification.

## Evidence handling and limitations

Published artifacts allow only reviewed IDs/statuses, hashes, minimized traces, coverage counts and input-free foundation screenshots. Raw reporter/staff DOM, assertion values, photos, receipts, verification codes, tokens and contact-bearing screenshots remain private. The partial local evidence does not masquerade as a successful complete CI gate. Mandatory skipped, pending, missing or failed tests cannot count as passed. Historical diagnostic failures remain distinct from later runs.

This is synthetic engineering only. External messaging, production KMS/IdP/hosting/signature-update operations, legal/retention/NGO approvals, independent penetration testing, manual accessibility/load acceptance and whole-case/backup erasure remain separate release requirements. Image evidence documents are supported; PDF/Office/SVG imports are rejected. The UI applies capture-year metadata to a selected batch; API metadata can be set per upload. Confidential operational review, custody/disclosure/release and production biometric identification remain unavailable. No production facial recognition or automated identity decision is implemented.

[Architecture](ARCHITECTURE.md), [reproduction](ENVIRONMENT.md), [locked dependencies](LOCKED_DEPENDENCIES.md), [source inventory](SOURCE_INVENTORY.md) and [traceability](TEST_TRACEABILITY.md) accompany this report. Completion requires committing/pushing the correction and evidence, a passing full hosted run on the final source, independent sanitized artifact verification, an updated draft PR and a clean committed working tree. Stop after Phase 1C review; no Phase 2 work is authorized.
