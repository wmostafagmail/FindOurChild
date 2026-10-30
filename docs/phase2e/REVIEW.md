> Current engineering update (2026-10-30): demo-governance source-only implementation is authorized on `codex/phase-2e-demo-governance`. See [governance validation](DEMO_GOVERNANCE_VALIDATION_REPORT.md). Earlier planning/approval text below is historical. Actual people, keys, permits, assets and inference remain unprovisioned/disabled; Phase2E is incomplete.

# Current checkpoint — approved design, implementation planning only

The owner approved the demo governance design at **797d94053b5c447d7c9956b37faaa73fdf1d5cae** as the future implementation baseline. See the [decision/scope record](DEMO_POLICY_DESIGN_APPROVAL.md). Current authorization covers planning and negative-test design, not runtime implementation or provisioning.

Review the [14 engineering packages and12 provisioning steps](DEMO_GOVERNANCE_IMPLEMENTATION_CHECKLIST.md), [64 pending negative scenarios](DEMO_GOVERNANCE_NEGATIVE_TEST_PLAN.md), and [machine-readable status](DEMO_GOVERNANCE_PLAN_STATUS.json). Each step identifies separate owner decisions and actual T/F human evidence. No person is appointed, key enrolled, permit issued, model/image body acquired or inference enabled by this planning packet. The original independent human A1b review remains unmet under the demo-only waiver; all technical and operational restrictions remain.

Stop for the next owner decision before implementation or provisioning. A read-only GitHub lookup now reports PR #11 already merged at `f1de81728efff491c2ecb964104dcd50e9f8a085`; the assistant did not merge it. This planning packet remains local, with no new commit/push/PR or main/history change. Phase2E remains incomplete; no current-main CI or implementation acceptance is inferred. Earlier review packets below retain their original status and evidence as historical records.

# Preserved previous review packets

# Demo approval-policy design checkpoint — 2026-10-30

**Owner review requested; policy not approved or implemented.** Independent human A1b review remains unmet and is waived only for the isolated demo. Proposed designated technical/blinded-fixture roles and owner final signatures are described in [DEMO_APPROVAL_POLICY_PROPOSAL.md](DEMO_APPROVAL_POLICY_PROPOSAL.md), with [enrollment](DEMO_KEY_ENROLLMENT_PROCEDURE.md), [threat assessment](DEMO_POLICY_THREAT_ASSESSMENT.md) and [evidence/status](DEMO_POLICY_DESIGN_REPORT.md). Technical/fixture reviewers are unappointed; no owner signing key or trusted-key/permit record is enrolled. The proposed matrix preserves mandatory technical gates and person-level separation while removing a proposed external-consultancy dependency; it confers no operational authority.

Stop before provisioning keys, issuing permits, acquiring model/image bodies or enabling inference. Existing source, history, locks, original tests/evidence and production safeguards remain unchanged. Phase2E is not complete/accepted. The previous review records below are retained as historical evidence.

# Preserved earlier records

# Phase 2E specification review packet

Prepared 2026-10-29 for owner review. **Documentation/research only. Phase 2E implementation, acquisition and execution have not begun.** [Phase 2D engineering acceptance](../phase2d/ACCEPTANCE.md) is separately recorded after merged PR #9 and successful required hosted CI on exact main `e168e1361af565c80c8d12f6c729f3b9fcd05376` were independently verified. A green PR-head check was not substituted.

Read the [preparation validation report](VALIDATION_REPORT.md), then:

- [Detailed implementation specification](IMPLEMENTATION_SPEC.md): E0–E2 scope, offline CPU worker, actual per-photo pipeline/vector retrieval, provider-v2 integration and safeguarding boundaries.
- [Independent licensing/compatibility revalidation](LICENSING_AND_COMPATIBILITY.md) with [fresh primary-source lock](research/source-lock.json) and [identity comparison](research/revalidation.json).
- [Proposed API/provider-v2/data boundaries](PROPOSED_CONTRACTS_AND_DATA.md): closed staff operations, versioned native-L2 provenance, relation/grant design and forward-only migration/recovery plan.
- [Artifact acquisition gates](ARTIFACT_ACQUISITION_GATES.md): owner approval, exact quarantine/download integrity, actual hashes, safe parsing/build, private media, execution authorization and revocation.
- [Testing/acceptance strategy](TESTING_AND_ACCEPTANCE.md) and [proposed feature-to-test matrix](TEST_MATRIX.md): all new cases pending, full previous regressions plus official three-browser additions.

The original roadmap/licensing packet and application source, migrations, dependencies, runtime model blocks, contracts and CI requirements are preserved. The source/weight/image publisher grants were independently checked against exact pinned references. Known compatibility gaps are explicit: v1 model DTO requires unit normalization; dlib baseline needs native L2; current procedural fixture import rejects new image lineage; native build/runtime/performance and actual bytes remain unverified. No false compatibility or acquisition pass is inferred from source metadata.

## Owner decisions requested for a subsequent implementation phase

Review the exact baseline and its documented training-provenance/third-party-rights limits; the 48-image allowlist/curation obligations; offline CPU execution and independent execution-manifest approval; additive provider-v2/native-space design; single-photo Phase 2E versus multi-photo/calibrated-open-set Phase 2F boundary; proposed inference timing protocol/targets and performance carry-forward; required test additions/private artifact delivery; and the final stop for review. Approval is not presumed and is not operational approval.

Existing [performance findings/corrective plan](../phase2d/PERFORMANCE_FINDINGS_AND_PLAN.md), [public exposure assessment](../phase2d/PUBLIC_EXPOSURE_ASSESSMENT.md) and [manual Phase 3 gates](../phase3/MANUAL_ACCEPTANCE_GATES.md) remain applicable. Passing functional tests does not close latency misses, independent-review/security-governance limitations, manual Arabic/screen-reader/long-history usability, training provenance, real child-data authority or independent biometric validation. No real missing-child data or uncleared model/dataset is introduced.

Validation of this packet consists of documentation/source-lock/link/metadata checks and preserved-source comparison. The actual commands/results are recorded in `documentation-checks.json` after execution; planned native/E2E cases remain pending. Exact-main Phase 2D execution evidence, when verified, belongs to [Phase 2D acceptance](../phase2d/ACCEPTANCE.md), not a claim that these new Phase 2E features have passed. Stop here until explicit Phase 2E implementation approval.
