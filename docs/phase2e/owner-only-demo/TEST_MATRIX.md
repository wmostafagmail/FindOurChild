# Proposed V3 test matrix — no new executable tests yet

**All V3 cases below are pending implementation and execution.** Scenario IDs are designs, not collected selectors or passed tests. `selectors` and `execution_evidence` are empty for every V3 case in the [machine inventory](TEST_MATRIX.json). Documentation checks must never populate them as application-test evidence.

The accepted V2 inventory remains exactly76 selectors/64 DG families. Its two-person conflict denials, Ed25519 signatures and original positive controls remain valid under V2; no old test is deleted, renamed into a pass or made conditional on missing reviewers. V3 intentionally allows a single actual owner/operator, without treating that human as T/F. Its separately scoped positive and negative tests prove the new authority boundary, while cross-mode tests keep V2 and operational/research rules unchanged.

Every row requires a matched valid synthetic control and its injected fault, exact future selector/layer/command/source/input digests, minimized observed result, audit/side-effect counters and sanitized evidence. Wrong setup failures do not count as the intended denial. Fixtures: **H** test-only owner/nonowner/service and MFA/session/CSRF states; **M** pinned metadata/generated benign bytes and scanner/decoder fault fixtures; **J** private authority/job/history journals and two fictional NGO grants in actual isolated PostgreSQL; **G** bounded non-neural Linux helper processes. None establishes actual human appointment, asset safety or model inference.

## Existing64 families mapped to separate V3 tests

For each row below, the original DG ID and exact selector are preserved in JSON. V3 security outcome is also the expected result; all rows need positive, unauthorized, malformed/concurrent/expiry edges as relevant and source-bound observed evidence. **Status for every row: pending.**

| Legacy → proposed ID | Negative scenario | Expected security outcome |
|---|---|---|
| DG-R01 → OD3-R01 | Caller self-asserts owner bootstrap or confirmation | Reject before store activation; pinned owner binding and real fresh MFA required |
| DG-R02 → OD3-R02 | Policy approval/schema validity presented as an execution authorization | Keep empty/default stores and acquisition/inference closed; no authorization side effects |
| DG-R03 → OD3-R03 | Owner confirmation/challenge belongs to another subject, session or digest | Reject exact owner/session/scope mismatch; nonce not transferable |
| DG-R04 → OD3-R04 | Expired/reused nonce or concurrent confirmation consumers | Reject stale/rebound request; at most one atomic confirmation and no duplicated work |
| DG-R05 → OD3-R05 | Untrusted IdP key, non-RS256 algorithm, key substitution or malformed cryptographic material | Reject owner authentication; no V2 human-key enrollment prerequisite invented for V3 |
| DG-R06 → OD3-R06 | Another account, service or principal alias claims the owner identity | Require exact pinned issuer/audience/subject and current owner mapping; no account-count proxy |
| DG-R07 → OD3-R07 | Caller fabricates T/F identities or treats one owner as three attestors | Reject unknown roles/reviewer attestations; one real owner/operator is permitted only by V3 |
| DG-R08 → OD3-R08 | Owner/operator supplies their own technical passed=true declaration | Deny untrusted measurement; owner/operator combination itself is allowed in V3 |
| DG-R09 → OD3-R09 | Changed pair/metadata is backdated after first image inference or known score exposure | Reject changed fixture; require authentic original seal/history; preserve DG-FIX-01 negative and unchanged-renewal control |
| DG-R10 → OD3-R10 | Owner-only demo authority is used to bypass existing case/safeguarding reviewer separation | Deny application approval override; original independent safeguarding rules remain intact |
| DG-R11 → OD3-R11 | Owner status/session or scope is expired, revoked or not yet valid | No admission, sensitive read or publication using stale authority |
| DG-R12 → OD3-R12 | Wrong project, deployment, policy namespace or broader action scope | Deny; no V2-to-V3 fallback or operational-policy change |
| DG-R13 → OD3-R13 | Browser/worker supplies store path, trusted root or deployment owner binding | Deny before path selection; privileged fixed deployment configuration only |
| DG-R14 → OD3-R14 | Tampered/partial authorization journal, draft commit or audit transaction crashes | Atomic valid old/new state or inactive denial; no half-active record |
| DG-R15 → OD3-R15 | Concurrent revocation or restored older epoch/first-run ledger | Do not lose revocation/tombstones; require externally current checkpoint before activation |
| DG-R16 → OD3-R16 | Audit unavailable or test/default owner packaged as real authority | No activation/confirmation; no trusted default or silent audit-success fallback |
| DG-S01 → OD3-S01 | V1/V2 signed permit or challenge submitted to V3; V3 submitted to older verifiers | Reject cross-domain use; every older validator retains its semantics |
| DG-S02 → OD3-S02 | Authorization body/draft digest or owner token signature is corrupted | Reject authentication/confirmation mismatch before downstream IO |
| DG-S03 → OD3-S03 | Cryptographically valid staff/service token has wrong owner/audience/issuer | Deny despite valid signature or MFA; no sole-owner scope inferred |
| DG-S04 → OD3-S04 | Duplicate/unknown fields, noncanonical order/escaping, trailing JSON | Reject bounded closed wire format before authorization commit |
| DG-S05 → OD3-S05 | NaN/float/boolean-integer confusion, unsafe range or invalid UTC values | Typed early rejection; no coercion to trusted rights/time |
| DG-S06 → OD3-S06 | Oversized/deep record, excessive action list or recursively linked receipt graph | Bounded rejection; measure parser CPU/memory, no unbounded walk |
| DG-S07 → OD3-S07 | Policy, build, space, fixture, deployment or authority epoch differs | Reject exact binding mismatch despite otherwise valid owner consent |
| DG-S08 → OD3-S08 | Required receipt missing/expired/failed/forged or chain cyclic | Hold dependent stage; owner consent cannot replace actual technical evidence |
| DG-S09 → OD3-S09 | Future/expired/overlong scope, UTC rollback or uncertainty | Fail closed; enforce maximum four-hour authority and monotonic execution deadline |
| DG-S10 → OD3-S10 | Scope/capability outlives current rights, session, epoch, scanner receipt or hard deadline | Use validity intersection; renewal requires fresh explicit owner action |
| DG-S11 → OD3-S11 | Record ID/digest replay changes action/inputs or races exact duplicate | Changed reuse denied; exact idempotence cannot extend expiry or duplicate side effects |
| DG-S12 → OD3-S12 | Load-only or quarantine-only action used for any image-model execution | Deny before native image call; inference is an explicit distinct action |
| DG-S13 → OD3-S13 | Fixture/image/group/split/gallery changes after seal or score-informed judgment | Reject and retain original; no new blind-review assertion |
| DG-S14 → OD3-S14 | Login, service receipt or demo authorization used for enrollment, custody/release or operational action | Reject action widening; approval evidence is not general application authority |
| DG-S15 → OD3-S15 | Revocation/expiry occurs during audit wait or immediately before commit/read | Recheck current authority and grants; atomic denial with no partial publication |
| DG-S16 → OD3-S16 | Untrusted synthetic test owner/record/receipt copied into real demo store | Deny real trust admission; no test-generated human identity or approval claim |
| DG-A01 → OD3-A01 | Missing owner authority, source qualification or fixed component identity | No network/quarantine/model open; default denial precedes IO |
| DG-A02 → OD3-A02 | Missing/extra/duplicate source among exact three models/48 images; arbitrary URL/path | Reject inventory before acquisition; counts alone do not prove membership |
| DG-A03 → OD3-A03 | Size/Git blob/LFS/compressed SHA-256 mismatch or truncated body | Reject before unpack/parser; record actual failure, no fabricated hash |
| DG-A04 → OD3-A04 | Symlink parent/final path, hardlink, FIFO/device/directory, wrong ownership or writable ancestry | Reject before blocking read/native admission; positive trusted-root control required |
| DG-A05 → OD3-A05 | Path exchanged after validation or reopened for native load | No mutable-path reopen; only validated immutable snapshot reaches parser |
| DG-A06 → OD3-A06 | Source bytes mutate while bounded snapshot is copied | Reject unstable/wrong sealed digest before parser call; no postparse-only defense |
| DG-A07 → OD3-A07 | Original changes after sealing or writer attempts shrink/grow/write | Kernel-enforced approved snapshot remains immutable; actual prohibited writes fail |
| DG-A08 → OD3-A08 | Sealing unsupported, fails or misses required locks | Fail before parser; no mutable buffer/hash-only fallback |
| DG-A09 → OD3-A09 | Malformed/truncated/concatenated/trailing bzip2 stream | Reject single-stream fixed-output contract; no partial output admitted |
| DG-A10 → OD3-A10 | Expansion, output, CPU, address-space, memory, wall or temp ceiling exceeded | Hard termination/reaping; no automatic bound increase or clean receipt |
| DG-A11 → OD3-A11 | Scanner missing/stale/dirty/timeout or synthetic scan receipt substituted | No clean state or downstream decode/load; actual fresh scanner evidence required |
| DG-A12 → OD3-A12 | Wrong image format/oversized pixels/malformed data or sandbox decoder crash | No clean derivative/display/embedding; retain failure and all selection accounting |
| DG-A13 → OD3-A13 | Source, scan/tool, derivative hash/lineage or current permission changes | Reject before consumption; suppress derived reads/results and fence queued work |
| DG-A14 → OD3-A14 | Quarantine ciphertext/tag/AAD/key or private directory relationship invalid | No plaintext admission or secret/body leakage in errors |
| DG-A15 → OD3-A15 | Wrong component/build/space/preprocessing despite matching dimensions or filename | Reject closed component identity and incompatible vector space |
| DG-A16 → OD3-A16 | Missing/tampered compiler/SBOM/source/wheel/binary evidence or excluded HOG/broad binding restored | Qualification incomplete; no acquisition/native action; receipt cannot substitute for actual build bytes |
| DG-W01 → OD3-W01 | Attached container client dies while owned helper runs | Independent watchdog enforces bounded termination/reaping; no client-exit success claim |
| DG-W02 → OD3-W02 | Control-plane/runtime API unavailable or stalled after admission | No new leases; independent hard bounds remain and output publication denies |
| DG-W03 → OD3-W03 | Supervisor/watchdog dies or trusted authority checkpoint is lost | Kernel/process isolation terminates or fences job; no authority fallback |
| DG-W04 → OD3-W04 | Sleeping or CPU-spinning helper exceeds distinct CPU/wall limits | Enforce actual hard limits; quota throttling is not a deadline |
| DG-W05 → OD3-W05 | Allocation reaches configured memory/address-space/cgroup ceiling | Whole job failure/fence; actual exit/OOM/RSS evidence, not partial success |
| DG-W06 → OD3-W06 | Descendant changes session/group or exhausts PID/FD/output/temp budgets | No namespace/resource escape; terminate/reap owned tree without host access |
| DG-W07 → OD3-W07 | Container/PID identity reused or caller asks cleanup of another job | Stable identity denies wrong target; unrelated services untouched |
| DG-W08 → OD3-W08 | Cancellation, old lease or requeue races late result | Current token/revision CAS rejects stale result; at most one logical completion |
| DG-W09 → OD3-W09 | Owner/session/model/image/case/media/purpose revoked after enqueue | Fence current and queued work, new projections and sensitive reads |
| DG-W10 → OD3-W10 | Authority/input/fixture revision changes while audit/transaction waits | Reconcile current identity/epoch/first-run state before native call and publication |
| DG-W11 → OD3-W11 | Foreign NGO/instance/gallery or unauthorized model/vector/path request | Real API/runtime-role RLS denial; hidden rows do not affect visible rankings/counts |
| DG-W12 → OD3-W12 | Crash between audit/result/outbox or audit service fails | Atomic rollback or safely fenced retry; no unaudited visible success |
| DG-W13 → OD3-W13 | Deadline/authority lease expires after helper exit but before publish; clock untrusted | Discard/hold output despite zero exit; current trusted authorization required |
| DG-W14 → OD3-W14 | Old database/authorization backup restores revoked rights or old fixture history | Start inactive; reconcile external epochs/tombstones before reads/jobs |
| DG-W15 → OD3-W15 | New UUID/time/authorization rerun attempts to launder rejected snapshot or alter fixture | Preserve semantic rejection and first-run lineage; no identity/custody decisions |
| DG-W16 → OD3-W16 | Log/trace/screenshot leaks secret/media/vector/owner identity or omits mandatory case | Block artifact/gate; retain private original; no skipped/mock result counted as passed |

## Additional V3 negatives

Every case has the same positive-control/fixture/evidence obligations above. All are pending.

| ID | Negative scenario | Expected outcome |
|---|---|---|
| OD3-X01 | MFA auth_time is stale while iat is fresh | Reject; newly issued access token is not fresh MFA |
| OD3-X02 | Malformed amr or claims, wrong algorithm/issuer/audience or future auth_time | Strict typed authentication denial, no coercion/fallback |
| OD3-X03 | IdP session/account disabled with otherwise unexpired JWT | Deny admission/read/publication on live-status failure or unavailability |
| OD3-X04 | Cross-origin/login-CSRF, wrong-session/stale nonce, changed reviewed digest or GET confirmation | No durable authorization or capability; proper same-session explicit POST positive |
| OD3-X05 | RTL/bidi/long text hides actual identity/action/digest or confirmation differs from displayed summary | Safe full bilingual scope disclosure and exact digest binding; no obscured-action success |
| OD3-X06 | Browser selects weaker policy or V2 denial is caught and retried as V3 | Reject; only privileged fixed deployment policy selection |
| OD3-X07 | V3 credentials/store/epoch used in operational/research or foreign demo namespace | Reject across deployments; no shared DB/realm/store authority |
| OD3-X08 | Untrusted producer posts passed=true or receipt from wrong source/build/job/tool | Reject provenance and incomplete actual evidence before next stage |
| OD3-X09 | Canned receipt substitutes for actual scanner, decoder or native parser execution | Required actual qualification stays pending/failed, no model capability |
| OD3-X10 | Detection-only diagnostic attempts image call before durable fixture seal | No model-image call until atomic first-run commitment; parser/admission spy zero |
| OD3-X11 | Two workers race different fixture plans at first model-image call | At most identical authorized plan admitted; changed plan rejected before native call |
| OD3-X12 | New UUID/session/lease/owner authorization or restored checkpoint resets prior exposure | Stable project-wide image-lineage lookup excludes mutable pair/split/model/instance/epoch keys; tombstone denies reset; original DG-FIX-01 evidence retained |
| OD3-X13 | No-face/error/dirty selected image dropped, replaced or removed from denominator | Retain all48 outcomes; hold/abort technical failure; no score-informed substitution |
| OD3-X14 | Owner/admin lacks current case/media/purpose or tries same-person safeguarding conclusion | Deny access/conclusion; original NGO review constraints unchanged |
| OD3-X15 | Arbitrary photograph/model, online fallback, public/reporter biometric or custody request | Deny before affected IO, provider execution or application state change |
| OD3-X16 | Public report includes tokens, private owner subject, images/chips/vectors or missing required test | Sanitizer/inventory gate blocks release; raw evidence remains private |
| OD3-X17 | DB exception used to relax1,000ms target, native hard bounds or missing tests | Preserve target/measurements; technical and native failures remain blocking |
| OD3-X18 | Design/schema approval or configuration toggle used as actual owner execution record | No bootstrap, enrollment, acquisition, unpack/scan/load/inference; protected default denial |

## Positive and integration controls

These controls use test-only identities and benign synthetic inputs; they cannot authorize real assets. All are pending.

| ID | Positive scenario | Required observation |
|---|---|---|
| OD3-P01 | One synthetic authenticated owner also operates the bounded tools | V3 sole-owner scope accepted for benign action; V2 owner-as-reviewer still denied; no human signing ceremony |
| OD3-P02 | Same-session canonical confirmation and exact concurrent duplicate | One immutable record/nonce consumption, idempotent response, no extra work or extended lifetime |
| OD3-P03 | Trusted synthetic receipt chain with no actual models | Only authorized generated-buffer transitions advance; missing stage and untrusted pass flags still deny; not neural evidence |
| OD3-P04 | Owner scope display in Arabic/English with keyboard/focus and digest agreement | Correct complete readable scope at all planned widths; explicit confirmation only |
| OD3-P05 | All selected metadata/48 outcomes and no-face/failure states retained | No replacement; actual failures distinct from no-result; score-access history does not demand new human stage permits |
| OD3-P06 | Fresh identical-scope renewal after expiry | New explicit owner confirmation, original authentic fixture/first-run history preserved; no changed pairing or renewed blind-review claim |
| OD3-P07 | Cancellation/revocation and private inactive restore | Current work/reads fenced, epoch reconciled before reopening, no stale success |
| OD3-P08 | Existing NGO investigative/safeguarding flow remains separate | Authorized review works; owner scope grants no case access or independent-sensitive-conclusion bypass |

## New official browser journeys

All six are pending. Each uses official TesterArmy/e2e0.21.3/web0.15.3 with deterministic assertions against actual web/backend/isolated PostgreSQL; Chromium, Firefox and WebKit × ar-EG/en-GB × widths320/360/390/1280 =24 targets, hence144 **proposed** new executions. Arabic/RTL, automated accessibility/focus/keyboard and responsive failures are included. Telemetry stays disabled and artifacts sanitized. These source-only synthetic journeys establish no real model results.

| ID | Journey | Positive/negative observable outcome |
|---|---|---|
| OD3-B01 | Owner MFA, complete scoped summary and one explicit synthetic confirmation | Valid owner sees exact reviewed scope and produces one bounded synthetic authorization; no model execution |
| OD3-B02 | Nonowner/reporter/service, missing MFA/expired session and CSRF denials | Actual BFF/API denial; no authority side effects or secret leakage |
| OD3-B03 | Changed digest, double-click/concurrent replay and cross-session confirmation | One exact canonical record at most; changed/rebound scope denied |
| OD3-B04 | Frozen48-image metadata,24 pairings, uncertainty and first-run history | Generated metadata shown honestly; simulated first-run fence denies edit/new-ID reset; no real photographs/model |
| OD3-B05 | Cancel/expire/revoke while synthetic worker/result/audit wait runs | Late result and stale page denied, recoverable status/accessible failure; no stale publication |
| OD3-B06 | NGO/case/purpose separation, no operational actions, safe error/privacy rendering | Authorized scope does not grant case rights; public/foreign/custody paths denied; bilingual responsive accessibility assertions |

## Regression, evidence and status rules

Keep the original747 Python/API/real PostgreSQL/RLS/security/integration tests,76 V2 governance selectors/64 families,136 E0 controls,52 source-only native cases and36 application migrations/recovery, plus all affected new tests/migrations. Baseline360 official browser executions remain mandatory. Preserve the original192 additional real-model workflow executions as pending until actual permitted assets and workflows exist. Do not replace them with these144 owner-interface executions: projected engineering delivery is at least504; later complete Phase2E at least696, subject to exact implemented selectors and any further discovered requirements.

Mandatory environment absence, failed technical gate, missing required selector or skip blocks the corresponding required suite; it is not a pass. Actual model tests stay visibly blocked/pending until later authorization, never mocked or skipped into completed validation. API/database/security/native/ML evaluations are separate from browser tests. Every affected feature change triggers full affected regression, with exact-head hosted checks and independent artifact/source verification.

Documentation/schema/traceability checks apply only to this design packet. No current V3 functional, cryptographic, API, PostgreSQL, browser or neural test has been executed. Current accepted-main test evidence remains historical and cannot be copied into these pending rows. Original human/native findings, database1,000ms target/exception and Phase3 manual Arabic/screen-reader/long-history gates remain open at their proper scope.

## Explicit component mapping: all 96 scenarios

Component IDs resolve to exact planned surfaces and existing retained boundaries in the [implementation catalog](IMPLEMENTATION_PLAN.md#component-catalog-for-the-96-scenario-mapping). This table includes **every** mapped negative, extra negative, positive/integration and browser scenario. The obligation column states what the named components must prove; every V3 selector and execution result remains pending. Old V2 selectors remain separately mandatory.

| Scenario | Affected components | Required boundary / outcome |
|---|---|---|
| OD3-R01 | C01, C03, C04 | Reject before store activation; pinned owner binding and real fresh MFA required |
| OD3-R02 | C08, C04 | Keep empty/default stores and acquisition/inference closed; no authorization side effects |
| OD3-R03 | C01, C03, C02 | Reject exact owner/session/scope mismatch; nonce not transferable |
| OD3-R04 | C03, C04, C10 | Reject stale/rebound request; at most one atomic confirmation and no duplicated work |
| OD3-R05 | C01 | Reject owner authentication; no V2 human-key enrollment prerequisite invented for V3 |
| OD3-R06 | C01, C04 | Require exact pinned issuer/audience/subject and current owner mapping; no account-count proxy |
| OD3-R07 | C01, C02, C08 | Reject unknown roles/reviewer attestations; one real owner/operator is permitted only by V3 |
| OD3-R08 | C06, C08, C13 | Deny untrusted measurement; owner/operator combination itself is allowed in V3 |
| OD3-R09 | C07, C04, C10 | Reject changed fixture; require authentic original seal/history; preserve DG-FIX-01 negative and unchanged-renewal control |
| OD3-R10 | C17, C09 | Deny application approval override; original independent safeguarding rules remain intact |
| OD3-R11 | C01, C09, C04 | No admission, sensitive read or publication using stale authority |
| OD3-R12 | C02, C05, C08 | Deny; no V2-to-V3 fallback or operational-policy change |
| OD3-R13 | C04, C05, C08 | Deny before path selection; privileged fixed deployment configuration only |
| OD3-R14 | C04, C10 | Atomic valid old/new state or inactive denial; no half-active record |
| OD3-R15 | C04, C07, C09, C10 | Do not lose revocation/tombstones; require externally current checkpoint before activation |
| OD3-R16 | C04, C16, C01 | No activation/confirmation; no trusted default or silent audit-success fallback |
| OD3-S01 | C02, C08, C17 | Reject cross-domain use; every older validator retains its semantics |
| OD3-S02 | C01, C02, C03 | Reject authentication/confirmation mismatch before downstream IO |
| OD3-S03 | C01, C08 | Deny despite valid signature or MFA; no sole-owner scope inferred |
| OD3-S04 | C02 | Reject bounded closed wire format before authorization commit |
| OD3-S05 | C02, C09 | Typed early rejection; no coercion to trusted rights/time |
| OD3-S06 | C02, C06 | Bounded rejection; measure parser CPU/memory, no unbounded walk |
| OD3-S07 | C02, C05, C08 | Reject exact binding mismatch despite otherwise valid owner consent |
| OD3-S08 | C06, C08 | Hold dependent stage; owner consent cannot replace actual technical evidence |
| OD3-S09 | C01, C02, C09 | Fail closed; enforce maximum four-hour authority and monotonic execution deadline |
| OD3-S10 | C06, C09 | Use validity intersection; renewal requires fresh explicit owner action |
| OD3-S11 | C02, C03, C04, C10 | Changed reuse denied; exact idempotence cannot extend expiry or duplicate side effects |
| OD3-S12 | C08, C14 | Deny before native image call; inference is an explicit distinct action |
| OD3-S13 | C07, C05 | Reject and retain original; no new blind-review assertion |
| OD3-S14 | C08, C17 | Reject action widening; approval evidence is not general application authority |
| OD3-S15 | C09, C10, C04 | Recheck current authority and grants; atomic denial with no partial publication |
| OD3-S16 | C01, C04, C06 | Deny real trust admission; no test-generated human identity or approval claim |
| OD3-A01 | C08, C05, C13 | No network/quarantine/model open; default denial precedes IO |
| OD3-A02 | C05, C13 | Reject inventory before acquisition; counts alone do not prove membership |
| OD3-A03 | C13, C06 | Reject before unpack/parser; record actual failure, no fabricated hash |
| OD3-A04 | C13, C14 | Reject before blocking read/native admission; positive trusted-root control required |
| OD3-A05 | C13, C14 | No mutable-path reopen; only validated immutable snapshot reaches parser |
| OD3-A06 | C13, C14 | Reject unstable/wrong sealed digest before parser call; no postparse-only defense |
| OD3-A07 | C13, C14 | Kernel-enforced approved snapshot remains immutable; actual prohibited writes fail |
| OD3-A08 | C13, C14 | Fail before parser; no mutable buffer/hash-only fallback |
| OD3-A09 | C13, C15 | Reject single-stream fixed-output contract; no partial output admitted |
| OD3-A10 | C13, C15, C06 | Hard termination/reaping; no automatic bound increase or clean receipt |
| OD3-A11 | C13, C06 | No clean state or downstream decode/load; actual fresh scanner evidence required |
| OD3-A12 | C13, C06 | No clean derivative/display/embedding; retain failure and all selection accounting |
| OD3-A13 | C13, C05, C09 | Reject before consumption; suppress derived reads/results and fence queued work |
| OD3-A14 | C13, C04 | No plaintext admission or secret/body leakage in errors |
| OD3-A15 | C05, C13, C14 | Reject closed component identity and incompatible vector space |
| OD3-A16 | C06, C14, C16 | Qualification incomplete; no acquisition/native action; receipt cannot substitute for actual build bytes |
| OD3-W01 | C15, C09 | Independent watchdog enforces bounded termination/reaping; no client-exit success claim |
| OD3-W02 | C15, C09 | No new leases; independent hard bounds remain and output publication denies |
| OD3-W03 | C15, C09 | Kernel/process isolation terminates or fences job; no authority fallback |
| OD3-W04 | C15, C09 | Enforce actual hard limits; quota throttling is not a deadline |
| OD3-W05 | C15, C09 | Whole job failure/fence; actual exit/OOM/RSS evidence, not partial success |
| OD3-W06 | C15, C09 | No namespace/resource escape; terminate/reap owned tree without host access |
| OD3-W07 | C15, C09 | Stable identity denies wrong target; unrelated services untouched |
| OD3-W08 | C09, C10 | Current token/revision CAS rejects stale result; at most one logical completion |
| OD3-W09 | C01, C09, C17, C10 | Fence current and queued work, new projections and sensitive reads |
| OD3-W10 | C09, C07, C10 | Reconcile current identity/epoch/first-run state before native call and publication |
| OD3-W11 | C17, C10, C11 | Real API/runtime-role RLS denial; hidden rows do not affect visible rankings/counts |
| OD3-W12 | C04, C09, C10 | Atomic rollback or safely fenced retry; no unaudited visible success |
| OD3-W13 | C09, C15, C10 | Discard/hold output despite zero exit; current trusted authorization required |
| OD3-W14 | C04, C07, C09, C10 | Start inactive; reconcile external epochs/tombstones before reads/jobs |
| OD3-W15 | C07, C09, C10, C17 | Preserve semantic rejection and first-run lineage; no identity/custody decisions |
| OD3-W16 | C16, C11, C12 | Block artifact/gate; retain private original; no skipped/mock result counted as passed |
| OD3-X01 | C01 | Reject; newly issued access token is not fresh MFA |
| OD3-X02 | C01, C02 | Strict typed authentication denial, no coercion/fallback |
| OD3-X03 | C01, C09 | Deny admission/read/publication on live-status failure or unavailability |
| OD3-X04 | C01, C03, C11 | No durable authorization or capability; proper same-session explicit POST positive |
| OD3-X05 | C12, C03 | Safe full bilingual scope disclosure and exact digest binding; no obscured-action success |
| OD3-X06 | C08, C17 | Reject; only privileged fixed deployment policy selection |
| OD3-X07 | C08, C04, C17 | Reject across deployments; no shared DB/realm/store authority |
| OD3-X08 | C06, C08 | Reject provenance and incomplete actual evidence before next stage |
| OD3-X09 | C06, C13, C14 | Required actual qualification stays pending/failed, no model capability |
| OD3-X10 | C07, C08, C14 | No model-image call until atomic first-run commitment; parser/admission spy zero |
| OD3-X11 | C07, C10, C14 | At most identical authorized plan admitted; changed plan rejected before native call |
| OD3-X12 | C07, C04, C09 | Permanent lineage/tombstone denies reset; original DG-FIX-01 evidence retained |
| OD3-X13 | C07, C13, C16 | Retain all48 outcomes; hold/abort technical failure; no score-informed substitution |
| OD3-X14 | C17, C09, C11 | Deny access/conclusion; original NGO review constraints unchanged |
| OD3-X15 | C05, C08, C17 | Deny before affected IO, provider execution or application state change |
| OD3-X16 | C16, C11, C12 | Sanitizer/inventory gate blocks release; raw evidence remains private |
| OD3-X17 | C15, C16, C06 | Preserve target/measurements; technical and native failures remain blocking |
| OD3-X18 | C02, C08, C14 | No bootstrap, enrollment, acquisition, unpack/scan/load/inference; protected default denial |
| OD3-P01 | C01, C03, C08, C17 | V3 sole-owner scope accepted for benign action; V2 owner-as-reviewer still denied; no human signing ceremony |
| OD3-P02 | C03, C04, C10 | One immutable record/nonce consumption, idempotent response, no extra work or extended lifetime |
| OD3-P03 | C05, C06, C08, C13 | Only authorized generated-buffer transitions advance; missing stage and untrusted pass flags still deny; not neural evidence |
| OD3-P04 | C12, C03 | Correct complete readable scope at all planned widths; explicit confirmation only |
| OD3-P05 | C07, C16 | No replacement; actual failures distinct from no-result; score-access history does not demand new human stage permits |
| OD3-P06 | C01, C03, C04, C07, C09 | New explicit owner confirmation, original authentic fixture/first-run history preserved; no changed pairing or renewed blind-review claim |
| OD3-P07 | C04, C09, C10, C15 | Current work/reads fenced, epoch reconciled before reopening, no stale success |
| OD3-P08 | C17, C09, C11 | Authorized review works; owner scope grants no case access or independent-sensitive-conclusion bypass |
| OD3-B01 | C01, C03, C11, C12 | Valid owner sees exact reviewed scope and produces one bounded synthetic authorization; no model execution |
| OD3-B02 | C01, C03, C11, C12, C17 | Actual BFF/API denial; no authority side effects or secret leakage |
| OD3-B03 | C02, C03, C10, C11, C12 | One exact canonical record at most; changed/rebound scope denied |
| OD3-B04 | C05, C07, C11, C12 | Generated metadata shown honestly; simulated first-run fence denies edit/new-ID reset; no real photographs/model |
| OD3-B05 | C09, C10, C11, C12, C15 | Late result and stale page denied, recoverable status/accessible failure; no stale publication |
| OD3-B06 | C17, C08, C11, C12, C16 | Authorized scope does not grant case rights; public/foreign/custody paths denied; bilingual responsive accessibility assertions |
