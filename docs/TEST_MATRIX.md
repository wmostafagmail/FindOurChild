# Find Our Child — test matrix

> Phase 2D: [traceability](phase2d/TEST_TRACEABILITY.md), [required inventory](phase2d/required-tests.json), [reverse test index](phase2d/test-to-feature.json), [validation report](phase2d/VALIDATION_REPORT.md). Required inventory: **738 Python / 360 official TesterArmy executions / 33 migrations**. Hosted validation of the final corrections is pending. Global registry: **210 features / 1296 cases; 572 passed, 724 pending**. New Phase 2D cases are not passed until exact-source hosted evidence is verified.

> Phase 2A extension: [research traceability](phase2a/TEST_TRACEABILITY.md). All 178 prior features and 972 cases are preserved exactly; 7 research groups append 124 logical cases: 118 passed after independent hosted verification, six real qualifications pending. Current registry: **185 features / 1096 cases; 464 passed, 632 pending**. Real model clearance and recognition qualification remain pending.

> Phase 1C: [current traceability and exact execution inventory](phase1c/TEST_TRACEABILITY.md). Phase 1B is accepted; all 119 new Phase 1C logical cases passed after independent current-source hosted artifact verification. Current registry: **178 features / 972 cases; 346 passed, 626 future cases pending**. Earlier counts below are historical snapshots. The immutable Phase 0 151/630 baseline is preserved.

> Phase 1B extension: [executable traceability](phase1b/TEST_TRACEABILITY.md). IDN-01–IDN-05 append exact identity/API/database/browser selectors to `docs/testing/test-matrix.json`; final hosted evidence passed on implementation `f2eb943` (216 Python and 96 browser executions), with [verified artifacts](phase1b/hosted-artifact-verification.json). Prior passing rows retain their historical Phase 1A evidence. Future reporting/safeguarding/ML tests remain pending.

Current traceability: **166 features, 787 logical test cases**. Statuses: passed=161, pending=626.

The immutable starting point is 151 features / 630 planned cases at commit `40231be73ab9a5eb577ccf5308c86f6b7282976b`. Four disabled-feature guards now have executed evidence; operational baseline scenarios remain pending. Foundation additions include idempotency storage, health contracts, result gates, and restore validation. Browser cases expand to 24 targets each; logical-case totals must not be confused with execution counts.

Phase 1A local required-results gate: **passed**. Hosted CI, App-bound main protection and actual failing-check merge rejection are verified; ready for owner review. A passed foundation guard does not validate future authentication, reporting, approval, media or biometric workflows. The original whole-Phase-1 regression obligation remains unchanged.

Machine-readable source: [test-matrix.json](testing/test-matrix.json). Original baseline: [test-matrix-phase0.json](testing/test-matrix-phase0.json). Evidence: [sanitized results](../artifacts/sanitized/results.json). Required Phase 1A inventory: [required-tests.json](phase1a/required-tests.json).

## FR-01 — Separate missing/found forms in Arabic RTL and English LTR; switch preserves entered values

Validation: **pending**. Suite: browser. Fixtures: FX-BASE, FX-UNCERTAIN, FX-A11Y.

Positive: Switch locale mid-form and submit each registry flow

Negative: Invalid locale or script payload is escaped

Security/authorization: Reporter sees no staff fields during locale switch

Edge cases: Arabic digits, long labels, interrupted connection and draft recovery

Expected: Correct registry, preserved original values, RTL/LTR semantics, one neutral receipt

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FR_01_P | positive | pending | `tests/browser/fr_01.e2e.ts` / `TC_FR_01_P` | pending |
| TC_FR_01_N | negative | pending | `tests/browser/fr_01.e2e.ts` / `TC_FR_01_N` | pending |
| TC_FR_01_S | security_authorization | pending | `tests/browser/fr_01.e2e.ts` / `TC_FR_01_S` | pending |
| TC_FR_01_E | edge | pending | `tests/browser/fr_01.e2e.ts` / `TC_FR_01_E` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FR-02 — Submit with uncertain/unknown child attributes and without a photo; staff receive a triage task

Validation: **pending**. Suite: browser. Fixtures: FX-UNCERTAIN.

Positive: Submit unknown name/age and no photo

Negative: Invalid ordered interval rejected without inventing values

Security/authorization: Unverified source cannot mark claims verified

Edge cases: Unknown vs zero age, estimated capture dates, individual finder

Expected: Claims retain uncertainty and a restricted triage task is created

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FR_02_P | positive | pending | `tests/browser/fr_02.e2e.ts` / `TC_FR_02_P` | pending |
| TC_FR_02_N | negative | pending | `tests/browser/fr_02.e2e.ts` / `TC_FR_02_N` | pending |
| TC_FR_02_S | security_authorization | pending | `tests/browser/fr_02.e2e.ts` / `TC_FR_02_S` | pending |
| TC_FR_02_E | edge | pending | `tests/browser/fr_02.e2e.ts` / `TC_FR_02_E` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FR-03 — Store original and submitted claims immutably by revision; verified facts cite evidence and verifier

Validation: **pending**. Suite: browser. Fixtures: FX-BASE, FX-UNCERTAIN.

Positive: Add evidence-backed verified assertion preserving original claim

Negative: Missing verifier/evidence cannot produce verified fact

Security/authorization: Unassigned user cannot change assertion provenance

Edge cases: Concurrent contradictory revisions and disputed evidence

Expected: Immutable claim history plus independently attributed verification

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FR_03_P | positive | pending | `tests/browser/fr_03.e2e.ts` / `TC_FR_03_P` | pending |
| TC_FR_03_N | negative | pending | `tests/browser/fr_03.e2e.ts` / `TC_FR_03_N` | pending |
| TC_FR_03_S | security_authorization | pending | `tests/browser/fr_03.e2e.ts` / `TC_FR_03_S` | pending |
| TC_FR_03_E | edge | pending | `tests/browser/fr_03.e2e.ts` / `TC_FR_03_E` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FR-04 — Reporter receipt authorizes only own-submission updates after verification, never staff data

Validation: **pending**. Suite: browser. Fixtures: FX-BASE, FX-IDP.

Positive: Verified reporter adds own supplement and views redacted receipt

Negative: Guess or replay receipt/code fails without revealing existence

Security/authorization: Own-report capability cannot read staff notes/counterpart case/custody

Edge cases: Revocation/expiry during supplement and safe recovery

Expected: Only own submitted facts accessible, no found-child disclosure

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FR_04_P | positive | pending | `tests/browser/fr_04.e2e.ts` / `TC_FR_04_P` | pending |
| TC_FR_04_N | negative | pending | `tests/browser/fr_04.e2e.ts` / `TC_FR_04_N` | pending |
| TC_FR_04_S | security_authorization | pending | `tests/browser/fr_04.e2e.ts` / `TC_FR_04_S` | pending |
| TC_FR_04_E | edge | pending | `tests/browser/fr_04.e2e.ts` / `TC_FR_04_E` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FR-05 — Multiple historical images retain capture-age uncertainty and explicit subject selection

Validation: **pending**. Suite: browser. Fixtures: FX-MEDIA, FX-UNCERTAIN.

Positive: Select correct subject among multiple photo regions and record capture interval

Negative: No-face/ambiguous subject remains held

Security/authorization: Unauthorized user cannot select another case photo

Edge cases: Historical photos, low quality and multiple children

Expected: Approved subject selection and original photo provenance; no silent largest-face choice

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FR_05_P | positive | pending | `tests/browser/fr_05.e2e.ts` / `TC_FR_05_P` | pending |
| TC_FR_05_N | negative | pending | `tests/browser/fr_05.e2e.ts` / `TC_FR_05_N` | pending |
| TC_FR_05_S | security_authorization | pending | `tests/browser/fr_05.e2e.ts` / `TC_FR_05_S` | pending |
| TC_FR_05_E | edge | pending | `tests/browser/fr_05.e2e.ts` / `TC_FR_05_E` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FR-06 — Moderation, assignment, case grants and every lifecycle transition are audited

Validation: **pending**. Suite: browser. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Moderate, assign and transition with valid purpose/revision

Negative: Illegal lifecycle jump and stale revision rejected

Security/authorization: Org admin without case grant cannot assign sensitive content to self

Edge cases: Audit sink outage and concurrent assignment/revocation

Expected: Authorized transition, assignment, audit and outbox commit atomically

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FR_06_P | positive | pending | `tests/browser/fr_06.e2e.ts` / `TC_FR_06_P` | pending |
| TC_FR_06_N | negative | pending | `tests/browser/fr_06.e2e.ts` / `TC_FR_06_N` | pending |
| TC_FR_06_S | security_authorization | pending | `tests/browser/fr_06.e2e.ts` / `TC_FR_06_S` | pending |
| TC_FR_06_E | edge | pending | `tests/browser/fr_06.e2e.ts` / `TC_FR_06_E` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FR-07 — Duplicate cases can be linked without destructive merging or loss of provenance

Validation: **pending**. Suite: browser. Fixtures: FX-BASE, FX-UNCERTAIN.

Positive: Confirm/reverse duplicate link with both case grants

Negative: Wrong pair or unreviewed merge request rejected

Security/authorization: Cross-org link cannot disclose records

Edge cases: New evidence after duplicate rejection and repeated requests

Expected: Reversible link with full independent provenance, no destructive merge

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FR_07_P | positive | pending | `tests/browser/fr_07.e2e.ts` / `TC_FR_07_P` | pending |
| TC_FR_07_N | negative | pending | `tests/browser/fr_07.e2e.ts` / `TC_FR_07_N` | pending |
| TC_FR_07_S | security_authorization | pending | `tests/browser/fr_07.e2e.ts` / `TC_FR_07_S` | pending |
| TC_FR_07_E | edge | pending | `tests/browser/fr_07.e2e.ts` / `TC_FR_07_E` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FR-08 — Candidate reviews can be rejected, held or escalated with reason and independent review

Validation: **pending**. Suite: browser. Fixtures: FX-MATCH, FX-APPROVAL.

Positive: Review wrong lead and reject/hold/escalate with reason

Negative: Model score alone cannot resolve case

Security/authorization: Unassigned reviewer cannot access lead or approve own request

Edge cases: New evidence after rejection and competing reviews

Expected: Lead decision retained, no automatic identity/custody action

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FR_08_P | positive | pending | `tests/browser/fr_08.e2e.ts` / `TC_FR_08_P` | pending |
| TC_FR_08_N | negative | pending | `tests/browser/fr_08.e2e.ts` / `TC_FR_08_N` | pending |
| TC_FR_08_S | security_authorization | pending | `tests/browser/fr_08.e2e.ts` / `TC_FR_08_S` | pending |
| TC_FR_08_E | edge | pending | `tests/browser/fr_08.e2e.ts` / `TC_FR_08_E` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FR-09 — Notifications target authorized staff and carry only a neutral task link

Validation: **pending**. Suite: browser. Fixtures: FX-EVENT, FX-BASE.

Positive: Authorized staff receives neutral task notification once

Negative: Invalid destination or provider error retried/dead-lettered

Security/authorization: Revoked recipient and claimant receive no identifying message

Edge cases: Duplicate event and grant revoked at send boundary

Expected: Neutral payload only, current permission rechecked and delivery audit retained

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FR_09_P | positive | pending | `tests/browser/fr_09.e2e.ts` / `TC_FR_09_P` | pending |
| TC_FR_09_N | negative | pending | `tests/browser/fr_09.e2e.ts` / `TC_FR_09_N` | pending |
| TC_FR_09_S | security_authorization | pending | `tests/browser/fr_09.e2e.ts` / `TC_FR_09_S` | pending |
| TC_FR_09_E | edge | pending | `tests/browser/fr_09.e2e.ts` / `TC_FR_09_E` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FR-10 — Identifying disclosure and safe reunion require separate, scoped approvals and authority evidence

Validation: **pending**. Suite: browser. Fixtures: FX-APPROVAL, FX-FAILURE.

Positive: Distinct safeguarding/authority actors approve scoped disclosure then supervised reunion

Negative: Missing authority, fraud concern or changed evidence holds release

Security/authorization: Requester/self-approval/admin bypass denied

Edge cases: Approval expiry/revocation races and actor with two roles

Expected: No identifying disclosure or custody transfer until every independent gate holds

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FR_10_P | positive | pending | `tests/browser/fr_10.e2e.ts` / `TC_FR_10_P` | pending |
| TC_FR_10_N | negative | pending | `tests/browser/fr_10.e2e.ts` / `TC_FR_10_N` | pending |
| TC_FR_10_S | security_authorization | pending | `tests/browser/fr_10.e2e.ts` / `TC_FR_10_S` | pending |
| TC_FR_10_E | edge | pending | `tests/browser/fr_10.e2e.ts` / `TC_FR_10_E` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FR-11 — Revocation and deletion cancel stale media links, jobs, indexes and queued notifications

Validation: **pending**. Suite: browser. Fixtures: FX-PURGE, FX-EVENT.

Positive: Approve deletion and verify every store/index/queue is purged

Negative: Active legal hold prevents only scoped erasure

Security/authorization: Revoked capability cannot serve image during purge

Edge cases: Delete during embedding insertion and restore from old backup

Expected: Tombstone first, all permitted purge acknowledgments recorded, no resurrection

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FR_11_P | positive | pending | `tests/browser/fr_11.e2e.ts` / `TC_FR_11_P` | pending |
| TC_FR_11_N | negative | pending | `tests/browser/fr_11.e2e.ts` / `TC_FR_11_N` | pending |
| TC_FR_11_S | security_authorization | pending | `tests/browser/fr_11.e2e.ts` / `TC_FR_11_S` | pending |
| TC_FR_11_E | edge | pending | `tests/browser/fr_11.e2e.ts` / `TC_FR_11_E` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FR-12 — No route exposes private child records across tenants without an explicit federation agreement and grant

Validation: **pending**. Suite: browser. Fixtures: FX-BASE, FX-MATCH, FX-APPROVAL.

Positive: Same-org authorized search and approved bilateral federation workflow

Negative: Unilateral/expired federation agreement yields no results

Security/authorization: Other organization sees no names/media/counts/vectors/custody

Edge cases: Opt-out during matching and disclosure expiry

Expected: Explicit scope and bilateral approvals enforced; federation off by default

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FR_12_P | positive | pending | `tests/browser/fr_12.e2e.ts` / `TC_FR_12_P` | pending |
| TC_FR_12_N | negative | pending | `tests/browser/fr_12.e2e.ts` / `TC_FR_12_N` | pending |
| TC_FR_12_S | security_authorization | pending | `tests/browser/fr_12.e2e.ts` / `TC_FR_12_S` | pending |
| TC_FR_12_E | edge | pending | `tests/browser/fr_12.e2e.ts` / `TC_FR_12_E` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FR-13 — Evidence addition, investigation notes, abuse reports and event history retain authorship/version

Validation: **pending**. Suite: browser. Fixtures: FX-BASE, FX-UNCERTAIN.

Positive: Append supplement/note/abuse report and inspect permitted history

Negative: Tampered evidence reference or history edit rejected

Security/authorization: Abuse report hidden from implicated user; audit reader sees minimized data

Edge cases: Conflicting notes, unverified evidence and pagination

Expected: Authorship/revisions retained; privileged notes never in reporter DTO

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FR_13_P | positive | pending | `tests/browser/fr_13.e2e.ts` / `TC_FR_13_P` | pending |
| TC_FR_13_N | negative | pending | `tests/browser/fr_13.e2e.ts` / `TC_FR_13_N` | pending |
| TC_FR_13_S | security_authorization | pending | `tests/browser/fr_13.e2e.ts` / `TC_FR_13_S` | pending |
| TC_FR_13_E | edge | pending | `tests/browser/fr_13.e2e.ts` / `TC_FR_13_E` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FR-14 — Screen-reader flow, keyboard use and narrow-screen RTL are verified before pilot

Validation: **pending**. Suite: browser. Fixtures: FX-A11Y.

Positive: Complete workflows using keyboard and screen reader in both languages

Negative: Hidden error or overflowing action fails acceptance

Security/authorization: Disabled controls do not replace backend authorization

Edge cases: All target widths, mixed bidi text, focus restoration, zoom/reduced motion

Expected: Accessible labels/order/status/errors and responsive layout verified

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FR_14_P | positive | pending | `tests/browser/fr_14.e2e.ts` / `TC_FR_14_P` | pending |
| TC_FR_14_N | negative | pending | `tests/browser/fr_14.e2e.ts` / `TC_FR_14_N` | pending |
| TC_FR_14_S | security_authorization | pending | `tests/browser/fr_14.e2e.ts` / `TC_FR_14_S` | pending |
| TC_FR_14_E | edge | pending | `tests/browser/fr_14.e2e.ts` / `TC_FR_14_E` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-001 — POST /v1/public/reports/missing

Validation: **pending**. Suite: api. Fixtures: FX-BASE, FX-UNCERTAIN.

Positive: Submit a missing report with uncertain data

Negative: Reject invalid interval/oversized payload

Security/authorization: Bound intake challenge, rate limit and idempotency; no search

Edge cases: Retry identical key and changed body

Expected: 202 neutral receipt, attributed missing claims and triage event

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_001_P | positive | pending | `tests/api/test_api_001.py` / `test_tc_api_001_p` | pending |
| TC_API_001_N | negative | pending | `tests/api/test_api_001.py` / `test_tc_api_001_n` | pending |
| TC_API_001_S | security_authorization | pending | `tests/api/test_api_001.py` / `test_tc_api_001_s` | pending |
| TC_API_001_E | edge | pending | `tests/api/test_api_001.py` / `test_tc_api_001_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-002 — POST /v1/public/reports/found

Validation: **pending**. Suite: api. Fixtures: FX-BASE, FX-UNCERTAIN.

Positive: Submit individual/organization found report safely

Negative: Reject malformed welfare/discovery inputs

Security/authorization: No shelter or identity disclosed to claimant

Edge cases: Unknown name, no photo and finder without organization

Expected: 202 found intake receipt; restricted custody follow-up

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_002_P | positive | pending | `tests/api/test_api_002.py` / `test_tc_api_002_p` | pending |
| TC_API_002_N | negative | pending | `tests/api/test_api_002.py` / `test_tc_api_002_n` | pending |
| TC_API_002_S | security_authorization | pending | `tests/api/test_api_002.py` / `test_tc_api_002_s` | pending |
| TC_API_002_E | edge | pending | `tests/api/test_api_002.py` / `test_tc_api_002_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-003 — POST /v1/public/access-requests

Validation: **pending**. Suite: api. Fixtures: FX-IDP.

Positive: Request recovery through verified safe channel

Negative: Malformed contact handled without existence leak

Security/authorization: Known and unknown contacts return indistinguishable neutral 202

Edge cases: Flood/shared IP and expired code

Expected: No case existence revealed; attempts bounded

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_003_P | positive | pending | `tests/api/test_api_003.py` / `test_tc_api_003_p` | pending |
| TC_API_003_N | negative | pending | `tests/api/test_api_003.py` / `test_tc_api_003_n` | pending |
| TC_API_003_S | security_authorization | pending | `tests/api/test_api_003.py` / `test_tc_api_003_s` | pending |
| TC_API_003_E | edge | pending | `tests/api/test_api_003.py` / `test_tc_api_003_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-004 — POST /v1/public/access-exchanges

Validation: **pending**. Suite: api. Fixtures: FX-IDP.

Positive: Exchange valid one-time code for own submission session

Negative: Invalid/reused code denied

Security/authorization: Cannot bind code to another receipt or privilege

Edge cases: Concurrent redemption and expiry boundary

Expected: Single use, submission-scoped access only

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_004_P | positive | pending | `tests/api/test_api_004.py` / `test_tc_api_004_p` | pending |
| TC_API_004_N | negative | pending | `tests/api/test_api_004.py` / `test_tc_api_004_n` | pending |
| TC_API_004_S | security_authorization | pending | `tests/api/test_api_004.py` / `test_tc_api_004_s` | pending |
| TC_API_004_E | edge | pending | `tests/api/test_api_004.py` / `test_tc_api_004_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-005 — GET /v1/reporter/submission

Validation: **pending**. Suite: api. Fixtures: FX-BASE, FX-IDP.

Positive: Read own submission

Negative: Unknown/deleted receipt denied

Security/authorization: No counterpart, staff notes, exact custody or vectors

Edge cases: Expired/revoked reporter session

Expected: Redacted own claims only

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_005_P | positive | pending | `tests/api/test_api_005.py` / `test_tc_api_005_p` | pending |
| TC_API_005_N | negative | pending | `tests/api/test_api_005.py` / `test_tc_api_005_n` | pending |
| TC_API_005_S | security_authorization | pending | `tests/api/test_api_005.py` / `test_tc_api_005_s` | pending |
| TC_API_005_E | edge | pending | `tests/api/test_api_005.py` / `test_tc_api_005_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-006 — POST /v1/reporter/supplements

Validation: **pending**. Suite: api. Fixtures: FX-UNCERTAIN.

Positive: Append new reported information

Negative: Bad evidence reference denied

Security/authorization: Cannot write verified facts or another case

Edge cases: Duplicate supplement and stale revision

Expected: Attributed immutable supplement; no verified fact overwrite

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_006_P | positive | pending | `tests/api/test_api_006.py` / `test_tc_api_006_p` | pending |
| TC_API_006_N | negative | pending | `tests/api/test_api_006.py` / `test_tc_api_006_n` | pending |
| TC_API_006_S | security_authorization | pending | `tests/api/test_api_006.py` / `test_tc_api_006_s` | pending |
| TC_API_006_E | edge | pending | `tests/api/test_api_006.py` / `test_tc_api_006_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-007 — POST /v1/reporter/contact

Validation: **pending**. Suite: api. Fixtures: FX-BASE, FX-EVENT.

Positive: Send safe NGO relay message

Negative: Malformed/oversized/XSS payload rejected or escaped

Security/authorization: No shelter/staff private contacts returned

Edge cases: Retry/provider outage and safe-channel changes

Expected: 202 neutral relay acknowledgment with no private recipients

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_007_P | positive | pending | `tests/api/test_api_007.py` / `test_tc_api_007_p` | pending |
| TC_API_007_N | negative | pending | `tests/api/test_api_007.py` / `test_tc_api_007_n` | pending |
| TC_API_007_S | security_authorization | pending | `tests/api/test_api_007.py` / `test_tc_api_007_s` | pending |
| TC_API_007_E | edge | pending | `tests/api/test_api_007.py` / `test_tc_api_007_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-008 — POST /v1/public/abuse-reports

Validation: **pending**. Suite: api. Fixtures: FX-BASE.

Positive: Submit safeguarding concern

Negative: Malformed reference gets neutral handling

Security/authorization: Implicated staff/claimant cannot read allegation

Edge cases: Anonymous/incomplete concern and duplicate attempts

Expected: Restricted abuse queue without lookup response

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_008_P | positive | pending | `tests/api/test_api_008.py` / `test_tc_api_008_p` | pending |
| TC_API_008_N | negative | pending | `tests/api/test_api_008.py` / `test_tc_api_008_n` | pending |
| TC_API_008_S | security_authorization | pending | `tests/api/test_api_008.py` / `test_tc_api_008_s` | pending |
| TC_API_008_E | edge | pending | `tests/api/test_api_008.py` / `test_tc_api_008_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-009 — GET /v1/public/safety

Validation: **pending**. Suite: api. Fixtures: FX-A11Y.

Positive: Read approved ar/en safety text

Negative: Unknown locale follows defined fallback

Security/authorization: No case data in public/cacheable response

Edge cases: Stale guidance version and accessibility alternative

Expected: Public approved locale/version text only

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_009_P | positive | pending | `tests/api/test_api_009.py` / `test_tc_api_009_p` | pending |
| TC_API_009_N | negative | pending | `tests/api/test_api_009.py` / `test_tc_api_009_n` | pending |
| TC_API_009_S | security_authorization | pending | `tests/api/test_api_009.py` / `test_tc_api_009_s` | pending |
| TC_API_009_E | edge | pending | `tests/api/test_api_009.py` / `test_tc_api_009_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-010 — POST /v1/reporter/upload-intents

Validation: **pending**. Suite: api. Fixtures: FX-MEDIA.

Positive: Create bounded quarantine upload intent

Negative: Disallowed type/size/quota rejected

Security/authorization: Capability bound to exact case/key and no public ACL

Edge cases: Intent expiry/orphan upload and replay

Expected: Expiring restricted upload permission

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_010_P | positive | pending | `tests/api/test_api_010.py` / `test_tc_api_010_p` | pending |
| TC_API_010_N | negative | pending | `tests/api/test_api_010.py` / `test_tc_api_010_n` | pending |
| TC_API_010_S | security_authorization | pending | `tests/api/test_api_010.py` / `test_tc_api_010_s` | pending |
| TC_API_010_E | edge | pending | `tests/api/test_api_010.py` / `test_tc_api_010_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-011 — POST /v1/reporter/upload-intents/{id}/complete

Validation: **pending**. Suite: api. Fixtures: FX-MEDIA, FX-EVENT.

Positive: Finalize immutable uploaded version/checksum

Negative: Mismatch/missing object denied

Security/authorization: Cannot retarget case, key or mutable object version

Edge cases: Duplicate completion, scan outage and deletion race

Expected: 202 scan job; image not served before acceptance

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_011_P | positive | pending | `tests/api/test_api_011.py` / `test_tc_api_011_p` | pending |
| TC_API_011_N | negative | pending | `tests/api/test_api_011.py` / `test_tc_api_011_n` | pending |
| TC_API_011_S | security_authorization | pending | `tests/api/test_api_011.py` / `test_tc_api_011_s` | pending |
| TC_API_011_E | edge | pending | `tests/api/test_api_011.py` / `test_tc_api_011_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-012 — GET /v1/staff/cases

Validation: **pending**. Suite: api. Fixtures: FX-BASE, FX-DB.

Positive: List granted cases using cursor

Negative: Bad cursor/filter rejected

Security/authorization: No inaccessible counts or cross-org rows

Edge cases: Grant revoke between pages and empty scope

Expected: Only permitted case summaries and pagination

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_012_P | positive | pending | `tests/api/test_api_012.py` / `test_tc_api_012_p` | pending |
| TC_API_012_N | negative | pending | `tests/api/test_api_012.py` / `test_tc_api_012_n` | pending |
| TC_API_012_S | security_authorization | pending | `tests/api/test_api_012.py` / `test_tc_api_012_s` | pending |
| TC_API_012_E | edge | pending | `tests/api/test_api_012.py` / `test_tc_api_012_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-013 — GET /v1/staff/cases/{id}

Validation: **pending**. Suite: api. Fixtures: FX-BASE, FX-DB.

Positive: Read assigned case with ETag

Negative: Missing/deleted case returns neutral inaccessible response

Security/authorization: No grant, wrong org and restricted custody denied

Edge cases: Membership expiry during pooled transaction

Expected: Authorized DTO plus revision; no generic database serialization

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_013_P | positive | pending | `tests/api/test_api_013.py` / `test_tc_api_013_p` | pending |
| TC_API_013_N | negative | pending | `tests/api/test_api_013.py` / `test_tc_api_013_n` | pending |
| TC_API_013_S | security_authorization | pending | `tests/api/test_api_013.py` / `test_tc_api_013_s` | pending |
| TC_API_013_E | edge | pending | `tests/api/test_api_013.py` / `test_tc_api_013_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-014 — POST /v1/staff/cases/{id}/transitions

Validation: **pending**. Suite: api. Fixtures: FX-APPROVAL, FX-DB.

Positive: Perform legal case transition

Negative: Illegal jump/missing evidence rejected

Security/authorization: No automatic score-triggered resolution or admin bypass

Edge cases: If-Match stale and concurrent transition

Expected: Only guarded new state and atomic audit/outbox

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_014_P | positive | pending | `tests/api/test_api_014.py` / `test_tc_api_014_p` | pending |
| TC_API_014_N | negative | pending | `tests/api/test_api_014.py` / `test_tc_api_014_n` | pending |
| TC_API_014_S | security_authorization | pending | `tests/api/test_api_014.py` / `test_tc_api_014_s` | pending |
| TC_API_014_E | edge | pending | `tests/api/test_api_014.py` / `test_tc_api_014_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-015 — POST /v1/staff/cases/{id}/assignments

Validation: **pending**. Suite: api. Fixtures: FX-BASE, FX-IDP.

Positive: Assign case/team and grant appropriately

Negative: Invalid/suspended member rejected

Security/authorization: Supervisor scope and least privilege enforced

Edge cases: Self-assignment privilege escalation and concurrent revocation

Expected: Audited authorized assignment

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_015_P | positive | pending | `tests/api/test_api_015.py` / `test_tc_api_015_p` | pending |
| TC_API_015_N | negative | pending | `tests/api/test_api_015.py` / `test_tc_api_015_n` | pending |
| TC_API_015_S | security_authorization | pending | `tests/api/test_api_015.py` / `test_tc_api_015_s` | pending |
| TC_API_015_E | edge | pending | `tests/api/test_api_015.py` / `test_tc_api_015_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-016 — POST /v1/staff/cases/{id}/assertions

Validation: **pending**. Suite: api. Fixtures: FX-UNCERTAIN.

Positive: Record claimed or evidence-verified assertion

Negative: Missing provenance/invalid interval denied

Security/authorization: Verification requires reviewer and evidence permissions

Edge cases: Conflicting revisions/disputed source

Expected: Immutable assertion; original remains preserved

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_016_P | positive | pending | `tests/api/test_api_016.py` / `test_tc_api_016_p` | pending |
| TC_API_016_N | negative | pending | `tests/api/test_api_016.py` / `test_tc_api_016_n` | pending |
| TC_API_016_S | security_authorization | pending | `tests/api/test_api_016.py` / `test_tc_api_016_s` | pending |
| TC_API_016_E | edge | pending | `tests/api/test_api_016.py` / `test_tc_api_016_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-017 — POST /v1/staff/photos/{id}/subject-selection

Validation: **pending**. Suite: api. Fixtures: FX-MEDIA.

Positive: Approve selected face region

Negative: Unknown region/ambiguous face held

Security/authorization: Only authorized case media reviewer selects

Edge cases: Two children, zero faces, stale detector revision

Expected: Explicit subject and source revision recorded

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_017_P | positive | pending | `tests/api/test_api_017.py` / `test_tc_api_017_p` | pending |
| TC_API_017_N | negative | pending | `tests/api/test_api_017.py` / `test_tc_api_017_n` | pending |
| TC_API_017_S | security_authorization | pending | `tests/api/test_api_017.py` / `test_tc_api_017_s` | pending |
| TC_API_017_E | edge | pending | `tests/api/test_api_017.py` / `test_tc_api_017_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-018 — GET /v1/staff/media/{id}/content

Validation: **pending**. Suite: api. Fixtures: FX-MEDIA, FX-IDP.

Positive: Stream permitted sanitized image

Negative: Unsafe/quarantined/deleted object denied

Security/authorization: Other org/expired/revoked token/original privilege denied

Edge cases: Range/cache request and revoke during streaming

Expected: Authorized content with no-store/no-referrer, no GPS metadata leak

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_018_P | positive | pending | `tests/api/test_api_018.py` / `test_tc_api_018_p` | pending |
| TC_API_018_N | negative | pending | `tests/api/test_api_018.py` / `test_tc_api_018_n` | pending |
| TC_API_018_S | security_authorization | pending | `tests/api/test_api_018.py` / `test_tc_api_018_s` | pending |
| TC_API_018_E | edge | pending | `tests/api/test_api_018.py` / `test_tc_api_018_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-019 — POST /v1/staff/cases/{id}/matching-runs

Validation: **pending**. Suite: api. Fixtures: FX-MATCH.

Positive: Queue matching with approved manifest/purpose

Negative: Uncleared model/missing subject denied

Security/authorization: No public biometric route or cross-org search grant

Edge cases: No photos, incompatible space and deleted revision

Expected: 202 internal scoped job; no raw vectors returned

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_019_P | positive | pending | `tests/api/test_api_019.py` / `test_tc_api_019_p` | pending |
| TC_API_019_N | negative | pending | `tests/api/test_api_019.py` / `test_tc_api_019_n` | pending |
| TC_API_019_S | security_authorization | pending | `tests/api/test_api_019.py` / `test_tc_api_019_s` | pending |
| TC_API_019_E | edge | pending | `tests/api/test_api_019.py` / `test_tc_api_019_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-020 — GET /v1/staff/cases/{id}/leads

Validation: **pending**. Suite: api. Fixtures: FX-MATCH, FX-BASE.

Positive: Read authorized case leads with reasons

Negative: Unknown lead/run denied

Security/authorization: Require both case scopes and federation disclosure policy

Edge cases: Rejected/stale lead and missing metadata

Expected: Permitted candidate DTO and uncertainty; no identity probability

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_020_P | positive | pending | `tests/api/test_api_020.py` / `test_tc_api_020_p` | pending |
| TC_API_020_N | negative | pending | `tests/api/test_api_020.py` / `test_tc_api_020_n` | pending |
| TC_API_020_S | security_authorization | pending | `tests/api/test_api_020.py` / `test_tc_api_020_s` | pending |
| TC_API_020_E | edge | pending | `tests/api/test_api_020.py` / `test_tc_api_020_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-021 — POST /v1/staff/leads/{id}/reviews

Validation: **pending**. Suite: api. Fixtures: FX-MATCH, FX-APPROVAL.

Positive: Hold/reject/escalate lead with evidence

Negative: No rationale/invalid outcome denied

Security/authorization: Assigned independent reviewer scope enforced

Edge cases: Stale review and new evidence after rejection

Expected: Immutable review, no automatic confirmation

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_021_P | positive | pending | `tests/api/test_api_021.py` / `test_tc_api_021_p` | pending |
| TC_API_021_N | negative | pending | `tests/api/test_api_021.py` / `test_tc_api_021_n` | pending |
| TC_API_021_S | security_authorization | pending | `tests/api/test_api_021.py` / `test_tc_api_021_s` | pending |
| TC_API_021_E | edge | pending | `tests/api/test_api_021.py` / `test_tc_api_021_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-022 — POST /v1/staff/cases/{id}/notes

Validation: **pending**. Suite: api. Fixtures: FX-BASE.

Positive: Append investigation note

Negative: Oversized/unsafe text handled

Security/authorization: Reporter/other org cannot read or modify notes

Edge cases: Concurrent versions and malicious Arabic text

Expected: Attributed restricted revision

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_022_P | positive | pending | `tests/api/test_api_022.py` / `test_tc_api_022_p` | pending |
| TC_API_022_N | negative | pending | `tests/api/test_api_022.py` / `test_tc_api_022_n` | pending |
| TC_API_022_S | security_authorization | pending | `tests/api/test_api_022.py` / `test_tc_api_022_s` | pending |
| TC_API_022_E | edge | pending | `tests/api/test_api_022.py` / `test_tc_api_022_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-023 — POST /v1/staff/duplicate-links

Validation: **pending**. Suite: api. Fixtures: FX-BASE.

Positive: Create/confirm reversible duplicate link

Negative: Same-case/invalid pair rejected

Security/authorization: Both grants and confirmation role required

Edge cases: Repeated link/reversal/concurrent update

Expected: Reversible reviewed link with independent reports intact

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_023_P | positive | pending | `tests/api/test_api_023.py` / `test_tc_api_023_p` | pending |
| TC_API_023_N | negative | pending | `tests/api/test_api_023.py` / `test_tc_api_023_n` | pending |
| TC_API_023_S | security_authorization | pending | `tests/api/test_api_023.py` / `test_tc_api_023_s` | pending |
| TC_API_023_E | edge | pending | `tests/api/test_api_023.py` / `test_tc_api_023_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-024 — POST /v1/staff/disclosure-requests

Validation: **pending**. Suite: api. Fixtures: FX-APPROVAL.

Positive: Request recipient/field-scoped disclosure

Negative: Missing purpose/mask/expiry denied

Security/authorization: Request grants no access; recipient identity verified independently

Edge cases: Expired agreement and snapshot changes

Expected: Pending restricted request only

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_024_P | positive | pending | `tests/api/test_api_024.py` / `test_tc_api_024_p` | pending |
| TC_API_024_N | negative | pending | `tests/api/test_api_024.py` / `test_tc_api_024_n` | pending |
| TC_API_024_S | security_authorization | pending | `tests/api/test_api_024.py` / `test_tc_api_024_s` | pending |
| TC_API_024_E | edge | pending | `tests/api/test_api_024.py` / `test_tc_api_024_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-025 — POST /v1/staff/disclosure-requests/{id}/approvals

Validation: **pending**. Suite: api. Fixtures: FX-APPROVAL.

Positive: Independent bilateral disclosure approval

Negative: Missing side/authority/evidence holds disclosure

Security/authorization: Self-approval or same principal in two roles denied

Edge cases: Expiry/revocation/snapshot race

Expected: Expiring field mask only after all required approvals

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_025_P | positive | pending | `tests/api/test_api_025.py` / `test_tc_api_025_p` | pending |
| TC_API_025_N | negative | pending | `tests/api/test_api_025.py` / `test_tc_api_025_n` | pending |
| TC_API_025_S | security_authorization | pending | `tests/api/test_api_025.py` / `test_tc_api_025_s` | pending |
| TC_API_025_E | edge | pending | `tests/api/test_api_025.py` / `test_tc_api_025_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-026 — POST /v1/staff/reunification-plans

Validation: **pending**. Suite: api. Fixtures: FX-APPROVAL.

Positive: Propose safe reunion after identity review

Negative: Unconfirmed identity/fraud concern prevents readiness

Security/authorization: Claimant cannot create or approve own handover

Edge cases: Disputed custody and child objection

Expected: Pending safeguarded plan, not release

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_026_P | positive | pending | `tests/api/test_api_026.py` / `test_tc_api_026_p` | pending |
| TC_API_026_N | negative | pending | `tests/api/test_api_026.py` / `test_tc_api_026_n` | pending |
| TC_API_026_S | security_authorization | pending | `tests/api/test_api_026.py` / `test_tc_api_026_s` | pending |
| TC_API_026_E | edge | pending | `tests/api/test_api_026.py` / `test_tc_api_026_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-027 — POST /v1/staff/reunification-plans/{id}/approvals

Validation: **pending**. Suite: api. Fixtures: FX-APPROVAL, FX-IDP.

Positive: Record distinct safeguarding and authority decisions

Negative: Missing/stale verification blocks

Security/authorization: Two-person identities and recent MFA enforced

Edge cases: Approver disabled or evidence revised after signing

Expected: Scope/snapshot-bound approval only

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_027_P | positive | pending | `tests/api/test_api_027.py` / `test_tc_api_027_p` | pending |
| TC_API_027_N | negative | pending | `tests/api/test_api_027.py` / `test_tc_api_027_n` | pending |
| TC_API_027_S | security_authorization | pending | `tests/api/test_api_027.py` / `test_tc_api_027_s` | pending |
| TC_API_027_E | edge | pending | `tests/api/test_api_027.py` / `test_tc_api_027_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-028 — POST /v1/staff/reunification-plans/{id}/handover

Validation: **pending**. Suite: api. Fixtures: FX-APPROVAL, FX-EVENT.

Positive: Record supervised authorized handover

Negative: Incomplete/expired approvals deny child release

Security/authorization: No admin/worker/claimant bypass or duplicate transfer

Edge cases: Concurrent replay/revocation and witness failure

Expected: Only complete independent gates permit witnessed transition

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_028_P | positive | pending | `tests/api/test_api_028.py` / `test_tc_api_028_p` | pending |
| TC_API_028_N | negative | pending | `tests/api/test_api_028.py` / `test_tc_api_028_n` | pending |
| TC_API_028_S | security_authorization | pending | `tests/api/test_api_028.py` / `test_tc_api_028_s` | pending |
| TC_API_028_E | edge | pending | `tests/api/test_api_028.py` / `test_tc_api_028_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-029 — POST /v1/staff/cases/{id}/deletion-requests

Validation: **pending**. Suite: api. Fixtures: FX-PURGE.

Positive: Request authorized erasure

Negative: Legal hold scoped/reviewed

Security/authorization: Request itself cannot reveal child existence or bypass privacy authority

Edge cases: Purge racing indexing and backups

Expected: Tombstone/revocation then verifiable purge workflow

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_029_P | positive | pending | `tests/api/test_api_029.py` / `test_tc_api_029_p` | pending |
| TC_API_029_N | negative | pending | `tests/api/test_api_029.py` / `test_tc_api_029_n` | pending |
| TC_API_029_S | security_authorization | pending | `tests/api/test_api_029.py` / `test_tc_api_029_s` | pending |
| TC_API_029_E | edge | pending | `tests/api/test_api_029.py` / `test_tc_api_029_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-030 — GET /v1/staff/audit-events

Validation: **pending**. Suite: api. Fixtures: FX-DB.

Positive: Read permitted minimized audit events

Negative: Invalid cursor denied

Security/authorization: Audit mandate does not grant media/custody or cross-org data

Edge cases: Hash-chain break and pagination boundary

Expected: Minimized scoped audit stream, no payload secrets

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_030_P | positive | pending | `tests/api/test_api_030.py` / `test_tc_api_030_p` | pending |
| TC_API_030_N | negative | pending | `tests/api/test_api_030.py` / `test_tc_api_030_n` | pending |
| TC_API_030_S | security_authorization | pending | `tests/api/test_api_030.py` / `test_tc_api_030_s` | pending |
| TC_API_030_E | edge | pending | `tests/api/test_api_030.py` / `test_tc_api_030_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-031 — GET /v1/staff/analytics

Validation: **pending**. Suite: api. Fixtures: FX-BASE.

Positive: Read approved aggregate analytics

Negative: Unsupported drilldown rejected

Security/authorization: Suppress small cells and cross-org differencing

Edge cases: Overlapping queries and zero/small samples

Expected: Nonidentifying approved aggregates only

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_031_P | positive | pending | `tests/api/test_api_031.py` / `test_tc_api_031_p` | pending |
| TC_API_031_N | negative | pending | `tests/api/test_api_031.py` / `test_tc_api_031_n` | pending |
| TC_API_031_S | security_authorization | pending | `tests/api/test_api_031.py` / `test_tc_api_031_s` | pending |
| TC_API_031_E | edge | pending | `tests/api/test_api_031.py` / `test_tc_api_031_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## API-032 — POST /v1/staff/organizations/{id}/memberships

Validation: **pending**. Suite: api. Fixtures: FX-IDP, FX-BASE.

Positive: Manage organization membership with permission

Negative: Invalid role/suspended organization rejected

Security/authorization: No automatic case/custody grant for org admin

Edge cases: Role change/session revoke and last-admin policy

Expected: Audited membership lifecycle with current grant enforcement

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_API_032_P | positive | pending | `tests/api/test_api_032.py` / `test_tc_api_032_p` | pending |
| TC_API_032_N | negative | pending | `tests/api/test_api_032.py` / `test_tc_api_032_n` | pending |
| TC_API_032_S | security_authorization | pending | `tests/api/test_api_032.py` / `test_tc_api_032_s` | pending |
| TC_API_032_E | edge | pending | `tests/api/test_api_032.py` / `test_tc_api_032_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-001 — organizations

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: organizations: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_001_P | positive | pending | `tests/database/test_db_001.py` / `test_tc_db_001_p` | pending |
| TC_DB_001_N | negative | pending | `tests/database/test_db_001.py` / `test_tc_db_001_n` | pending |
| TC_DB_001_S | security_authorization | pending | `tests/database/test_db_001.py` / `test_tc_db_001_s` | pending |
| TC_DB_001_E | edge | pending | `tests/database/test_db_001.py` / `test_tc_db_001_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-002 — staff_principals

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: staff_principals: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_002_P | positive | pending | `tests/database/test_db_002.py` / `test_tc_db_002_p` | pending |
| TC_DB_002_N | negative | pending | `tests/database/test_db_002.py` / `test_tc_db_002_n` | pending |
| TC_DB_002_S | security_authorization | pending | `tests/database/test_db_002.py` / `test_tc_db_002_s` | pending |
| TC_DB_002_E | edge | pending | `tests/database/test_db_002.py` / `test_tc_db_002_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-003 — memberships

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: memberships: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_003_P | positive | pending | `tests/database/test_db_003.py` / `test_tc_db_003_p` | pending |
| TC_DB_003_N | negative | pending | `tests/database/test_db_003.py` / `test_tc_db_003_n` | pending |
| TC_DB_003_S | security_authorization | pending | `tests/database/test_db_003.py` / `test_tc_db_003_s` | pending |
| TC_DB_003_E | edge | pending | `tests/database/test_db_003.py` / `test_tc_db_003_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-004 — cases

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: cases: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_004_P | positive | pending | `tests/database/test_db_004.py` / `test_tc_db_004_p` | pending |
| TC_DB_004_N | negative | pending | `tests/database/test_db_004.py` / `test_tc_db_004_n` | pending |
| TC_DB_004_S | security_authorization | pending | `tests/database/test_db_004.py` / `test_tc_db_004_s` | pending |
| TC_DB_004_E | edge | pending | `tests/database/test_db_004.py` / `test_tc_db_004_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-005 — case_grants

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: case_grants: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_005_P | positive | pending | `tests/database/test_db_005.py` / `test_tc_db_005_p` | pending |
| TC_DB_005_N | negative | pending | `tests/database/test_db_005.py` / `test_tc_db_005_n` | pending |
| TC_DB_005_S | security_authorization | pending | `tests/database/test_db_005.py` / `test_tc_db_005_s` | pending |
| TC_DB_005_E | edge | pending | `tests/database/test_db_005.py` / `test_tc_db_005_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-006 — report_access

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: Explicit restricted-purpose grant permits only needed fields

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: report_access: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_006_P | positive | pending | `tests/database/test_db_006.py` / `test_tc_db_006_p` | pending |
| TC_DB_006_N | negative | pending | `tests/database/test_db_006.py` / `test_tc_db_006_n` | pending |
| TC_DB_006_S | security_authorization | pending | `tests/database/test_db_006.py` / `test_tc_db_006_s` | pending |
| TC_DB_006_E | edge | pending | `tests/database/test_db_006.py` / `test_tc_db_006_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-007 — reporters

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: Explicit restricted-purpose grant permits only needed fields

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: reporters: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_007_P | positive | pending | `tests/database/test_db_007.py` / `test_tc_db_007_p` | pending |
| TC_DB_007_N | negative | pending | `tests/database/test_db_007.py` / `test_tc_db_007_n` | pending |
| TC_DB_007_S | security_authorization | pending | `tests/database/test_db_007.py` / `test_tc_db_007_s` | pending |
| TC_DB_007_E | edge | pending | `tests/database/test_db_007.py` / `test_tc_db_007_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-008 — child_profiles

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: child_profiles: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_008_P | positive | pending | `tests/database/test_db_008.py` / `test_tc_db_008_p` | pending |
| TC_DB_008_N | negative | pending | `tests/database/test_db_008.py` / `test_tc_db_008_n` | pending |
| TC_DB_008_S | security_authorization | pending | `tests/database/test_db_008.py` / `test_tc_db_008_s` | pending |
| TC_DB_008_E | edge | pending | `tests/database/test_db_008.py` / `test_tc_db_008_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-009 — name_variants

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: name_variants: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_009_P | positive | pending | `tests/database/test_db_009.py` / `test_tc_db_009_p` | pending |
| TC_DB_009_N | negative | pending | `tests/database/test_db_009.py` / `test_tc_db_009_n` | pending |
| TC_DB_009_S | security_authorization | pending | `tests/database/test_db_009.py` / `test_tc_db_009_s` | pending |
| TC_DB_009_E | edge | pending | `tests/database/test_db_009.py` / `test_tc_db_009_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-010 — assertions

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Attempt UPDATE/DELETE as application role; preserve immutable history

Expected: assertions: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_010_P | positive | pending | `tests/database/test_db_010.py` / `test_tc_db_010_p` | pending |
| TC_DB_010_N | negative | pending | `tests/database/test_db_010.py` / `test_tc_db_010_n` | pending |
| TC_DB_010_S | security_authorization | pending | `tests/database/test_db_010.py` / `test_tc_db_010_s` | pending |
| TC_DB_010_E | edge | pending | `tests/database/test_db_010.py` / `test_tc_db_010_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-011 — registry_events

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: registry_events: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_011_P | positive | pending | `tests/database/test_db_011.py` / `test_tc_db_011_p` | pending |
| TC_DB_011_N | negative | pending | `tests/database/test_db_011.py` / `test_tc_db_011_n` | pending |
| TC_DB_011_S | security_authorization | pending | `tests/database/test_db_011.py` / `test_tc_db_011_s` | pending |
| TC_DB_011_E | edge | pending | `tests/database/test_db_011.py` / `test_tc_db_011_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-012 — restricted_custody

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: Explicit restricted-purpose grant permits only needed fields

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: restricted_custody: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_012_P | positive | pending | `tests/database/test_db_012.py` / `test_tc_db_012_p` | pending |
| TC_DB_012_N | negative | pending | `tests/database/test_db_012.py` / `test_tc_db_012_n` | pending |
| TC_DB_012_S | security_authorization | pending | `tests/database/test_db_012.py` / `test_tc_db_012_s` | pending |
| TC_DB_012_E | edge | pending | `tests/database/test_db_012.py` / `test_tc_db_012_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-013 — legal_bases

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: legal_bases: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_013_P | positive | pending | `tests/database/test_db_013.py` / `test_tc_db_013_p` | pending |
| TC_DB_013_N | negative | pending | `tests/database/test_db_013.py` / `test_tc_db_013_n` | pending |
| TC_DB_013_S | security_authorization | pending | `tests/database/test_db_013.py` / `test_tc_db_013_s` | pending |
| TC_DB_013_E | edge | pending | `tests/database/test_db_013.py` / `test_tc_db_013_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-014 — evidence_documents

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: evidence_documents: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_014_P | positive | pending | `tests/database/test_db_014.py` / `test_tc_db_014_p` | pending |
| TC_DB_014_N | negative | pending | `tests/database/test_db_014.py` / `test_tc_db_014_n` | pending |
| TC_DB_014_S | security_authorization | pending | `tests/database/test_db_014.py` / `test_tc_db_014_s` | pending |
| TC_DB_014_E | edge | pending | `tests/database/test_db_014.py` / `test_tc_db_014_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-015 — upload_intents

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: upload_intents: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_015_P | positive | pending | `tests/database/test_db_015.py` / `test_tc_db_015_p` | pending |
| TC_DB_015_N | negative | pending | `tests/database/test_db_015.py` / `test_tc_db_015_n` | pending |
| TC_DB_015_S | security_authorization | pending | `tests/database/test_db_015.py` / `test_tc_db_015_s` | pending |
| TC_DB_015_E | edge | pending | `tests/database/test_db_015.py` / `test_tc_db_015_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-016 — photographs

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: photographs: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_016_P | positive | pending | `tests/database/test_db_016.py` / `test_tc_db_016_p` | pending |
| TC_DB_016_N | negative | pending | `tests/database/test_db_016.py` / `test_tc_db_016_n` | pending |
| TC_DB_016_S | security_authorization | pending | `tests/database/test_db_016.py` / `test_tc_db_016_s` | pending |
| TC_DB_016_E | edge | pending | `tests/database/test_db_016.py` / `test_tc_db_016_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-017 — objects

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: objects: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_017_P | positive | pending | `tests/database/test_db_017.py` / `test_tc_db_017_p` | pending |
| TC_DB_017_N | negative | pending | `tests/database/test_db_017.py` / `test_tc_db_017_n` | pending |
| TC_DB_017_S | security_authorization | pending | `tests/database/test_db_017.py` / `test_tc_db_017_s` | pending |
| TC_DB_017_E | edge | pending | `tests/database/test_db_017.py` / `test_tc_db_017_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-018 — photo_derivatives

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: photo_derivatives: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_018_P | positive | pending | `tests/database/test_db_018.py` / `test_tc_db_018_p` | pending |
| TC_DB_018_N | negative | pending | `tests/database/test_db_018.py` / `test_tc_db_018_n` | pending |
| TC_DB_018_S | security_authorization | pending | `tests/database/test_db_018.py` / `test_tc_db_018_s` | pending |
| TC_DB_018_E | edge | pending | `tests/database/test_db_018.py` / `test_tc_db_018_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-019 — face_regions

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: face_regions: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_019_P | positive | pending | `tests/database/test_db_019.py` / `test_tc_db_019_p` | pending |
| TC_DB_019_N | negative | pending | `tests/database/test_db_019.py` / `test_tc_db_019_n` | pending |
| TC_DB_019_S | security_authorization | pending | `tests/database/test_db_019.py` / `test_tc_db_019_s` | pending |
| TC_DB_019_E | edge | pending | `tests/database/test_db_019.py` / `test_tc_db_019_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-020 — model_manifests

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: Authorized signed/versioned control metadata read; administrator performs approved append

Negative: Reject incompatible dimension/manifest mutation and invalid version

Security/authorization: Deny ordinary principal mutation; no embedded child payload in global control metadata

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: model_manifests: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_020_P | positive | pending | `tests/database/test_db_020.py` / `test_tc_db_020_p` | pending |
| TC_DB_020_N | negative | pending | `tests/database/test_db_020.py` / `test_tc_db_020_n` | pending |
| TC_DB_020_S | security_authorization | pending | `tests/database/test_db_020.py` / `test_tc_db_020_s` | pending |
| TC_DB_020_E | edge | pending | `tests/database/test_db_020.py` / `test_tc_db_020_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-021 — embedding_spaces

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: Authorized signed/versioned control metadata read; administrator performs approved append

Negative: Reject incompatible dimension/manifest mutation and invalid version

Security/authorization: Deny ordinary principal mutation; no embedded child payload in global control metadata

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: embedding_spaces: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_021_P | positive | pending | `tests/database/test_db_021.py` / `test_tc_db_021_p` | pending |
| TC_DB_021_N | negative | pending | `tests/database/test_db_021.py` / `test_tc_db_021_n` | pending |
| TC_DB_021_S | security_authorization | pending | `tests/database/test_db_021.py` / `test_tc_db_021_s` | pending |
| TC_DB_021_E | edge | pending | `tests/database/test_db_021.py` / `test_tc_db_021_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-022 — embeddings

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: embeddings: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_022_P | positive | pending | `tests/database/test_db_022.py` / `test_tc_db_022_p` | pending |
| TC_DB_022_N | negative | pending | `tests/database/test_db_022.py` / `test_tc_db_022_n` | pending |
| TC_DB_022_S | security_authorization | pending | `tests/database/test_db_022.py` / `test_tc_db_022_s` | pending |
| TC_DB_022_E | edge | pending | `tests/database/test_db_022.py` / `test_tc_db_022_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-023 — matching_runs

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: matching_runs: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_023_P | positive | pending | `tests/database/test_db_023.py` / `test_tc_db_023_p` | pending |
| TC_DB_023_N | negative | pending | `tests/database/test_db_023.py` / `test_tc_db_023_n` | pending |
| TC_DB_023_S | security_authorization | pending | `tests/database/test_db_023.py` / `test_tc_db_023_s` | pending |
| TC_DB_023_E | edge | pending | `tests/database/test_db_023.py` / `test_tc_db_023_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-024 — candidate_leads

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: candidate_leads: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_024_P | positive | pending | `tests/database/test_db_024.py` / `test_tc_db_024_p` | pending |
| TC_DB_024_N | negative | pending | `tests/database/test_db_024.py` / `test_tc_db_024_n` | pending |
| TC_DB_024_S | security_authorization | pending | `tests/database/test_db_024.py` / `test_tc_db_024_s` | pending |
| TC_DB_024_E | edge | pending | `tests/database/test_db_024.py` / `test_tc_db_024_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-025 — federation_agreements

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: Broker/approval actor performs only agreement-and-purpose-scoped access

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: Tenant roles cannot read broker-only edges; unilateral agreement cannot authorize disclosure

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: federation_agreements: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_025_P | positive | pending | `tests/database/test_db_025.py` / `test_tc_db_025_p` | pending |
| TC_DB_025_N | negative | pending | `tests/database/test_db_025.py` / `test_tc_db_025_n` | pending |
| TC_DB_025_S | security_authorization | pending | `tests/database/test_db_025.py` / `test_tc_db_025_s` | pending |
| TC_DB_025_E | edge | pending | `tests/database/test_db_025.py` / `test_tc_db_025_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-026 — broker_candidate_edges

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: Broker/approval actor performs only agreement-and-purpose-scoped access

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: Tenant roles cannot read broker-only edges; unilateral agreement cannot authorize disclosure

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: broker_candidate_edges: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_026_P | positive | pending | `tests/database/test_db_026.py` / `test_tc_db_026_p` | pending |
| TC_DB_026_N | negative | pending | `tests/database/test_db_026.py` / `test_tc_db_026_n` | pending |
| TC_DB_026_S | security_authorization | pending | `tests/database/test_db_026.py` / `test_tc_db_026_s` | pending |
| TC_DB_026_E | edge | pending | `tests/database/test_db_026.py` / `test_tc_db_026_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-027 — disclosure_grants

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: Broker/approval actor performs only agreement-and-purpose-scoped access

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: Tenant roles cannot read broker-only edges; unilateral agreement cannot authorize disclosure

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: disclosure_grants: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_027_P | positive | pending | `tests/database/test_db_027.py` / `test_tc_db_027_p` | pending |
| TC_DB_027_N | negative | pending | `tests/database/test_db_027.py` / `test_tc_db_027_n` | pending |
| TC_DB_027_S | security_authorization | pending | `tests/database/test_db_027.py` / `test_tc_db_027_s` | pending |
| TC_DB_027_E | edge | pending | `tests/database/test_db_027.py` / `test_tc_db_027_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-028 — investigations / notes

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Attempt UPDATE/DELETE as application role; preserve immutable history

Expected: investigations / notes: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_028_P | positive | pending | `tests/database/test_db_028.py` / `test_tc_db_028_p` | pending |
| TC_DB_028_N | negative | pending | `tests/database/test_db_028.py` / `test_tc_db_028_n` | pending |
| TC_DB_028_S | security_authorization | pending | `tests/database/test_db_028.py` / `test_tc_db_028_s` | pending |
| TC_DB_028_E | edge | pending | `tests/database/test_db_028.py` / `test_tc_db_028_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-029 — duplicate_links

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: duplicate_links: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_029_P | positive | pending | `tests/database/test_db_029.py` / `test_tc_db_029_p` | pending |
| TC_DB_029_N | negative | pending | `tests/database/test_db_029.py` / `test_tc_db_029_n` | pending |
| TC_DB_029_S | security_authorization | pending | `tests/database/test_db_029.py` / `test_tc_db_029_s` | pending |
| TC_DB_029_E | edge | pending | `tests/database/test_db_029.py` / `test_tc_db_029_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-030 — human_reviews

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Attempt UPDATE/DELETE as application role; preserve immutable history

Expected: human_reviews: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_030_P | positive | pending | `tests/database/test_db_030.py` / `test_tc_db_030_p` | pending |
| TC_DB_030_N | negative | pending | `tests/database/test_db_030.py` / `test_tc_db_030_n` | pending |
| TC_DB_030_S | security_authorization | pending | `tests/database/test_db_030.py` / `test_tc_db_030_s` | pending |
| TC_DB_030_E | edge | pending | `tests/database/test_db_030.py` / `test_tc_db_030_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-031 — reunification_plans

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: reunification_plans: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_031_P | positive | pending | `tests/database/test_db_031.py` / `test_tc_db_031_p` | pending |
| TC_DB_031_N | negative | pending | `tests/database/test_db_031.py` / `test_tc_db_031_n` | pending |
| TC_DB_031_S | security_authorization | pending | `tests/database/test_db_031.py` / `test_tc_db_031_s` | pending |
| TC_DB_031_E | edge | pending | `tests/database/test_db_031.py` / `test_tc_db_031_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-032 — approvals

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: Explicit restricted-purpose grant permits only needed fields

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: approvals: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_032_P | positive | pending | `tests/database/test_db_032.py` / `test_tc_db_032_p` | pending |
| TC_DB_032_N | negative | pending | `tests/database/test_db_032.py` / `test_tc_db_032_n` | pending |
| TC_DB_032_S | security_authorization | pending | `tests/database/test_db_032.py` / `test_tc_db_032_s` | pending |
| TC_DB_032_E | edge | pending | `tests/database/test_db_032.py` / `test_tc_db_032_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-033 — handovers

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: Explicit restricted-purpose grant permits only needed fields

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: handovers: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_033_P | positive | pending | `tests/database/test_db_033.py` / `test_tc_db_033_p` | pending |
| TC_DB_033_N | negative | pending | `tests/database/test_db_033.py` / `test_tc_db_033_n` | pending |
| TC_DB_033_S | security_authorization | pending | `tests/database/test_db_033.py` / `test_tc_db_033_s` | pending |
| TC_DB_033_E | edge | pending | `tests/database/test_db_033.py` / `test_tc_db_033_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-034 — jobs / outbox_events

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: jobs / outbox_events: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_034_P | positive | pending | `tests/database/test_db_034.py` / `test_tc_db_034_p` | pending |
| TC_DB_034_N | negative | pending | `tests/database/test_db_034.py` / `test_tc_db_034_n` | pending |
| TC_DB_034_S | security_authorization | pending | `tests/database/test_db_034.py` / `test_tc_db_034_s` | pending |
| TC_DB_034_E | edge | pending | `tests/database/test_db_034.py` / `test_tc_db_034_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-035 — notification_deliveries

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: notification_deliveries: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_035_P | positive | pending | `tests/database/test_db_035.py` / `test_tc_db_035_p` | pending |
| TC_DB_035_N | negative | pending | `tests/database/test_db_035.py` / `test_tc_db_035_n` | pending |
| TC_DB_035_S | security_authorization | pending | `tests/database/test_db_035.py` / `test_tc_db_035_s` | pending |
| TC_DB_035_E | edge | pending | `tests/database/test_db_035.py` / `test_tc_db_035_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-036 — audit_events

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Attempt UPDATE/DELETE as application role; preserve immutable history

Expected: audit_events: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_036_P | positive | pending | `tests/database/test_db_036.py` / `test_tc_db_036_p` | pending |
| TC_DB_036_N | negative | pending | `tests/database/test_db_036.py` / `test_tc_db_036_n` | pending |
| TC_DB_036_S | security_authorization | pending | `tests/database/test_db_036.py` / `test_tc_db_036_s` | pending |
| TC_DB_036_E | edge | pending | `tests/database/test_db_036.py` / `test_tc_db_036_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-037 — deletion_requests / tombstones

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-BASE.

Positive: API/worker non-owner role performs authorized same-org case-scoped operation

Negative: Deny missing tenant/purpose/context, invalid FK or unauthorized table action

Security/authorization: FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant

Edge cases: Revoke/expire grant or legal basis during transaction; connection pool reused for another org

Expected: deletion_requests / tombstones: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DB_037_P | positive | pending | `tests/database/test_db_037.py` / `test_tc_db_037_p` | pending |
| TC_DB_037_N | negative | pending | `tests/database/test_db_037.py` / `test_tc_db_037_n` | pending |
| TC_DB_037_S | security_authorization | pending | `tests/database/test_db_037.py` / `test_tc_db_037_s` | pending |
| TC_DB_037_E | edge | pending | `tests/database/test_db_037.py` / `test_tc_db_037_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## TXN-01 — Tenant pool/context isolation

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-EVENT, FX-PURGE.

Positive: Use transaction-local server-set principal/organization

Negative: Missing context fails closed

Security/authorization: Forged user-supplied organization cannot set DB identity

Edge cases: Reuse pooled connection after rollback and session revoke

Expected: No residual tenant/purpose context or leaked rows

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_TXN_01_P | positive | pending | `tests/database/test_txn_01.py` / `test_tc_txn_01_p` | pending |
| TC_TXN_01_N | negative | pending | `tests/database/test_txn_01.py` / `test_tc_txn_01_n` | pending |
| TC_TXN_01_S | security_authorization | pending | `tests/database/test_txn_01.py` / `test_tc_txn_01_s` | pending |
| TC_TXN_01_E | edge | pending | `tests/database/test_txn_01.py` / `test_tc_txn_01_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## TXN-02 — Composite cross-organization foreign keys

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-EVENT, FX-PURGE.

Positive: Insert same-org case/evidence relation

Negative: Reject other-org parent with guessed ID

Security/authorization: No deferred FK bypass through worker or bulk path

Edge cases: Concurrent parent deletion and reused readable identifiers

Expected: Composite ownership enforced at DB boundary

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_TXN_02_P | positive | pending | `tests/database/test_txn_02.py` / `test_tc_txn_02_p` | pending |
| TC_TXN_02_N | negative | pending | `tests/database/test_txn_02.py` / `test_tc_txn_02_n` | pending |
| TC_TXN_02_S | security_authorization | pending | `tests/database/test_txn_02.py` / `test_tc_txn_02_s` | pending |
| TC_TXN_02_E | edge | pending | `tests/database/test_txn_02.py` / `test_tc_txn_02_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## TXN-03 — Audit/outbox/domain atomic commit

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-EVENT, FX-PURGE.

Positive: Commit authorized mutation with one audit/outbox record

Negative: Inject failure before each commit boundary

Security/authorization: Unprivileged actor cannot suppress audit

Edge cases: Crash before/after commit and retried idempotency key

Expected: All three commit or none; no unlogged side effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_TXN_03_P | positive | pending | `tests/database/test_txn_03.py` / `test_tc_txn_03_p` | pending |
| TC_TXN_03_N | negative | pending | `tests/database/test_txn_03.py` / `test_tc_txn_03_n` | pending |
| TC_TXN_03_S | security_authorization | pending | `tests/database/test_txn_03.py` / `test_tc_txn_03_s` | pending |
| TC_TXN_03_E | edge | pending | `tests/database/test_txn_03.py` / `test_tc_txn_03_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## TXN-04 — Approval/revocation race

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-EVENT, FX-PURGE.

Positive: Approve valid independent plan transaction

Negative: Revoke approval or change snapshot before release

Security/authorization: Same signer in two roles still cannot approve own release

Edge cases: Concurrent handover/revoke at deterministic barrier

Expected: Release denied when any current gate invalid

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_TXN_04_P | positive | pending | `tests/database/test_txn_04.py` / `test_tc_txn_04_p` | pending |
| TC_TXN_04_N | negative | pending | `tests/database/test_txn_04.py` / `test_tc_txn_04_n` | pending |
| TC_TXN_04_S | security_authorization | pending | `tests/database/test_txn_04.py` / `test_tc_txn_04_s` | pending |
| TC_TXN_04_E | edge | pending | `tests/database/test_txn_04.py` / `test_tc_txn_04_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## TXN-05 — Deletion/index race

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-EVENT, FX-PURGE.

Positive: Tombstone then purge all model partitions

Negative: Stale embedding completion cannot resurrect row

Security/authorization: Worker must recheck legal basis and generation

Edge cases: Crash/retry between object deletion and vector write

Expected: No reachable vector/media after deletion; purge audit remains

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_TXN_05_P | positive | pending | `tests/database/test_txn_05.py` / `test_tc_txn_05_p` | pending |
| TC_TXN_05_N | negative | pending | `tests/database/test_txn_05.py` / `test_tc_txn_05_n` | pending |
| TC_TXN_05_S | security_authorization | pending | `tests/database/test_txn_05.py` / `test_tc_txn_05_s` | pending |
| TC_TXN_05_E | edge | pending | `tests/database/test_txn_05.py` / `test_tc_txn_05_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## TXN-06 — Schema install/upgrade/restore

Validation: **pending**. Suite: database. Fixtures: FX-DB, FX-EVENT, FX-PURGE.

Positive: Apply migrations to empty and prior synthetic release

Negative: Fail interrupted/incompatible backfill safely

Security/authorization: Migration role separated from API roles

Edge cases: Large resumable backfill and restore tombstones

Expected: Constraints/RLS preserved and rollback path demonstrated

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_TXN_06_P | positive | pending | `tests/database/test_txn_06.py` / `test_tc_txn_06_p` | pending |
| TC_TXN_06_N | negative | pending | `tests/database/test_txn_06.py` / `test_tc_txn_06_n` | pending |
| TC_TXN_06_S | security_authorization | pending | `tests/database/test_txn_06.py` / `test_tc_txn_06_s` | pending |
| TC_TXN_06_E | edge | pending | `tests/database/test_txn_06.py` / `test_tc_txn_06_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## JOB-001 — report.submitted

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-BASE, FX-FAILURE.

Positive: Create restricted triage/assignment task

Negative: Malformed/unknown version goes to dead-letter review with no sensitive processing

Security/authorization: No child data in event; unverified source cannot self-approve

Edge cases: Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis

Expected: Create restricted triage/assignment task exactly within current permissions; retry is idempotent and audit/dedup retained

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_JOB_001_P | positive | pending | `tests/workers/test_job_001.py` / `test_tc_job_001_p` | pending |
| TC_JOB_001_N | negative | pending | `tests/workers/test_job_001.py` / `test_tc_job_001_n` | pending |
| TC_JOB_001_S | security_authorization | pending | `tests/workers/test_job_001.py` / `test_tc_job_001_s` | pending |
| TC_JOB_001_E | edge | pending | `tests/workers/test_job_001.py` / `test_tc_job_001_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## JOB-002 — media.uploaded

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-BASE, FX-FAILURE.

Positive: Lease malware/validation job against immutable object version

Negative: Malformed/unknown version goes to dead-letter review with no sensitive processing

Security/authorization: No serve/embed until valid scan; outage keeps quarantine

Edge cases: Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis

Expected: Lease malware/validation job against immutable object version exactly within current permissions; retry is idempotent and audit/dedup retained

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_JOB_002_P | positive | pending | `tests/workers/test_job_002.py` / `test_tc_job_002_p` | pending |
| TC_JOB_002_N | negative | pending | `tests/workers/test_job_002.py` / `test_tc_job_002_n` | pending |
| TC_JOB_002_S | security_authorization | pending | `tests/workers/test_job_002.py` / `test_tc_job_002_s` | pending |
| TC_JOB_002_E | edge | pending | `tests/workers/test_job_002.py` / `test_tc_job_002_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## JOB-003 — media.ready

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-BASE, FX-FAILURE.

Positive: Schedule approved-subject processing or staff selection

Negative: Malformed/unknown version goes to dead-letter review with no sensitive processing

Security/authorization: No automatic subject choice for multiple faces

Edge cases: Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis

Expected: Schedule approved-subject processing or staff selection exactly within current permissions; retry is idempotent and audit/dedup retained

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_JOB_003_P | positive | pending | `tests/workers/test_job_003.py` / `test_tc_job_003_p` | pending |
| TC_JOB_003_N | negative | pending | `tests/workers/test_job_003.py` / `test_tc_job_003_n` | pending |
| TC_JOB_003_S | security_authorization | pending | `tests/workers/test_job_003.py` / `test_tc_job_003_s` | pending |
| TC_JOB_003_E | edge | pending | `tests/workers/test_job_003.py` / `test_tc_job_003_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## JOB-004 — media.quarantined

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-BASE, FX-FAILURE.

Positive: Hold processing and create authorized moderation task

Negative: Malformed/unknown version goes to dead-letter review with no sensitive processing

Security/authorization: No image URL/raw bytes in notification

Edge cases: Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis

Expected: Hold processing and create authorized moderation task exactly within current permissions; retry is idempotent and audit/dedup retained

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_JOB_004_P | positive | pending | `tests/workers/test_job_004.py` / `test_tc_job_004_p` | pending |
| TC_JOB_004_N | negative | pending | `tests/workers/test_job_004.py` / `test_tc_job_004_n` | pending |
| TC_JOB_004_S | security_authorization | pending | `tests/workers/test_job_004.py` / `test_tc_job_004_s` | pending |
| TC_JOB_004_E | edge | pending | `tests/workers/test_job_004.py` / `test_tc_job_004_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## JOB-005 — subject.selected

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-BASE, FX-FAILURE.

Positive: Queue selected-region alignment/quality/embedding

Negative: Malformed/unknown version goes to dead-letter review with no sensitive processing

Security/authorization: Deny unapproved or stale source revision

Edge cases: Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis

Expected: Queue selected-region alignment/quality/embedding exactly within current permissions; retry is idempotent and audit/dedup retained

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_JOB_005_P | positive | pending | `tests/workers/test_job_005.py` / `test_tc_job_005_p` | pending |
| TC_JOB_005_N | negative | pending | `tests/workers/test_job_005.py` / `test_tc_job_005_n` | pending |
| TC_JOB_005_S | security_authorization | pending | `tests/workers/test_job_005.py` / `test_tc_job_005_s` | pending |
| TC_JOB_005_E | edge | pending | `tests/workers/test_job_005.py` / `test_tc_job_005_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## JOB-006 — embedding.ready

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-BASE, FX-FAILURE.

Positive: Insert compatible-space vector and schedule retrieval

Negative: Malformed/unknown version goes to dead-letter review with no sensitive processing

Security/authorization: Never compare equal-sized incompatible model vectors

Edge cases: Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis

Expected: Insert compatible-space vector and schedule retrieval exactly within current permissions; retry is idempotent and audit/dedup retained

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_JOB_006_P | positive | pending | `tests/workers/test_job_006.py` / `test_tc_job_006_p` | pending |
| TC_JOB_006_N | negative | pending | `tests/workers/test_job_006.py` / `test_tc_job_006_n` | pending |
| TC_JOB_006_S | security_authorization | pending | `tests/workers/test_job_006.py` / `test_tc_job_006_s` | pending |
| TC_JOB_006_E | edge | pending | `tests/workers/test_job_006.py` / `test_tc_job_006_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## JOB-007 — matching.requested

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-BASE, FX-FAILURE.

Positive: Run scoped face and independent metadata retrieval

Negative: Malformed/unknown version goes to dead-letter review with no sensitive processing

Security/authorization: Reject unlicensed model, absent purpose or unauthorized federation

Edge cases: Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis

Expected: Run scoped face and independent metadata retrieval exactly within current permissions; retry is idempotent and audit/dedup retained

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_JOB_007_P | positive | pending | `tests/workers/test_job_007.py` / `test_tc_job_007_p` | pending |
| TC_JOB_007_N | negative | pending | `tests/workers/test_job_007.py` / `test_tc_job_007_n` | pending |
| TC_JOB_007_S | security_authorization | pending | `tests/workers/test_job_007.py` / `test_tc_job_007_s` | pending |
| TC_JOB_007_E | edge | pending | `tests/workers/test_job_007.py` / `test_tc_job_007_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## JOB-008 — matching.completed

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-BASE, FX-FAILURE.

Positive: Persist lead run and neutral review task

Negative: Malformed/unknown version goes to dead-letter review with no sensitive processing

Security/authorization: No auto identity resolution or claimant message

Edge cases: Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis

Expected: Persist lead run and neutral review task exactly within current permissions; retry is idempotent and audit/dedup retained

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_JOB_008_P | positive | pending | `tests/workers/test_job_008.py` / `test_tc_job_008_p` | pending |
| TC_JOB_008_N | negative | pending | `tests/workers/test_job_008.py` / `test_tc_job_008_n` | pending |
| TC_JOB_008_S | security_authorization | pending | `tests/workers/test_job_008.py` / `test_tc_job_008_s` | pending |
| TC_JOB_008_E | edge | pending | `tests/workers/test_job_008.py` / `test_tc_job_008_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## JOB-009 — lead.reviewed

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-BASE, FX-FAILURE.

Positive: Persist rejection/hold/escalation effect and follow-up

Negative: Malformed/unknown version goes to dead-letter review with no sensitive processing

Security/authorization: No automatic child release

Edge cases: Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis

Expected: Persist rejection/hold/escalation effect and follow-up exactly within current permissions; retry is idempotent and audit/dedup retained

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_JOB_009_P | positive | pending | `tests/workers/test_job_009.py` / `test_tc_job_009_p` | pending |
| TC_JOB_009_N | negative | pending | `tests/workers/test_job_009.py` / `test_tc_job_009_n` | pending |
| TC_JOB_009_S | security_authorization | pending | `tests/workers/test_job_009.py` / `test_tc_job_009_s` | pending |
| TC_JOB_009_E | edge | pending | `tests/workers/test_job_009.py` / `test_tc_job_009_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## JOB-010 — disclosure.approved

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-BASE, FX-FAILURE.

Positive: Prepare expiring field-scoped permitted package

Negative: Malformed/unknown version goes to dead-letter review with no sensitive processing

Security/authorization: Recheck both sides, signer and snapshot before release

Edge cases: Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis

Expected: Prepare expiring field-scoped permitted package exactly within current permissions; retry is idempotent and audit/dedup retained

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_JOB_010_P | positive | pending | `tests/workers/test_job_010.py` / `test_tc_job_010_p` | pending |
| TC_JOB_010_N | negative | pending | `tests/workers/test_job_010.py` / `test_tc_job_010_n` | pending |
| TC_JOB_010_S | security_authorization | pending | `tests/workers/test_job_010.py` / `test_tc_job_010_s` | pending |
| TC_JOB_010_E | edge | pending | `tests/workers/test_job_010.py` / `test_tc_job_010_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## JOB-011 — approval.revoked

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-BASE, FX-FAILURE.

Positive: Invalidate dependent package/plan before next use

Negative: Malformed/unknown version goes to dead-letter review with no sensitive processing

Security/authorization: No stale send/release from queued worker

Edge cases: Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis

Expected: Invalidate dependent package/plan before next use exactly within current permissions; retry is idempotent and audit/dedup retained

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_JOB_011_P | positive | pending | `tests/workers/test_job_011.py` / `test_tc_job_011_p` | pending |
| TC_JOB_011_N | negative | pending | `tests/workers/test_job_011.py` / `test_tc_job_011_n` | pending |
| TC_JOB_011_S | security_authorization | pending | `tests/workers/test_job_011.py` / `test_tc_job_011_s` | pending |
| TC_JOB_011_E | edge | pending | `tests/workers/test_job_011.py` / `test_tc_job_011_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## JOB-012 — reunification.recorded

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-BASE, FX-FAILURE.

Positive: Create supervised welfare follow-up and history

Negative: Malformed/unknown version goes to dead-letter review with no sensitive processing

Security/authorization: No public reunion story or exact location exposure

Edge cases: Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis

Expected: Create supervised welfare follow-up and history exactly within current permissions; retry is idempotent and audit/dedup retained

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_JOB_012_P | positive | pending | `tests/workers/test_job_012.py` / `test_tc_job_012_p` | pending |
| TC_JOB_012_N | negative | pending | `tests/workers/test_job_012.py` / `test_tc_job_012_n` | pending |
| TC_JOB_012_S | security_authorization | pending | `tests/workers/test_job_012.py` / `test_tc_job_012_s` | pending |
| TC_JOB_012_E | edge | pending | `tests/workers/test_job_012.py` / `test_tc_job_012_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## JOB-013 — deletion.requested

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-BASE, FX-FAILURE.

Positive: Tombstone/revoke, cancel jobs, purge media/vectors/provider artifacts

Negative: Malformed/unknown version goes to dead-letter review with no sensitive processing

Security/authorization: Scoped legal hold; no reinsertion from stale jobs

Edge cases: Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis

Expected: Tombstone/revoke, cancel jobs, purge media/vectors/provider artifacts exactly within current permissions; retry is idempotent and audit/dedup retained

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_JOB_013_P | positive | pending | `tests/workers/test_job_013.py` / `test_tc_job_013_p` | pending |
| TC_JOB_013_N | negative | pending | `tests/workers/test_job_013.py` / `test_tc_job_013_n` | pending |
| TC_JOB_013_S | security_authorization | pending | `tests/workers/test_job_013.py` / `test_tc_job_013_s` | pending |
| TC_JOB_013_E | edge | pending | `tests/workers/test_job_013.py` / `test_tc_job_013_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## JOB-014 — deletion.completed

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-BASE, FX-FAILURE.

Positive: Verify negative retrieval and purge acknowledgments

Negative: Malformed/unknown version goes to dead-letter review with no sensitive processing

Security/authorization: Retain only legally approved minimized audit

Edge cases: Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis

Expected: Verify negative retrieval and purge acknowledgments exactly within current permissions; retry is idempotent and audit/dedup retained

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_JOB_014_P | positive | pending | `tests/workers/test_job_014.py` / `test_tc_job_014_p` | pending |
| TC_JOB_014_N | negative | pending | `tests/workers/test_job_014.py` / `test_tc_job_014_n` | pending |
| TC_JOB_014_S | security_authorization | pending | `tests/workers/test_job_014.py` / `test_tc_job_014_s` | pending |
| TC_JOB_014_E | edge | pending | `tests/workers/test_job_014.py` / `test_tc_job_014_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## JOB-015 — notification.requested

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-BASE, FX-FAILURE.

Positive: Deduplicate neutral alert to currently permitted recipient

Negative: Malformed/unknown version goes to dead-letter review with no sensitive processing

Security/authorization: No claimant identity/location/image/vector leak

Edge cases: Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis

Expected: Deduplicate neutral alert to currently permitted recipient exactly within current permissions; retry is idempotent and audit/dedup retained

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_JOB_015_P | positive | pending | `tests/workers/test_job_015.py` / `test_tc_job_015_p` | pending |
| TC_JOB_015_N | negative | pending | `tests/workers/test_job_015.py` / `test_tc_job_015_n` | pending |
| TC_JOB_015_S | security_authorization | pending | `tests/workers/test_job_015.py` / `test_tc_job_015_s` | pending |
| TC_JOB_015_E | edge | pending | `tests/workers/test_job_015.py` / `test_tc_job_015_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## WORK-01 — media_sanitize

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-MEDIA, FX-PURGE, FX-FAILURE.

Positive: Produce orientation-correct sanitized derivative and encrypted preserved original

Negative: Reject unsafe decode and fail closed on scanner/metadata tool outage

Security/authorization: Separate original/EXIF access permission

Edge cases: GPS embedded thumbnail and image-size bomb

Expected: Safe derivative only; originals remain restricted

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_WORK_01_P | positive | pending | `tests/workers/test_work_01.py` / `test_tc_work_01_p` | pending |
| TC_WORK_01_N | negative | pending | `tests/workers/test_work_01.py` / `test_tc_work_01_n` | pending |
| TC_WORK_01_S | security_authorization | pending | `tests/workers/test_work_01.py` / `test_tc_work_01_s` | pending |
| TC_WORK_01_E | edge | pending | `tests/workers/test_work_01.py` / `test_tc_work_01_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## WORK-02 — lease_retry_dead_letter

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-MEDIA, FX-PURGE, FX-FAILURE.

Positive: Recover orphaned lease and retry transient error

Negative: No blind retry of permanent auth/model-license failure

Security/authorization: Recheck permission and deletion generation on every effect

Edge cases: Clock skew, duplicate lease and exhaustion

Expected: No double external effect; actionable dead-letter

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_WORK_02_P | positive | pending | `tests/workers/test_work_02.py` / `test_tc_work_02_p` | pending |
| TC_WORK_02_N | negative | pending | `tests/workers/test_work_02.py` / `test_tc_work_02_n` | pending |
| TC_WORK_02_S | security_authorization | pending | `tests/workers/test_work_02.py` / `test_tc_work_02_s` | pending |
| TC_WORK_02_E | edge | pending | `tests/workers/test_work_02.py` / `test_tc_work_02_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## WORK-03 — orphan_upload_cleanup

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-MEDIA, FX-PURGE, FX-FAILURE.

Positive: Expire bounded unused intent and orphan object

Negative: Do not erase finalized legitimate evidence

Security/authorization: Only owning organization/quarantine scope

Edge cases: Finalize racing cleanup

Expected: No orphan storage leak or wrongful evidence deletion

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_WORK_03_P | positive | pending | `tests/workers/test_work_03.py` / `test_tc_work_03_p` | pending |
| TC_WORK_03_N | negative | pending | `tests/workers/test_work_03.py` / `test_tc_work_03_n` | pending |
| TC_WORK_03_S | security_authorization | pending | `tests/workers/test_work_03.py` / `test_tc_work_03_s` | pending |
| TC_WORK_03_E | edge | pending | `tests/workers/test_work_03.py` / `test_tc_work_03_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## WORK-04 — audit_export

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-MEDIA, FX-PURGE, FX-FAILURE.

Positive: Export chained events to independent signed-root sink

Negative: Detect gap/tamper/sink outage

Security/authorization: Exporter cannot read media/vector payloads

Edge cases: Crash between export and acknowledgment

Expected: Verifiable root/sequence and durable backlog; sensitive decisions hold when required

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_WORK_04_P | positive | pending | `tests/workers/test_work_04.py` / `test_tc_work_04_p` | pending |
| TC_WORK_04_N | negative | pending | `tests/workers/test_work_04.py` / `test_tc_work_04_n` | pending |
| TC_WORK_04_S | security_authorization | pending | `tests/workers/test_work_04.py` / `test_tc_work_04_s` | pending |
| TC_WORK_04_E | edge | pending | `tests/workers/test_work_04.py` / `test_tc_work_04_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## WORK-05 — retention_hold_review

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-MEDIA, FX-PURGE, FX-FAILURE.

Positive: Apply approved purpose/TTL and review expiring legal hold

Negative: No invented production retention schedule

Security/authorization: Only privacy authority changes holds

Edge cases: Withdrawal/closure racing retention timer

Expected: Scoped hold and approved erasure; no indefinite silent reuse

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_WORK_05_P | positive | pending | `tests/workers/test_work_05.py` / `test_tc_work_05_p` | pending |
| TC_WORK_05_N | negative | pending | `tests/workers/test_work_05.py` / `test_tc_work_05_n` | pending |
| TC_WORK_05_S | security_authorization | pending | `tests/workers/test_work_05.py` / `test_tc_work_05_s` | pending |
| TC_WORK_05_E | edge | pending | `tests/workers/test_work_05.py` / `test_tc_work_05_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## WORK-06 — index_reprocess_reconcile

Validation: **pending**. Suite: workers. Fixtures: FX-EVENT, FX-MEDIA, FX-PURGE, FX-FAILURE.

Positive: Reprocess manifest-versioned vectors and reconcile object/index tombstones

Negative: Never switch incompatible spaces silently

Security/authorization: No worker privilege escalation or cleared-license bypass

Edge cases: Partial migration, rollback, deletion and ANN filtered-shortfall

Expected: Versioned reproducible indexes with no deleted-case resurrection

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_WORK_06_P | positive | pending | `tests/workers/test_work_06.py` / `test_tc_work_06_p` | pending |
| TC_WORK_06_N | negative | pending | `tests/workers/test_work_06.py` / `test_tc_work_06_n` | pending |
| TC_WORK_06_S | security_authorization | pending | `tests/workers/test_work_06.py` / `test_tc_work_06_s` | pending |
| TC_WORK_06_E | edge | pending | `tests/workers/test_work_06.py` / `test_tc_work_06_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SAF-01 — Fraudulent guardian

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.

Positive: Verify safe contact separately from independently established relationship

Negative: Forged/stolen relationship evidence is held

Security/authorization: No child identity/location revealed during fraud inquiry

Edge cases: Actual guardian may still be unsafe; child objection/conflict

Expected: Only qualified independent review advances claim

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SAF_01_P | positive | pending | `tests/security/test_saf_01.py` / `test_tc_saf_01_p` | pending |
| TC_SAF_01_N | negative | pending | `tests/security/test_saf_01.py` / `test_tc_saf_01_n` | pending |
| TC_SAF_01_S | security_authorization | pending | `tests/security/test_saf_01.py` / `test_tc_saf_01_s` | pending |
| TC_SAF_01_E | edge | pending | `tests/security/test_saf_01.py` / `test_tc_saf_01_e` | pending |
| TC_SAF_01_BROWSER | companion_browser | pending | `tests/browser/saf_01.e2e.ts` / `TC_SAF_01_BROWSER` | pending |
| TC_SAF_01_STATE | companion_state | pending | `tests/security/test_saf_01.py` / `test_tc_saf_01_state` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SAF-02 — Found-child location discovery

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.

Positive: Authorized safeguarding reader sees only approved fields

Negative: Guess URLs, search/filter/export/analytics to locate shelter

Security/authorization: Unverified claimant sees no existence/count/location hints

Edge cases: Same missing-report owner and mixed federation grants

Expected: No shelter/custody leak via response, cache, logs or notifications

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SAF_02_P | positive | pending | `tests/security/test_saf_02.py` / `test_tc_saf_02_p` | pending |
| TC_SAF_02_N | negative | pending | `tests/security/test_saf_02.py` / `test_tc_saf_02_n` | pending |
| TC_SAF_02_S | security_authorization | pending | `tests/security/test_saf_02.py` / `test_tc_saf_02_s` | pending |
| TC_SAF_02_E | edge | pending | `tests/security/test_saf_02.py` / `test_tc_saf_02_e` | pending |
| TC_SAF_02_BROWSER | companion_browser | pending | `tests/browser/saf_02.e2e.ts` / `TC_SAF_02_BROWSER` | pending |
| TC_SAF_02_STATE | companion_state | pending | `tests/security/test_saf_02.py` / `test_tc_saf_02_state` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SAF-03 — Unauthorized image access

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.

Positive: Case/media grant permits sanitized derivative

Negative: Direct object key/original/GPS request denied

Security/authorization: Cross-org and expired/revoked session denied at request boundary

Edge cases: Range/read cache, stale presigned URL and revocation race

Expected: No private image access outside exact scope

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SAF_03_P | positive | pending | `tests/security/test_saf_03.py` / `test_tc_saf_03_p` | pending |
| TC_SAF_03_N | negative | pending | `tests/security/test_saf_03.py` / `test_tc_saf_03_n` | pending |
| TC_SAF_03_S | security_authorization | pending | `tests/security/test_saf_03.py` / `test_tc_saf_03_s` | pending |
| TC_SAF_03_E | edge | pending | `tests/security/test_saf_03.py` / `test_tc_saf_03_e` | pending |
| TC_SAF_03_BROWSER | companion_browser | pending | `tests/browser/saf_03.e2e.ts` / `TC_SAF_03_BROWSER` | pending |
| TC_SAF_03_STATE | companion_state | pending | `tests/security/test_saf_03.py` / `test_tc_saf_03_state` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SAF-04 — Unauthorized biometric search

Validation: **partial**. Suite: security. Fixtures: FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.

Positive: Authorized internal job uses compatible-space scope

Negative: Public, reporter or arbitrary query vectors denied

Security/authorization: No embedding array or public identity-to-location endpoint

Edge cases: Raw SQL vector path and federation worker credentials

Expected: Internal scoped lead retrieval only

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SAF_04_P | positive | pending | `tests/security/test_saf_04.py` / `test_tc_saf_04_p` | pending |
| TC_SAF_04_N | negative | pending | `tests/security/test_saf_04.py` / `test_tc_saf_04_n` | pending |
| TC_SAF_04_S | security_authorization | pending | `tests/security/test_saf_04.py` / `test_tc_saf_04_s` | pending |
| TC_SAF_04_E | edge | pending | `tests/security/test_saf_04.py` / `test_tc_saf_04_e` | pending |
| TC_SAF_04_BROWSER | companion_browser | pending | `tests/browser/saf_04.e2e.ts` / `TC_SAF_04_BROWSER` | pending |
| TC_SAF_04_STATE | companion_state | pending | `tests/security/test_saf_04.py` / `test_tc_saf_04_state` | pending |
| TC_SAF_04_DISABLED_P1 | disabled_capability_guard | passed | `tests/security/test_saf_04.py` / `test_tc_saf_04_disabled_p1` | artifacts/sanitized/results.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SAF-05 — Cross-organization leakage

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.

Positive: Authorized same-org and approved bilateral disclosure works

Negative: Wrong-org case ID, vectors, cursor and object key denied

Security/authorization: Both tenant RLS and application permission checks enforced

Edge cases: Pooled connection reuse and opt-out during in-flight job

Expected: No private row/media/count leak

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SAF_05_P | positive | pending | `tests/security/test_saf_05.py` / `test_tc_saf_05_p` | pending |
| TC_SAF_05_N | negative | pending | `tests/security/test_saf_05.py` / `test_tc_saf_05_n` | pending |
| TC_SAF_05_S | security_authorization | pending | `tests/security/test_saf_05.py` / `test_tc_saf_05_s` | pending |
| TC_SAF_05_E | edge | pending | `tests/security/test_saf_05.py` / `test_tc_saf_05_e` | pending |
| TC_SAF_05_BROWSER | companion_browser | pending | `tests/browser/saf_05.e2e.ts` / `TC_SAF_05_BROWSER` | pending |
| TC_SAF_05_STATE | companion_state | pending | `tests/security/test_saf_05.py` / `test_tc_saf_05_state` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SAF-06 — Expired and revoked access

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.

Positive: Current valid purpose-specific grants work

Negative: Expired receipt/MFA/session/grant/approval denied

Security/authorization: Revoked actor cannot send notification or stream image

Edge cases: Expiry at use time and stale outbox task

Expected: Fail closed and revoke pending dependent effects

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SAF_06_P | positive | pending | `tests/security/test_saf_06.py` / `test_tc_saf_06_p` | pending |
| TC_SAF_06_N | negative | pending | `tests/security/test_saf_06.py` / `test_tc_saf_06_n` | pending |
| TC_SAF_06_S | security_authorization | pending | `tests/security/test_saf_06.py` / `test_tc_saf_06_s` | pending |
| TC_SAF_06_E | edge | pending | `tests/security/test_saf_06.py` / `test_tc_saf_06_e` | pending |
| TC_SAF_06_BROWSER | companion_browser | pending | `tests/browser/saf_06.e2e.ts` / `TC_SAF_06_BROWSER` | pending |
| TC_SAF_06_STATE | companion_state | pending | `tests/security/test_saf_06.py` / `test_tc_saf_06_state` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SAF-07 — Incorrect match and human rejection

Validation: **partial**. Suite: security. Fixtures: FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.

Positive: Reviewer rejects deliberately wrong synthetic candidate

Negative: High score cannot confirm identity automatically

Security/authorization: Unauthorized reviewer cannot see/act on lead

Edge cases: New evidence after rejection and missing metadata

Expected: Audited rejection, no claimant message or case resolution

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SAF_07_P | positive | pending | `tests/security/test_saf_07.py` / `test_tc_saf_07_p` | pending |
| TC_SAF_07_N | negative | pending | `tests/security/test_saf_07.py` / `test_tc_saf_07_n` | pending |
| TC_SAF_07_S | security_authorization | pending | `tests/security/test_saf_07.py` / `test_tc_saf_07_s` | pending |
| TC_SAF_07_E | edge | pending | `tests/security/test_saf_07.py` / `test_tc_saf_07_e` | pending |
| TC_SAF_07_BROWSER | companion_browser | pending | `tests/browser/saf_07.e2e.ts` / `TC_SAF_07_BROWSER` | pending |
| TC_SAF_07_STATE | companion_state | pending | `tests/security/test_saf_07.py` / `test_tc_saf_07_state` | pending |
| TC_SAF_07_DISABLED_P1 | disabled_capability_guard | passed | `tests/security/test_saf_07.py` / `test_tc_saf_07_disabled_p1` | artifacts/sanitized/results.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SAF-08 — Two-person approval

Validation: **partial**. Suite: security. Fixtures: FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.

Positive: Two distinct competent principals approve current snapshot

Negative: Same principal with two roles or requester approval denied

Security/authorization: Org admin cannot override independent-actor requirement

Edge cases: Account sharing, approver suspension and concurrent signing

Expected: Distinct identity/action/scope enforced at API and DB transition

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SAF_08_P | positive | pending | `tests/security/test_saf_08.py` / `test_tc_saf_08_p` | pending |
| TC_SAF_08_N | negative | pending | `tests/security/test_saf_08.py` / `test_tc_saf_08_n` | pending |
| TC_SAF_08_S | security_authorization | pending | `tests/security/test_saf_08.py` / `test_tc_saf_08_s` | pending |
| TC_SAF_08_E | edge | pending | `tests/security/test_saf_08.py` / `test_tc_saf_08_e` | pending |
| TC_SAF_08_BROWSER | companion_browser | pending | `tests/browser/saf_08.e2e.ts` / `TC_SAF_08_BROWSER` | pending |
| TC_SAF_08_STATE | companion_state | pending | `tests/security/test_saf_08.py` / `test_tc_saf_08_state` | pending |
| TC_SAF_08_DISABLED_P1 | disabled_capability_guard | passed | `tests/security/test_saf_08.py` / `test_tc_saf_08_disabled_p1` | artifacts/sanitized/results.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SAF-09 — Child-release bypass

Validation: **partial**. Suite: security. Fixtures: FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.

Positive: Supervised plan with all current approvals proceeds

Negative: Direct lifecycle call, handover replay, missing authority or service outage denied

Security/authorization: Requester/admin/worker cannot bypass custody gate

Edge cases: Changed evidence, expiry, legal dispute or audit failure

Expected: No child-release state or disclosure when any verification incomplete

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SAF_09_P | positive | pending | `tests/security/test_saf_09.py` / `test_tc_saf_09_p` | pending |
| TC_SAF_09_N | negative | pending | `tests/security/test_saf_09.py` / `test_tc_saf_09_n` | pending |
| TC_SAF_09_S | security_authorization | pending | `tests/security/test_saf_09.py` / `test_tc_saf_09_s` | pending |
| TC_SAF_09_E | edge | pending | `tests/security/test_saf_09.py` / `test_tc_saf_09_e` | pending |
| TC_SAF_09_BROWSER | companion_browser | pending | `tests/browser/saf_09.e2e.ts` / `TC_SAF_09_BROWSER` | pending |
| TC_SAF_09_STATE | companion_state | pending | `tests/security/test_saf_09.py` / `test_tc_saf_09_state` | pending |
| TC_SAF_09_DISABLED_P1 | disabled_capability_guard | passed | `tests/security/test_saf_09.py` / `test_tc_saf_09_disabled_p1` | artifacts/sanitized/results.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SAF-10 — Deletion and biometric cleanup

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.

Positive: Erase permitted original/derivative/all embedding spaces and queues

Negative: Stale worker and old backup cannot restore reachability

Security/authorization: Removed grants deny image/vector read before purge completes

Edge cases: Legal hold, object versions, crash/retry and index race

Expected: Verified tombstone-first purge with minimal lawful audit

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SAF_10_P | positive | pending | `tests/security/test_saf_10.py` / `test_tc_saf_10_p` | pending |
| TC_SAF_10_N | negative | pending | `tests/security/test_saf_10.py` / `test_tc_saf_10_n` | pending |
| TC_SAF_10_S | security_authorization | pending | `tests/security/test_saf_10.py` / `test_tc_saf_10_s` | pending |
| TC_SAF_10_E | edge | pending | `tests/security/test_saf_10.py` / `test_tc_saf_10_e` | pending |
| TC_SAF_10_BROWSER | companion_browser | pending | `tests/browser/saf_10.e2e.ts` / `TC_SAF_10_BROWSER` | pending |
| TC_SAF_10_STATE | companion_state | pending | `tests/security/test_saf_10.py` / `test_tc_saf_10_state` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SAF-11 — Notification information leakage

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.

Positive: Neutral task link reaches authorized staff once

Negative: Template containing identifying/location/image/vector data fails

Security/authorization: Revoke recipient between enqueue and send; claimant gets no lead

Edge cases: Lock-screen preview, provider retry, log and URL leakage

Expected: Neutral/redacted delivery with current authorization and dedup

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SAF_11_P | positive | pending | `tests/security/test_saf_11.py` / `test_tc_saf_11_p` | pending |
| TC_SAF_11_N | negative | pending | `tests/security/test_saf_11.py` / `test_tc_saf_11_n` | pending |
| TC_SAF_11_S | security_authorization | pending | `tests/security/test_saf_11.py` / `test_tc_saf_11_s` | pending |
| TC_SAF_11_E | edge | pending | `tests/security/test_saf_11.py` / `test_tc_saf_11_e` | pending |
| TC_SAF_11_BROWSER | companion_browser | pending | `tests/browser/saf_11.e2e.ts` / `TC_SAF_11_BROWSER` | pending |
| TC_SAF_11_STATE | companion_state | pending | `tests/security/test_saf_11.py` / `test_tc_saf_11_state` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T01 — IDOR, forged org ID, pooled tenant leakage

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Server-validated principal/org, FORCE RLS, case grants, composite FKs, non-owner API role

Negative: Inject the named attack/failure and require denial/hold: IDOR, forged org ID, pooled tenant leakage

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Cross-tenant API+SQL negative tests, pooled connection race tests; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T01_P | positive | pending | `tests/security/test_sec_t01.py` / `test_tc_sec_t01_p` | pending |
| TC_SEC_T01_N | negative | pending | `tests/security/test_sec_t01.py` / `test_tc_sec_t01_n` | pending |
| TC_SEC_T01_S | security_authorization | pending | `tests/security/test_sec_t01.py` / `test_tc_sec_t01_s` | pending |
| TC_SEC_T01_E | edge | pending | `tests/security/test_sec_t01.py` / `test_tc_sec_t01_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T02 — Fraudulent claimant obtains identity/location

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Separate contact vs relationship vs custody verification; no candidate disclosure; independent scoped approvals

Negative: Inject the named attack/failure and require denial/hold: Fraudulent claimant obtains identity/location

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Adversarial claimant journeys and safeguarding review; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T02_P | positive | pending | `tests/security/test_sec_t02.py` / `test_tc_sec_t02_p` | pending |
| TC_SEC_T02_N | negative | pending | `tests/security/test_sec_t02.py` / `test_tc_sec_t02_n` | pending |
| TC_SEC_T02_S | security_authorization | pending | `tests/security/test_sec_t02.py` / `test_tc_sec_t02_s` | pending |
| TC_SEC_T02_E | edge | pending | `tests/security/test_sec_t02.py` / `test_tc_sec_t02_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T03 — Insider enumerates/export cases

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Purpose-based grants, explicit media permission, no bulk export by default, audit/anomaly review

Negative: Inject the named attack/failure and require denial/hold: Insider enumerates/export cases

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Role matrix, export abuse tests, access-review drill; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T03_P | positive | pending | `tests/security/test_sec_t03.py` / `test_tc_sec_t03_p` | pending |
| TC_SEC_T03_N | negative | pending | `tests/security/test_sec_t03.py` / `test_tc_sec_t03_n` | pending |
| TC_SEC_T03_S | security_authorization | pending | `tests/security/test_sec_t03.py` / `test_tc_sec_t03_s` | pending |
| TC_SEC_T03_E | edge | pending | `tests/security/test_sec_t03.py` / `test_tc_sec_t03_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T04 — Session theft, phishing or shared staff account

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Named users, MFA, short sessions, recent step-up for disclosure, secure cookies/CSRF, logout/revocation

Negative: Inject the named attack/failure and require denial/hold: Session theft, phishing or shared staff account

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: IdP/BFF integration and session replay tests; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T04_P | positive | pending | `tests/security/test_sec_t04.py` / `test_tc_sec_t04_p` | pending |
| TC_SEC_T04_N | negative | pending | `tests/security/test_sec_t04.py` / `test_tc_sec_t04_n` | pending |
| TC_SEC_T04_S | security_authorization | pending | `tests/security/test_sec_t04.py` / `test_tc_sec_t04_s` | pending |
| TC_SEC_T04_E | edge | pending | `tests/security/test_sec_t04.py` / `test_tc_sec_t04_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T05 — Malware, polyglot files, decompression bombs

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Quarantine, content validation, versioned malware scan, decode sandbox and resource ceilings

Negative: Inject the named attack/failure and require denial/hold: Malware, polyglot files, decompression bombs

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Adversarial files and scanner-down failure tests; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T05_P | positive | pending | `tests/security/test_sec_t05.py` / `test_tc_sec_t05_p` | pending |
| TC_SEC_T05_N | negative | pending | `tests/security/test_sec_t05.py` / `test_tc_sec_t05_n` | pending |
| TC_SEC_T05_S | security_authorization | pending | `tests/security/test_sec_t05.py` / `test_tc_sec_t05_s` | pending |
| TC_SEC_T05_E | edge | pending | `tests/security/test_sec_t05.py` / `test_tc_sec_t05_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T06 — EXIF GPS/shelter leaks

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Private original, sanitized derivative, metadata/thumbnail stripping and separate custody table

Negative: Inject the named attack/failure and require denial/hold: EXIF GPS/shelter leaks

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Byte-level EXIF/thumbnail checks and DTO snapshots; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T06_P | positive | pending | `tests/security/test_sec_t06.py` / `test_tc_sec_t06_p` | pending |
| TC_SEC_T06_N | negative | pending | `tests/security/test_sec_t06.py` / `test_tc_sec_t06_n` | pending |
| TC_SEC_T06_S | security_authorization | pending | `tests/security/test_sec_t06.py` / `test_tc_sec_t06_s` | pending |
| TC_SEC_T06_E | edge | pending | `tests/security/test_sec_t06.py` / `test_tc_sec_t06_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T07 — Link leakage/cache/search indexing

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Reauthorizing media gateway, no-store/no-referrer, no public buckets, restrictive CSP

Negative: Inject the named attack/failure and require denial/hold: Link leakage/cache/search indexing

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Header, cache, CDN and bucket-policy tests; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T07_P | positive | pending | `tests/security/test_sec_t07.py` / `test_tc_sec_t07_p` | pending |
| TC_SEC_T07_N | negative | pending | `tests/security/test_sec_t07.py` / `test_tc_sec_t07_n` | pending |
| TC_SEC_T07_S | security_authorization | pending | `tests/security/test_sec_t07.py` / `test_tc_sec_t07_s` | pending |
| TC_SEC_T07_E | edge | pending | `tests/security/test_sec_t07.py` / `test_tc_sec_t07_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T08 — Model/vector leak or malicious weights

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: No public inference/vector endpoints; approved hashes, trusted serialization, no worker egress

Negative: Inject the named attack/failure and require denial/hold: Model/vector leak or malicious weights

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Egress denial, weight-tamper and incompatible-space tests; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T08_P | positive | pending | `tests/security/test_sec_t08.py` / `test_tc_sec_t08_p` | pending |
| TC_SEC_T08_N | negative | pending | `tests/security/test_sec_t08.py` / `test_tc_sec_t08_n` | pending |
| TC_SEC_T08_S | security_authorization | pending | `tests/security/test_sec_t08.py` / `test_tc_sec_t08_s` | pending |
| TC_SEC_T08_E | edge | pending | `tests/security/test_sec_t08.py` / `test_tc_sec_t08_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T09 — False leads or adversarial image edits

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Independent models/evaluation, uncertainty, human review, no automatic resolution

Negative: Inject the named attack/failure and require denial/hold: False leads or adversarial image edits

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Open-set benchmark and staff false-lead exercises; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T09_P | positive | pending | `tests/security/test_sec_t09.py` / `test_tc_sec_t09_p` | pending |
| TC_SEC_T09_N | negative | pending | `tests/security/test_sec_t09.py` / `test_tc_sec_t09_n` | pending |
| TC_SEC_T09_S | security_authorization | pending | `tests/security/test_sec_t09.py` / `test_tc_sec_t09_s` | pending |
| TC_SEC_T09_E | edge | pending | `tests/security/test_sec_t09.py` / `test_tc_sec_t09_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T10 — Replay/race bypass of approval or deletion

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Revision-bound approvals, unique actors, expiry, serializable/locked transition, tombstone checks

Negative: Inject the named attack/failure and require denial/hold: Replay/race bypass of approval or deletion

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Concurrent approval/revocation/deletion tests; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T10_P | positive | pending | `tests/security/test_sec_t10.py` / `test_tc_sec_t10_p` | pending |
| TC_SEC_T10_N | negative | pending | `tests/security/test_sec_t10.py` / `test_tc_sec_t10_n` | pending |
| TC_SEC_T10_S | security_authorization | pending | `tests/security/test_sec_t10.py` / `test_tc_sec_t10_s` | pending |
| TC_SEC_T10_E | edge | pending | `tests/security/test_sec_t10.py` / `test_tc_sec_t10_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T11 — Notification leaks or spam

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Neutral template, authorized recipient at send time, dedup/quota/retries and delivery audit

Negative: Inject the named attack/failure and require denial/hold: Notification leaks or spam

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Provider stub tests, duplicate/out-of-order/revoked grant cases; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T11_P | positive | pending | `tests/security/test_sec_t11.py` / `test_tc_sec_t11_p` | pending |
| TC_SEC_T11_N | negative | pending | `tests/security/test_sec_t11.py` / `test_tc_sec_t11_n` | pending |
| TC_SEC_T11_S | security_authorization | pending | `tests/security/test_sec_t11.py` / `test_tc_sec_t11_s` | pending |
| TC_SEC_T11_E | edge | pending | `tests/security/test_sec_t11.py` / `test_tc_sec_t11_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T12 — Audit alteration or sensitive logs

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Append-only role, chained hashes and external signed roots; allowlisted fields

Negative: Inject the named attack/failure and require denial/hold: Audit alteration or sensitive logs

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Tamper detection, denied UPDATE/DELETE and log leakage scans; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T12_P | positive | pending | `tests/security/test_sec_t12.py` / `test_tc_sec_t12_p` | pending |
| TC_SEC_T12_N | negative | pending | `tests/security/test_sec_t12.py` / `test_tc_sec_t12_n` | pending |
| TC_SEC_T12_S | security_authorization | pending | `tests/security/test_sec_t12.py` / `test_tc_sec_t12_s` | pending |
| TC_SEC_T12_E | edge | pending | `tests/security/test_sec_t12.py` / `test_tc_sec_t12_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T13 — Lost keys/ransomware/backups restore deleted children

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Separate KMS custody, encrypted backups, offline/immutable copies, tombstone replay

Negative: Inject the named attack/failure and require denial/hold: Lost keys/ransomware/backups restore deleted children

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Measured recovery/erasure drills; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T13_P | positive | pending | `tests/security/test_sec_t13.py` / `test_tc_sec_t13_p` | pending |
| TC_SEC_T13_N | negative | pending | `tests/security/test_sec_t13.py` / `test_tc_sec_t13_n` | pending |
| TC_SEC_T13_S | security_authorization | pending | `tests/security/test_sec_t13.py` / `test_tc_sec_t13_s` | pending |
| TC_SEC_T13_E | edge | pending | `tests/security/test_sec_t13.py` / `test_tc_sec_t13_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T14 — Cross-NGO metadata inference

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Disabled-default federation, bilateral purpose grants, broker-only edges, no hidden counts

Negative: Inject the named attack/failure and require denial/hold: Cross-NGO metadata inference

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Unauthorized-count/timing tests, opt-out race and bilateral disclosure tests; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T14_P | positive | pending | `tests/security/test_sec_t14.py` / `test_tc_sec_t14_p` | pending |
| TC_SEC_T14_N | negative | pending | `tests/security/test_sec_t14.py` / `test_tc_sec_t14_n` | pending |
| TC_SEC_T14_S | security_authorization | pending | `tests/security/test_sec_t14.py` / `test_tc_sec_t14_s` | pending |
| TC_SEC_T14_E | edge | pending | `tests/security/test_sec_t14.py` / `test_tc_sec_t14_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T15 — XSS from notes/names/generated output

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Escaped text rendering, sanitized limited markup, strict CSP, no inline executable remote content

Negative: Inject the named attack/failure and require denial/hold: XSS from notes/names/generated output

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Stored-XSS cases in Arabic/English, rich-text and evidence previews; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T15_P | positive | pending | `tests/security/test_sec_t15.py` / `test_tc_sec_t15_p` | pending |
| TC_SEC_T15_N | negative | pending | `tests/security/test_sec_t15.py` / `test_tc_sec_t15_n` | pending |
| TC_SEC_T15_S | security_authorization | pending | `tests/security/test_sec_t15.py` / `test_tc_sec_t15_s` | pending |
| TC_SEC_T15_E | edge | pending | `tests/security/test_sec_t15.py` / `test_tc_sec_t15_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T16 — SSRF through URL image/report import

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Do not accept remote image URLs initially; safe resolver/egress restrictions if added

Negative: Inject the named attack/failure and require denial/hold: SSRF through URL image/report import

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Loopback/private/redirect/metadata-target tests; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T16_P | positive | pending | `tests/security/test_sec_t16.py` / `test_tc_sec_t16_p` | pending |
| TC_SEC_T16_N | negative | pending | `tests/security/test_sec_t16.py` / `test_tc_sec_t16_n` | pending |
| TC_SEC_T16_S | security_authorization | pending | `tests/security/test_sec_t16.py` / `test_tc_sec_t16_s` | pending |
| TC_SEC_T16_E | edge | pending | `tests/security/test_sec_t16.py` / `test_tc_sec_t16_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T17 — Bot flooding and storage exhaustion

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Limits by contact/session/org/IP, accessible challenges, quotas, orphan cleanup

Negative: Inject the named attack/failure and require denial/hold: Bot flooding and storage exhaustion

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Load/abuse test without denying all shared-network users; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T17_P | positive | pending | `tests/security/test_sec_t17.py` / `test_tc_sec_t17_p` | pending |
| TC_SEC_T17_N | negative | pending | `tests/security/test_sec_t17.py` / `test_tc_sec_t17_n` | pending |
| TC_SEC_T17_S | security_authorization | pending | `tests/security/test_sec_t17.py` / `test_tc_sec_t17_s` | pending |
| TC_SEC_T17_E | edge | pending | `tests/security/test_sec_t17.py` / `test_tc_sec_t17_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T18 — Compromised dependency or stale service

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Exact locks/digests, SBOM, license/CVE checks, signatures/provenance review and patch owner

Negative: Inject the named attack/failure and require denial/hold: Compromised dependency or stale service

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Clean install, reproducible build and patch drill; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T18_P | positive | pending | `tests/security/test_sec_t18.py` / `test_tc_sec_t18_p` | pending |
| TC_SEC_T18_N | negative | pending | `tests/security/test_sec_t18.py` / `test_tc_sec_t18_n` | pending |
| TC_SEC_T18_S | security_authorization | pending | `tests/security/test_sec_t18.py` / `test_tc_sec_t18_s` | pending |
| TC_SEC_T18_E | edge | pending | `tests/security/test_sec_t18.py` / `test_tc_sec_t18_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## SEC-T19 — Unauthorized aggregate inference

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-DB, FX-FAILURE.

Positive: Demonstrate legitimate flow with control enabled: Small-cell suppression, fixed approved reports, no row drilldown

Negative: Inject the named attack/failure and require denial/hold: Unauthorized aggregate inference

Security/authorization: Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries

Edge cases: Concurrent revocation/outage/retry and alternate read/export/cache path

Expected: Differencing and low-count analytics tests; preserve safe care/intake and prevent unauthorized sensitive effect

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_SEC_T19_P | positive | pending | `tests/security/test_sec_t19.py` / `test_tc_sec_t19_p` | pending |
| TC_SEC_T19_N | negative | pending | `tests/security/test_sec_t19.py` / `test_tc_sec_t19_n` | pending |
| TC_SEC_T19_S | security_authorization | pending | `tests/security/test_sec_t19.py` / `test_tc_sec_t19_s` | pending |
| TC_SEC_T19_E | edge | pending | `tests/security/test_sec_t19.py` / `test_tc_sec_t19_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## UNIT-01 — Domain/unit and rendered component invariants

Validation: **pending**. Suite: unit. Fixtures: FX-UNCERTAIN, FX-A11Y.

Positive: Pure interval/name normalization and form/verification-state rendering

Negative: Malformed intervals/unknown vs contradiction

Security/authorization: No hidden verified state or unsafe HTML rendering

Edge cases: Arabic diacritics, Unicode variants and component event reordering

Expected: Original claims preserved; deterministic domain and component assertions

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_UNIT_01_P | positive | pending | `tests/unit/test_unit_01.py` / `test_tc_unit_01_p` | pending |
| TC_UNIT_01_N | negative | pending | `tests/unit/test_unit_01.py` / `test_tc_unit_01_n` | pending |
| TC_UNIT_01_S | security_authorization | pending | `tests/unit/test_unit_01.py` / `test_tc_unit_01_s` | pending |
| TC_UNIT_01_E | edge | pending | `tests/unit/test_unit_01.py` / `test_tc_unit_01_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## UNIT-02 — React form and review components

Validation: **pending**. Suite: components. Fixtures: FX-UNCERTAIN, FX-A11Y.

Positive: Render forms/review controls and dispatch validated input events

Negative: Missing labels, invalid errors and unsafe HTML fail

Security/authorization: Sensitive fields absent without granted projection; hidden button is not authorization

Edge cases: Locale switch, keyboard focus, long Arabic text and loading states

Expected: Deterministic rendered component assertions independent of browser E2E

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_UNIT_02_P | positive | pending | `tests/components/unit_02.test.ts` / `TC_UNIT_02_P` | pending |
| TC_UNIT_02_N | negative | pending | `tests/components/unit_02.test.ts` / `TC_UNIT_02_N` | pending |
| TC_UNIT_02_S | security_authorization | pending | `tests/components/unit_02.test.ts` / `TC_UNIT_02_S` | pending |
| TC_UNIT_02_E | edge | pending | `tests/components/unit_02.test.ts` / `TC_UNIT_02_E` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## AUTH-01 — OIDC/MFA/session lifecycle

Validation: **pending**. Suite: auth. Fixtures: FX-IDP, FX-BASE.

Positive: Actual test Keycloak login, correct issuer/audience and fresh step-up

Negative: Wrong JWT claims, stale MFA, logout/revocation denied

Security/authorization: CSRF/cookie/session fixation/account deprovisioning protection

Edge cases: IdP/JWKS rotation outage and membership update mid-session

Expected: Authenticated current purpose/grants enforced; no fallback anonymous access

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_AUTH_01_P | positive | pending | `tests/auth/test_auth_01.py` / `test_tc_auth_01_p` | pending |
| TC_AUTH_01_N | negative | pending | `tests/auth/test_auth_01.py` / `test_tc_auth_01_n` | pending |
| TC_AUTH_01_S | security_authorization | pending | `tests/auth/test_auth_01.py` / `test_tc_auth_01_s` | pending |
| TC_AUTH_01_E | edge | pending | `tests/auth/test_auth_01.py` / `test_tc_auth_01_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## A11Y-01 — Arabic/English responsive/accessibility journeys

Validation: **pending**. Suite: accessibility. Fixtures: FX-A11Y.

Positive: Keyboard/labels/focus/status/zoom/manual screen-reader review

Negative: Missing names, focus traps and clipped actionable text fail

Security/authorization: Private content absent from accessible tree and page title

Edge cases: 3 browsers × 2 locales × 4 widths; reduced motion, bidi and low bandwidth

Expected: WCAG acceptance evidence plus deterministic layout/DOM checks; manual results separate

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_A11Y_01_P | positive | pending | `tests/browser/a11y_01.e2e.ts` / `TC_A11Y_01_P` | pending |
| TC_A11Y_01_N | negative | pending | `tests/browser/a11y_01.e2e.ts` / `TC_A11Y_01_N` | pending |
| TC_A11Y_01_S | security_authorization | pending | `tests/browser/a11y_01.e2e.ts` / `TC_A11Y_01_S` | pending |
| TC_A11Y_01_E | edge | pending | `tests/browser/a11y_01.e2e.ts` / `TC_A11Y_01_E` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## ML-01 — Lawful longitudinal identification benchmark

Validation: **pending**. Suite: ml. Fixtures: FX-EVAL.

Positive: Frozen independent ground-truth subject/family-disjoint evaluation

Negative: Leakage, missing provenance/license or synthetic-only accuracy claims rejected

Security/authorization: Restricted lawful images never exported to testing model/logs

Edge cases: Age gaps, quality/occlusion, demographic uncertainty, no-mate probes

Expected: Recall@1/10/50, false leads/FPIR, workload and confidence intervals; unset go/no-go pending NGO approval

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_ML_01_P | positive | pending | `tests/ml/test_ml_01.py` / `test_tc_ml_01_p` | pending |
| TC_ML_01_N | negative | pending | `tests/ml/test_ml_01.py` / `test_tc_ml_01_n` | pending |
| TC_ML_01_S | security_authorization | pending | `tests/ml/test_ml_01.py` / `test_tc_ml_01_s` | pending |
| TC_ML_01_E | edge | pending | `tests/ml/test_ml_01.py` / `test_tc_ml_01_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## ML-02 — Embedding/fusion/reprocessing regression

Validation: **pending**. Suite: ml. Fixtures: FX-MATCH, FX-MEDIA.

Positive: Compatible deterministic embeddings/ranking with independent retrieval

Negative: RGB/BGR/dimension/weight/metric mismatch fails

Security/authorization: Uncleared manifest or production-data training denied

Edge cases: Photo count max-score inflation, missing metadata and age uncertainty

Expected: Versioned provenance, no incompatible vector comparison or auto-confirmation

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_ML_02_P | positive | pending | `tests/ml/test_ml_02.py` / `test_tc_ml_02_p` | pending |
| TC_ML_02_N | negative | pending | `tests/ml/test_ml_02.py` / `test_tc_ml_02_n` | pending |
| TC_ML_02_S | security_authorization | pending | `tests/ml/test_ml_02.py` / `test_tc_ml_02_s` | pending |
| TC_ML_02_E | edge | pending | `tests/ml/test_ml_02.py` / `test_tc_ml_02_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## PERF-01 — Pilot capacity/load and filtered search

Validation: **pending**. Suite: performance. Fixtures: FX-BASE, FX-MATCH, FX-FAILURE.

Positive: Measure proposed workload with controls enabled

Negative: Resource saturation/queue overload fails capacity gate

Security/authorization: No rate-limit/authorization bypass for benchmark

Edge cases: 50k cases × five synthetic photos, 30 staff, 100 reports/hour; scoped ANN vs exact

Expected: Observed p50/p95/p99/error/resources and review workload; provisional SLOs not assumed passed

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_PERF_01_P | positive | pending | `tests/performance/test_perf_01.py` / `test_tc_perf_01_p` | pending |
| TC_PERF_01_N | negative | pending | `tests/performance/test_perf_01.py` / `test_tc_perf_01_n` | pending |
| TC_PERF_01_S | security_authorization | pending | `tests/performance/test_perf_01.py` / `test_tc_perf_01_s` | pending |
| TC_PERF_01_E | edge | pending | `tests/performance/test_perf_01.py` / `test_tc_perf_01_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## RES-01 — Failure, concurrency and recovery

Validation: **pending**. Suite: resilience. Fixtures: FX-FAILURE, FX-EVENT, FX-DB.

Positive: Recover scanner/IdP/DB/storage/KMS/audit/worker failures

Negative: Unavailable sensitive gate blocks serve/disclose/release

Security/authorization: No plaintext/admin/anonymous fallback

Edge cases: Kill before/after commits, partitions, race barriers and at-least-once events

Expected: Fail-safe sensitive paths, bounded retries, no double effect; measured recovery evidence

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_RES_01_P | positive | pending | `tests/resilience/test_res_01.py` / `test_tc_res_01_p` | pending |
| TC_RES_01_N | negative | pending | `tests/resilience/test_res_01.py` / `test_tc_res_01_n` | pending |
| TC_RES_01_S | security_authorization | pending | `tests/resilience/test_res_01.py` / `test_tc_res_01_s` | pending |
| TC_RES_01_E | edge | pending | `tests/resilience/test_res_01.py` / `test_tc_res_01_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DEP-01 — Clean installation and release candidate validation

Validation: **pending**. Suite: deployment. Fixtures: FX-DEPLOY, FX-DB.

Positive: Build locked candidate and install fresh isolated full stack

Negative: Missing lock/digest/signature/schema guard blocks promotion

Security/authorization: No PR secrets, floating images or production data

Edge cases: Clean and upgrade paths, browser binaries/platform mismatch

Expected: Candidate health, migrations and full mandatory regression evidence tied to digests

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DEP_01_P | positive | pending | `tests/deployment/test_dep_01.py` / `test_tc_dep_01_p` | pending |
| TC_DEP_01_N | negative | pending | `tests/deployment/test_dep_01.py` / `test_tc_dep_01_n` | pending |
| TC_DEP_01_S | security_authorization | pending | `tests/deployment/test_dep_01.py` / `test_tc_dep_01_s` | pending |
| TC_DEP_01_E | edge | pending | `tests/deployment/test_dep_01.py` / `test_tc_dep_01_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DEP-02 — Rollback and backup/deletion recovery

Validation: **pending**. Suite: deployment. Fixtures: FX-DEPLOY, FX-PURGE.

Positive: Restore/rollback to compatible approved release

Negative: Destructive incompatible downgrade or tombstone loss blocks

Security/authorization: No resurrection of deleted case, revoked approval or model

Edge cases: Coherent DB/object cut, key recovery and incomplete backfill

Expected: Verified RPO/RTO, revocation/deletion replay and permission-safe reopening

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_DEP_02_P | positive | pending | `tests/deployment/test_dep_02.py` / `test_tc_dep_02_p` | pending |
| TC_DEP_02_N | negative | pending | `tests/deployment/test_dep_02.py` / `test_tc_dep_02_n` | pending |
| TC_DEP_02_S | security_authorization | pending | `tests/deployment/test_dep_02.py` / `test_tc_dep_02_s` | pending |
| TC_DEP_02_E | edge | pending | `tests/deployment/test_dep_02.py` / `test_tc_dep_02_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## TOOL-01 — TesterArmy telemetry/model/artifact boundaries

Validation: **pending**. Suite: security. Fixtures: FX-BASE, FX-FAILURE.

Positive: Model-free local browser runner with both opt-out flags and isolated DB

Negative: Telemetry unset, production target, external model with real data denied

Security/authorization: Egress policy plus synthetic canaries and independent artifact redaction

Edge cases: Cache miss, automatic browser install, malicious page link and raw command.log

Expected: No optional telemetry or real child data to external testing model; artifacts sanitized before publishing

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_TOOL_01_P | positive | pending | `tests/security/test_tool_01.py` / `test_tc_tool_01_p` | pending |
| TC_TOOL_01_N | negative | pending | `tests/security/test_tool_01.py` / `test_tc_tool_01_n` | pending |
| TC_TOOL_01_S | security_authorization | pending | `tests/security/test_tool_01.py` / `test_tc_tool_01_s` | pending |
| TC_TOOL_01_E | edge | pending | `tests/security/test_tool_01.py` / `test_tc_tool_01_e` | pending |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FND-01 — Synthetic-only configuration and secret isolation

Validation: **passed**. Suite: unit. Fixtures: FX-FOUNDATION.

Positive: Startup accepts only the isolated synthetic database; web/browser processes receive no database or model credentials.

Negative: Invalid, missing or unavailable inputs/dependencies reject rather than granting access or claiming validation.

Security/authorization: Non-owner roles and forged/expired/missing authority cannot enable a sensitive operation; test artifacts contain only the synthetic shell.

Edge cases: Isolation, tenant/case mixing, replay, rollback, missing results and platform-specific launch failure are checked where applicable; unimplemented operational scenarios remain pending in the original baseline.

Expected: Startup accepts only the isolated synthetic database; web/browser processes receive no database or model credentials.

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FND_8FE85FEBB745 | negative | passed | `tests/unit/test_foundation.py` / `test_fnd_config_rejects_non_synthetic[None]` | artifacts/sanitized/results.json |
| TC_FND_B2D49AEB8A38 | negative | passed | `tests/unit/test_foundation.py` / `test_fnd_config_rejects_non_synthetic[production]` | artifacts/sanitized/results.json |
| TC_FND_33D9D1C09E66 | negative | passed | `tests/unit/test_foundation.py` / `test_fnd_config_rejects_non_synthetic[real]` | artifacts/sanitized/results.json |
| TC_FND_591A1CA1A618 | negative | passed | `tests/unit/test_foundation.py` / `test_fnd_config_rejects_non_synthetic[]` | artifacts/sanitized/results.json |
| TC_FND_737E1CEE619D | negative | passed | `tests/unit/test_foundation.py` / `test_fnd_config_rejects_non_synthetic[Synthetic]` | artifacts/sanitized/results.json |
| TC_FND_1B99EE6535E7 | negative | passed | `tests/unit/test_foundation.py` / `test_fnd_config_rejects_untrusted_database[postgresql://user@remote.invalid/foc_synthetic]` | artifacts/sanitized/results.json |
| TC_FND_10AFA5E0DBDC | negative | passed | `tests/unit/test_foundation.py` / `test_fnd_config_rejects_untrusted_database[postgresql://user@127.0.0.1/production]` | artifacts/sanitized/results.json |
| TC_FND_6EFF710710BA | negative | passed | `tests/unit/test_foundation.py` / `test_fnd_config_rejects_untrusted_database[https://127.0.0.1/foc_synthetic]` | artifacts/sanitized/results.json |
| TC_FND_49EC814F89B9 | negative | passed | `tests/unit/test_foundation.py` / `test_fnd_config_rejects_untrusted_database[postgresql://user@localhost/postgres]` | artifacts/sanitized/results.json |
| TC_FND_CFE5A7E252C7 | negative | passed | `tests/unit/test_foundation.py` / `test_fnd_config_rejects_untrusted_database[]` | artifacts/sanitized/results.json |
| TC_FND_49B5EA8D1834 | positive | passed | `tests/unit/test_foundation.py` / `test_fnd_config_accepts_local_synthetic` | artifacts/sanitized/results.json |
| TC_FND_60685E95ACA1 | security_authorization | passed | `tests/unit/test_foundation.py` / `test_fnd_browser_environment_removes_privileged_credentials[FOC_CONTAINER_ADMIN_URL]` | artifacts/sanitized/results.json |
| TC_FND_861430644ED5 | security_authorization | passed | `tests/unit/test_foundation.py` / `test_fnd_browser_environment_removes_privileged_credentials[FOC_CONTAINER_DATABASE_URL]` | artifacts/sanitized/results.json |
| TC_FND_F726306C0981 | security_authorization | passed | `tests/unit/test_foundation.py` / `test_fnd_browser_environment_removes_privileged_credentials[FOC_DATABASE_ADMIN_URL]` | artifacts/sanitized/results.json |
| TC_FND_122F38F4FA8B | security_authorization | passed | `tests/unit/test_foundation.py` / `test_fnd_browser_environment_removes_privileged_credentials[FOC_DATABASE_URL]` | artifacts/sanitized/results.json |
| TC_FND_264022D0259F | security_authorization | passed | `tests/unit/test_foundation.py` / `test_fnd_browser_environment_removes_privileged_credentials[FOC_DB_API_PASSWORD]` | artifacts/sanitized/results.json |
| TC_FND_D91952D12159 | security_authorization | passed | `tests/unit/test_foundation.py` / `test_fnd_browser_environment_removes_privileged_credentials[OPENAI_API_KEY]` | artifacts/sanitized/results.json |
| TC_FND_64705E149272 | security_authorization | passed | `tests/unit/test_foundation.py` / `test_fnd_browser_environment_removes_privileged_credentials[AWS_SECRET_ACCESS_KEY]` | artifacts/sanitized/results.json |
| TC_FND_C49D96F7CD0E | security_authorization | passed | `tests/unit/test_foundation.py` / `test_fnd_browser_environment_removes_privileged_credentials[E2E_API_KEY]` | artifacts/sanitized/results.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FND-02 — Liveness, readiness and response security headers

Validation: **passed**. Suite: api. Fixtures: FX-FOUNDATION.

Positive: Public health responses use no-store and generated request IDs; unavailable or untrusted database fails readiness.

Negative: Invalid, missing or unavailable inputs/dependencies reject rather than granting access or claiming validation.

Security/authorization: Non-owner roles and forged/expired/missing authority cannot enable a sensitive operation; test artifacts contain only the synthetic shell.

Edge cases: Isolation, tenant/case mixing, replay, rollback, missing results and platform-specific launch failure are checked where applicable; unimplemented operational scenarios remain pending in the original baseline.

Expected: Public health responses use no-store and generated request IDs; unavailable or untrusted database fails readiness.

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FND_1F31FE3A87DF | positive | passed | `tests/api/test_foundation.py` / `test_fnd_live` | artifacts/sanitized/results.json |
| TC_FND_D3AE561BEDD0 | positive | passed | `tests/api/test_foundation.py` / `test_fnd_real_database_readiness` | artifacts/sanitized/results.json |
| TC_FND_B9220AD6BDCB | negative | passed | `tests/api/test_foundation.py` / `test_fnd_unavailable_database_fails_safely` | artifacts/sanitized/results.json |
| TC_FND_76295B80AE34 | positive | passed | `tests/api/test_foundation.py` / `test_fnd_security_headers_and_request_id` | artifacts/sanitized/results.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FND-03 — Complete versioned OpenAPI and closed DTOs

Validation: **passed**. Suite: api. Fixtures: FX-FOUNDATION.

Positive: All 32 domain contracts plus three foundation operations validate; domain behavior remains disabled.

Negative: Invalid, missing or unavailable inputs/dependencies reject rather than granting access or claiming validation.

Security/authorization: Non-owner roles and forged/expired/missing authority cannot enable a sensitive operation; test artifacts contain only the synthetic shell.

Edge cases: Isolation, tenant/case mixing, replay, rollback, missing results and platform-specific launch failure are checked where applicable; unimplemented operational scenarios remain pending in the original baseline.

Expected: All 32 domain contracts plus three foundation operations validate; domain behavior remains disabled.

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FND_03DA8CFB8FD5 | positive | passed | `tests/api/test_foundation.py` / `test_fnd_full_openapi` | artifacts/sanitized/results.json |
| TC_FND_0439323FE0AF | positive | passed | `tests/api/test_foundation.py` / `test_fnd_closed_report_schema` | artifacts/sanitized/results.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FND-04 — Executable schema, migration replay and same-case integrity

Validation: **passed**. Suite: database. Fixtures: FX-FOUNDATION.

Positive: Both immutable migrations apply/replay, tenant and same-case foreign keys reject mixed references, and all 41 domain relations force RLS.

Negative: Invalid, missing or unavailable inputs/dependencies reject rather than granting access or claiming validation.

Security/authorization: Non-owner roles and forged/expired/missing authority cannot enable a sensitive operation; test artifacts contain only the synthetic shell.

Edge cases: Isolation, tenant/case mixing, replay, rollback, missing results and platform-specific launch failure are checked where applicable; unimplemented operational scenarios remain pending in the original baseline.

Expected: Both immutable migrations apply/replay, tenant and same-case foreign keys reject mixed references, and all 41 domain relations force RLS.

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FND_BA452118EF58 | security_authorization | passed | `tests/database/test_contract_hardening.py` / `test_fnd_same_tenant_wrong_case_object_rejected` | artifacts/sanitized/results.json |
| TC_FND_60F67AAE25AF | positive | passed | `tests/database/test_rls.py` / `test_fnd_all_domain_relations_force_rls` | artifacts/sanitized/results.json |
| TC_FND_D45355E15320 | security_authorization | passed | `tests/database/test_rls.py` / `test_fnd_composite_foreign_key_rejects_tenant_mix` | artifacts/sanitized/results.json |
| TC_FND_D100ECEC24D4 | negative | passed | `tests/database/test_rls.py` / `test_fnd_invalid_age_interval_rejected` | artifacts/sanitized/results.json |
| TC_FND_A55C052FE603 | edge | passed | `tests/integration/test_contracts.py` / `test_fnd_migration_replay_and_checksum` | artifacts/sanitized/results.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FND-05 — Tenant/case/purpose/expiry database boundaries

Validation: **passed**. Suite: database. Fixtures: FX-FOUNDATION.

Positive: Non-owner runtime reads only a granted active case; missing context, revocation, wrong purpose and sensitive classifications deny access.

Negative: Invalid, missing or unavailable inputs/dependencies reject rather than granting access or claiming validation.

Security/authorization: Non-owner roles and forged/expired/missing authority cannot enable a sensitive operation; test artifacts contain only the synthetic shell.

Edge cases: Isolation, tenant/case mixing, replay, rollback, missing results and platform-specific launch failure are checked where applicable; unimplemented operational scenarios remain pending in the original baseline.

Expected: Non-owner runtime reads only a granted active case; missing context, revocation, wrong purpose and sensitive classifications deny access.

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FND_7356E8341A88 | positive | passed | `tests/database/test_rls.py` / `test_fnd_no_context_denied` | artifacts/sanitized/results.json |
| TC_FND_33F9683479AC | positive | passed | `tests/database/test_rls.py` / `test_fnd_authorized_case_only` | artifacts/sanitized/results.json |
| TC_FND_A0791E10F649 | security_authorization | passed | `tests/database/test_rls.py` / `test_fnd_cross_tenant_denied` | artifacts/sanitized/results.json |
| TC_FND_0D4555FE65BB | positive | passed | `tests/database/test_rls.py` / `test_fnd_org_admin_without_case_grant_denied` | artifacts/sanitized/results.json |
| TC_FND_231C3B833B20 | negative | passed | `tests/database/test_rls.py` / `test_fnd_revocation_and_expiry[revoked-grant]` | artifacts/sanitized/results.json |
| TC_FND_075A427E134F | negative | passed | `tests/database/test_rls.py` / `test_fnd_revocation_and_expiry[expired-grant]` | artifacts/sanitized/results.json |
| TC_FND_B83AD5E5C9B9 | negative | passed | `tests/database/test_rls.py` / `test_fnd_revocation_and_expiry[revoked-member]` | artifacts/sanitized/results.json |
| TC_FND_BEACC678BDF5 | negative | passed | `tests/database/test_rls.py` / `test_fnd_revocation_and_expiry[expired-member]` | artifacts/sanitized/results.json |
| TC_FND_73FEDFD01F64 | negative | passed | `tests/database/test_rls.py` / `test_fnd_revocation_and_expiry[suspended-org]` | artifacts/sanitized/results.json |
| TC_FND_0471BFAA8E16 | negative | passed | `tests/database/test_rls.py` / `test_fnd_revocation_and_expiry[deleted-case]` | artifacts/sanitized/results.json |
| TC_FND_240CFB5A7AF2 | security_authorization | passed | `tests/database/test_rls.py` / `test_fnd_disabled_principal_denied` | artifacts/sanitized/results.json |
| TC_FND_D95F44BA64D1 | security_authorization | passed | `tests/database/test_rls.py` / `test_fnd_wrong_purpose_denied` | artifacts/sanitized/results.json |
| TC_FND_9BCE6E38D98F | edge | passed | `tests/database/test_rls.py` / `test_fnd_context_does_not_survive_pool_reuse` | artifacts/sanitized/results.json |
| TC_FND_2E84F63487C7 | security_authorization | passed | `tests/database/test_rls.py` / `test_fnd_sensitive_boundaries_deny_runtime[restricted_custody]` | artifacts/sanitized/results.json |
| TC_FND_11C9BBA7F55F | security_authorization | passed | `tests/database/test_rls.py` / `test_fnd_sensitive_boundaries_deny_runtime[photographs]` | artifacts/sanitized/results.json |
| TC_FND_234C04A8869E | security_authorization | passed | `tests/database/test_rls.py` / `test_fnd_sensitive_boundaries_deny_runtime[objects]` | artifacts/sanitized/results.json |
| TC_FND_473D6712A40D | security_authorization | passed | `tests/database/test_rls.py` / `test_fnd_sensitive_boundaries_deny_runtime[embeddings]` | artifacts/sanitized/results.json |
| TC_FND_81C91A65B72D | security_authorization | passed | `tests/database/test_rls.py` / `test_fnd_sensitive_boundaries_deny_runtime[broker_candidate_edges]` | artifacts/sanitized/results.json |
| TC_FND_330C0CDB37ED | security_authorization | passed | `tests/database/test_rls.py` / `test_fnd_sensitive_boundaries_deny_runtime[approvals]` | artifacts/sanitized/results.json |
| TC_FND_506984EF69A2 | security_authorization | passed | `tests/database/test_rls.py` / `test_fnd_sensitive_boundaries_deny_runtime[handovers]` | artifacts/sanitized/results.json |
| TC_FND_84A6AC555C62 | security_authorization | passed | `tests/database/test_rls.py` / `test_fnd_sensitive_boundaries_deny_runtime[memberships]` | artifacts/sanitized/results.json |
| TC_FND_9C5F98D22312 | security_authorization | passed | `tests/database/test_rls.py` / `test_fnd_sensitive_boundaries_deny_runtime[case_grants]` | artifacts/sanitized/results.json |
| TC_FND_3B47B98B55F7 | security_authorization | passed | `tests/database/test_rls.py` / `test_fnd_sensitive_boundaries_deny_runtime[audit_events]` | artifacts/sanitized/results.json |
| TC_FND_430451EE1D5E | positive | passed | `tests/database/test_rls.py` / `test_fnd_runtime_cannot_write_or_elevate` | artifacts/sanitized/results.json |
| TC_FND_A47C3B67AF2C | security_authorization | passed | `tests/database/test_rls.py` / `test_fnd_non_owner_runtime_role` | artifacts/sanitized/results.json |
| TC_FND_00236ED24DA9 | positive | passed | `tests/database/test_rls.py` / `test_fnd_runtime_cannot_insert_handover` | artifacts/sanitized/results.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FND-06 — Case/outbox transaction atomicity

Validation: **passed**. Suite: database. Fixtures: FX-FOUNDATION.

Positive: Rollback removes both revision and outbox changes; no partial event escapes.

Negative: Invalid, missing or unavailable inputs/dependencies reject rather than granting access or claiming validation.

Security/authorization: Non-owner roles and forged/expired/missing authority cannot enable a sensitive operation; test artifacts contain only the synthetic shell.

Edge cases: Isolation, tenant/case mixing, replay, rollback, missing results and platform-specific launch failure are checked where applicable; unimplemented operational scenarios remain pending in the original baseline.

Expected: Rollback removes both revision and outbox changes; no partial event escapes.

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FND_837E6D3C20AD | edge | passed | `tests/database/test_rls.py` / `test_fnd_outbox_atomic_rollback` | artifacts/sanitized/results.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FND-07 — Disabled domain operations and sensitive routes

Validation: **passed**. Suite: security. Fixtures: FX-FOUNDATION.

Positive: All 32 future operations reject both anonymous and forged credentials without mutation or sensitive echo.

Negative: Invalid, missing or unavailable inputs/dependencies reject rather than granting access or claiming validation.

Security/authorization: Non-owner roles and forged/expired/missing authority cannot enable a sensitive operation; test artifacts contain only the synthetic shell.

Edge cases: Isolation, tenant/case mixing, replay, rollback, missing results and platform-specific launch failure are checked where applicable; unimplemented operational scenarios remain pending in the original baseline.

Expected: All 32 future operations reject both anonymous and forged credentials without mutation or sensitive echo.

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FND_EAEFCA7E8CF3 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_01]` | artifacts/sanitized/results.json |
| TC_FND_C4F623A90077 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_02]` | artifacts/sanitized/results.json |
| TC_FND_0B236446D62B | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_03]` | artifacts/sanitized/results.json |
| TC_FND_A20199F970E4 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_04]` | artifacts/sanitized/results.json |
| TC_FND_B5C1AF68793A | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_05]` | artifacts/sanitized/results.json |
| TC_FND_F202C61C63E4 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_06]` | artifacts/sanitized/results.json |
| TC_FND_16BDED2D6773 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_07]` | artifacts/sanitized/results.json |
| TC_FND_280C4D0F4586 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_08]` | artifacts/sanitized/results.json |
| TC_FND_33CDC849C2D7 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_09]` | artifacts/sanitized/results.json |
| TC_FND_7F68AF16400C | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_10]` | artifacts/sanitized/results.json |
| TC_FND_493E768EFD64 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_11]` | artifacts/sanitized/results.json |
| TC_FND_98A64877C6B3 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_12]` | artifacts/sanitized/results.json |
| TC_FND_C6D2BB3AE0B8 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_13]` | artifacts/sanitized/results.json |
| TC_FND_8A61432AFDB8 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_14]` | artifacts/sanitized/results.json |
| TC_FND_EBD7F91E400E | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_15]` | artifacts/sanitized/results.json |
| TC_FND_41EDAFB25798 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_16]` | artifacts/sanitized/results.json |
| TC_FND_CF2B85EDE3E2 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_17]` | artifacts/sanitized/results.json |
| TC_FND_C3F2E2779947 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_18]` | artifacts/sanitized/results.json |
| TC_FND_6D496F35E9BB | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_19]` | artifacts/sanitized/results.json |
| TC_FND_2FC88C6F88B9 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_20]` | artifacts/sanitized/results.json |
| TC_FND_0542F268A46F | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_21]` | artifacts/sanitized/results.json |
| TC_FND_A252ACE4CF65 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_22]` | artifacts/sanitized/results.json |
| TC_FND_E1A7689FD722 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_23]` | artifacts/sanitized/results.json |
| TC_FND_45DE90602E3F | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_24]` | artifacts/sanitized/results.json |
| TC_FND_2415094FC8D8 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_25]` | artifacts/sanitized/results.json |
| TC_FND_668660E110A7 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_26]` | artifacts/sanitized/results.json |
| TC_FND_8EA0044F49C6 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_27]` | artifacts/sanitized/results.json |
| TC_FND_3B713F95A4CD | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_28]` | artifacts/sanitized/results.json |
| TC_FND_4D4659EA57C4 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_29]` | artifacts/sanitized/results.json |
| TC_FND_E7CB6FA7DD7B | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_30]` | artifacts/sanitized/results.json |
| TC_FND_DA6D1D8A667F | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_31]` | artifacts/sanitized/results.json |
| TC_FND_DD37122ABBCF | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[anonymous-fnd_disabled_32]` | artifacts/sanitized/results.json |
| TC_FND_03753CDF9960 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_01]` | artifacts/sanitized/results.json |
| TC_FND_8C96FBC93787 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_02]` | artifacts/sanitized/results.json |
| TC_FND_5526EEA3FC32 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_03]` | artifacts/sanitized/results.json |
| TC_FND_98EF02880416 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_04]` | artifacts/sanitized/results.json |
| TC_FND_027CD4587E31 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_05]` | artifacts/sanitized/results.json |
| TC_FND_DF467CBDBDED | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_06]` | artifacts/sanitized/results.json |
| TC_FND_016DA9F35909 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_07]` | artifacts/sanitized/results.json |
| TC_FND_20E257024E71 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_08]` | artifacts/sanitized/results.json |
| TC_FND_DEF9F0A505C0 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_09]` | artifacts/sanitized/results.json |
| TC_FND_5A0B81B769BA | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_10]` | artifacts/sanitized/results.json |
| TC_FND_D552E748CF70 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_11]` | artifacts/sanitized/results.json |
| TC_FND_8F6766A10F89 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_12]` | artifacts/sanitized/results.json |
| TC_FND_5B7E00BBAB0D | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_13]` | artifacts/sanitized/results.json |
| TC_FND_79FFFEA6F5AD | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_14]` | artifacts/sanitized/results.json |
| TC_FND_75DAF64153C8 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_15]` | artifacts/sanitized/results.json |
| TC_FND_D171CA76AFCC | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_16]` | artifacts/sanitized/results.json |
| TC_FND_95F200710AEF | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_17]` | artifacts/sanitized/results.json |
| TC_FND_9D6E1781F2CA | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_18]` | artifacts/sanitized/results.json |
| TC_FND_5746212B687E | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_19]` | artifacts/sanitized/results.json |
| TC_FND_8F98B40014AD | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_20]` | artifacts/sanitized/results.json |
| TC_FND_DF41A0467D00 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_21]` | artifacts/sanitized/results.json |
| TC_FND_54BC34B85288 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_22]` | artifacts/sanitized/results.json |
| TC_FND_296CB6DABBEB | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_23]` | artifacts/sanitized/results.json |
| TC_FND_41B77BB62841 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_24]` | artifacts/sanitized/results.json |
| TC_FND_BD8676DE1002 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_25]` | artifacts/sanitized/results.json |
| TC_FND_688C6468EE68 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_26]` | artifacts/sanitized/results.json |
| TC_FND_CAD1DFEC313D | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_27]` | artifacts/sanitized/results.json |
| TC_FND_697021EB48FB | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_28]` | artifacts/sanitized/results.json |
| TC_FND_9E792DBE82C8 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_29]` | artifacts/sanitized/results.json |
| TC_FND_E4C718F351C5 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_30]` | artifacts/sanitized/results.json |
| TC_FND_19D65488056A | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_31]` | artifacts/sanitized/results.json |
| TC_FND_CD125E4F0155 | security_authorization | passed | `tests/security/test_disabled_operations.py` / `test_fnd_domain_operations_fail_closed[forged-fnd_disabled_32]` | artifacts/sanitized/results.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FND-08 — Arabic/English foundation browser shell

Validation: **passed**. Suite: browser. Fixtures: FX-FOUNDATION.

Positive: Real web/API/database render both locales without overflow, preserve HTML direction, support keyboard navigation, pass automated axe rules and expose no reporting inputs.

Negative: Invalid, missing or unavailable inputs/dependencies reject rather than granting access or claiming validation.

Security/authorization: Non-owner roles and forged/expired/missing authority cannot enable a sensitive operation; test artifacts contain only the synthetic shell.

Edge cases: Isolation, tenant/case mixing, replay, rollback, missing results and platform-specific launch failure are checked where applicable; unimplemented operational scenarios remain pending in the original baseline.

Expected: Real web/API/database render both locales without overflow, preserve HTML direction, support keyboard navigation, pass automated axe rules and expose no reporting inputs.

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FND_BROWSER_AR_READY | security_authorization | passed | `tests/browser/foundation.e2e.ts` / `TC_FND_BROWSER_AR_READY` | artifacts/sanitized/results.json |
| TC_FND_BROWSER_EN_READY | security_authorization | passed | `tests/browser/foundation.e2e.ts` / `TC_FND_BROWSER_EN_READY` | artifacts/sanitized/results.json |
| TC_FND_BROWSER_LANGUAGE_SWITCH | positive | passed | `tests/browser/foundation.e2e.ts` / `TC_FND_BROWSER_LANGUAGE_SWITCH` | artifacts/sanitized/results.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FND-09 — Required-result enforcement and artifact sanitization

Validation: **passed**. Suite: unit. Fixtures: FX-FOUNDATION.

Positive: Missing/duplicated/skipped/retried/stale/model-assisted results fail the gate; PNG metadata and path escapes cannot be published.

Negative: Invalid, missing or unavailable inputs/dependencies reject rather than granting access or claiming validation.

Security/authorization: Non-owner roles and forged/expired/missing authority cannot enable a sensitive operation; test artifacts contain only the synthetic shell.

Edge cases: Isolation, tenant/case mixing, replay, rollback, missing results and platform-specific launch failure are checked where applicable; unimplemented operational scenarios remain pending in the original baseline.

Expected: Missing/duplicated/skipped/retried/stale/model-assisted results fail the gate; PNG metadata and path escapes cannot be published.

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FND_E14CDAD4799B | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_gate_rejects_missing_python_result` | artifacts/sanitized/results.json |
| TC_FND_35DE5AE3C169 | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_gate_rejects_nonpassing_stage[failed-setup]` | artifacts/sanitized/results.json |
| TC_FND_19985F3A5ABC | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_gate_rejects_nonpassing_stage[failed-call]` | artifacts/sanitized/results.json |
| TC_FND_42DB6DF71A2E | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_gate_rejects_nonpassing_stage[failed-teardown]` | artifacts/sanitized/results.json |
| TC_FND_8A224FB90A8A | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_gate_rejects_nonpassing_stage[skipped-setup]` | artifacts/sanitized/results.json |
| TC_FND_8C26C9BA76D3 | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_gate_rejects_nonpassing_stage[skipped-call]` | artifacts/sanitized/results.json |
| TC_FND_C3C6DF51272A | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_gate_rejects_nonpassing_stage[skipped-teardown]` | artifacts/sanitized/results.json |
| TC_FND_42C7C5EAFF2F | positive | passed | `tests/unit/test_results_gate.py` / `test_fnd_gate_accepts_complete_validator_fixture` | artifacts/sanitized/results.json |
| TC_FND_A0235B395503 | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_gate_rejects_browser_defects[missing-target]` | artifacts/sanitized/results.json |
| TC_FND_EEC38BC6F231 | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_gate_rejects_browser_defects[duplicate-result]` | artifacts/sanitized/results.json |
| TC_FND_D8038BE1E399 | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_gate_rejects_browser_defects[retry]` | artifacts/sanitized/results.json |
| TC_FND_A78835433198 | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_gate_rejects_browser_defects[skip]` | artifacts/sanitized/results.json |
| TC_FND_46E6845A5760 | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_gate_rejects_browser_defects[cleanup]` | artifacts/sanitized/results.json |
| TC_FND_E94F55770C42 | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_gate_rejects_browser_defects[runner]` | artifacts/sanitized/results.json |
| TC_FND_E63AD2E17051 | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_gate_rejects_browser_defects[origin]` | artifacts/sanitized/results.json |
| TC_FND_B88E9C9F3E8B | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_gate_rejects_browser_defects[model]` | artifacts/sanitized/results.json |
| TC_FND_23C8AADFF302 | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_gate_rejects_browser_defects[stale]` | artifacts/sanitized/results.json |
| TC_FND_030C5D77CE47 | edge | passed | `tests/unit/test_results_gate.py` / `test_fnd_png_sanitizer_strips_metadata_canary` | artifacts/sanitized/results.json |
| TC_FND_06549A1CC8CE | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_png_sanitizer_rejects_invalid_input[not-a-png]` | artifacts/sanitized/results.json |
| TC_FND_927C70456B06 | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_png_sanitizer_rejects_invalid_input[\x89PNG\r\n\x1a\n]` | artifacts/sanitized/results.json |
| TC_FND_6CED6A3FD812 | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_png_sanitizer_rejects_invalid_input[\x89PNG\r\n\x1a\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00]` | artifacts/sanitized/results.json |
| TC_FND_0B76BC968DDE | negative | passed | `tests/unit/test_results_gate.py` / `test_fnd_artifact_path_rejects_escape_and_symlink` | artifacts/sanitized/results.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FND-10 — Locked local environment and production web build

Validation: **passed**. Suite: deployment. Fixtures: FX-FOUNDATION.

Positive: A clean exact npm install, locked Python container build, TypeScript check and production web build complete using the selected runtimes.

Negative: Invalid, missing or unavailable inputs/dependencies reject rather than granting access or claiming validation.

Security/authorization: Non-owner roles and forged/expired/missing authority cannot enable a sensitive operation; test artifacts contain only the synthetic shell.

Edge cases: Isolation, tenant/case mixing, replay, rollback, missing results and platform-specific launch failure are checked where applicable; unimplemented operational scenarios remain pending in the original baseline.

Expected: A clean exact npm install, locked Python container build, TypeScript check and production web build complete using the selected runtimes.

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FND_INSTALL | positive | passed | `package-lock.json` / `clean-lock-and-build` | docs/phase1a/ENVIRONMENT.md |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FND-11 — Closed event envelope and outbox metadata

Validation: **passed**. Suite: integration. Fixtures: FX-FOUNDATION.

Positive: Only opaque IDs/revisions/policy metadata form a schema-valid event; arbitrary child payloads and unknown event types are rejected.

Negative: Invalid, missing or unavailable inputs/dependencies reject rather than granting access or claiming validation.

Security/authorization: Non-owner roles and forged/expired/missing authority cannot enable a sensitive operation; test artifacts contain only the synthetic shell.

Edge cases: Isolation, tenant/case mixing, replay, rollback, missing results and platform-specific launch failure are checked where applicable; unimplemented operational scenarios remain pending in the original baseline.

Expected: Only opaque IDs/revisions/policy metadata form a schema-valid event; arbitrary child payloads and unknown event types are rejected.

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FND_9588D8472B6C | positive | passed | `tests/database/test_contract_hardening.py` / `test_fnd_outbox_reconstructs_closed_envelope` | artifacts/sanitized/results.json |
| TC_FND_66A7E8CCCD63 | negative | passed | `tests/integration/test_contracts.py` / `test_fnd_event_envelope_rejects_child_payload` | artifacts/sanitized/results.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FND-12 — Current dependency security audits

Validation: **passed**. Suite: security. Fixtures: FX-FOUNDATION.

Positive: The current application/test locks have no known npm or Python advisories in the recorded audit; historical research locks are excluded.

Negative: Invalid, missing or unavailable inputs/dependencies reject rather than granting access or claiming validation.

Security/authorization: Non-owner roles and forged/expired/missing authority cannot enable a sensitive operation; test artifacts contain only the synthetic shell.

Edge cases: Isolation, tenant/case mixing, replay, rollback, missing results and platform-specific launch failure are checked where applicable; unimplemented operational scenarios remain pending in the original baseline.

Expected: The current application/test locks have no known npm or Python advisories in the recorded audit; historical research locks are excluded.

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FND_AUDIT_NPM | positive | passed | `scripts/audit.py` / `npm current lock audit` | artifacts/sanitized/results.json |
| TC_FND_AUDIT_PYTHON | positive | passed | `scripts/audit.py` / `python current lock audit` | artifacts/sanitized/results.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FND-13 — CI policy and remote enforcement

Validation: **passed**. Suite: deployment. Fixtures: FX-FOUNDATION.

Positive: Pinned-action pull-request/full-regression workflow enforces required results and publishes only sanitized artifacts; remote run/protection must be independently verified.

Negative: Invalid, missing or unavailable inputs/dependencies reject rather than granting access or claiming validation.

Security/authorization: Non-owner roles and forged/expired/missing authority cannot enable a sensitive operation; test artifacts contain only the synthetic shell.

Edge cases: Isolation, tenant/case mixing, replay, rollback, missing results and platform-specific launch failure are checked where applicable; unimplemented operational scenarios remain pending in the original baseline.

Expected: Pinned-action pull-request/full-regression workflow enforces required results and publishes only sanitized artifacts; remote run/protection must be independently verified.

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FND_CI_CONFIG | positive | passed | `.github/workflows/phase1a.yml` / `immutable-pins-and-required-gate` | docs/phase1a/configuration-checks.json |
| TC_FND_CI_REMOTE_RUN | security_authorization | passed | `.github/workflows/phase1a.yml` / `REMOTE_RUN` | docs/phase1a/hosted-evidence.json |
| TC_FND_CI_BRANCH_PROTECTION | security_authorization | passed | `.github/workflows/phase1a.yml` / `BRANCH_PROTECTION` | docs/phase1a/hosted-evidence.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## FND-14 — Synthetic backup and restore validation

Validation: **passed**. Suite: deployment. Fixtures: FX-FOUNDATION.

Positive: Restored schema retains both migration checksums, pgvector and 41 forced-RLS relations; runtime reads deny without context. Operational erasure remains pending.

Negative: Invalid, missing or unavailable inputs/dependencies reject rather than granting access or claiming validation.

Security/authorization: Non-owner roles and forged/expired/missing authority cannot enable a sensitive operation; test artifacts contain only the synthetic shell.

Edge cases: Isolation, tenant/case mixing, replay, rollback, missing results and platform-specific launch failure are checked where applicable; unimplemented operational scenarios remain pending in the original baseline.

Expected: Restored schema retains both migration checksums, pgvector and 41 forced-RLS relations; runtime reads deny without context. Operational erasure remains pending.

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FND_RESTORE | positive | passed | `scripts/recovery.py` / `synthetic-schema-and-rls-restore` | artifacts/sanitized/results.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.

## DB-38 — idempotency_records

Validation: **passed**. Suite: database. Fixtures: FX-FOUNDATION.

Positive: Tenant/principal/operation/key scope is unique, hashes have fixed length, response storage is ciphertext, and runtime access stays denied until reviewed Phase 1C policies.

Negative: Invalid, missing or unavailable inputs/dependencies reject rather than granting access or claiming validation.

Security/authorization: Non-owner roles and forged/expired/missing authority cannot enable a sensitive operation; test artifacts contain only the synthetic shell.

Edge cases: Isolation, tenant/case mixing, replay, rollback, missing results and platform-specific launch failure are checked where applicable; unimplemented operational scenarios remain pending in the original baseline.

Expected: Tenant/principal/operation/key scope is unique, hashes have fixed length, response storage is ciphertext, and runtime access stays denied until reviewed Phase 1C policies.

| Test case | Kind | Status | Executable / selector | Evidence |
|---|---|---|---|---|
| TC_FND_5774B9899A05 | security_authorization | passed | `tests/database/test_contract_hardening.py` / `test_fnd_idempotency_scoped_uniqueness_and_default_deny` | artifacts/sanitized/results.json |
| TC_FND_1B9F10FA62CB | security_authorization | passed | `tests/database/test_rls.py` / `test_fnd_sensitive_boundaries_deny_runtime[idempotency_records]` | artifacts/sanitized/results.json |

Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.


Phase 2D final review adds explicit exact selectors and records broader unexecuted variants in `phase2d/traceability.json` (`remaining_validation`). A passing executable inventory is not a claim that every clause of every broad scenario has been exercised.
