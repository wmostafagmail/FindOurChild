# Security and child safeguarding test catalogue

Phase 0 planned executable catalogue. Every case is **pending**, with no application execution evidence. Exact planned case IDs/files/selectors, positive/negative/security/edge scenarios and fixtures are in [TEST_MATRIX](TEST_MATRIX.md) and its [machine-readable registry](testing/test-matrix.json).

## Mandatory safeguarding controls

Each SAF row has four planned Python security cases `TC_SAF_XX_P/N/S/E` plus the browser companion `TC_SAF_XX_BROWSER` and API/database/worker companion `TC_SAF_XX_STATE` recorded in the matrix. Browser checks use TesterArmy/e2e against actual services and the isolated database. Authoritative state checks are independently executed with non-owner roles and restricted read-only observers. Browser-only visibility cannot prove the security property.

Each executable target has an explicit required_from_phase. SAF-04/07/08/09 additionally have `TC_SAF_XX_DISABLED_P1` guard cases: before their positive workflow exists, direct API/worker/lifecycle bypass must fail closed without sensitive effects. Future full positive cases remain pending, not skipped-and-passed. Thus Phase 1 enforces all critical protection categories without pretending later matching/reunion functionality is implemented.

| Feature | Required attack/positive fixtures | Deterministic browser/API and state oracle | Fail-safe result / criticality |
|---|---|---|---|
| SAF-01 Fraudulent guardian | Verified contact with forged relationship, unrelated parent, abusive actual guardian, disputed authority | No counterpart/shelter fields in DTO/DOM/network; no approved disclosure/plan transition; qualified reviewer can hold | Verification unavailable/contradictory → hold; no contact-triggered release. Critical |
| SAF-02 Found-child location | Guess case/media URLs, search/analytics/cursors/exports, owner of old missing report | Restricted custody absent from response, accessible tree, cache/title, logs and notifications; inaccessible existence/count response neutral | No location/existence hints to claimant. Critical |
| SAF-03 Image access | Other org/case, original vs derivative, direct bucket key, expired/revoked grants | API/storage deny; no body bytes/range cache leak; sanitized permitted derivative strips EXIF/embedded GPS | Missing grant/scan/KMS verification → no image serve. Critical |
| SAF-04 Biometric search | Reporter/public/arbitrary-vector request, uncleared model or worker scope | No public endpoint/vector output; internal retrieval SQL uses current tenant/case/model space and active lawful basis | Missing scope/license/purpose → no retrieval, no claimant alert. Critical |
| SAF-05 Cross-org leakage | Same readable names/IDs, wrong-org JWT/input, pooled connection, federation off/opt-out | API plus direct SQL show zero unauthorized rows; no media/vectors/counts/broker details; stale broker edge unusable | Missing bilateral scope → deny; no global fallback. Critical |
| SAF-06 Expiry/revocation | Receipt/code/session/MFA/membership/grant/purpose/approval expires at use | Reauthorize at media/disclosure/worker effect; no queued send/release after revoke; pooled session context cleared | Uncertain current verification → deny/hold. Critical |
| SAF-07 Wrong match/rejection | Deliberately strong wrong synthetic lead, no-mate, incomplete metadata | Reviewer rejects with rationale; lead history preserved; case not confirmed; no notification to claimant | Model score alone has no confirming authority. Critical |
| SAF-08 Two-person approval | Same principal two roles, requester/self-approval, shared identity, suspended signer | API and DB reject same actor; two distinct authorized current signers succeed only on same evidence/scope | Missing independent signer or recent MFA → hold. Critical |
| SAF-09 Release bypass | Direct transition/handover, admin/worker attempt, stale evidence, revoked authority, outage | No handover/disclosure row or outbox effect on bypass; no lifecycle leap; witnessed valid flow separate | Any incomplete sensitive gate → no child release or identifying disclosure. Critical |
| SAF-10 Deletion/index cleanup | All original/derivative versions, multiple embedding spaces, stale workers/backup, scoped hold | Revoke/tombstone first; negative image/vector search, purge acknowledgments and restored deletion ledger; no reinsert | Incomplete purge remains pending and inaccessible; no false completed status. Critical |
| SAF-11 Notification leakage | Lock-screen preview, duplicate/reordered event, revoked recipient, signed URL/PII/vector canaries | Inspect actual adapter-to-local-sink payload and logs; neutral task reference only; check authorization at send time | Cannot verify recipient/template → no send; retry/task remains restricted. Critical |

For every denial, assert no unauthorized mutation, no outbox/message, no object read/export, and appropriate minimized audit outcome, as relevant. Check direct API calls as well as UI controls. Error handling must preserve essential child care and safe intake where possible without relaxing disclosure/release protections.

## Original threat coverage preserved

All original T01–T19 map to four planned `SEC-Txx` cases in the matrix: IDOR/RLS and pooled tenant leakage; claimant fraud; insider enumeration/exports; session/MFA/CSRF; hostile uploads/scanner outage; EXIF; bearer-link/cache leakage; malicious model/embedding exposure; false leads; approval/deletion races; notification abuse; audit tamper; keys/backups/erasure; federation inference; stored XSS; SSRF; flooding/storage quotas; dependency supply chain; aggregate differencing.

A signed-in org administrator has no automatic sensitive-case access. Broker, scanner/inference, notification, migration, backup and audit roles each require negative privilege tests. All tenant-owned tables use actual FORCE RLS/non-owner roles; global model manifests and broker agreement/edge tables have their distinct reviewed policy instead of pretending they carry an organization column.

No scanner, custody-authority, audit, model-license or KMS outage can turn into a permissive fallback. Simulate dependency failure at deterministic race barriers and require the last safe state, durable audit/backlog where possible and a restricted staff task.

## Test methods and boundaries

- API/DB: parameterized role×organization×case×purpose×expiry matrices; scoped response schema allowlists; SQL/FK/transaction rollback tests under real roles; no superuser oracle mistaken for application behavior.
- Browser: actual services, direct route attempts, malicious text, mixed-direction labels, private accessible-tree/cache/URL canaries and deterministic response/state checks.
- Worker: crash-before/after-commit, duplicate event delivery, lease recovery, revoke/delete mid-run, source/model revision changes and unauthorized effect denial.
- Media/model: malformed headers, MIME polyglots, decompression/resource bounds, EXIF/thumbnail inspection, tampered weights and incompatible spaces. Use generated benign artifacts and approved test samples in a sandbox.
- Tooling: both telemetry flags enforced; no remote model/browser/artifact reporter; network-denial tests catch off-origin navigation, feedback/update/provider traffic; no raw trace/log upload; verify transformation-resistant canary detection.
- Penetration testing: independent authenticated/unauthenticated assessments before pilot and material boundary changes. Automated scanners and e2e runs do not replace it.
- ML safety: separate lawful open-set/longitudinal/subgroup evaluation and reviewer-anchoring study; synthetic lead fixtures establish workflow behavior only, not recognition accuracy.

## Evidence and escalation

Record test ID/target, real service/build/lock/schema/fixture identity, role/scope, assertion/outcome, side-effect observations, sanitized artifact hashes and current verdict. No real child data in public/CI/debug reports or external testing models. Critical failure blocks required-results, phase exit and release. Keep the capability disabled, preserve safe diagnostic evidence, correct the cause and rerun the full affected regression plus independent review. Missing/blocked/skipped/flaky evidence never counts as passing.

This catalogue is a design requirement. Result parser, sanitizer, fixtures, CI jobs and executable application tests remain to be implemented in their authorized phases.
