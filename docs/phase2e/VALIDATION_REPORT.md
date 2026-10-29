# Phase 2E validation report

## Implementation checkpoint after owner authorization

**A1b is blocked.** The [source-policy disposition](e0/SOURCE_POLICY_DISPOSITION.md) invalidates the initial data-free claim: the standard dlib binding source includes an embedded HOG payload. It was not invoked. Named weights/images remain unacquired, and intake is hard-disabled pending review of a clean minimal worker design. Historical successful chip/ABI checks are not acquisition approval.

Phase 2E E0 implementation has started on `codex/phase-2e-licensed-recognition`, after verifying required hosted CI on exact accepted main `4082dbf97da3fd1aa55a336b9d7e9caa4e0a8281`. [E0_PROGRESS.md](E0_PROGRESS.md) records executable code, source/dependency manifests, tests and current hard gate boundaries. E0 is incomplete; E1/E2 and actual-model/browser additions are pending. No Phase 2E acceptance is claimed.

The earlier preparation report below is preserved as historical evidence; its documentation-only scope describes that earlier snapshot.

---

Date: 2026-10-29. Scope: acceptance evidence for existing Phase 2D plus **Phase 2E documentation and primary-source revalidation only**. No Phase 2E application feature, native dependency, migration, runtime flag, asset acquisition or model execution was implemented. The proposed actual-inference tests are all pending.

## Existing Phase 2D acceptance gate

PR #9 merged into main at `e168e1361af565c80c8d12f6c729f3b9fcd05376` on 2026-10-29T08:15:12Z. Acceptance requires independent verification of successful required Actions on that exact merge commit, not the old PR head. The definitive result and archive verification are recorded in [Phase 2D acceptance](../phase2d/ACCEPTANCE.md), [CI receipt](../phase2d/main-ci-verification.json) and [source-bound archive receipt](../phase2d/main-merge-verification.json) only after that gate succeeds. Required main run 40840815727 and its app 15368 check passed. Independent artifact verification matched 225 committed inputs, 747 Python cases, 360 official browser cases (120/engine), 36 migrations and 53 payload hashes. Coverage 94.66962798445309%; artifact 12886421860, SHA-256 `20758b076467d0e0fb4fe27eea822ad32a6c4e964aeb5f3dfb1431d77ab44466`. This packet does not use planned Phase 2E tests as Phase 2D evidence.

## Preparation checks actually executed

| Check | Method/result | Scope limit |
|---|---|---|
| Existing file preservation | Streamed Git blob hashes and executable modes for all 864 pre-existing tracked files; zero mismatches. Merged main tree equals reviewed `cbcd2b9…` head | Evidence before new acceptance documentation; does not claim model compatibility |
| Exact code identity | Fresh official tag/commit metadata: dlib v20.0 resolves `2e0b3846b4dcd0953951a9c0172503c666975229` | Source metadata only; upstream code commit signature not verified |
| Permission evidence | Fresh official license/README/example/binding/build text and legal-code responses, locked by size/SHA-256 | Publisher grants and source-level API behavior, not complete underlying training-subject rights or legal warranty |
| Weight identities | All three approved Git blob IDs and declared compressed sizes match pinned model tree | No weight bytes acquired; compressed/decompressed SHA-256 unknown |
| Image identities/linkage | All 48 prospective LFS hashes/sizes/Git pointer IDs and 24 filename links match | No pixels acquired, visual correspondence reviewed or true identity/age labels established |
| Source snapshot comparison | Prior license/source/image metadata match byte-for-byte; model-tree snapshot changed only from a six-file projection to the full pinned response, all six entries match | Representation difference retained and explained, not silently normalized away |
| Locked local environment | Initial `.venv` check failed importing `yaml` because temporary venv metadata expired. Recreated the existing `uv.lock` environment in a new private temporary directory with `uv sync --locked` | Failure log preserved; no manifest changes or native recognition dependency installed |
| Foundation/configuration | Repaired environment: `python -m scripts.check_foundation` passed 203 checks plus both historical Phase 0 validators | These are configuration/preservation checks, not new application/native execution |
| Ruff | Existing `services/api scripts tests` passes; documentation checker also passes after import formatting | Static checks; no biometric result |
| Documentation/reference validator | Run `python3 docs/phase2e/check_specification.py`; result and actual check counts in [documentation-checks.json](documentation-checks.json) | Initial run caught abbreviated second scenario IDs; all 54 IDs were made explicit without weakening the assertion; the feature-row parser was also corrected to include titled cells while requiring all 27 unique IDs and seven columns. Final run checks offline links/hashes/metadata/locks/preservation/planned statuses only; no download or inference |

Private original logs/checksums are retained in ignored `artifacts/raw/phase2e-documentation/` (directory mode 700, files 600). Prior evidence was not replaced. No model/media/raw browser trace was published by this packet. Fresh official text/metadata copies are in [research/source-lock.json](research/source-lock.json); the raw source files are inspection evidence, not installed dependencies or runnable inference components.

Reproduction on a normal full-history checkout: use the repository's existing locked Python environment, then run `python -m scripts.check_foundation`, `ruff check services/api scripts tests docs/phase2e/check_specification.py`, and `python3 docs/phase2e/check_specification.py`. This workstation used `FOC_GIT_DIR=/private/tmp/foc-phase1a-hosted-git` for existing Git objects and `/private/tmp/foc-phase2e-docs-venv/bin/python` after the environment repair; the old `.venv` symlink to expired temporary metadata was preserved, so local reproduction uses the explicit repaired-environment path. Neither override changes source, dependency pins or Git history. The private mirror's expired metadata was restored while preserving objects; branch creation used guarded refs only after proving the main/head trees and index identical, without replacing working files.

## Unexecuted requirements and limitations

All 27 Phase 2E feature groups, 54 reserved non-browser scenario groups and eight proposed browser journeys are **pending**. No new executable inference test, pretrained load, detection, alignment, embedding, SQL descriptor parity, native performance test or real-model E2E has passed. No weights, demonstration images, generators or training datasets were acquired. Original asset proposal byte-verification/download/execution flags and all eight blocked runtime profiles are unchanged.

Technical incompatibilities and unknowns remain explicit: v1's unit-normalized future DTO conflicts with native dlib L2; current media/provider path admits only procedural fixtures; CPU/ABI/build/dependency/codec compatibility requires A1b before weight/image acquisition; actual parser safety, file hashes, image suitability and measured inference performance require subsequent gated work. These are implementation dependencies, not unsupported assumptions marked as resolved.

Existing Phase 2D performance planning misses/corrective plan, public-exposure/security-governance limitations and all three manual Phase 3 gates remain open/carried forward. Exact-main direct database p95 again missed the unchanged 1,000 ms target at 1,189.44 ms, while queue 948.68 ms and comparison 715.07 ms met their respective targets; [fresh observation](../phase2d/main-performance-observation.json). No target is relaxed or performance gap closed by this documentation. Scientific child-identification accuracy, authorized longitudinal-child data and operational approval remain unmeasured/unapproved. Synthetic demonstration success cannot settle those questions.

Owner review must approve the [specification](IMPLEMENTATION_SPEC.md), [exact candidate and restrictions](LICENSING_AND_COMPATIBILITY.md), [acquisition gates](ARTIFACT_ACQUISITION_GATES.md) and [testing/acceptance criteria](TESTING_AND_ACCEPTANCE.md) before implementation. Stop at this packet; no Phase 2E, 2F or operational activation is started.
