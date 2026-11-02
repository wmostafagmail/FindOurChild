# V3 D1–D4 source-only implementation review

Frozen design: `51c29c0e39424db243f30ce4d6d5ee8900ee122f`. Follow the implementation
commit history after that checkpoint; no history rewrite or automatic merge.

## Components

| Component | Executable source or retained integration |
|---|---|
| C01 pinned owner/typed fresh MFA/live session | `identity.py`; private API `OwnerBackend` calls existing authentication, introspection and session lookup |
| C02 closed record/canonical digest | `records.py`; exact approved schema fingerprints, depth/size/type/format bounds |
| C03 explicit confirmation | `confirmation.py`; server draft, five-minute nonce, session/auth-event binding, four-hour maximum, immutable idempotent record |
| C04 protected authority | `store.py`, `checkpoint.py`; separate PostgreSQL, append-only journal, audit/outbox, external CAS reservation before commit |
| C05 source catalog | `plans.py`; exact pinned 3/48 membership, commit/blob/size; no body fetch |
| C06 technical measurements | `receipts.py`; pinned service signatures, source/build/job/tool/input/output/limits/exit/dependency checks; sealed output hashing |
| C07 fixture freeze | `fixtures.py`; strict 48/24 schema, individual uncertainty, stable project-wide key, immutable external seal, no replacement denominator |
| C08 fixed dispatcher | `dispatcher.py`; distinct namespace/actions, no fallback; real effects unconditionally denied |
| C09 current fences | `fencing.py`; MAC-bound job/input/action/epoch/revision leases, validity intersection, maximum 30 seconds, live grants and repeated publication checks |
| C10 private PostgreSQL | `database/owner_only_demo/0001_authority.sql`; forced RLS, scoped service role, no runtime enable/enroll/epoch write or history mutation |
| C11 private API | `services/api/foc_api/owner_only_demo.py`; existing secure-session/CSRF boundary, status/prepare/confirm/revoke, default unprovisioned |
| C12 bilingual UI/BFF | localized `demo-authorization` page/panel; fixed upstream/path allowlist; complete digest/scope disclosure, explicit checkbox and POST, no browser credential storage |
| C13 immutable processing boundary | `processing.py` reuses existing kernel-sealed snapshot/closed registry; actual processing unconditionally denied |
| C14 native execution guard | original closed interface and unconditional unprovisioned native authority guard unchanged |
| C15 worker isolation | `worker.py` integrates V3 lease checks with the original fixed non-neural Linux supervisor; actual 3-second/CPU/AS/cgroup bounds unchanged |
| C16 evidence/gates | `evidence.py`, `run_checks.py`, `browser_checks.py`, required selector inventory, CI prerequisites and sanitized artifacts |
| C17 application safeguarding | original identity, NGO/case/purpose/RLS and independent safeguarding controls unchanged; owner intent never grants case or custody rights |

Paths without a directory in the table are under `tools/phase2e/owner_only_v3/`.
The production application factory has **no V3 backend or owner binding**. Setting
a flag or sending `owner=true` cannot provision one. No V2 registry/native guard
has been removed. The CI-only factory is explicitly under `tests/`, demands a
synthetic hosted environment and uses real Keycloak, secure sessions and separate
private PostgreSQL. Every synthetic account has one owner in its own instance.

## State, restore and first-image history

All confirmations serialize under the private authority row. Records, audit,
outbox, revocations and jobs are insert-only; SQL triggers reject mutation.
Runtime cannot change enabled state or authority epochs. Global fixture history
is keyed by the fixed approved publisher lineage, independently of instance,
tenant, labels, scores, pairing, model, split, authorization or deployment epoch.
A separate locked, fsynced checkpoint records the seal before the SQL mutation.
New instances cannot reset that tombstone. Only identical sealed plans can renew.

Checkpoint reservation precedes SQL commit. A crash can produce an external/SQL
mismatch and availability loss; it cannot silently authorize older restored
state. Recovery must start inactive and reconcile against the protected external
checkpoint and original exposure seal. No administrative reconciliation or real
bootstrap endpoint is provided by this milestone. Host/root rollback of both
stores remains within the explicitly accepted host trust limitation.

Native image execution still cannot occur. `freeze()` exercises the prospective
commit boundary with synthetic metadata and generated derivative digests; that
is not actual image-run history. Future native execution must invoke the same
atomic freeze before **any** detection/diagnostic image call, after separate
actual-asset gates. The old 64 MiB helper profile is not qualified for neural use.

## Receipt and worker limits

An owner declaration cannot create a trusted technical producer. Producer keys
are distinct from human approval keys, are empty in deployment, and bind exact
source/build/tool identities. Only immutable sealed output FDs are measured by
the ingestion adapter; a signed output digest must agree with the actual bytes.
Generated-buffer receipts are accepted only by explicitly constructed test
verifiers, never the actual-measurement verifier. Actual scanner, decoder and
native model qualification remain pending, with no successful receipt invented.

V3 cancellation/revocation and live session/grant checks fence publication.
Independent Linux hard limits operate without a control-plane request. Checks
against an external IdP cannot be atomic with a PostgreSQL commit; short leases,
rechecks and hard worker bounds limit exposure, rather than proving instantaneous
cross-system revocation. The current adapter runs only the fixed benign probe.

## Fixture metadata distinction

The approved source catalog uses `sealed_demo_test` for its holdout partition;
the approved V3 fixture schema names that partition `evaluation`. Synthetic test
composition maps this label explicitly, retaining the catalog/source digest and
all 48 original source identities. It issues no real fixture selection, image
approval or score-blinding claim. No approved design/schema is silently changed.

## Test inventories and evidence

`required-tests.json` freezes 90 parameterized scenario selectors and eight
additional boundary/integration selectors, plus six official browser titles.
`TRACEABILITY.json` maps all 96 approved designs to executable selectors and the
original component obligations. The six browser titles run on all 24 targets:
Chromium/Firefox/WebKit × ar-EG/en-GB × 320/360/390/1280 = **144** executions.
The original 360 official executions remain a separate, unchanged inventory.

Hosted V3 Python validation requires a real private PostgreSQL service and Linux
kernel/container controls. No missing infrastructure is skipped. It also retains
the actual source-only supervisor/build outputs, benign isolation receipts,
backup hash and inactive-restore/forced-RLS assertions. The old 747 application,
76 V2 governance, 136 E0, 52 native and 36 migration/recovery inventories remain.

Public artifacts contain allowlisted selectors/status, source hashes, sanitized
action traces and signed-out-shell PNGs only. Raw authentication, scope, database
and failure logs remain private. Every hosted result must be bound to its exact
checkout and source-manifest digest; pending/failed/canceled checks are not passes.

This review describes implemented source, not completed hosted validation.
See `VALIDATION_REPORT.md` and final PR source-bound evidence for actual results.
