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
