# Owner-only demo policy: implementation and provisioning plan

**Proposed work only. Current authorization ends at this document packet.** No V3 verifier, BFF route, test, schema migration or policy switch is implemented. Existing source, V1/V2 validators, trust configuration and all acquisition/native guards remain unchanged.

## Work packages and gates

| Milestone | Precise future work | Required acceptance evidence / authority |
|---|---|---|
| D0 — policy review | Review policy clauses, one-owner/MFA contract, first-run freeze, lifecycle, receipt provenance and residual-risk acknowledgments | Owner approves/revises this exact packet digest. Approval alone authorizes no implementation, trust deployment or bodies. |
| D1 — source-only engineering | After separate authorization, add a separate V3 closed parser/owner adapter, private authorization store and privileged dispatcher. Do not alter V2 signatures/conflict checks or v1/research rules. | Exact source review; typed canonicalization/authentication/nonce/session/CSRF negatives; V1/V2 compatibility and explicit nonfallback tests. All existing tests retained. |
| D2 — receipt and history store | Implement exact immutable plan resolution, trusted stage-receipt producers, append-only state/authority epochs and first-run tombstones. Server inputs cannot assert pass or choose files. | Actual transactional persistence/concurrency/audit/recovery tests; DG-FIX-01 regressions; atomic pre-native admission; old-backup history reconciliation, inactive restore. No real asset required. |
| D3 — owner interface and fencing | Implement one explicit bilingual owner confirmation through existing sessions/MFA; exact displayed digest, cancellation/revocation/status. Service-to-worker scoped leases and current read/publication checks reuse hard supervisor/isolation. | Real BFF/API, two synthetic NGO tenants, real private PostgreSQL/RLS, security and full three-browser journeys; no worker owner-token access or automatic provider enable. |
| D4 — engineering review | Commit exact source; normal protected draft PR; independent artifact/source verification and owner review | All original 747 regressions, 76 V2 governance tests/64 families, 136 E0 controls, 52 source-only native cases, 36 application migrations/recovery plus new control migrations; all new negatives/positives and new official browser coverage. Zero mandatory skips; exact-head hosted CI, sanitized artifacts, source/build/SBOM inventories. This is not actual parser or biometric qualification. |
| D5 — controlled provisioning | Only after separate explicit authorization, deploy protected demo-only owner binding/store/checkpoints, trusted clock and pinned producer identities; establish secure IdP session/revocation integration | Confirm actual owner authentication under existing MFA. No human T/F appointment or human Ed25519 key required for V3. No test/default principal or caller-selected trust root. Operational/research/V2 deployments remain unchanged. |
| D6 — one bounded owner scope | Actual owner reviews exact approved source/build, primary license/source evidence, 51 reference identities, complete 48/24 fixture declaration, plan/resource/retention caps and expiry; confirms one immutable authorization | Real fresh MFA, session/CSRF/nonce binding and durable audit. This record is not fabricated now. It may permit a precisely enumerated staged pipeline, not arbitrary inputs or technical overrides. |
| D7 — actual technical qualification | Separately authorized bounded acquisition into quarantine, actual byte validation, safe unpack/scanning/decoding, immutable registry, native load-only qualification | Every stage receipt contains measured actual bytes/tool outcomes and trusted provenance; all mandatory gates pass before dependent work. Stop on failure, retain originals, do not raise limits or weaken controls. Unknown hashes remain unverified until measured. |
| D8 — isolated demonstration | Only with valid D6 authority and successful D7 dependencies: seal actual fixture lineage before first model-image call; actual detection/alignment/128D embedding/retrieval through existing NGO contracts | Genuine model outputs, preserved failure denominators/uncertainty, current grant/epoch checks, full native/API/DB/security/recovery/model-workflow UI tests and measured bounds. No operational/accuracy acceptance inferred. |
| D9 — owner review / stop | Submit exact-head draft implementation PR, evidence, limitations and remaining approvals | Later explicit owner review of full Phase 2E. No automatic merge, Phase 2F/3, real data, public search, identity/custody/release decision or operational activation. |

No second human or multi-person signing process is introduced at any V3 milestone. Technical and fixture observations are actual evidence; they are not fictitious reviewer attestations. Independent technical custody of epoch/checkpoint state is a process/storage boundary rather than an approval role.

## Specific source changes to propose after D0

| Accepted surface | Planned treatment |
|---|---|
| `records.py`, `registry.py`, `fixtures.py` in accepted V2 | Preserve executable semantics and all existing 76 selectors. New V3 code lives separately; do not add permissive switches or fake O/T/F identities. |
| `authenticate_owner` and application session/MFA boundary | Reuse pinned identity assurance via a narrow reviewed adapter, adding typed/live-session/CSRF/digest-confirmation checks; do not weaken MFA or export bearer tokens. |
| Existing artifact helpers/native loader | Reuse approved immutable-byte/closed-path mechanisms only after new authorization and real receipts are reconciled. Original fixed guard remains false until a separately reviewed native integration passes actual qualification. |
| `database/demo_governance/0001_control_plane.sql` | Keep historical SQL unchanged. Add new private schema/migration and upgrade/restore tests as needed; never edit the 36-step application ledger or use operational DB credentials. |
| Worker supervisor / cgroups | Retain actual hard enforcement and failure receipts. Qualify a frozen real-model profile later; existing synthetic helper measurements are not neural CPU/RSS evidence. |
| Configured policy selection | Separate protected demo deployment selection, with no browser-controlled version negotiation, fallback on denial or boolean provider activation. Null anchors/stores and actual processing flags remain closed in this packet. |
| Required-test inventories / workflows | Add V3 selectors and strict evidence enforcement; retain every current selector and required check. Do not count historical V2 passes as new V3 tests or omit actual model tests because assets are absent. |

## Testing and evidence budget

The [matrix](TEST_MATRIX.md) preserves the exact 64 V2 families and maps each to a separate V3 scenario. It also proposes 18 additional negative families, 8 positive/integration families and 6 owner-interface browser journeys. **These are scenario designs, not executable test counts.** Exact Python/API/native selectors and expected collection counts must be frozen during implementation; every row is pending today.

New owner-interface journeys use the pinned official TesterArmy/e2e 0.21.3 / web engine 0.15.3, real application/backend and isolated test PostgreSQL, deterministic assertions, synthetic fixtures and telemetry disabled. Six journeys × Chromium/Firefox/WebKit × Arabic/English × 320/360/390/1280 widths = **144 proposed additional executions**. Do not repurpose the original 360 regressions or the previously required 192 model-workflow executions. Engineering owner-UI delivery therefore targets at least 504 executions; later complete Phase 2E with those original model journeys targets at least 696. Counts stay proposed until selectors/targets exist and actually execute. No original model journey is reported passed by synthetic owner-UI tests.

Keep unit, API/contract, integration, actual PostgreSQL/RLS/migration/concurrency, authentication/security/adversarial, worker cancellation/resource, recovery and performance suites separate and coordinated. Browser success is not parser, database, penetration or ML evaluation evidence. Preserve full affected regression; security/safeguarding failures block progression; no green skip for missing mandatory environments or assets. Actual model-dependent stages remain blocked/pending until later authorization and availability.

All reports require exact commit/checkout identity, commands/tool versions, selector/target outcomes, zero-skip inventory enforcement, source/binary/ZIP hashes, scanner/decoder versions, private actual failure evidence and sanitized screenshots/traces/coverage. Never publish model/image bodies, chips, vectors, owner tokens or private authorization records in public CI artifacts.

## Carry-forward acceptance limits

The database target remains 1,000 ms; preserve all original misses and the accepted demo exception. Accepted-main p95 680.841914 ms is one observation, not a resolved performance gate. Native failure/resource targets have no waiver. Phase 3 human Arabic review, actual screen-reader and long-history usability remain explicit later gates. No scientific child-identification accuracy, threshold qualification or Phase 2F work is authorized here.

## Owner decision checklist

- [ ] Approve/revise the exact new demo-only clauses and the loss of second-person human review.
- [ ] Approve/revise the proposed four-hour authorization/five-minute confirmation/30-second internal lease ceilings and fail-closed lifecycle.
- [ ] Approve/revise immutable fixture semantics, pre-first-image-call seal, permanent exposure history and no score-informed replacement/reset.
- [ ] Accept/revise the threat assumptions and evidence-custody requirements; no technical failure override.
- [ ] If continuation is desired, separately authorize named source-only D1–D4 work. Provisioning, actual acquisition and inference require their stated later scope.

All boxes are unconfirmed proposed decisions. This packet is not an issued authorization or a request to appoint a second human. Stop for owner policy review.

## Component catalog for the 96-scenario mapping

All paths in the **planned surface** column are future design targets, not files implemented by this packet. Existing boundaries are cited for reuse/preservation and must not be weakened. The [matrix](TEST_MATRIX.md#explicit-component-mapping-all-96-scenarios) names the responsible components for every individual case; JSON repeats the complete mapping and retained source paths. No component ID is an executable selector or approval.

| ID / component | Planned surface | Existing boundary / responsibility |
|---|---|---|
| C01 — Owner identity / MFA adapter | `tools/phase2e/owner_only_v3/identity.py` | `tools/phase2e/demo_governance/registry.py`; `services/api/foc_api/identity.py`; Pinned real owner, typed fresh MFA, live session/account status; no self-asserted owner |
| C02 — Closed V3 intent codec | `tools/phase2e/owner_only_v3/records.py` | New isolated V3 component proposed; Canonical bounded records, exact scope/domain/build/time; draft schemas are documentation only |
| C03 — Reviewed digest and confirmation | `tools/phase2e/owner_only_v3/confirmation.py` | New isolated V3 component proposed; Session/CSRF/origin, five-minute nonce, explicit owner consent and exact replay idempotence |
| C04 — Private authorization / audit journal | `tools/phase2e/owner_only_v3/store.py` | `tools/phase2e/demo_governance/registry.py`; Immutable owner records, protected binding, revocation/epochs, audit and external checkpoint reconciliation |
| C05 — Closed source / scope plan resolver | `tools/phase2e/owner_only_v3/plans.py` | `docs/planning/demo/DEMO_ASSET_PROPOSAL.json`; Exact3/48 membership, license/provenance plans, space/build/input and processing limits |
| C06 — Trusted technical receipt state machine | `tools/phase2e/owner_only_v3/receipts.py` | New isolated V3 component proposed; Authenticated actual measurements and full gate dependencies; no caller-supplied successful approvals |
| C07 — Fixture lineage and first-run freeze | `tools/phase2e/owner_only_v3/fixtures.py` | `tools/phase2e/demo_governance/fixtures.py`; Stable project-wide lookup, immutable48/24 selection, uncertainty, failure denominators and DG-FIX-01 regression |
| C08 — Privileged V3 dispatcher / capability admission | `tools/phase2e/owner_only_v3/dispatcher.py` | `tools/phase2e/demo_governance/registry.py`; No policy fallback or flag activation; exact actions, protected owner state and successful technical conjunction |
| C09 — Live lifecycle / lease / publication fence | `tools/phase2e/owner_only_v3/fencing.py` | `tools/phase2e/demo_governance/fencing.py`; Revocation, expiry, cancellation, short leases, current grants and atomic post-audit checks |
| C10 — Private DB migrations and transactional API | `database/owner_only_demo/0001_authority.sql` | `database/demo_governance/0001_control_plane.sql`; Proposed separate private schema, forced RLS, CAS/first-run history, audit/outbox and inactive restore; no old SQL edits |
| C11 — Authenticated owner BFF/API | `services/api/foc_api/owner_only_demo.py` | `services/api/foc_api/identity.py`; `services/api/foc_api/synthetic_workflow.py`; Proposed prepare/confirm/revoke/status endpoints with existing session/MFA/case boundaries; none exists now |
| C12 — Bilingual owner UI and route adapter | `apps/web/app/[locale]/demo-authorization/page.tsx` | `apps/web/app/[locale]/identity/page.tsx`; `apps/web/app/[locale]/identity/session.tsx`; `apps/web/app/identity/[...path]/route.ts`; Proposed owner interface/BFF route, RTL, keyboard/focus/accessibility/responsive, clear scope/error and synthetic labels |
| C13 — Closed acquisition / immutable artifact / processing boundary | `tools/phase2e/owner_only_v3/processing.py` | `tools/phase2e/demo_governance/artifacts.py`; `tools/phase2e/intake.py`; Retain sealed FD/no-replace/trusted-path mechanisms; actual scanner/decoder/asset integration later, no body acquisition now |
| C14 — Native fixed-component qualification boundary | `no V3 native implementation approved` | `services/demo_recognition/native/execution_guard.cpp`; `services/demo_recognition/native/fixed_interface.cpp`; `services/demo_recognition/native/verified_stream.cpp`; Existing unconditional denial preserved; future actual parser integration requires explicit review, measured byte manifests and qualification |
| C15 — Independent worker supervisor / isolation | `future V3 job adapter; retain current hard supervisor` | `services/demo_governance/supervisor.cpp`; `services/demo_governance/synthetic_probe.cpp`; `tools/phase2e/demo_governance/isolation.py`; Hard process/namespace/cgroup/deadline controls, stable identities and actual failure receipts; synthetic helper is not neural qualification |
| C16 — Strict evidence / regression / report integration | `tools/phase2e/owner_only_v3/evidence.py; tests/owner_only_v3/` | `tools/phase2e/demo_governance/evidence.py`; `tools/phase2e/demo_governance/run_checks.py`; `docs/phase2e/governance-required-tests.json`; Proposed exact new selectors, all old regressions, no skips, source/binary/archive integrity and sanitized output |
| C17 — Unchanged case / safeguarding / operational boundary | `no weakening or replacement proposed` | `services/api/foc_api/identity.py`; `services/api/foc_api/synthetic_workflow.py`; `tools/phase2e/approval.py`; `config/qualification-models.json`; Tenant/case/purpose/RLS, reviewer separation, no public/operational recognition, no custody/release; older policy semantics retained |
