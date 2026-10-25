# Phase 1B validation report

> Current status (2026-10-25): Phase 1B is accepted after PR #3 merged and required hosted CI passed on exact main `9fcb6ef`. See [acceptance](ACCEPTANCE.md). Phase 1C implementation is under validation on `codex/phase-1c-reporting-case-management`. No Phase 2 authorization is inferred. Earlier status descriptions below are historical.

**Assessment: Phase 1B technical validation passed; ready for owner review in [draft PR #3](https://github.com/wmostafagmail/FindOurChild/pull/3). Stop before Phase 1C.** No production or operational safeguarding approval is implied.

Phase 1A is accepted after PR #1 merged into main at `683180e298d1dc0a461aa152007999f79ee70c71` and required hosted CI passed on that exact commit. [Acceptance](../phase1a/ACCEPTANCE.md) and [independently verified main evidence](../phase1a/main-merge-validation.json) preserve the 151 Python/72 browser results.

## Implemented boundary

The dedicated branch `codex/phase-1b-identity-security` implements the Next BFF and bilingual staff session page, Keycloak authorization code/S256 PKCE with mandatory password+OTP, strict JWT validation and live introspection, encrypted server-held tokens, hashed expiring/revocable sessions, Secure cookies, exact-origin/CSRF checks, live organizational membership and case authorization, bounded membership administration with scoped idempotency, and append-only hash-chained audit metadata with per-organization sequences. No browser bearer-token storage exists. The runtime cannot modify validation reports.

There are 42 machine-readable API operations: the 35 original contracts plus seven identity operations. All 32 original reporting/media/matching/safeguarding domain operations remain disabled with 503. Six immutable migrations apply and replay with checksums; all 41 application tables and the two identity metadata tables force RLS. Runtime stays non-owner/NOBYPASSRLS with fixed security-definer entry points. No Phase 1C implementation or real child information was introduced.

## Exact execution evidence

Validated implementation commit: `f2eb943485c4d2a9b6bbdf587212d2583d97e65b`. Hosted [required run 40105948297](https://github.com/wmostafagmail/FindOurChild/actions/runs/40105948297), job `120907547192`, completed successfully with every step successful. The PR checkout was `d501b5486d3f26e748d049f6a9294a5729b72831`; every one of its 85 execution-relevant source hashes matches the committed implementation.

Execution source digest: `42ce28bce1ca47065f5f27487ed3101cae09ac384973f245b327008e55b9b768`. Evidence/report-only commits preserve this digest. See [job steps](hosted-job-steps.json), [run metadata](hosted-evidence.json), [artifact verification](hosted-artifact-verification.json), and the versioned [sanitized results](../../artifacts/phase1b-sanitized/results.json).

| Required suite/check | Exact result |
|---|---|
| Foundation/unit/API/database/security/integration regression | 158 passed: original 151 retained, seven identity database tests added |
| Identity tests | 58 passed: real IdP/BFF/API and container flows, in-process API negatives, and explicitly scoped cryptographic unit doubles |
| Python total | **216 passed; zero mandatory skips** |
| Official TesterArmy/e2e browser suite | **96 passed: Chromium 32, Firefox 32, WebKit 32** |
| Browser configuration | All 24 engine/locale/width targets retained; four logical titles each; zero retries/skips/model calls |
| Browser assertions | Real TLS application/backend/private database; actual MFA, tenant denial, CSRF denial, logout, ar/en accessibility/layout plus full foundation regression |
| Contracts/configuration | Closed OpenAPI validates; immutable Phase 0 research/configuration checks pass |
| Migrations/RLS/recovery | All six migration checksums, replay and synthetic backup/restore pass; tenant, grant, role, context, command/session ACL and rollback negatives pass |
| Python line coverage | **298/311 statements, 95.82%**; API/migration Python scope only; unchanged 75% minimum enforced after combining API-process and test coverage |
| Dependency audit | npm 0 known vulnerabilities; Python 0 known vulnerabilities |
| Sanitized evidence | 54 files, all 53 payload checksums verified; 48 metadata-stripped foundation PNGs; identity screenshots/DOM/cookies/raw traces excluded |

Browser acceptance uses official **e2e 0.21.3**, **web engine 0.15.3**, **Playwright 1.64.1**, deterministic assertions, real services and an isolated database. Ordinary Playwright-only functional acceptance tests: **0**. Unit doubles are unit evidence only; they do not substitute for IdP, database or browser execution. No pending, skipped, failed or unexecuted workflow is represented as passed. Future reporting/safeguarding/ML cases remain pending in the [master matrix](../TEST_MATRIX.md) and [identity traceability](TEST_TRACEABILITY.md).

Artifact `12565235547` archive SHA-256: `e9f3fa00813acaa2146ed1d1a1b131d4bcc4991348dda407eb99374412aba103`. Its versioned checksums, source manifest, minimized traces, coverage and log remain reviewable after hosted retention expires. Optional telemetry is disabled; no external testing model is configured.

## Corrections and historical failures

[Failure history](failed-hosted-run.json) preserves failed runs rather than relabeling them. The original local HTTP browser attempt had 87 passes/9 failures. Hosted Firefox initially rejected the test certificate/issuer; a separate constrained CA/server leaf and Playwright's documented custom-policy selector resolved all 32 failures. Python strict TLS additionally required standard subject/authority key identifiers. Real HTTP testing then caught a BFF omission of `Idempotency-Key`; forwarding was repaired while strict API enforcement remained. Audit sequence allocation was scoped per organization to remove cross-tenant activity inference. New database and full hosted regressions verify these changes.

Raw original logs are preserved under ignored, private `artifacts/raw/phase1b-hosted/` with checksums. Historical failed private GitHub logs contained now-expired synthetic loopback session values in assertion representations; no real child data was present. Current Python diagnostics are captured privately and hosted output is restricted to safe counts. Published artifacts use reviewed-ID/status allowlists and strip screenshot metadata.

The owner approved temporary macOS certificate trust, but OS authorization was canceled and the owner selected hosted validation only. The exact leftover certificate was removed from the login keychain and absence verified. No local certificate trust remains, and local TLS browser acceptance is not claimed. Disposable hosted runners use constrained test CA/NSS trust and the documented Firefox policy setting; certificate verification and Secure-cookie requirements remain enabled.

## Review and operational limits

Main protection was read from GitHub: `phase1a-required` from GitHub Actions app 15368, strict up-to-date checks and administrator enforcement; conversations must resolve; force pushes/deletion blocked. **Independent review is not required: 0 approvals, code-owner and latest-push approval off.** [Observed settings](main-protection.observed.json) are actual API evidence; this branch does not change them. The existing required job now includes all identity and regression gates. Draft PR #3 remains for owner review.

This is a synthetic engineering environment. Keycloak development mode/embedded storage, generated local secrets and loopback TLS are fixtures. Production IdP HA/database/TLS, key custody/rotation, approved organizational/sensitive-role/case-grant bootstrap, ledger retention and independently administered write-once audit export/signing remain operational release requirements. Hash chaining is not immunity from database administrators. Local logout revokes the application session; it does not claim global invalidation of a separately stolen bearer token. Every protected request still checks IdP validity and live DB permissions; no refresh token is retained. Synthetic restore proves schema/data/RLS recovery, not operational erasure, tombstone replay or key-vault disaster recovery. Independent penetration/production load/ML evaluations are not replaced by browser tests.

Phase 1B is submitted for review. Phase 1C remains unauthorized and has not begun. Existing research, legal, safeguarding, privacy and model-release decisions are preserved.
