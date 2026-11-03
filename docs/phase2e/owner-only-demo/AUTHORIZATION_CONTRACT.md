# Proposed owner authorization contract

**Specification only. No record is issued, verifier installed, key enrolled or capability created here.** [JSON Schema](authorization-record.schema.json) specifies the proposed stored intent; schema validity alone never authorizes an action. [Policy clauses](POLICY_AMENDMENT.md) and runtime invariants below are mandatory together.

## Identity and one owner action

Use the existing pinned owner/MFA boundary in `tools/phase2e/demo_governance/registry.py::authenticate_owner` as the minimum assurance baseline: RS256 signature with privileged pinned IdP key, exact issuer/audience/subject, unexpired token, required claims and `pwd` plus `otp`, with server-checked `auth_time` no older than 300 seconds. Do not substitute a fresh `iat` for fresh MFA. The future V3 adapter must also enforce typed claims, issuer/session/account revocation, future/invalid times, correct deployment owner binding and current privileged owner status. The owner token is not itself an execution permit and must never reach a worker.

A future staff-owner BFF surface prepares a server-held canonical draft and a one-use challenge. Render the complete action set, synthetic warnings, source/image/fixture counts and identities, scope/build digests, expiry, restrictions and exceptions to the owner. Authenticated confirmation must POST the **same reviewed digest** with session-bound CSRF/origin protection and the matching challenge within five minutes. Reject changed bodies, login CSRF, cross-origin calls, GET actions, double consumption and replay from another session. Service accounts and other MFA-authenticated staff are not the project owner.

Only this confirmation creates the single human authorization. It is durably stored before any capability is issued; a successful login, draft preview, scanner receipt or generic "continue" click is insufficient. Do not generate a human signing key or service-sign a fictional owner permit. Any server integrity seal is explicitly a service-storage attestation, not an Ed25519 human signature or independent review.

## Record, protected plans and encoding

Proposed domain: `FOC-PHASE2E-DEMO-OWNER-AUTHORIZATION-V3`. Revision 1 is a separate namespace from V2 and all operational/research policies. The schema is closed, UTF-8 JSON, maximum canonical record size **16 KiB**, depth **4**, strings and arrays individually bounded, safe nonnegative integers only. Reject duplicate keys, unknown fields, trailing input, floats, NaN/Infinity, boolean-as-integer, unsafe numeric ranges and noncanonical representations. Use the existing sorted compact ASCII-escaped project encoding after strict parse; do not label it JCS. The record digest is SHA-256 of canonical stored bytes; it is kept outside the digest's own input. Exact submitted bytes and the normalized record must agree with the displayed draft commitment.

The record contains identity/event references, not raw access/refresh tokens, MFA secrets, photographs, model paths or vectors. Full records are private. Public evidence exposes allowlisted hashes, counts and outcomes only.

To avoid a self-referential digest, the reviewed draft commitment is SHA-256 of the complete canonical record with **only `confirmation.reviewed_draft_sha256` omitted**. The server preallocates the record/confirmation IDs, nonce digest and exact timestamps before display. Confirmation cannot change any other field; the submitted commitment must match the displayed/stored draft. The full immutable record digest, including that commitment, is computed afterward and retained externally. `issued_at` is the server draft-issuance time; authority starts only after durable confirmed commit and `not_before`, and still expires within four hours of draft issuance. Confirmation is limited to five minutes and fresh MFA must still hold; reauthentication that changes the bound event requires a fresh reviewed draft. This is not signing a digest on the owner's behalf.

| Field group | Exact meaning / semantic checks beyond JSON Schema |
|---|---|
| `domain`, `schema_version`, `record_id`, `policy_digest` | Exact new domain/version; unique immutable ID; owner-approved digest of this policy bundle. No unknown/latest policy or self-issued test root. |
| `owner` | Server-derived pinned issuer/audience/subject and authentication-event reference/time. Caller assertions are never identity evidence. Current deployment owner mapping must agree. |
| `deployment` | Exact project, synthetic-only namespace, one private instance and NGO/tenant, deployment activation and authority/revocation epochs. No caller-provided DB/realm/store path. |
| `source` | Exact approved application commit/tree, worker build manifest, native interface, source-projection and dependency/SBOM digests. No branch-name or latest-image substitution. |
| `scope.actions` | Nonempty explicit subset: quarantine acquisition, byte verification, processing, load-only qualification, private image inference, private retrieval and private result view. No implied extra action, public search or case grant. |
| `scope.*_sha256` | Content-addressed, privately stored model/image source plans, primary license/disposition evidence, complete fixture plan, processing/resource/retention/evaluation/preprocessing/embedding-space contracts. Every object must exist, be canonical/closed and pass semantic checks before confirmation. |
| `scope` counts and data class | Exactly three approved components, 48 approved image references and 24 fictional links/groups; synthetic-only. Counts do not substitute for exact membership checks. |
| `time` | Trusted server UTC; issued/not-before/expiry order, positive lifetime at most four hours. No authorization outlives current session/owner status, rights, epoch, gate receipt or resource lease. Expiry is never auto-extended. |
| `confirmation` | Server-side event, one-use nonce digest and reviewed draft digest, with prior validated MFA/session/CSRF/origin. No raw token/CSRF secret retained in the scope object. |
| `exceptions`, `prohibitions` | Fixed acknowledged demo limitations and mandatory exclusions. No generic override map, `skip_gate`, human-review-complete claim or enabled-provider field. |

### Required private scope objects

The model/image plans expand the unchanged pinned proposal into exact immutable repository commits, allowed HTTPS identities, Git blob IDs or LFS SHA-256 values, sizes and permitted notices. Model components are CNN detector, five-point predictor and 128D ResNet encoder only. Upstream grants and restrictions must be rechecked and snapshotted; unresolved required permission or source evidence holds the stage. Training-data provenance limitations remain explicit and cannot become operational clearance through owner consent.

The fixture plan lists **each image independently**: source identity, fictional group/pair, intended query/gallery/partition/enrollment membership, metadata version, capture-date/age interval or explicit unknown, uncertainty basis, duplicate/content identity rule, exclusions/failure policy and label provenance. Store the owner's declaration and known/unknown prior score exposure honestly; do not invent human content review. Model/preprocessing and ranking/evaluation choices are pinned before scoring. The proposal does not implement Phase 2F threshold qualification or longitudinal accuracy evaluation.

The separate [fixture-plan schema](fixture-plan.schema.json) is a draft shape, not a reviewed fixture instance. Its proposed wire cap is 128 KiB and depth six; null is allowed only for explicitly unknown date/age bounds, unlike the authorization record's non-null format. Semantic validation additionally requires each of the exact 48 pinned image references once, each of the exact 24 group links once, correct source size/Git/LFS values, two distinct eligible members per link, no orphan/group/split mismatch, complete gallery/query accounting and cross-split duplicate checks. `uniqueItems` alone does not prove identity uniqueness. Known intervals require lower <= upper; exact values have equal bounds; unknowns retain null, not fabricated zero. Apparent facial age is not a measured capture age. All duplicate handling, evaluation/selection rules and preprocessing must resolve to the pinned scope contracts, with no arbitrary policy selected by the browser.

These full objects, not browser paths, are loaded from a trusted closed manifest registry. Their digests must resolve to precisely the same reviewed bytes on every use. Unknown decompressed-model hashes are **not placeholders marked verified**: the owner authorizes bounded derivation from exact pinned compressed inputs. Actual outputs become write-once measured receipts linked to that input, approved transformation and resource profile. Output identity must then be rehashed from sealed bytes before any native parser. No external receipt can nominate unrelated bytes.

## Technical receipt state machine

One record may allow the bounded pipeline; it does not waive stage dependencies. A caller/owner supplies no trusted `pass` flag. Only isolated, authenticated measurement tools may append receipts with exact source/build/job/input/plan/output digests, tool/version, limits, observation time, actual exit/failure and audit link. A privileged dispatcher verifies provenance, reproduces required byte checks and checks every mandatory result. An audit hash alone does not prove a truthful measurement.

| State transition | Mandatory actual evidence / allowed next boundary |
|---|---|
| `draft → authorized` | Fresh real owner confirmation; immutable plans; durable audit, current private epoch; no bodies acquired by draft preparation |
| `authorized → source_qualified` | Actual source/dependency/projection/ABI/build/SBOM/security disposition and retained binaries; original A1b human waiver remains explicit |
| `source_qualified → quarantined` | Authorized acquisition action, exact transport/byte caps, encrypted private quarantine and actual source receipts; no unpack/parse |
| `quarantined → bytes_verified` | Closed 51-member inventory; independent measurement pass over actual Git blob/size or LFS SHA-256/size and measured compressed SHA-256; no self-declared hashes |
| `bytes_verified → processed` | Approved per-file bounded single-stream unpack; real fresh malware scans of required inputs/outputs; sandboxed bounded decoder and clean-derivative lineage; all actual output hashes |
| `processed → load_qualified` | Fixed three-component native load-only tests with immutable sealed input, exact binary/ABI and hard process limits; crash/OOM/hang/parse/integrity failures hold everything dependent; no image inference |
| `processed + load_qualified → run_ready` | All 48 images/24 pairings and ranking-relevant metadata match owner-frozen plan; complete source-to-clean lineage; current rights/grants; seal stored independently of caller time |
| `run_ready → running` | Inference action explicitly present; compare-and-swap first-image-run tombstone persisted **before any model-image call**, source/space/lease/input identities and live authority rechecked |
| `running → private_result` | Actual result counters/provenance and failures; current case/media/purpose rights, unexpired lease/authority/epochs; atomic result/audit/outbox transaction; no partial success |
| `any → held/failed/revoked/expired` | Required dependency unavailable, technical failure, rights withdrawal, cancellation or lifecycle fault; stop/fence work and deny new reads/publication; retain minimized private evidence |

The `acquire`, `process`, `load` and `infer` action sets are distinct. A record omitting inference cannot reach a model-image call. A record allowing inference cannot skip source, integrity, scan, decode or load qualification. Existing validated receipts may be reused only for identical bytes/build/plan and while their rights/freshness remain current; there is no success cache keyed just by filename or dimension.

Owner safety observations may hold a campaign at any time; they cannot add permissions, change the immutable plan or turn a failing receipt into a pass. No second owner signature/permit is required per successful technical stage. Scope expansion, expiry renewal or legitimate pre-first-run plan revision is a new explicit authorization, not an in-place edit.

## Fencing, first-run history and recovery

Keep first-image-run history distinct from authority epochs. Persisting first-run/score-access history advances an append-only ledger cursor without invalidating a valid V3 scope or requiring a new human A7 signature. Revocation, owner/session loss, deployment changes and restore activation do invalidate authority. Acknowledged score viewing cannot erase pre-run selections or invent a fresh blind review.

The permanent freeze **lookup key must exclude mutable labels, pairings, splits, evaluation choices, model/space aliases, authorization/run IDs, instance IDs and deployment epochs**. Otherwise changing those fields would create a new key and evade the freeze. For this closed asset set, derive the stable project-wide lineage from the project, fixed dataset catalog/source commit and canonical sorted set of the 48 approved upstream image identities. Store the original pairing/partition/evaluation/preprocessing/metadata and actual clean-byte commitments **inside the sealed value**, not as a way to choose a new history key. Before native admission, require equality with that original value. Map actual source/content aliases to the same lineage; a copied asset or a new instance cannot reset it. A future different catalog/dataset needs separate protocol review, not an automatic new-key path.

New UUIDs, sessions, model aliases, authorization IDs, deployment changes or restored snapshots cannot reset that project-wide first-run tombstone. Concurrency tests must prove only the identical sealed plan crosses the first-run boundary, including a test that changes only a field formerly used in a lookup key. The original DG-FIX-01 changed-link/backdating reproduction remains a required regression under both policies.

Use protected external epoch/audit checkpoints and restore inactive, with revocation and first-run history reconciled before reads/jobs. This is independent technical custody, not a requirement for another human approver. If that state cannot be trusted or reconciled, remain inactive. Hash chains without protected external custody are insufficient against a privileged rollback.

A trusted dispatcher may issue an internal, job/input/action-bound capability with a **maximum 30-second authority lease** (proposal), never longer than remaining authorization, receipt validity or hard job deadline. It is service-to-worker transport, not a human permit, cannot widen actions, and renews only after current authority/grant checks. Worker I/O stays offline. Control-plane loss stops new lease issuance and the independent supervisor terminates/fences work by expiry. Deny publication and sensitive reads whenever current authority is unavailable, including after audit waits. Preserve kernel-enforced resource/namespace isolation and actual termination/reaping evidence.

The existing synthetic helper's 3-second deadline, 64 MiB process address-space cap and 128 MiB cgroup memory cap are **not** a qualified dlib inference profile. Actual per-stage hard CPU/wall/address-space/cgroup-memory/PID/FD/output/temp caps must be explicitly frozen in the reviewed resource contract and pass actual parser/inference qualification later. No automatic limit increase or mutable-FD fallback is permitted to obtain success. The owner cannot waive a mandatory technical failure.

## Migration boundaries

Future V3 records use a new protected store/namespace and explicitly selected dispatcher. The V2 verifier/Ed25519 registry, v1 verifier, existing operational/research permissions, case authorization and safeguarding checks remain unchanged and executable. Do not add `allow_owner_as_T`, catch a V2 denial and retry V3, or interpret any JSON policy field/browser toggle as provider activation.

The draft schema describes immutable intent only. Implementing authentication integration, receipt issuers, store immutability, trusted-state reconciliation, wire parsing and native/job handoff requires separate engineering authorization and evidence. Configured acquisition/parsing/inference stays disabled until later explicit provisioning and all applicable technical gates pass.

## Activation confirmation: present code versus proposed enforcement

**V3 cannot be activated today by a configuration flag or an unverified owner claim: it has no implemented parser, dispatcher, endpoint, trust store or installed authorization route.** This publication changes documentation only. The following accepted-source barriers remain unchanged:

- `config/phase2e/demo-governance.json`: owner anchor and registry are null; provisioning, acquisition, unpacking, scanning, native parsing, inference and operational switches are false.
- `tools/phase2e/demo_governance/registry.py::configured_registry`: after requiring a provisioned anchor/store, it unconditionally denies with `deployment_enrollment_not_authorized`. Supplying a path or changing a boolean is not enrollment or authority.
- `services/demo_recognition/native/execution_guard.cpp::require_execution_review`: the capability check is followed by an unconditional `actual_manifest_authority_unprovisioned` exception. Even flipping the capability constant alone does not authorize native execution.
- Existing V1/V2 verifiers and research/operational controls are not altered or given a V3 fallback. The draft schema, documentation status and owner fields are not loaded as execution authority.

For a **future** V3 implementation, protected deployment selection is necessary but explicitly insufficient. It must require actual verified owner/MFA confirmation of the exact immutable scope, authenticated private-store readback, current epochs/grants, successful actual technical receipts, sealed approved inputs and a qualified native build. A boolean, caller-built `Registry` object, browser policy version, `owner=true`, generic bearer token or forged `passed=true` receipt must fail. These are proposed enforcement/test obligations, not claims that an unimplemented V3 endpoint has already passed security testing. Privileged source/host compromise remains a residual risk, not something a configuration guard proves impossible.
