# Find Our Child — test traceability matrix

**Every application test below is pending and unimplemented. No execution evidence exists.** A planned file/selector/command is an implementation target, not an existing executable test. This matrix makes future executables traceable without claiming they run before the application exists.

Machine-readable source: [test-matrix.json](testing/test-matrix.json). Regenerate with `python3 tools/build_test_matrix.py`. Phase 0 checks validate inventory/coverage/status consistency only.

Scope: all 14 numbered functional requirements, all 32 API operations in API_CONTRACTS, every schema relation security boundary (composite relation rows explicitly cover both named tables), all 15 event contracts, additional worker/timer jobs, transaction races, 11 requested safeguarding workflows, 19 original threats and the independent testing suites. New requirements/routes/jobs/tables must extend this inventory in the same PR.

Status vocabulary: pending = not implemented; implemented-not-run = executable exists without accepted evidence; blocked/failed/skipped/interrupted/flaky = not accepted; passed = exact executable/target/fixture result accepted with artifact ID. Current status is pending for every feature and test case.

Each ID has four separately planned cases: `_P` positive, `_N` negative, `_S` security/authorization, `_E` edge. SAF IDs additionally have `_BROWSER` and `_STATE` companion cases. Future-phase SAF capabilities also have `_DISABLED_P1` denial cases required from Phase 1; full positive cases stay pending until their required_from_phase. This explicit applicability is not a runtime skip. Expected success for a browser case additionally requires actual API/database side-effect oracles, not merely a visible success toast. UI selectors are authored against live synthetic services in Phase 1. API exact status/DTOs beyond the existing outline are contract-completion gates, not invented here.

Python selectors below target planned pytest suites; rendered components target Vitest. Browser/accessibility selectors target TesterArmy/e2e tests; Playwright supplies its engine only. Frameworks/versions for other future suites require their own release locks before implementation. No file is generated under application test directories by this tool.

Evidence for every future accepted result: source/build/contract/lock/model versions, test ID, target, fixture hash, timestamps, exit, status/counts, sanitized artifact hashes/location, migration/SQL oracles where relevant and reviewer. No mandatory skip or absent test may count as passed. Critical safeguarding scenarios run as browser + API/DB/worker checks; companion layers are specified in [security catalog](SECURITY_TEST_CATALOG.md).

## Synthetic and restricted fixture catalog

- **FX-BASE:** Synthetic organizations A/B, unrelated cases, named requester/reviewer/authority/auditor/operator, same-role different principals, explicit grants; no real identities.
- **FX-UNCERTAIN:** Original Arabic/English spellings, Arabic digits, NULL/approximate/disputed intervals, no-photo reports, impossible chronology and multiple revisions.
- **FX-MEDIA:** Generated non-child drawings and consent-free geometric test images, EXIF/GPS canaries, multiple face-region adapter outputs, malformed/MIME/polyglot/decompression fixtures; no real child photos.
- **FX-IDP:** Local test Keycloak realm, synthetic users, fresh/stale MFA, wrong issuer/audience, expired/revoked sessions and pooled connection contexts; disposable credentials.
- **FX-MATCH:** Synthetic case/score/vector manifests, incompatible spaces, deliberate wrong leads, no-mate cases and human rejection; synthetic vectors cannot demonstrate recognition accuracy.
- **FX-APPROVAL:** Synthetic claimant, missing/found pair, independently verified-authority fixture, distinct actors, same actor with two roles, revision/expiry/conflict variants.
- **FX-EVENT:** Closed event envelopes with duplicate/reordered IDs, lease expiry, crash checkpoints, tombstone generations, provider stub receipts and deterministic clock.
- **FX-PURGE:** Synthetic original/derivative/object versions, vector partitions, grants, exports, cache markers, queues and backup copies; scoped legal-hold variants.
- **FX-DB:** Fresh/previous synthetic schema snapshots, actual non-owner DB roles, deliberate cross-org FK links, empty/missing tenant contexts, rollback/fault barriers.
- **FX-FAILURE:** Isolated scanner/IdP/KMS/storage/audit/provider outages, latency/network partitions and process kills; no production failure injection.
- **FX-A11Y:** Approved Arabic/English synthetic UI strings, mixed-direction IDs, 320/360/390/1280px viewports, keyboard/screen-reader scripts, 200% zoom/reduced motion.
- **FX-EVAL:** Separately authorized subject-disjoint evaluation manifest with independent identity ground truth and rights record, restricted data store; never external testing models.
- **FX-DEPLOY:** Immutable candidate/previous release digests, synthetic staging topology, migrations/WAL/object backups, independent deletion ledger and rollback approval fixture.

## Functional

### FR-01 — Separate missing/found forms in Arabic RTL and English LTR; switch preserves entered values

- **Source / phase / suite:** PRODUCT_REQUIREMENTS.md#FR-01; phase 1; browser.
- **Positive:** Switch locale mid-form and submit each registry flow.
- **Negative:** Invalid locale or script payload is escaped.
- **Security and authorization:** Reporter sees no staff fields during locale switch.
- **Edge cases:** Arabic digits, long labels, interrupted connection and draft recovery.
- **Fixtures:** FX-BASE, FX-UNCERTAIN, FX-A11Y.
- **Expected outcomes:** Correct registry, preserved original values, RTL/LTR semantics, one neutral receipt.
- **Planned test IDs:** TC_FR_01_P, TC_FR_01_N, TC_FR_01_S, TC_FR_01_E.
- **Planned executable targets:** `tests/browser/fr_01.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### FR-02 — Submit with uncertain/unknown child attributes and without a photo; staff receive a triage task

- **Source / phase / suite:** PRODUCT_REQUIREMENTS.md#FR-02; phase 1; browser.
- **Positive:** Submit unknown name/age and no photo.
- **Negative:** Invalid ordered interval rejected without inventing values.
- **Security and authorization:** Unverified source cannot mark claims verified.
- **Edge cases:** Unknown vs zero age, estimated capture dates, individual finder.
- **Fixtures:** FX-UNCERTAIN.
- **Expected outcomes:** Claims retain uncertainty and a restricted triage task is created.
- **Planned test IDs:** TC_FR_02_P, TC_FR_02_N, TC_FR_02_S, TC_FR_02_E.
- **Planned executable targets:** `tests/browser/fr_02.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### FR-03 — Store original and submitted claims immutably by revision; verified facts cite evidence and verifier

- **Source / phase / suite:** PRODUCT_REQUIREMENTS.md#FR-03; phase 1; browser.
- **Positive:** Add evidence-backed verified assertion preserving original claim.
- **Negative:** Missing verifier/evidence cannot produce verified fact.
- **Security and authorization:** Unassigned user cannot change assertion provenance.
- **Edge cases:** Concurrent contradictory revisions and disputed evidence.
- **Fixtures:** FX-BASE, FX-UNCERTAIN.
- **Expected outcomes:** Immutable claim history plus independently attributed verification.
- **Planned test IDs:** TC_FR_03_P, TC_FR_03_N, TC_FR_03_S, TC_FR_03_E.
- **Planned executable targets:** `tests/browser/fr_03.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### FR-04 — Reporter receipt authorizes only own-submission updates after verification, never staff data

- **Source / phase / suite:** PRODUCT_REQUIREMENTS.md#FR-04; phase 1; browser.
- **Positive:** Verified reporter adds own supplement and views redacted receipt.
- **Negative:** Guess or replay receipt/code fails without revealing existence.
- **Security and authorization:** Own-report capability cannot read staff notes/counterpart case/custody.
- **Edge cases:** Revocation/expiry during supplement and safe recovery.
- **Fixtures:** FX-BASE, FX-IDP.
- **Expected outcomes:** Only own submitted facts accessible, no found-child disclosure.
- **Planned test IDs:** TC_FR_04_P, TC_FR_04_N, TC_FR_04_S, TC_FR_04_E.
- **Planned executable targets:** `tests/browser/fr_04.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### FR-05 — Multiple historical images retain capture-age uncertainty and explicit subject selection

- **Source / phase / suite:** PRODUCT_REQUIREMENTS.md#FR-05; phase 1; browser.
- **Positive:** Select correct subject among multiple photo regions and record capture interval.
- **Negative:** No-face/ambiguous subject remains held.
- **Security and authorization:** Unauthorized user cannot select another case photo.
- **Edge cases:** Historical photos, low quality and multiple children.
- **Fixtures:** FX-MEDIA, FX-UNCERTAIN.
- **Expected outcomes:** Approved subject selection and original photo provenance; no silent largest-face choice.
- **Planned test IDs:** TC_FR_05_P, TC_FR_05_N, TC_FR_05_S, TC_FR_05_E.
- **Planned executable targets:** `tests/browser/fr_05.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### FR-06 — Moderation, assignment, case grants and every lifecycle transition are audited

- **Source / phase / suite:** PRODUCT_REQUIREMENTS.md#FR-06; phase 1; browser.
- **Positive:** Moderate, assign and transition with valid purpose/revision.
- **Negative:** Illegal lifecycle jump and stale revision rejected.
- **Security and authorization:** Org admin without case grant cannot assign sensitive content to self.
- **Edge cases:** Audit sink outage and concurrent assignment/revocation.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Authorized transition, assignment, audit and outbox commit atomically.
- **Planned test IDs:** TC_FR_06_P, TC_FR_06_N, TC_FR_06_S, TC_FR_06_E.
- **Planned executable targets:** `tests/browser/fr_06.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### FR-07 — Duplicate cases can be linked without destructive merging or loss of provenance

- **Source / phase / suite:** PRODUCT_REQUIREMENTS.md#FR-07; phase 1; browser.
- **Positive:** Confirm/reverse duplicate link with both case grants.
- **Negative:** Wrong pair or unreviewed merge request rejected.
- **Security and authorization:** Cross-org link cannot disclose records.
- **Edge cases:** New evidence after duplicate rejection and repeated requests.
- **Fixtures:** FX-BASE, FX-UNCERTAIN.
- **Expected outcomes:** Reversible link with full independent provenance, no destructive merge.
- **Planned test IDs:** TC_FR_07_P, TC_FR_07_N, TC_FR_07_S, TC_FR_07_E.
- **Planned executable targets:** `tests/browser/fr_07.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### FR-08 — Candidate reviews can be rejected, held or escalated with reason and independent review

- **Source / phase / suite:** PRODUCT_REQUIREMENTS.md#FR-08; phase 2; browser.
- **Positive:** Review wrong lead and reject/hold/escalate with reason.
- **Negative:** Model score alone cannot resolve case.
- **Security and authorization:** Unassigned reviewer cannot access lead or approve own request.
- **Edge cases:** New evidence after rejection and competing reviews.
- **Fixtures:** FX-MATCH, FX-APPROVAL.
- **Expected outcomes:** Lead decision retained, no automatic identity/custody action.
- **Planned test IDs:** TC_FR_08_P, TC_FR_08_N, TC_FR_08_S, TC_FR_08_E.
- **Planned executable targets:** `tests/browser/fr_08.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### FR-09 — Notifications target authorized staff and carry only a neutral task link

- **Source / phase / suite:** PRODUCT_REQUIREMENTS.md#FR-09; phase 1; browser.
- **Positive:** Authorized staff receives neutral task notification once.
- **Negative:** Invalid destination or provider error retried/dead-lettered.
- **Security and authorization:** Revoked recipient and claimant receive no identifying message.
- **Edge cases:** Duplicate event and grant revoked at send boundary.
- **Fixtures:** FX-EVENT, FX-BASE.
- **Expected outcomes:** Neutral payload only, current permission rechecked and delivery audit retained.
- **Planned test IDs:** TC_FR_09_P, TC_FR_09_N, TC_FR_09_S, TC_FR_09_E.
- **Planned executable targets:** `tests/browser/fr_09.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### FR-10 — Identifying disclosure and safe reunion require separate, scoped approvals and authority evidence

- **Source / phase / suite:** PRODUCT_REQUIREMENTS.md#FR-10; phase 4; browser.
- **Positive:** Distinct safeguarding/authority actors approve scoped disclosure then supervised reunion.
- **Negative:** Missing authority, fraud concern or changed evidence holds release.
- **Security and authorization:** Requester/self-approval/admin bypass denied.
- **Edge cases:** Approval expiry/revocation races and actor with two roles.
- **Fixtures:** FX-APPROVAL, FX-FAILURE.
- **Expected outcomes:** No identifying disclosure or custody transfer until every independent gate holds.
- **Planned test IDs:** TC_FR_10_P, TC_FR_10_N, TC_FR_10_S, TC_FR_10_E.
- **Planned executable targets:** `tests/browser/fr_10.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### FR-11 — Revocation and deletion cancel stale media links, jobs, indexes and queued notifications

- **Source / phase / suite:** PRODUCT_REQUIREMENTS.md#FR-11; phase 1; browser.
- **Positive:** Approve deletion and verify every store/index/queue is purged.
- **Negative:** Active legal hold prevents only scoped erasure.
- **Security and authorization:** Revoked capability cannot serve image during purge.
- **Edge cases:** Delete during embedding insertion and restore from old backup.
- **Fixtures:** FX-PURGE, FX-EVENT.
- **Expected outcomes:** Tombstone first, all permitted purge acknowledgments recorded, no resurrection.
- **Planned test IDs:** TC_FR_11_P, TC_FR_11_N, TC_FR_11_S, TC_FR_11_E.
- **Planned executable targets:** `tests/browser/fr_11.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### FR-12 — No route exposes private child records across tenants without an explicit federation agreement and grant

- **Source / phase / suite:** PRODUCT_REQUIREMENTS.md#FR-12; phase 1; browser.
- **Positive:** Same-org authorized search and approved bilateral federation workflow.
- **Negative:** Unilateral/expired federation agreement yields no results.
- **Security and authorization:** Other organization sees no names/media/counts/vectors/custody.
- **Edge cases:** Opt-out during matching and disclosure expiry.
- **Fixtures:** FX-BASE, FX-MATCH, FX-APPROVAL.
- **Expected outcomes:** Explicit scope and bilateral approvals enforced; federation off by default.
- **Planned test IDs:** TC_FR_12_P, TC_FR_12_N, TC_FR_12_S, TC_FR_12_E.
- **Planned executable targets:** `tests/browser/fr_12.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### FR-13 — Evidence addition, investigation notes, abuse reports and event history retain authorship/version

- **Source / phase / suite:** PRODUCT_REQUIREMENTS.md#FR-13; phase 1; browser.
- **Positive:** Append supplement/note/abuse report and inspect permitted history.
- **Negative:** Tampered evidence reference or history edit rejected.
- **Security and authorization:** Abuse report hidden from implicated user; audit reader sees minimized data.
- **Edge cases:** Conflicting notes, unverified evidence and pagination.
- **Fixtures:** FX-BASE, FX-UNCERTAIN.
- **Expected outcomes:** Authorship/revisions retained; privileged notes never in reporter DTO.
- **Planned test IDs:** TC_FR_13_P, TC_FR_13_N, TC_FR_13_S, TC_FR_13_E.
- **Planned executable targets:** `tests/browser/fr_13.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### FR-14 — Screen-reader flow, keyboard use and narrow-screen RTL are verified before pilot

- **Source / phase / suite:** PRODUCT_REQUIREMENTS.md#FR-14; phase 1; browser.
- **Positive:** Complete workflows using keyboard and screen reader in both languages.
- **Negative:** Hidden error or overflowing action fails acceptance.
- **Security and authorization:** Disabled controls do not replace backend authorization.
- **Edge cases:** All target widths, mixed bidi text, focus restoration, zoom/reduced motion.
- **Fixtures:** FX-A11Y.
- **Expected outcomes:** Accessible labels/order/status/errors and responsive layout verified.
- **Planned test IDs:** TC_FR_14_P, TC_FR_14_N, TC_FR_14_S, TC_FR_14_E.
- **Planned executable targets:** `tests/browser/fr_14.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**


## Api Operation

### API-001 — POST /v1/public/reports/missing

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Submit a missing report with uncertain data.
- **Negative:** Reject invalid interval/oversized payload.
- **Security and authorization:** Bound intake challenge, rate limit and idempotency; no search.
- **Edge cases:** Retry identical key and changed body.
- **Fixtures:** FX-BASE, FX-UNCERTAIN.
- **Expected outcomes:** 202 neutral receipt, attributed missing claims and triage event.
- **Planned test IDs:** TC_API_001_P, TC_API_001_N, TC_API_001_S, TC_API_001_E.
- **Planned executable targets:** `tests/api/test_api_001.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-002 — POST /v1/public/reports/found

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Submit individual/organization found report safely.
- **Negative:** Reject malformed welfare/discovery inputs.
- **Security and authorization:** No shelter or identity disclosed to claimant.
- **Edge cases:** Unknown name, no photo and finder without organization.
- **Fixtures:** FX-BASE, FX-UNCERTAIN.
- **Expected outcomes:** 202 found intake receipt; restricted custody follow-up.
- **Planned test IDs:** TC_API_002_P, TC_API_002_N, TC_API_002_S, TC_API_002_E.
- **Planned executable targets:** `tests/api/test_api_002.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-003 — POST /v1/public/access-requests

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Request recovery through verified safe channel.
- **Negative:** Malformed contact handled without existence leak.
- **Security and authorization:** Known and unknown contacts return indistinguishable neutral 202.
- **Edge cases:** Flood/shared IP and expired code.
- **Fixtures:** FX-IDP.
- **Expected outcomes:** No case existence revealed; attempts bounded.
- **Planned test IDs:** TC_API_003_P, TC_API_003_N, TC_API_003_S, TC_API_003_E.
- **Planned executable targets:** `tests/api/test_api_003.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-004 — POST /v1/public/access-exchanges

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Exchange valid one-time code for own submission session.
- **Negative:** Invalid/reused code denied.
- **Security and authorization:** Cannot bind code to another receipt or privilege.
- **Edge cases:** Concurrent redemption and expiry boundary.
- **Fixtures:** FX-IDP.
- **Expected outcomes:** Single use, submission-scoped access only.
- **Planned test IDs:** TC_API_004_P, TC_API_004_N, TC_API_004_S, TC_API_004_E.
- **Planned executable targets:** `tests/api/test_api_004.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-005 — GET /v1/reporter/submission

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Read own submission.
- **Negative:** Unknown/deleted receipt denied.
- **Security and authorization:** No counterpart, staff notes, exact custody or vectors.
- **Edge cases:** Expired/revoked reporter session.
- **Fixtures:** FX-BASE, FX-IDP.
- **Expected outcomes:** Redacted own claims only.
- **Planned test IDs:** TC_API_005_P, TC_API_005_N, TC_API_005_S, TC_API_005_E.
- **Planned executable targets:** `tests/api/test_api_005.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-006 — POST /v1/reporter/supplements

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Append new reported information.
- **Negative:** Bad evidence reference denied.
- **Security and authorization:** Cannot write verified facts or another case.
- **Edge cases:** Duplicate supplement and stale revision.
- **Fixtures:** FX-UNCERTAIN.
- **Expected outcomes:** Attributed immutable supplement; no verified fact overwrite.
- **Planned test IDs:** TC_API_006_P, TC_API_006_N, TC_API_006_S, TC_API_006_E.
- **Planned executable targets:** `tests/api/test_api_006.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-007 — POST /v1/reporter/contact

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Send safe NGO relay message.
- **Negative:** Malformed/oversized/XSS payload rejected or escaped.
- **Security and authorization:** No shelter/staff private contacts returned.
- **Edge cases:** Retry/provider outage and safe-channel changes.
- **Fixtures:** FX-BASE, FX-EVENT.
- **Expected outcomes:** 202 neutral relay acknowledgment with no private recipients.
- **Planned test IDs:** TC_API_007_P, TC_API_007_N, TC_API_007_S, TC_API_007_E.
- **Planned executable targets:** `tests/api/test_api_007.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-008 — POST /v1/public/abuse-reports

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Submit safeguarding concern.
- **Negative:** Malformed reference gets neutral handling.
- **Security and authorization:** Implicated staff/claimant cannot read allegation.
- **Edge cases:** Anonymous/incomplete concern and duplicate attempts.
- **Fixtures:** FX-BASE.
- **Expected outcomes:** Restricted abuse queue without lookup response.
- **Planned test IDs:** TC_API_008_P, TC_API_008_N, TC_API_008_S, TC_API_008_E.
- **Planned executable targets:** `tests/api/test_api_008.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-009 — GET /v1/public/safety

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Read approved ar/en safety text.
- **Negative:** Unknown locale follows defined fallback.
- **Security and authorization:** No case data in public/cacheable response.
- **Edge cases:** Stale guidance version and accessibility alternative.
- **Fixtures:** FX-A11Y.
- **Expected outcomes:** Public approved locale/version text only.
- **Planned test IDs:** TC_API_009_P, TC_API_009_N, TC_API_009_S, TC_API_009_E.
- **Planned executable targets:** `tests/api/test_api_009.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-010 — POST /v1/reporter/upload-intents

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Create bounded quarantine upload intent.
- **Negative:** Disallowed type/size/quota rejected.
- **Security and authorization:** Capability bound to exact case/key and no public ACL.
- **Edge cases:** Intent expiry/orphan upload and replay.
- **Fixtures:** FX-MEDIA.
- **Expected outcomes:** Expiring restricted upload permission.
- **Planned test IDs:** TC_API_010_P, TC_API_010_N, TC_API_010_S, TC_API_010_E.
- **Planned executable targets:** `tests/api/test_api_010.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-011 — POST /v1/reporter/upload-intents/{id}/complete

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Finalize immutable uploaded version/checksum.
- **Negative:** Mismatch/missing object denied.
- **Security and authorization:** Cannot retarget case, key or mutable object version.
- **Edge cases:** Duplicate completion, scan outage and deletion race.
- **Fixtures:** FX-MEDIA, FX-EVENT.
- **Expected outcomes:** 202 scan job; image not served before acceptance.
- **Planned test IDs:** TC_API_011_P, TC_API_011_N, TC_API_011_S, TC_API_011_E.
- **Planned executable targets:** `tests/api/test_api_011.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-012 — GET /v1/staff/cases

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** List granted cases using cursor.
- **Negative:** Bad cursor/filter rejected.
- **Security and authorization:** No inaccessible counts or cross-org rows.
- **Edge cases:** Grant revoke between pages and empty scope.
- **Fixtures:** FX-BASE, FX-DB.
- **Expected outcomes:** Only permitted case summaries and pagination.
- **Planned test IDs:** TC_API_012_P, TC_API_012_N, TC_API_012_S, TC_API_012_E.
- **Planned executable targets:** `tests/api/test_api_012.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-013 — GET /v1/staff/cases/{id}

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Read assigned case with ETag.
- **Negative:** Missing/deleted case returns neutral inaccessible response.
- **Security and authorization:** No grant, wrong org and restricted custody denied.
- **Edge cases:** Membership expiry during pooled transaction.
- **Fixtures:** FX-BASE, FX-DB.
- **Expected outcomes:** Authorized DTO plus revision; no generic database serialization.
- **Planned test IDs:** TC_API_013_P, TC_API_013_N, TC_API_013_S, TC_API_013_E.
- **Planned executable targets:** `tests/api/test_api_013.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-014 — POST /v1/staff/cases/{id}/transitions

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Perform legal case transition.
- **Negative:** Illegal jump/missing evidence rejected.
- **Security and authorization:** No automatic score-triggered resolution or admin bypass.
- **Edge cases:** If-Match stale and concurrent transition.
- **Fixtures:** FX-APPROVAL, FX-DB.
- **Expected outcomes:** Only guarded new state and atomic audit/outbox.
- **Planned test IDs:** TC_API_014_P, TC_API_014_N, TC_API_014_S, TC_API_014_E.
- **Planned executable targets:** `tests/api/test_api_014.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-015 — POST /v1/staff/cases/{id}/assignments

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Assign case/team and grant appropriately.
- **Negative:** Invalid/suspended member rejected.
- **Security and authorization:** Supervisor scope and least privilege enforced.
- **Edge cases:** Self-assignment privilege escalation and concurrent revocation.
- **Fixtures:** FX-BASE, FX-IDP.
- **Expected outcomes:** Audited authorized assignment.
- **Planned test IDs:** TC_API_015_P, TC_API_015_N, TC_API_015_S, TC_API_015_E.
- **Planned executable targets:** `tests/api/test_api_015.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-016 — POST /v1/staff/cases/{id}/assertions

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Record claimed or evidence-verified assertion.
- **Negative:** Missing provenance/invalid interval denied.
- **Security and authorization:** Verification requires reviewer and evidence permissions.
- **Edge cases:** Conflicting revisions/disputed source.
- **Fixtures:** FX-UNCERTAIN.
- **Expected outcomes:** Immutable assertion; original remains preserved.
- **Planned test IDs:** TC_API_016_P, TC_API_016_N, TC_API_016_S, TC_API_016_E.
- **Planned executable targets:** `tests/api/test_api_016.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-017 — POST /v1/staff/photos/{id}/subject-selection

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Approve selected face region.
- **Negative:** Unknown region/ambiguous face held.
- **Security and authorization:** Only authorized case media reviewer selects.
- **Edge cases:** Two children, zero faces, stale detector revision.
- **Fixtures:** FX-MEDIA.
- **Expected outcomes:** Explicit subject and source revision recorded.
- **Planned test IDs:** TC_API_017_P, TC_API_017_N, TC_API_017_S, TC_API_017_E.
- **Planned executable targets:** `tests/api/test_api_017.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-018 — GET /v1/staff/media/{id}/content

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Stream permitted sanitized image.
- **Negative:** Unsafe/quarantined/deleted object denied.
- **Security and authorization:** Other org/expired/revoked token/original privilege denied.
- **Edge cases:** Range/cache request and revoke during streaming.
- **Fixtures:** FX-MEDIA, FX-IDP.
- **Expected outcomes:** Authorized content with no-store/no-referrer, no GPS metadata leak.
- **Planned test IDs:** TC_API_018_P, TC_API_018_N, TC_API_018_S, TC_API_018_E.
- **Planned executable targets:** `tests/api/test_api_018.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-019 — POST /v1/staff/cases/{id}/matching-runs

- **Source / phase / suite:** API_CONTRACTS.md; phase 2; api.
- **Positive:** Queue matching with approved manifest/purpose.
- **Negative:** Uncleared model/missing subject denied.
- **Security and authorization:** No public biometric route or cross-org search grant.
- **Edge cases:** No photos, incompatible space and deleted revision.
- **Fixtures:** FX-MATCH.
- **Expected outcomes:** 202 internal scoped job; no raw vectors returned.
- **Planned test IDs:** TC_API_019_P, TC_API_019_N, TC_API_019_S, TC_API_019_E.
- **Planned executable targets:** `tests/api/test_api_019.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-020 — GET /v1/staff/cases/{id}/leads

- **Source / phase / suite:** API_CONTRACTS.md; phase 2; api.
- **Positive:** Read authorized case leads with reasons.
- **Negative:** Unknown lead/run denied.
- **Security and authorization:** Require both case scopes and federation disclosure policy.
- **Edge cases:** Rejected/stale lead and missing metadata.
- **Fixtures:** FX-MATCH, FX-BASE.
- **Expected outcomes:** Permitted candidate DTO and uncertainty; no identity probability.
- **Planned test IDs:** TC_API_020_P, TC_API_020_N, TC_API_020_S, TC_API_020_E.
- **Planned executable targets:** `tests/api/test_api_020.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-021 — POST /v1/staff/leads/{id}/reviews

- **Source / phase / suite:** API_CONTRACTS.md; phase 2; api.
- **Positive:** Hold/reject/escalate lead with evidence.
- **Negative:** No rationale/invalid outcome denied.
- **Security and authorization:** Assigned independent reviewer scope enforced.
- **Edge cases:** Stale review and new evidence after rejection.
- **Fixtures:** FX-MATCH, FX-APPROVAL.
- **Expected outcomes:** Immutable review, no automatic confirmation.
- **Planned test IDs:** TC_API_021_P, TC_API_021_N, TC_API_021_S, TC_API_021_E.
- **Planned executable targets:** `tests/api/test_api_021.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-022 — POST /v1/staff/cases/{id}/notes

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Append investigation note.
- **Negative:** Oversized/unsafe text handled.
- **Security and authorization:** Reporter/other org cannot read or modify notes.
- **Edge cases:** Concurrent versions and malicious Arabic text.
- **Fixtures:** FX-BASE.
- **Expected outcomes:** Attributed restricted revision.
- **Planned test IDs:** TC_API_022_P, TC_API_022_N, TC_API_022_S, TC_API_022_E.
- **Planned executable targets:** `tests/api/test_api_022.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-023 — POST /v1/staff/duplicate-links

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Create/confirm reversible duplicate link.
- **Negative:** Same-case/invalid pair rejected.
- **Security and authorization:** Both grants and confirmation role required.
- **Edge cases:** Repeated link/reversal/concurrent update.
- **Fixtures:** FX-BASE.
- **Expected outcomes:** Reversible reviewed link with independent reports intact.
- **Planned test IDs:** TC_API_023_P, TC_API_023_N, TC_API_023_S, TC_API_023_E.
- **Planned executable targets:** `tests/api/test_api_023.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-024 — POST /v1/staff/disclosure-requests

- **Source / phase / suite:** API_CONTRACTS.md; phase 4; api.
- **Positive:** Request recipient/field-scoped disclosure.
- **Negative:** Missing purpose/mask/expiry denied.
- **Security and authorization:** Request grants no access; recipient identity verified independently.
- **Edge cases:** Expired agreement and snapshot changes.
- **Fixtures:** FX-APPROVAL.
- **Expected outcomes:** Pending restricted request only.
- **Planned test IDs:** TC_API_024_P, TC_API_024_N, TC_API_024_S, TC_API_024_E.
- **Planned executable targets:** `tests/api/test_api_024.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-025 — POST /v1/staff/disclosure-requests/{id}/approvals

- **Source / phase / suite:** API_CONTRACTS.md; phase 4; api.
- **Positive:** Independent bilateral disclosure approval.
- **Negative:** Missing side/authority/evidence holds disclosure.
- **Security and authorization:** Self-approval or same principal in two roles denied.
- **Edge cases:** Expiry/revocation/snapshot race.
- **Fixtures:** FX-APPROVAL.
- **Expected outcomes:** Expiring field mask only after all required approvals.
- **Planned test IDs:** TC_API_025_P, TC_API_025_N, TC_API_025_S, TC_API_025_E.
- **Planned executable targets:** `tests/api/test_api_025.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-026 — POST /v1/staff/reunification-plans

- **Source / phase / suite:** API_CONTRACTS.md; phase 4; api.
- **Positive:** Propose safe reunion after identity review.
- **Negative:** Unconfirmed identity/fraud concern prevents readiness.
- **Security and authorization:** Claimant cannot create or approve own handover.
- **Edge cases:** Disputed custody and child objection.
- **Fixtures:** FX-APPROVAL.
- **Expected outcomes:** Pending safeguarded plan, not release.
- **Planned test IDs:** TC_API_026_P, TC_API_026_N, TC_API_026_S, TC_API_026_E.
- **Planned executable targets:** `tests/api/test_api_026.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-027 — POST /v1/staff/reunification-plans/{id}/approvals

- **Source / phase / suite:** API_CONTRACTS.md; phase 4; api.
- **Positive:** Record distinct safeguarding and authority decisions.
- **Negative:** Missing/stale verification blocks.
- **Security and authorization:** Two-person identities and recent MFA enforced.
- **Edge cases:** Approver disabled or evidence revised after signing.
- **Fixtures:** FX-APPROVAL, FX-IDP.
- **Expected outcomes:** Scope/snapshot-bound approval only.
- **Planned test IDs:** TC_API_027_P, TC_API_027_N, TC_API_027_S, TC_API_027_E.
- **Planned executable targets:** `tests/api/test_api_027.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-028 — POST /v1/staff/reunification-plans/{id}/handover

- **Source / phase / suite:** API_CONTRACTS.md; phase 4; api.
- **Positive:** Record supervised authorized handover.
- **Negative:** Incomplete/expired approvals deny child release.
- **Security and authorization:** No admin/worker/claimant bypass or duplicate transfer.
- **Edge cases:** Concurrent replay/revocation and witness failure.
- **Fixtures:** FX-APPROVAL, FX-EVENT.
- **Expected outcomes:** Only complete independent gates permit witnessed transition.
- **Planned test IDs:** TC_API_028_P, TC_API_028_N, TC_API_028_S, TC_API_028_E.
- **Planned executable targets:** `tests/api/test_api_028.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-029 — POST /v1/staff/cases/{id}/deletion-requests

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Request authorized erasure.
- **Negative:** Legal hold scoped/reviewed.
- **Security and authorization:** Request itself cannot reveal child existence or bypass privacy authority.
- **Edge cases:** Purge racing indexing and backups.
- **Fixtures:** FX-PURGE.
- **Expected outcomes:** Tombstone/revocation then verifiable purge workflow.
- **Planned test IDs:** TC_API_029_P, TC_API_029_N, TC_API_029_S, TC_API_029_E.
- **Planned executable targets:** `tests/api/test_api_029.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-030 — GET /v1/staff/audit-events

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Read permitted minimized audit events.
- **Negative:** Invalid cursor denied.
- **Security and authorization:** Audit mandate does not grant media/custody or cross-org data.
- **Edge cases:** Hash-chain break and pagination boundary.
- **Fixtures:** FX-DB.
- **Expected outcomes:** Minimized scoped audit stream, no payload secrets.
- **Planned test IDs:** TC_API_030_P, TC_API_030_N, TC_API_030_S, TC_API_030_E.
- **Planned executable targets:** `tests/api/test_api_030.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-031 — GET /v1/staff/analytics

- **Source / phase / suite:** API_CONTRACTS.md; phase 4; api.
- **Positive:** Read approved aggregate analytics.
- **Negative:** Unsupported drilldown rejected.
- **Security and authorization:** Suppress small cells and cross-org differencing.
- **Edge cases:** Overlapping queries and zero/small samples.
- **Fixtures:** FX-BASE.
- **Expected outcomes:** Nonidentifying approved aggregates only.
- **Planned test IDs:** TC_API_031_P, TC_API_031_N, TC_API_031_S, TC_API_031_E.
- **Planned executable targets:** `tests/api/test_api_031.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### API-032 — POST /v1/staff/organizations/{id}/memberships

- **Source / phase / suite:** API_CONTRACTS.md; phase 1; api.
- **Positive:** Manage organization membership with permission.
- **Negative:** Invalid role/suspended organization rejected.
- **Security and authorization:** No automatic case/custody grant for org admin.
- **Edge cases:** Role change/session revoke and last-admin policy.
- **Fixtures:** FX-IDP, FX-BASE.
- **Expected outcomes:** Audited membership lifecycle with current grant enforcement.
- **Planned test IDs:** TC_API_032_P, TC_API_032_N, TC_API_032_S, TC_API_032_E.
- **Planned executable targets:** `tests/api/test_api_032.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**


## Database Boundary

### DB-001 — organizations

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** organizations: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_001_P, TC_DB_001_N, TC_DB_001_S, TC_DB_001_E.
- **Planned executable targets:** `tests/database/test_db_001.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-002 — staff_principals

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** staff_principals: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_002_P, TC_DB_002_N, TC_DB_002_S, TC_DB_002_E.
- **Planned executable targets:** `tests/database/test_db_002.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-003 — memberships

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** memberships: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_003_P, TC_DB_003_N, TC_DB_003_S, TC_DB_003_E.
- **Planned executable targets:** `tests/database/test_db_003.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-004 — cases

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** cases: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_004_P, TC_DB_004_N, TC_DB_004_S, TC_DB_004_E.
- **Planned executable targets:** `tests/database/test_db_004.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-005 — case_grants

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** case_grants: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_005_P, TC_DB_005_N, TC_DB_005_S, TC_DB_005_E.
- **Planned executable targets:** `tests/database/test_db_005.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-006 — report_access

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** Explicit restricted-purpose grant permits only needed fields.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** report_access: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_006_P, TC_DB_006_N, TC_DB_006_S, TC_DB_006_E.
- **Planned executable targets:** `tests/database/test_db_006.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-007 — reporters

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** Explicit restricted-purpose grant permits only needed fields.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** reporters: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_007_P, TC_DB_007_N, TC_DB_007_S, TC_DB_007_E.
- **Planned executable targets:** `tests/database/test_db_007.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-008 — child_profiles

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** child_profiles: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_008_P, TC_DB_008_N, TC_DB_008_S, TC_DB_008_E.
- **Planned executable targets:** `tests/database/test_db_008.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-009 — name_variants

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** name_variants: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_009_P, TC_DB_009_N, TC_DB_009_S, TC_DB_009_E.
- **Planned executable targets:** `tests/database/test_db_009.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-010 — assertions

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Attempt UPDATE/DELETE as application role; preserve immutable history.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** assertions: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_010_P, TC_DB_010_N, TC_DB_010_S, TC_DB_010_E.
- **Planned executable targets:** `tests/database/test_db_010.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-011 — registry_events

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** registry_events: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_011_P, TC_DB_011_N, TC_DB_011_S, TC_DB_011_E.
- **Planned executable targets:** `tests/database/test_db_011.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-012 — restricted_custody

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** Explicit restricted-purpose grant permits only needed fields.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** restricted_custody: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_012_P, TC_DB_012_N, TC_DB_012_S, TC_DB_012_E.
- **Planned executable targets:** `tests/database/test_db_012.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-013 — legal_bases

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** legal_bases: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_013_P, TC_DB_013_N, TC_DB_013_S, TC_DB_013_E.
- **Planned executable targets:** `tests/database/test_db_013.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-014 — evidence_documents

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** evidence_documents: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_014_P, TC_DB_014_N, TC_DB_014_S, TC_DB_014_E.
- **Planned executable targets:** `tests/database/test_db_014.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-015 — upload_intents

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** upload_intents: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_015_P, TC_DB_015_N, TC_DB_015_S, TC_DB_015_E.
- **Planned executable targets:** `tests/database/test_db_015.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-016 — photographs

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** photographs: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_016_P, TC_DB_016_N, TC_DB_016_S, TC_DB_016_E.
- **Planned executable targets:** `tests/database/test_db_016.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-017 — objects

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** objects: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_017_P, TC_DB_017_N, TC_DB_017_S, TC_DB_017_E.
- **Planned executable targets:** `tests/database/test_db_017.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-018 — photo_derivatives

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** photo_derivatives: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_018_P, TC_DB_018_N, TC_DB_018_S, TC_DB_018_E.
- **Planned executable targets:** `tests/database/test_db_018.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-019 — face_regions

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 2; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** face_regions: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_019_P, TC_DB_019_N, TC_DB_019_S, TC_DB_019_E.
- **Planned executable targets:** `tests/database/test_db_019.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-020 — model_manifests

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 2; database.
- **Positive:** Authorized signed/versioned control metadata read; administrator performs approved append.
- **Negative:** Reject incompatible dimension/manifest mutation and invalid version.
- **Security and authorization:** Deny ordinary principal mutation; no embedded child payload in global control metadata.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** model_manifests: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_020_P, TC_DB_020_N, TC_DB_020_S, TC_DB_020_E.
- **Planned executable targets:** `tests/database/test_db_020.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-021 — embedding_spaces

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 2; database.
- **Positive:** Authorized signed/versioned control metadata read; administrator performs approved append.
- **Negative:** Reject incompatible dimension/manifest mutation and invalid version.
- **Security and authorization:** Deny ordinary principal mutation; no embedded child payload in global control metadata.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** embedding_spaces: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_021_P, TC_DB_021_N, TC_DB_021_S, TC_DB_021_E.
- **Planned executable targets:** `tests/database/test_db_021.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-022 — embeddings

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 2; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** embeddings: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_022_P, TC_DB_022_N, TC_DB_022_S, TC_DB_022_E.
- **Planned executable targets:** `tests/database/test_db_022.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-023 — matching_runs

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 2; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** matching_runs: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_023_P, TC_DB_023_N, TC_DB_023_S, TC_DB_023_E.
- **Planned executable targets:** `tests/database/test_db_023.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-024 — candidate_leads

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 2; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** candidate_leads: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_024_P, TC_DB_024_N, TC_DB_024_S, TC_DB_024_E.
- **Planned executable targets:** `tests/database/test_db_024.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-025 — federation_agreements

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 4; database.
- **Positive:** Broker/approval actor performs only agreement-and-purpose-scoped access.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** Tenant roles cannot read broker-only edges; unilateral agreement cannot authorize disclosure.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** federation_agreements: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_025_P, TC_DB_025_N, TC_DB_025_S, TC_DB_025_E.
- **Planned executable targets:** `tests/database/test_db_025.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-026 — broker_candidate_edges

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 4; database.
- **Positive:** Broker/approval actor performs only agreement-and-purpose-scoped access.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** Tenant roles cannot read broker-only edges; unilateral agreement cannot authorize disclosure.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** broker_candidate_edges: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_026_P, TC_DB_026_N, TC_DB_026_S, TC_DB_026_E.
- **Planned executable targets:** `tests/database/test_db_026.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-027 — disclosure_grants

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 4; database.
- **Positive:** Broker/approval actor performs only agreement-and-purpose-scoped access.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** Tenant roles cannot read broker-only edges; unilateral agreement cannot authorize disclosure.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** disclosure_grants: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_027_P, TC_DB_027_N, TC_DB_027_S, TC_DB_027_E.
- **Planned executable targets:** `tests/database/test_db_027.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-028 — investigations / notes

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Attempt UPDATE/DELETE as application role; preserve immutable history.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** investigations / notes: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_028_P, TC_DB_028_N, TC_DB_028_S, TC_DB_028_E.
- **Planned executable targets:** `tests/database/test_db_028.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-029 — duplicate_links

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** duplicate_links: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_029_P, TC_DB_029_N, TC_DB_029_S, TC_DB_029_E.
- **Planned executable targets:** `tests/database/test_db_029.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-030 — human_reviews

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Attempt UPDATE/DELETE as application role; preserve immutable history.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** human_reviews: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_030_P, TC_DB_030_N, TC_DB_030_S, TC_DB_030_E.
- **Planned executable targets:** `tests/database/test_db_030.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-031 — reunification_plans

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** reunification_plans: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_031_P, TC_DB_031_N, TC_DB_031_S, TC_DB_031_E.
- **Planned executable targets:** `tests/database/test_db_031.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-032 — approvals

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** Explicit restricted-purpose grant permits only needed fields.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** approvals: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_032_P, TC_DB_032_N, TC_DB_032_S, TC_DB_032_E.
- **Planned executable targets:** `tests/database/test_db_032.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-033 — handovers

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** Explicit restricted-purpose grant permits only needed fields.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** handovers: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_033_P, TC_DB_033_N, TC_DB_033_S, TC_DB_033_E.
- **Planned executable targets:** `tests/database/test_db_033.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-034 — jobs / outbox_events

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** jobs / outbox_events: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_034_P, TC_DB_034_N, TC_DB_034_S, TC_DB_034_E.
- **Planned executable targets:** `tests/database/test_db_034.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-035 — notification_deliveries

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** notification_deliveries: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_035_P, TC_DB_035_N, TC_DB_035_S, TC_DB_035_E.
- **Planned executable targets:** `tests/database/test_db_035.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-036 — audit_events

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Attempt UPDATE/DELETE as application role; preserve immutable history.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** audit_events: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_036_P, TC_DB_036_N, TC_DB_036_S, TC_DB_036_E.
- **Planned executable targets:** `tests/database/test_db_036.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DB-037 — deletion_requests / tombstones

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** API/worker non-owner role performs authorized same-org case-scoped operation.
- **Negative:** Deny missing tenant/purpose/context, invalid FK or unauthorized table action.
- **Security and authorization:** FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant.
- **Edge cases:** Revoke/expire grant or legal basis during transaction; connection pool reused for another org.
- **Fixtures:** FX-DB, FX-BASE.
- **Expected outcomes:** deletion_requests / tombstones: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect.
- **Planned test IDs:** TC_DB_037_P, TC_DB_037_N, TC_DB_037_S, TC_DB_037_E.
- **Planned executable targets:** `tests/database/test_db_037.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**


## Transaction

### TXN-01 — Tenant pool/context isolation

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** Use transaction-local server-set principal/organization.
- **Negative:** Missing context fails closed.
- **Security and authorization:** Forged user-supplied organization cannot set DB identity.
- **Edge cases:** Reuse pooled connection after rollback and session revoke.
- **Fixtures:** FX-DB, FX-EVENT, FX-PURGE.
- **Expected outcomes:** No residual tenant/purpose context or leaked rows.
- **Planned test IDs:** TC_TXN_01_P, TC_TXN_01_N, TC_TXN_01_S, TC_TXN_01_E.
- **Planned executable targets:** `tests/database/test_txn_01.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### TXN-02 — Composite cross-organization foreign keys

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** Insert same-org case/evidence relation.
- **Negative:** Reject other-org parent with guessed ID.
- **Security and authorization:** No deferred FK bypass through worker or bulk path.
- **Edge cases:** Concurrent parent deletion and reused readable identifiers.
- **Fixtures:** FX-DB, FX-EVENT, FX-PURGE.
- **Expected outcomes:** Composite ownership enforced at DB boundary.
- **Planned test IDs:** TC_TXN_02_P, TC_TXN_02_N, TC_TXN_02_S, TC_TXN_02_E.
- **Planned executable targets:** `tests/database/test_txn_02.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### TXN-03 — Audit/outbox/domain atomic commit

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** Commit authorized mutation with one audit/outbox record.
- **Negative:** Inject failure before each commit boundary.
- **Security and authorization:** Unprivileged actor cannot suppress audit.
- **Edge cases:** Crash before/after commit and retried idempotency key.
- **Fixtures:** FX-DB, FX-EVENT, FX-PURGE.
- **Expected outcomes:** All three commit or none; no unlogged side effect.
- **Planned test IDs:** TC_TXN_03_P, TC_TXN_03_N, TC_TXN_03_S, TC_TXN_03_E.
- **Planned executable targets:** `tests/database/test_txn_03.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### TXN-04 — Approval/revocation race

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** Approve valid independent plan transaction.
- **Negative:** Revoke approval or change snapshot before release.
- **Security and authorization:** Same signer in two roles still cannot approve own release.
- **Edge cases:** Concurrent handover/revoke at deterministic barrier.
- **Fixtures:** FX-DB, FX-EVENT, FX-PURGE.
- **Expected outcomes:** Release denied when any current gate invalid.
- **Planned test IDs:** TC_TXN_04_P, TC_TXN_04_N, TC_TXN_04_S, TC_TXN_04_E.
- **Planned executable targets:** `tests/database/test_txn_04.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### TXN-05 — Deletion/index race

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** Tombstone then purge all model partitions.
- **Negative:** Stale embedding completion cannot resurrect row.
- **Security and authorization:** Worker must recheck legal basis and generation.
- **Edge cases:** Crash/retry between object deletion and vector write.
- **Fixtures:** FX-DB, FX-EVENT, FX-PURGE.
- **Expected outcomes:** No reachable vector/media after deletion; purge audit remains.
- **Planned test IDs:** TC_TXN_05_P, TC_TXN_05_N, TC_TXN_05_S, TC_TXN_05_E.
- **Planned executable targets:** `tests/database/test_txn_05.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### TXN-06 — Schema install/upgrade/restore

- **Source / phase / suite:** DATABASE_SCHEMA.md; phase 1; database.
- **Positive:** Apply migrations to empty and prior synthetic release.
- **Negative:** Fail interrupted/incompatible backfill safely.
- **Security and authorization:** Migration role separated from API roles.
- **Edge cases:** Large resumable backfill and restore tombstones.
- **Fixtures:** FX-DB, FX-EVENT, FX-PURGE.
- **Expected outcomes:** Constraints/RLS preserved and rollback path demonstrated.
- **Planned test IDs:** TC_TXN_06_P, TC_TXN_06_N, TC_TXN_06_S, TC_TXN_06_E.
- **Planned executable targets:** `tests/database/test_txn_06.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**


## Background Event

### JOB-001 — report.submitted

- **Source / phase / suite:** contracts/event-envelope.schema.json; phase 1; workers.
- **Positive:** Create restricted triage/assignment task.
- **Negative:** Malformed/unknown version goes to dead-letter review with no sensitive processing.
- **Security and authorization:** No child data in event; unverified source cannot self-approve.
- **Edge cases:** Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis.
- **Fixtures:** FX-EVENT, FX-BASE, FX-FAILURE.
- **Expected outcomes:** Create restricted triage/assignment task exactly within current permissions; retry is idempotent and audit/dedup retained.
- **Planned test IDs:** TC_JOB_001_P, TC_JOB_001_N, TC_JOB_001_S, TC_JOB_001_E.
- **Planned executable targets:** `tests/workers/test_job_001.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### JOB-002 — media.uploaded

- **Source / phase / suite:** contracts/event-envelope.schema.json; phase 1; workers.
- **Positive:** Lease malware/validation job against immutable object version.
- **Negative:** Malformed/unknown version goes to dead-letter review with no sensitive processing.
- **Security and authorization:** No serve/embed until valid scan; outage keeps quarantine.
- **Edge cases:** Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis.
- **Fixtures:** FX-EVENT, FX-BASE, FX-FAILURE.
- **Expected outcomes:** Lease malware/validation job against immutable object version exactly within current permissions; retry is idempotent and audit/dedup retained.
- **Planned test IDs:** TC_JOB_002_P, TC_JOB_002_N, TC_JOB_002_S, TC_JOB_002_E.
- **Planned executable targets:** `tests/workers/test_job_002.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### JOB-003 — media.ready

- **Source / phase / suite:** contracts/event-envelope.schema.json; phase 1; workers.
- **Positive:** Schedule approved-subject processing or staff selection.
- **Negative:** Malformed/unknown version goes to dead-letter review with no sensitive processing.
- **Security and authorization:** No automatic subject choice for multiple faces.
- **Edge cases:** Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis.
- **Fixtures:** FX-EVENT, FX-BASE, FX-FAILURE.
- **Expected outcomes:** Schedule approved-subject processing or staff selection exactly within current permissions; retry is idempotent and audit/dedup retained.
- **Planned test IDs:** TC_JOB_003_P, TC_JOB_003_N, TC_JOB_003_S, TC_JOB_003_E.
- **Planned executable targets:** `tests/workers/test_job_003.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### JOB-004 — media.quarantined

- **Source / phase / suite:** contracts/event-envelope.schema.json; phase 1; workers.
- **Positive:** Hold processing and create authorized moderation task.
- **Negative:** Malformed/unknown version goes to dead-letter review with no sensitive processing.
- **Security and authorization:** No image URL/raw bytes in notification.
- **Edge cases:** Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis.
- **Fixtures:** FX-EVENT, FX-BASE, FX-FAILURE.
- **Expected outcomes:** Hold processing and create authorized moderation task exactly within current permissions; retry is idempotent and audit/dedup retained.
- **Planned test IDs:** TC_JOB_004_P, TC_JOB_004_N, TC_JOB_004_S, TC_JOB_004_E.
- **Planned executable targets:** `tests/workers/test_job_004.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### JOB-005 — subject.selected

- **Source / phase / suite:** contracts/event-envelope.schema.json; phase 2; workers.
- **Positive:** Queue selected-region alignment/quality/embedding.
- **Negative:** Malformed/unknown version goes to dead-letter review with no sensitive processing.
- **Security and authorization:** Deny unapproved or stale source revision.
- **Edge cases:** Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis.
- **Fixtures:** FX-EVENT, FX-BASE, FX-FAILURE.
- **Expected outcomes:** Queue selected-region alignment/quality/embedding exactly within current permissions; retry is idempotent and audit/dedup retained.
- **Planned test IDs:** TC_JOB_005_P, TC_JOB_005_N, TC_JOB_005_S, TC_JOB_005_E.
- **Planned executable targets:** `tests/workers/test_job_005.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### JOB-006 — embedding.ready

- **Source / phase / suite:** contracts/event-envelope.schema.json; phase 2; workers.
- **Positive:** Insert compatible-space vector and schedule retrieval.
- **Negative:** Malformed/unknown version goes to dead-letter review with no sensitive processing.
- **Security and authorization:** Never compare equal-sized incompatible model vectors.
- **Edge cases:** Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis.
- **Fixtures:** FX-EVENT, FX-BASE, FX-FAILURE.
- **Expected outcomes:** Insert compatible-space vector and schedule retrieval exactly within current permissions; retry is idempotent and audit/dedup retained.
- **Planned test IDs:** TC_JOB_006_P, TC_JOB_006_N, TC_JOB_006_S, TC_JOB_006_E.
- **Planned executable targets:** `tests/workers/test_job_006.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### JOB-007 — matching.requested

- **Source / phase / suite:** contracts/event-envelope.schema.json; phase 2; workers.
- **Positive:** Run scoped face and independent metadata retrieval.
- **Negative:** Malformed/unknown version goes to dead-letter review with no sensitive processing.
- **Security and authorization:** Reject unlicensed model, absent purpose or unauthorized federation.
- **Edge cases:** Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis.
- **Fixtures:** FX-EVENT, FX-BASE, FX-FAILURE.
- **Expected outcomes:** Run scoped face and independent metadata retrieval exactly within current permissions; retry is idempotent and audit/dedup retained.
- **Planned test IDs:** TC_JOB_007_P, TC_JOB_007_N, TC_JOB_007_S, TC_JOB_007_E.
- **Planned executable targets:** `tests/workers/test_job_007.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### JOB-008 — matching.completed

- **Source / phase / suite:** contracts/event-envelope.schema.json; phase 2; workers.
- **Positive:** Persist lead run and neutral review task.
- **Negative:** Malformed/unknown version goes to dead-letter review with no sensitive processing.
- **Security and authorization:** No auto identity resolution or claimant message.
- **Edge cases:** Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis.
- **Fixtures:** FX-EVENT, FX-BASE, FX-FAILURE.
- **Expected outcomes:** Persist lead run and neutral review task exactly within current permissions; retry is idempotent and audit/dedup retained.
- **Planned test IDs:** TC_JOB_008_P, TC_JOB_008_N, TC_JOB_008_S, TC_JOB_008_E.
- **Planned executable targets:** `tests/workers/test_job_008.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### JOB-009 — lead.reviewed

- **Source / phase / suite:** contracts/event-envelope.schema.json; phase 1; workers.
- **Positive:** Persist rejection/hold/escalation effect and follow-up.
- **Negative:** Malformed/unknown version goes to dead-letter review with no sensitive processing.
- **Security and authorization:** No automatic child release.
- **Edge cases:** Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis.
- **Fixtures:** FX-EVENT, FX-BASE, FX-FAILURE.
- **Expected outcomes:** Persist rejection/hold/escalation effect and follow-up exactly within current permissions; retry is idempotent and audit/dedup retained.
- **Planned test IDs:** TC_JOB_009_P, TC_JOB_009_N, TC_JOB_009_S, TC_JOB_009_E.
- **Planned executable targets:** `tests/workers/test_job_009.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### JOB-010 — disclosure.approved

- **Source / phase / suite:** contracts/event-envelope.schema.json; phase 1; workers.
- **Positive:** Prepare expiring field-scoped permitted package.
- **Negative:** Malformed/unknown version goes to dead-letter review with no sensitive processing.
- **Security and authorization:** Recheck both sides, signer and snapshot before release.
- **Edge cases:** Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis.
- **Fixtures:** FX-EVENT, FX-BASE, FX-FAILURE.
- **Expected outcomes:** Prepare expiring field-scoped permitted package exactly within current permissions; retry is idempotent and audit/dedup retained.
- **Planned test IDs:** TC_JOB_010_P, TC_JOB_010_N, TC_JOB_010_S, TC_JOB_010_E.
- **Planned executable targets:** `tests/workers/test_job_010.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### JOB-011 — approval.revoked

- **Source / phase / suite:** contracts/event-envelope.schema.json; phase 1; workers.
- **Positive:** Invalidate dependent package/plan before next use.
- **Negative:** Malformed/unknown version goes to dead-letter review with no sensitive processing.
- **Security and authorization:** No stale send/release from queued worker.
- **Edge cases:** Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis.
- **Fixtures:** FX-EVENT, FX-BASE, FX-FAILURE.
- **Expected outcomes:** Invalidate dependent package/plan before next use exactly within current permissions; retry is idempotent and audit/dedup retained.
- **Planned test IDs:** TC_JOB_011_P, TC_JOB_011_N, TC_JOB_011_S, TC_JOB_011_E.
- **Planned executable targets:** `tests/workers/test_job_011.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### JOB-012 — reunification.recorded

- **Source / phase / suite:** contracts/event-envelope.schema.json; phase 1; workers.
- **Positive:** Create supervised welfare follow-up and history.
- **Negative:** Malformed/unknown version goes to dead-letter review with no sensitive processing.
- **Security and authorization:** No public reunion story or exact location exposure.
- **Edge cases:** Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis.
- **Fixtures:** FX-EVENT, FX-BASE, FX-FAILURE.
- **Expected outcomes:** Create supervised welfare follow-up and history exactly within current permissions; retry is idempotent and audit/dedup retained.
- **Planned test IDs:** TC_JOB_012_P, TC_JOB_012_N, TC_JOB_012_S, TC_JOB_012_E.
- **Planned executable targets:** `tests/workers/test_job_012.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### JOB-013 — deletion.requested

- **Source / phase / suite:** contracts/event-envelope.schema.json; phase 1; workers.
- **Positive:** Tombstone/revoke, cancel jobs, purge media/vectors/provider artifacts.
- **Negative:** Malformed/unknown version goes to dead-letter review with no sensitive processing.
- **Security and authorization:** Scoped legal hold; no reinsertion from stale jobs.
- **Edge cases:** Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis.
- **Fixtures:** FX-EVENT, FX-BASE, FX-FAILURE.
- **Expected outcomes:** Tombstone/revoke, cancel jobs, purge media/vectors/provider artifacts exactly within current permissions; retry is idempotent and audit/dedup retained.
- **Planned test IDs:** TC_JOB_013_P, TC_JOB_013_N, TC_JOB_013_S, TC_JOB_013_E.
- **Planned executable targets:** `tests/workers/test_job_013.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### JOB-014 — deletion.completed

- **Source / phase / suite:** contracts/event-envelope.schema.json; phase 1; workers.
- **Positive:** Verify negative retrieval and purge acknowledgments.
- **Negative:** Malformed/unknown version goes to dead-letter review with no sensitive processing.
- **Security and authorization:** Retain only legally approved minimized audit.
- **Edge cases:** Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis.
- **Fixtures:** FX-EVENT, FX-BASE, FX-FAILURE.
- **Expected outcomes:** Verify negative retrieval and purge acknowledgments exactly within current permissions; retry is idempotent and audit/dedup retained.
- **Planned test IDs:** TC_JOB_014_P, TC_JOB_014_N, TC_JOB_014_S, TC_JOB_014_E.
- **Planned executable targets:** `tests/workers/test_job_014.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### JOB-015 — notification.requested

- **Source / phase / suite:** contracts/event-envelope.schema.json; phase 1; workers.
- **Positive:** Deduplicate neutral alert to currently permitted recipient.
- **Negative:** Malformed/unknown version goes to dead-letter review with no sensitive processing.
- **Security and authorization:** No claimant identity/location/image/vector leak.
- **Edge cases:** Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis.
- **Fixtures:** FX-EVENT, FX-BASE, FX-FAILURE.
- **Expected outcomes:** Deduplicate neutral alert to currently permitted recipient exactly within current permissions; retry is idempotent and audit/dedup retained.
- **Planned test IDs:** TC_JOB_015_P, TC_JOB_015_N, TC_JOB_015_S, TC_JOB_015_E.
- **Planned executable targets:** `tests/workers/test_job_015.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**


## Background Job

### WORK-01 — media_sanitize

- **Source / phase / suite:** ENGINEERING_ARCHITECTURE.md / DEPLOYMENT_OPERATIONS.md; phase 1; workers.
- **Positive:** Produce orientation-correct sanitized derivative and encrypted preserved original.
- **Negative:** Reject unsafe decode and fail closed on scanner/metadata tool outage.
- **Security and authorization:** Separate original/EXIF access permission.
- **Edge cases:** GPS embedded thumbnail and image-size bomb.
- **Fixtures:** FX-EVENT, FX-MEDIA, FX-PURGE, FX-FAILURE.
- **Expected outcomes:** Safe derivative only; originals remain restricted.
- **Planned test IDs:** TC_WORK_01_P, TC_WORK_01_N, TC_WORK_01_S, TC_WORK_01_E.
- **Planned executable targets:** `tests/workers/test_work_01.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### WORK-02 — lease_retry_dead_letter

- **Source / phase / suite:** ENGINEERING_ARCHITECTURE.md / DEPLOYMENT_OPERATIONS.md; phase 1; workers.
- **Positive:** Recover orphaned lease and retry transient error.
- **Negative:** No blind retry of permanent auth/model-license failure.
- **Security and authorization:** Recheck permission and deletion generation on every effect.
- **Edge cases:** Clock skew, duplicate lease and exhaustion.
- **Fixtures:** FX-EVENT, FX-MEDIA, FX-PURGE, FX-FAILURE.
- **Expected outcomes:** No double external effect; actionable dead-letter.
- **Planned test IDs:** TC_WORK_02_P, TC_WORK_02_N, TC_WORK_02_S, TC_WORK_02_E.
- **Planned executable targets:** `tests/workers/test_work_02.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### WORK-03 — orphan_upload_cleanup

- **Source / phase / suite:** ENGINEERING_ARCHITECTURE.md / DEPLOYMENT_OPERATIONS.md; phase 1; workers.
- **Positive:** Expire bounded unused intent and orphan object.
- **Negative:** Do not erase finalized legitimate evidence.
- **Security and authorization:** Only owning organization/quarantine scope.
- **Edge cases:** Finalize racing cleanup.
- **Fixtures:** FX-EVENT, FX-MEDIA, FX-PURGE, FX-FAILURE.
- **Expected outcomes:** No orphan storage leak or wrongful evidence deletion.
- **Planned test IDs:** TC_WORK_03_P, TC_WORK_03_N, TC_WORK_03_S, TC_WORK_03_E.
- **Planned executable targets:** `tests/workers/test_work_03.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### WORK-04 — audit_export

- **Source / phase / suite:** ENGINEERING_ARCHITECTURE.md / DEPLOYMENT_OPERATIONS.md; phase 1; workers.
- **Positive:** Export chained events to independent signed-root sink.
- **Negative:** Detect gap/tamper/sink outage.
- **Security and authorization:** Exporter cannot read media/vector payloads.
- **Edge cases:** Crash between export and acknowledgment.
- **Fixtures:** FX-EVENT, FX-MEDIA, FX-PURGE, FX-FAILURE.
- **Expected outcomes:** Verifiable root/sequence and durable backlog; sensitive decisions hold when required.
- **Planned test IDs:** TC_WORK_04_P, TC_WORK_04_N, TC_WORK_04_S, TC_WORK_04_E.
- **Planned executable targets:** `tests/workers/test_work_04.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### WORK-05 — retention_hold_review

- **Source / phase / suite:** ENGINEERING_ARCHITECTURE.md / DEPLOYMENT_OPERATIONS.md; phase 1; workers.
- **Positive:** Apply approved purpose/TTL and review expiring legal hold.
- **Negative:** No invented production retention schedule.
- **Security and authorization:** Only privacy authority changes holds.
- **Edge cases:** Withdrawal/closure racing retention timer.
- **Fixtures:** FX-EVENT, FX-MEDIA, FX-PURGE, FX-FAILURE.
- **Expected outcomes:** Scoped hold and approved erasure; no indefinite silent reuse.
- **Planned test IDs:** TC_WORK_05_P, TC_WORK_05_N, TC_WORK_05_S, TC_WORK_05_E.
- **Planned executable targets:** `tests/workers/test_work_05.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### WORK-06 — index_reprocess_reconcile

- **Source / phase / suite:** ENGINEERING_ARCHITECTURE.md / DEPLOYMENT_OPERATIONS.md; phase 1; workers.
- **Positive:** Reprocess manifest-versioned vectors and reconcile object/index tombstones.
- **Negative:** Never switch incompatible spaces silently.
- **Security and authorization:** No worker privilege escalation or cleared-license bypass.
- **Edge cases:** Partial migration, rollback, deletion and ANN filtered-shortfall.
- **Fixtures:** FX-EVENT, FX-MEDIA, FX-PURGE, FX-FAILURE.
- **Expected outcomes:** Versioned reproducible indexes with no deleted-case resurrection.
- **Planned test IDs:** TC_WORK_06_P, TC_WORK_06_N, TC_WORK_06_S, TC_WORK_06_E.
- **Planned executable targets:** `tests/workers/test_work_06.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**


## Safeguarding

### SAF-01 — Fraudulent guardian

- **Source / phase / suite:** CHILD_SAFEGUARDING_POLICY.md / user correction; phase 1; security.
- **Positive:** Verify safe contact separately from independently established relationship.
- **Negative:** Forged/stolen relationship evidence is held.
- **Security and authorization:** No child identity/location revealed during fraud inquiry.
- **Edge cases:** Actual guardian may still be unsafe; child objection/conflict.
- **Fixtures:** FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.
- **Expected outcomes:** Only qualified independent review advances claim.
- **Planned test IDs:** TC_SAF_01_P, TC_SAF_01_N, TC_SAF_01_S, TC_SAF_01_E, TC_SAF_01_BROWSER, TC_SAF_01_STATE.
- **Planned executable targets:** `tests/security/test_saf_01.py`, `tests/browser/saf_01.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SAF-02 — Found-child location discovery

- **Source / phase / suite:** CHILD_SAFEGUARDING_POLICY.md / user correction; phase 1; security.
- **Positive:** Authorized safeguarding reader sees only approved fields.
- **Negative:** Guess URLs, search/filter/export/analytics to locate shelter.
- **Security and authorization:** Unverified claimant sees no existence/count/location hints.
- **Edge cases:** Same missing-report owner and mixed federation grants.
- **Fixtures:** FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.
- **Expected outcomes:** No shelter/custody leak via response, cache, logs or notifications.
- **Planned test IDs:** TC_SAF_02_P, TC_SAF_02_N, TC_SAF_02_S, TC_SAF_02_E, TC_SAF_02_BROWSER, TC_SAF_02_STATE.
- **Planned executable targets:** `tests/security/test_saf_02.py`, `tests/browser/saf_02.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SAF-03 — Unauthorized image access

- **Source / phase / suite:** CHILD_SAFEGUARDING_POLICY.md / user correction; phase 1; security.
- **Positive:** Case/media grant permits sanitized derivative.
- **Negative:** Direct object key/original/GPS request denied.
- **Security and authorization:** Cross-org and expired/revoked session denied at request boundary.
- **Edge cases:** Range/read cache, stale presigned URL and revocation race.
- **Fixtures:** FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.
- **Expected outcomes:** No private image access outside exact scope.
- **Planned test IDs:** TC_SAF_03_P, TC_SAF_03_N, TC_SAF_03_S, TC_SAF_03_E, TC_SAF_03_BROWSER, TC_SAF_03_STATE.
- **Planned executable targets:** `tests/security/test_saf_03.py`, `tests/browser/saf_03.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SAF-04 — Unauthorized biometric search

- **Source / phase / suite:** CHILD_SAFEGUARDING_POLICY.md / user correction; phase 2; security.
- **Positive:** Authorized internal job uses compatible-space scope.
- **Negative:** Public, reporter or arbitrary query vectors denied.
- **Security and authorization:** No embedding array or public identity-to-location endpoint.
- **Edge cases:** Raw SQL vector path and federation worker credentials.
- **Fixtures:** FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.
- **Expected outcomes:** Internal scoped lead retrieval only.
- **Planned test IDs:** TC_SAF_04_P, TC_SAF_04_N, TC_SAF_04_S, TC_SAF_04_E, TC_SAF_04_BROWSER, TC_SAF_04_STATE, TC_SAF_04_DISABLED_P1.
- **Planned executable targets:** `tests/security/test_saf_04.py`, `tests/browser/saf_04.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SAF-05 — Cross-organization leakage

- **Source / phase / suite:** CHILD_SAFEGUARDING_POLICY.md / user correction; phase 1; security.
- **Positive:** Authorized same-org and approved bilateral disclosure works.
- **Negative:** Wrong-org case ID, vectors, cursor and object key denied.
- **Security and authorization:** Both tenant RLS and application permission checks enforced.
- **Edge cases:** Pooled connection reuse and opt-out during in-flight job.
- **Fixtures:** FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.
- **Expected outcomes:** No private row/media/count leak.
- **Planned test IDs:** TC_SAF_05_P, TC_SAF_05_N, TC_SAF_05_S, TC_SAF_05_E, TC_SAF_05_BROWSER, TC_SAF_05_STATE.
- **Planned executable targets:** `tests/security/test_saf_05.py`, `tests/browser/saf_05.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SAF-06 — Expired and revoked access

- **Source / phase / suite:** CHILD_SAFEGUARDING_POLICY.md / user correction; phase 1; security.
- **Positive:** Current valid purpose-specific grants work.
- **Negative:** Expired receipt/MFA/session/grant/approval denied.
- **Security and authorization:** Revoked actor cannot send notification or stream image.
- **Edge cases:** Expiry at use time and stale outbox task.
- **Fixtures:** FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.
- **Expected outcomes:** Fail closed and revoke pending dependent effects.
- **Planned test IDs:** TC_SAF_06_P, TC_SAF_06_N, TC_SAF_06_S, TC_SAF_06_E, TC_SAF_06_BROWSER, TC_SAF_06_STATE.
- **Planned executable targets:** `tests/security/test_saf_06.py`, `tests/browser/saf_06.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SAF-07 — Incorrect match and human rejection

- **Source / phase / suite:** CHILD_SAFEGUARDING_POLICY.md / user correction; phase 2; security.
- **Positive:** Reviewer rejects deliberately wrong synthetic candidate.
- **Negative:** High score cannot confirm identity automatically.
- **Security and authorization:** Unauthorized reviewer cannot see/act on lead.
- **Edge cases:** New evidence after rejection and missing metadata.
- **Fixtures:** FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.
- **Expected outcomes:** Audited rejection, no claimant message or case resolution.
- **Planned test IDs:** TC_SAF_07_P, TC_SAF_07_N, TC_SAF_07_S, TC_SAF_07_E, TC_SAF_07_BROWSER, TC_SAF_07_STATE, TC_SAF_07_DISABLED_P1.
- **Planned executable targets:** `tests/security/test_saf_07.py`, `tests/browser/saf_07.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SAF-08 — Two-person approval

- **Source / phase / suite:** CHILD_SAFEGUARDING_POLICY.md / user correction; phase 4; security.
- **Positive:** Two distinct competent principals approve current snapshot.
- **Negative:** Same principal with two roles or requester approval denied.
- **Security and authorization:** Org admin cannot override independent-actor requirement.
- **Edge cases:** Account sharing, approver suspension and concurrent signing.
- **Fixtures:** FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.
- **Expected outcomes:** Distinct identity/action/scope enforced at API and DB transition.
- **Planned test IDs:** TC_SAF_08_P, TC_SAF_08_N, TC_SAF_08_S, TC_SAF_08_E, TC_SAF_08_BROWSER, TC_SAF_08_STATE, TC_SAF_08_DISABLED_P1.
- **Planned executable targets:** `tests/security/test_saf_08.py`, `tests/browser/saf_08.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SAF-09 — Child-release bypass

- **Source / phase / suite:** CHILD_SAFEGUARDING_POLICY.md / user correction; phase 4; security.
- **Positive:** Supervised plan with all current approvals proceeds.
- **Negative:** Direct lifecycle call, handover replay, missing authority or service outage denied.
- **Security and authorization:** Requester/admin/worker cannot bypass custody gate.
- **Edge cases:** Changed evidence, expiry, legal dispute or audit failure.
- **Fixtures:** FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.
- **Expected outcomes:** No child-release state or disclosure when any verification incomplete.
- **Planned test IDs:** TC_SAF_09_P, TC_SAF_09_N, TC_SAF_09_S, TC_SAF_09_E, TC_SAF_09_BROWSER, TC_SAF_09_STATE, TC_SAF_09_DISABLED_P1.
- **Planned executable targets:** `tests/security/test_saf_09.py`, `tests/browser/saf_09.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SAF-10 — Deletion and biometric cleanup

- **Source / phase / suite:** CHILD_SAFEGUARDING_POLICY.md / user correction; phase 1; security.
- **Positive:** Erase permitted original/derivative/all embedding spaces and queues.
- **Negative:** Stale worker and old backup cannot restore reachability.
- **Security and authorization:** Removed grants deny image/vector read before purge completes.
- **Edge cases:** Legal hold, object versions, crash/retry and index race.
- **Fixtures:** FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.
- **Expected outcomes:** Verified tombstone-first purge with minimal lawful audit.
- **Planned test IDs:** TC_SAF_10_P, TC_SAF_10_N, TC_SAF_10_S, TC_SAF_10_E, TC_SAF_10_BROWSER, TC_SAF_10_STATE.
- **Planned executable targets:** `tests/security/test_saf_10.py`, `tests/browser/saf_10.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SAF-11 — Notification information leakage

- **Source / phase / suite:** CHILD_SAFEGUARDING_POLICY.md / user correction; phase 1; security.
- **Positive:** Neutral task link reaches authorized staff once.
- **Negative:** Template containing identifying/location/image/vector data fails.
- **Security and authorization:** Revoke recipient between enqueue and send; claimant gets no lead.
- **Edge cases:** Lock-screen preview, provider retry, log and URL leakage.
- **Fixtures:** FX-BASE, FX-IDP, FX-APPROVAL, FX-MATCH, FX-PURGE, FX-FAILURE.
- **Expected outcomes:** Neutral/redacted delivery with current authorization and dedup.
- **Planned test IDs:** TC_SAF_11_P, TC_SAF_11_N, TC_SAF_11_S, TC_SAF_11_E, TC_SAF_11_BROWSER, TC_SAF_11_STATE.
- **Planned executable targets:** `tests/security/test_saf_11.py`, `tests/browser/saf_11.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**


## Security Threat

### SEC-T01 — IDOR, forged org ID, pooled tenant leakage

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T01; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Server-validated principal/org, FORCE RLS, case grants, composite FKs, non-owner API role.
- **Negative:** Inject the named attack/failure and require denial/hold: IDOR, forged org ID, pooled tenant leakage.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Cross-tenant API+SQL negative tests, pooled connection race tests; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T01_P, TC_SEC_T01_N, TC_SEC_T01_S, TC_SEC_T01_E.
- **Planned executable targets:** `tests/security/test_sec_t01.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T02 — Fraudulent claimant obtains identity/location

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T02; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Separate contact vs relationship vs custody verification; no candidate disclosure; independent scoped approvals.
- **Negative:** Inject the named attack/failure and require denial/hold: Fraudulent claimant obtains identity/location.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Adversarial claimant journeys and safeguarding review; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T02_P, TC_SEC_T02_N, TC_SEC_T02_S, TC_SEC_T02_E.
- **Planned executable targets:** `tests/security/test_sec_t02.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T03 — Insider enumerates/export cases

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T03; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Purpose-based grants, explicit media permission, no bulk export by default, audit/anomaly review.
- **Negative:** Inject the named attack/failure and require denial/hold: Insider enumerates/export cases.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Role matrix, export abuse tests, access-review drill; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T03_P, TC_SEC_T03_N, TC_SEC_T03_S, TC_SEC_T03_E.
- **Planned executable targets:** `tests/security/test_sec_t03.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T04 — Session theft, phishing or shared staff account

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T04; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Named users, MFA, short sessions, recent step-up for disclosure, secure cookies/CSRF, logout/revocation.
- **Negative:** Inject the named attack/failure and require denial/hold: Session theft, phishing or shared staff account.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** IdP/BFF integration and session replay tests; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T04_P, TC_SEC_T04_N, TC_SEC_T04_S, TC_SEC_T04_E.
- **Planned executable targets:** `tests/security/test_sec_t04.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T05 — Malware, polyglot files, decompression bombs

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T05; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Quarantine, content validation, versioned malware scan, decode sandbox and resource ceilings.
- **Negative:** Inject the named attack/failure and require denial/hold: Malware, polyglot files, decompression bombs.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Adversarial files and scanner-down failure tests; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T05_P, TC_SEC_T05_N, TC_SEC_T05_S, TC_SEC_T05_E.
- **Planned executable targets:** `tests/security/test_sec_t05.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T06 — EXIF GPS/shelter leaks

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T06; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Private original, sanitized derivative, metadata/thumbnail stripping and separate custody table.
- **Negative:** Inject the named attack/failure and require denial/hold: EXIF GPS/shelter leaks.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Byte-level EXIF/thumbnail checks and DTO snapshots; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T06_P, TC_SEC_T06_N, TC_SEC_T06_S, TC_SEC_T06_E.
- **Planned executable targets:** `tests/security/test_sec_t06.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T07 — Link leakage/cache/search indexing

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T07; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Reauthorizing media gateway, no-store/no-referrer, no public buckets, restrictive CSP.
- **Negative:** Inject the named attack/failure and require denial/hold: Link leakage/cache/search indexing.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Header, cache, CDN and bucket-policy tests; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T07_P, TC_SEC_T07_N, TC_SEC_T07_S, TC_SEC_T07_E.
- **Planned executable targets:** `tests/security/test_sec_t07.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T08 — Model/vector leak or malicious weights

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T08; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: No public inference/vector endpoints; approved hashes, trusted serialization, no worker egress.
- **Negative:** Inject the named attack/failure and require denial/hold: Model/vector leak or malicious weights.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Egress denial, weight-tamper and incompatible-space tests; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T08_P, TC_SEC_T08_N, TC_SEC_T08_S, TC_SEC_T08_E.
- **Planned executable targets:** `tests/security/test_sec_t08.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T09 — False leads or adversarial image edits

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T09; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Independent models/evaluation, uncertainty, human review, no automatic resolution.
- **Negative:** Inject the named attack/failure and require denial/hold: False leads or adversarial image edits.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Open-set benchmark and staff false-lead exercises; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T09_P, TC_SEC_T09_N, TC_SEC_T09_S, TC_SEC_T09_E.
- **Planned executable targets:** `tests/security/test_sec_t09.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T10 — Replay/race bypass of approval or deletion

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T10; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Revision-bound approvals, unique actors, expiry, serializable/locked transition, tombstone checks.
- **Negative:** Inject the named attack/failure and require denial/hold: Replay/race bypass of approval or deletion.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Concurrent approval/revocation/deletion tests; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T10_P, TC_SEC_T10_N, TC_SEC_T10_S, TC_SEC_T10_E.
- **Planned executable targets:** `tests/security/test_sec_t10.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T11 — Notification leaks or spam

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T11; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Neutral template, authorized recipient at send time, dedup/quota/retries and delivery audit.
- **Negative:** Inject the named attack/failure and require denial/hold: Notification leaks or spam.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Provider stub tests, duplicate/out-of-order/revoked grant cases; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T11_P, TC_SEC_T11_N, TC_SEC_T11_S, TC_SEC_T11_E.
- **Planned executable targets:** `tests/security/test_sec_t11.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T12 — Audit alteration or sensitive logs

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T12; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Append-only role, chained hashes and external signed roots; allowlisted fields.
- **Negative:** Inject the named attack/failure and require denial/hold: Audit alteration or sensitive logs.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Tamper detection, denied UPDATE/DELETE and log leakage scans; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T12_P, TC_SEC_T12_N, TC_SEC_T12_S, TC_SEC_T12_E.
- **Planned executable targets:** `tests/security/test_sec_t12.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T13 — Lost keys/ransomware/backups restore deleted children

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T13; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Separate KMS custody, encrypted backups, offline/immutable copies, tombstone replay.
- **Negative:** Inject the named attack/failure and require denial/hold: Lost keys/ransomware/backups restore deleted children.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Measured recovery/erasure drills; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T13_P, TC_SEC_T13_N, TC_SEC_T13_S, TC_SEC_T13_E.
- **Planned executable targets:** `tests/security/test_sec_t13.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T14 — Cross-NGO metadata inference

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T14; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Disabled-default federation, bilateral purpose grants, broker-only edges, no hidden counts.
- **Negative:** Inject the named attack/failure and require denial/hold: Cross-NGO metadata inference.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Unauthorized-count/timing tests, opt-out race and bilateral disclosure tests; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T14_P, TC_SEC_T14_N, TC_SEC_T14_S, TC_SEC_T14_E.
- **Planned executable targets:** `tests/security/test_sec_t14.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T15 — XSS from notes/names/generated output

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T15; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Escaped text rendering, sanitized limited markup, strict CSP, no inline executable remote content.
- **Negative:** Inject the named attack/failure and require denial/hold: XSS from notes/names/generated output.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Stored-XSS cases in Arabic/English, rich-text and evidence previews; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T15_P, TC_SEC_T15_N, TC_SEC_T15_S, TC_SEC_T15_E.
- **Planned executable targets:** `tests/security/test_sec_t15.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T16 — SSRF through URL image/report import

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T16; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Do not accept remote image URLs initially; safe resolver/egress restrictions if added.
- **Negative:** Inject the named attack/failure and require denial/hold: SSRF through URL image/report import.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Loopback/private/redirect/metadata-target tests; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T16_P, TC_SEC_T16_N, TC_SEC_T16_S, TC_SEC_T16_E.
- **Planned executable targets:** `tests/security/test_sec_t16.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T17 — Bot flooding and storage exhaustion

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T17; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Limits by contact/session/org/IP, accessible challenges, quotas, orphan cleanup.
- **Negative:** Inject the named attack/failure and require denial/hold: Bot flooding and storage exhaustion.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Load/abuse test without denying all shared-network users; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T17_P, TC_SEC_T17_N, TC_SEC_T17_S, TC_SEC_T17_E.
- **Planned executable targets:** `tests/security/test_sec_t17.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T18 — Compromised dependency or stale service

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T18; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Exact locks/digests, SBOM, license/CVE checks, signatures/provenance review and patch owner.
- **Negative:** Inject the named attack/failure and require denial/hold: Compromised dependency or stale service.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Clean install, reproducible build and patch drill; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T18_P, TC_SEC_T18_N, TC_SEC_T18_S, TC_SEC_T18_E.
- **Planned executable targets:** `tests/security/test_sec_t18.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### SEC-T19 — Unauthorized aggregate inference

- **Source / phase / suite:** SECURITY_THREAT_MODEL.md#T19; phase 1; security.
- **Positive:** Demonstrate legitimate flow with control enabled: Small-cell suppression, fixed approved reports, no row drilldown.
- **Negative:** Inject the named attack/failure and require denial/hold: Unauthorized aggregate inference.
- **Security and authorization:** Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries.
- **Edge cases:** Concurrent revocation/outage/retry and alternate read/export/cache path.
- **Fixtures:** FX-BASE, FX-DB, FX-FAILURE.
- **Expected outcomes:** Differencing and low-count analytics tests; preserve safe care/intake and prevent unauthorized sensitive effect.
- **Planned test IDs:** TC_SEC_T19_P, TC_SEC_T19_N, TC_SEC_T19_S, TC_SEC_T19_E.
- **Planned executable targets:** `tests/security/test_sec_t19.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**


## Unit Component

### UNIT-01 — Domain/unit and rendered component invariants

- **Source / phase / suite:** TEST_STRATEGY.md / CI_CD_TEST_GATES.md; phase 1; unit.
- **Positive:** Pure interval/name normalization and form/verification-state rendering.
- **Negative:** Malformed intervals/unknown vs contradiction.
- **Security and authorization:** No hidden verified state or unsafe HTML rendering.
- **Edge cases:** Arabic diacritics, Unicode variants and component event reordering.
- **Fixtures:** FX-UNCERTAIN, FX-A11Y.
- **Expected outcomes:** Original claims preserved; deterministic domain and component assertions.
- **Planned test IDs:** TC_UNIT_01_P, TC_UNIT_01_N, TC_UNIT_01_S, TC_UNIT_01_E.
- **Planned executable targets:** `tests/unit/test_unit_01.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### UNIT-02 — React form and review components

- **Source / phase / suite:** TEST_STRATEGY.md / CI_CD_TEST_GATES.md; phase 1; components.
- **Positive:** Render forms/review controls and dispatch validated input events.
- **Negative:** Missing labels, invalid errors and unsafe HTML fail.
- **Security and authorization:** Sensitive fields absent without granted projection; hidden button is not authorization.
- **Edge cases:** Locale switch, keyboard focus, long Arabic text and loading states.
- **Fixtures:** FX-UNCERTAIN, FX-A11Y.
- **Expected outcomes:** Deterministic rendered component assertions independent of browser E2E.
- **Planned test IDs:** TC_UNIT_02_P, TC_UNIT_02_N, TC_UNIT_02_S, TC_UNIT_02_E.
- **Planned executable targets:** `tests/components/unit_02.test.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**


## Authentication

### AUTH-01 — OIDC/MFA/session lifecycle

- **Source / phase / suite:** TEST_STRATEGY.md / CI_CD_TEST_GATES.md; phase 1; auth.
- **Positive:** Actual test Keycloak login, correct issuer/audience and fresh step-up.
- **Negative:** Wrong JWT claims, stale MFA, logout/revocation denied.
- **Security and authorization:** CSRF/cookie/session fixation/account deprovisioning protection.
- **Edge cases:** IdP/JWKS rotation outage and membership update mid-session.
- **Fixtures:** FX-IDP, FX-BASE.
- **Expected outcomes:** Authenticated current purpose/grants enforced; no fallback anonymous access.
- **Planned test IDs:** TC_AUTH_01_P, TC_AUTH_01_N, TC_AUTH_01_S, TC_AUTH_01_E.
- **Planned executable targets:** `tests/auth/test_auth_01.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**


## Accessibility

### A11Y-01 — Arabic/English responsive/accessibility journeys

- **Source / phase / suite:** TEST_STRATEGY.md / CI_CD_TEST_GATES.md; phase 1; accessibility.
- **Positive:** Keyboard/labels/focus/status/zoom/manual screen-reader review.
- **Negative:** Missing names, focus traps and clipped actionable text fail.
- **Security and authorization:** Private content absent from accessible tree and page title.
- **Edge cases:** 3 browsers × 2 locales × 4 widths; reduced motion, bidi and low bandwidth.
- **Fixtures:** FX-A11Y.
- **Expected outcomes:** WCAG acceptance evidence plus deterministic layout/DOM checks; manual results separate.
- **Planned test IDs:** TC_A11Y_01_P, TC_A11Y_01_N, TC_A11Y_01_S, TC_A11Y_01_E.
- **Planned executable targets:** `tests/browser/a11y_01.e2e.ts`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**


## Model Evaluation

### ML-01 — Lawful longitudinal identification benchmark

- **Source / phase / suite:** TEST_STRATEGY.md / CI_CD_TEST_GATES.md; phase 2; ml.
- **Positive:** Frozen independent ground-truth subject/family-disjoint evaluation.
- **Negative:** Leakage, missing provenance/license or synthetic-only accuracy claims rejected.
- **Security and authorization:** Restricted lawful images never exported to testing model/logs.
- **Edge cases:** Age gaps, quality/occlusion, demographic uncertainty, no-mate probes.
- **Fixtures:** FX-EVAL.
- **Expected outcomes:** Recall@1/10/50, false leads/FPIR, workload and confidence intervals; unset go/no-go pending NGO approval.
- **Planned test IDs:** TC_ML_01_P, TC_ML_01_N, TC_ML_01_S, TC_ML_01_E.
- **Planned executable targets:** `tests/ml/test_ml_01.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**


## Model Regression

### ML-02 — Embedding/fusion/reprocessing regression

- **Source / phase / suite:** TEST_STRATEGY.md / CI_CD_TEST_GATES.md; phase 2; ml.
- **Positive:** Compatible deterministic embeddings/ranking with independent retrieval.
- **Negative:** RGB/BGR/dimension/weight/metric mismatch fails.
- **Security and authorization:** Uncleared manifest or production-data training denied.
- **Edge cases:** Photo count max-score inflation, missing metadata and age uncertainty.
- **Fixtures:** FX-MATCH, FX-MEDIA.
- **Expected outcomes:** Versioned provenance, no incompatible vector comparison or auto-confirmation.
- **Planned test IDs:** TC_ML_02_P, TC_ML_02_N, TC_ML_02_S, TC_ML_02_E.
- **Planned executable targets:** `tests/ml/test_ml_02.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**


## Performance

### PERF-01 — Pilot capacity/load and filtered search

- **Source / phase / suite:** TEST_STRATEGY.md / CI_CD_TEST_GATES.md; phase 1; performance.
- **Positive:** Measure proposed workload with controls enabled.
- **Negative:** Resource saturation/queue overload fails capacity gate.
- **Security and authorization:** No rate-limit/authorization bypass for benchmark.
- **Edge cases:** 50k cases × five synthetic photos, 30 staff, 100 reports/hour; scoped ANN vs exact.
- **Fixtures:** FX-BASE, FX-MATCH, FX-FAILURE.
- **Expected outcomes:** Observed p50/p95/p99/error/resources and review workload; provisional SLOs not assumed passed.
- **Planned test IDs:** TC_PERF_01_P, TC_PERF_01_N, TC_PERF_01_S, TC_PERF_01_E.
- **Planned executable targets:** `tests/performance/test_perf_01.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**


## Resilience

### RES-01 — Failure, concurrency and recovery

- **Source / phase / suite:** TEST_STRATEGY.md / CI_CD_TEST_GATES.md; phase 1; resilience.
- **Positive:** Recover scanner/IdP/DB/storage/KMS/audit/worker failures.
- **Negative:** Unavailable sensitive gate blocks serve/disclose/release.
- **Security and authorization:** No plaintext/admin/anonymous fallback.
- **Edge cases:** Kill before/after commits, partitions, race barriers and at-least-once events.
- **Fixtures:** FX-FAILURE, FX-EVENT, FX-DB.
- **Expected outcomes:** Fail-safe sensitive paths, bounded retries, no double effect; measured recovery evidence.
- **Planned test IDs:** TC_RES_01_P, TC_RES_01_N, TC_RES_01_S, TC_RES_01_E.
- **Planned executable targets:** `tests/resilience/test_res_01.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**


## Deployment

### DEP-01 — Clean installation and release candidate validation

- **Source / phase / suite:** TEST_STRATEGY.md / CI_CD_TEST_GATES.md; phase 1; deployment.
- **Positive:** Build locked candidate and install fresh isolated full stack.
- **Negative:** Missing lock/digest/signature/schema guard blocks promotion.
- **Security and authorization:** No PR secrets, floating images or production data.
- **Edge cases:** Clean and upgrade paths, browser binaries/platform mismatch.
- **Fixtures:** FX-DEPLOY, FX-DB.
- **Expected outcomes:** Candidate health, migrations and full mandatory regression evidence tied to digests.
- **Planned test IDs:** TC_DEP_01_P, TC_DEP_01_N, TC_DEP_01_S, TC_DEP_01_E.
- **Planned executable targets:** `tests/deployment/test_dep_01.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

### DEP-02 — Rollback and backup/deletion recovery

- **Source / phase / suite:** TEST_STRATEGY.md / CI_CD_TEST_GATES.md; phase 5; deployment.
- **Positive:** Restore/rollback to compatible approved release.
- **Negative:** Destructive incompatible downgrade or tombstone loss blocks.
- **Security and authorization:** No resurrection of deleted case, revoked approval or model.
- **Edge cases:** Coherent DB/object cut, key recovery and incomplete backfill.
- **Fixtures:** FX-DEPLOY, FX-PURGE.
- **Expected outcomes:** Verified RPO/RTO, revocation/deletion replay and permission-safe reopening.
- **Planned test IDs:** TC_DEP_02_P, TC_DEP_02_N, TC_DEP_02_S, TC_DEP_02_E.
- **Planned executable targets:** `tests/deployment/test_dep_02.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**


## Testing Policy

### TOOL-01 — TesterArmy telemetry/model/artifact boundaries

- **Source / phase / suite:** TEST_STRATEGY.md / CI_CD_TEST_GATES.md; phase 1; security.
- **Positive:** Model-free local browser runner with both opt-out flags and isolated DB.
- **Negative:** Telemetry unset, production target, external model with real data denied.
- **Security and authorization:** Egress policy plus synthetic canaries and independent artifact redaction.
- **Edge cases:** Cache miss, automatic browser install, malicious page link and raw command.log.
- **Fixtures:** FX-BASE, FX-FAILURE.
- **Expected outcomes:** No optional telemetry or real child data to external testing model; artifacts sanitized before publishing.
- **Planned test IDs:** TC_TOOL_01_P, TC_TOOL_01_N, TC_TOOL_01_S, TC_TOOL_01_E.
- **Planned executable targets:** `tests/security/test_tool_01.py`; exact selectors/commands in the JSON record.
- **Execution evidence:** none (not run). **Current validation status: pending.**

