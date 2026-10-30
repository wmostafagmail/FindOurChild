# Phase 2E validation report — blocked E0 review checkpoint

**Phase 2E is incomplete and is not accepted. A1b is blocked pending review of the corrected minimal worker design and completion/review of its real-model execution interface.** The default acquisition policy is false. E1/E2, model loading, actual facial recognition, all additional 192 browser executions and production activation remain unimplemented/unexecuted. No pending scenario is counted as passed.

This is an executable engineering checkpoint, with a draft implementation [PR #11](https://github.com/wmostafagmail/FindOurChild/pull/11), not a completed recognition demonstration. The owner authorized bounded Phase 2E through the attached master directive (SHA-256 `3fa889d0ac10bc5818e8ba1120d61536f54ddeb4b0837669b05d179c64ba9270`). That satisfies A0 only. No Phase 2F/3, real-child processing or operational authority is inferred.

## Accepted source and preservation

Before modification, PR #10 was verified merged into main `4082dbf97da3fd1aa55a336b9d7e9caa4e0a8281`, with successful required app 15368 / `phase1a-required` check and [push run 40923134520](https://github.com/wmostafagmail/FindOurChild/actions/runs/40923134520) on that exact commit. [Independent verification](e0/accepted-main-evidence.json) matched all source inputs and the actual 747 Python/API/database/security tests, 360 official TesterArmy executions (120 Chromium, 120 Firefox, 120 WebKit), 36 migrations, coverage and recovery/security evidence. ZIP SHA-256 `b0d289dd2c6ba2fda22590b56b21130a3b8aad41702806391d03b4ed31a1c86e`.

All [899 pre-existing tracked contents/modes](e0/preservation-before-implementation.json) matched before work. The branch `codex/phase-2e-licensed-recognition` was created from that accepted merge, whose tree matched the reviewed specification. No accepted history was rewritten; application/API/BFF source, existing browser tests, migrations, contracts, application dependency locks and the full required workflow are preserved. Existing local services and research evidence were not reset. This checkpoint adds an isolated worker prototype, engineering tools/tests, source/dependency policies, a separate prototype workflow and review evidence.

## Material source-policy finding

The initial extension-based code projection included `dlib/image_processing/frontal_face_detector.h`, which contains a serialized pretrained HOG detector. It acquired 219,037 source bytes, SHA-256 `6de4864e431c5696225ae53501b3b9b5223db800c5354b40d48ad1096a76cd52`. The broad standard Python binding compiled that payload. **The initial claim that this source/build contained no pretrained material was incorrect.** The detector was never invoked, and no actual CNN/ResNet/five-point model file, 68-point model, dataset photograph or real child record was acquired/processed.

The original source and immutable Actions/Git evidence are preserved. Historical success proved only source integrity, import and generated-array transforms; it cannot clear A1b. The full disposition and corrective scope are in [SOURCE_POLICY_DISPOSITION.md](e0/SOURCE_POLICY_DISPOSITION.md). Acquisition is now hard-disabled before any review-file read or network call, so a green source check or fabricated unit review cannot advance the gate.

The corrected [minimal worker profile](e0/MINIMAL_WORKER_REVIEW.md) excludes both frontal-detector headers, every broad upstream Python binding, packaging entry points, photographs, datasets and unused vendored codecs. Its version-2 projection contains 1,141 pinned code/license blobs, 14,274,490 bytes. A semantic sentinel also rejects the known pretrained payload signature; file suffixes alone are not treated as sufficient. Original noncompliant source is retained privately and never reused as the new build context.

## Delivered executable scope

| Component | Delivered behavior | Limit / validation boundary |
|---|---|---|
| Code-only projection | Exact immutable source paths, size/Git blob comparison, actual SHA-256, bounded TLS transport, no archive/clone/redirect fallback, semantic pretrained-source exclusion | Approved dlib core pin remains `2e0b3846b4dcd0953951a9c0172503c666975229`; no new source/model family |
| Native source prototype | `_foc_dlib_native`, wheel `foc-dlib-native==0.1.0`; real dlib chip transforms; selected CNN/ResNet/predictor type declarations compile | No model constructor/loading, CNN detection, landmark prediction, embedding or retrieval API; `model_execution_api_available=false` |
| Offline build/runtime | Pinned Python 3.13.13 images, CMake 3.31.6, NumPy 2.3.3; source/build/wheel/image/SBOM/notices/runtime ELF inventory; inspected nonroot/read-only/no-egress/capability/resource controls | Actual Linux x86_64 hosted execution; local ARM is not qualification; no pretrained input in the clean probe |
| Approval primitives | Real Ed25519 verification on explicitly synthetic fixtures; closed scope/gate/digest/time/reviewer binding and revocation/independence denial | Does not issue review, provision real trusted keys or prove human review occurred; no browser approval endpoint |
| Integrity/unpack primitives | Separate Git/SHA-256/size identities; bounded single-stream bzip2 with trailing/concatenated/bomb/deadline negatives | Synthetic bytes only; not an OS sandbox or permission to decompress an actual weight |
| Encrypted intake tool | Frozen three-weight/48-image plan, exact HTTPS host/delegation checks, bounded transfer, AES-GCM private quarantine and separate keys, source/time/operator receipts; no decoding/unpacking/model call | Entry point hard-disabled by current policy; no quarantine asset/key set was created; no live dataset import or enrollment |
| Independent verifiers | Git-object/source/test/ZIP/checksum audit; separate encrypted-byte audit that never loads a model | Source prototype verified; actual model/image byte audit unexecuted because assets are unacquired |
| Testing/CI | 119 locked E0 control selectors, native generated-array probe, five native input denials; separate workflow; full prior application regression retained | These are source/security/geometry tests, never recognition success or governance approval |

The primitive accepts contiguous RGB uint8, exactly five bounded points and bounded image dimensions; fixes chip size 150×150/padding .25. It does not accept image filenames, URLs, arbitrary model paths, HOG, pickle or learned outputs. Old procedural fixtures and v1 score/normalization restrictions remain unchanged; no unsupported `licensed_demo_model` switch or weakened media hash gate was introduced.

## Executed evidence and publication gate

[Clean prototype verification](e0/CLEAN_SOURCE_PROTOTYPE_VERIFICATION.json) independently checks [push run 40957891039](https://github.com/wmostafagmail/FindOurChild/actions/runs/40957891039) on exact implementation source `a634328b014abc26e2413e18390a255be7eb9b61`:

- Artifact 12933817882, ZIP SHA-256 `2fede5d2ac2a3228886744139cd1f5a73617fab7b09ea784d462333c1f2472c2`.
- All 24 committed prototype inputs, 119 selected unit controls and 1,141 upstream source references matched. All control setup/call/teardown stages passed; no mandatory skips/retries. All 457 sanitized payload checksums matched.
- Actual CPython ABI `cpython-313-x86_64-linux-gnu`, dlib core version 20.0.0, compiled CUDA/AVX false; direct/batch/repeated chip outputs matched; five actual native input denials passed.
- Wheel `foc_dlib_native-0.1.0-cp313-cp313-linux_x86_64.whl`, 130,571 bytes, SHA-256 `4570ec9f896e6f88faed32e138690ebe1ccaaac344c6c553145dbcb6460361e5`.
- Generated-chip output SHA-256 `5c3bab292f6894aa2dc445d38311bb4531a7d4e8c33441a32f16a4dd1377a213`. One source-probe observation: 8.550996 ms for the reported primitive scope, peak RSS 40,912 KiB. These exclude actual model loading/inference and establish no per-photo latency target or statistical distribution.
- Actual loaded-library inventory: 41 ELF files; runtime packages `foc-dlib-native 0.1.0`, `numpy 2.3.3`, `pip 26.0.1`. Exact native bits/notices, build packages, dependency hashes and image ID are in the receipt/ZIP. Package-advisory scope is distinct from full native vulnerability/parser qualification.

Local Ruff and 203 foundation/configuration checks plus historical Phase 0 checks also passed. The application did already exist before this phase: its accepted-main results above are genuine application tests, not substitutes for current-head validation or future recognition tests.

**Final publication requires successful exact-current-review-head push and PR checks, complete source-bound artifacts and independent audits.** The final current-head run links, source/check/artifact identities and verification outcome are recorded in the [PR #11 review packet/checks](https://github.com/wmostafagmail/FindOurChild/pull/11) after inspection. The embedded receipt here deliberately identifies its actual execution SHA, rather than pretending that a documentation commit is self-referential execution evidence. No older result may substitute for that final gate.

The new source-prototype check is separate from the current protected-branch rule, which still requires `phase1a-required` (app 15368, strict/up-to-date). Administrators and conversation resolution are enforced; independent GitHub approvals are **not required** (count 0), force pushes/deletion are disabled. [Read-only settings snapshot](e0/MAIN_PROTECTION_SNAPSHOT.json). No protection setting was modified. An eventual actual-inference gate must become explicitly required before Phase 2E acceptance.

The preserved full workflow must execute every existing lane: 747 Python/API/real-PostgreSQL/RLS/security/integration/recovery tests, all 36 migrations/restore checks, and all 360 official TesterArmy targets. `e2e 0.21.3`, web engine `0.15.3`, Chromium/Firefox/WebKit × two locales × four widths remain pinned; deterministic assertions, zero retries/cache, zero external model calls and telemetry disabled remain unchanged. No local macOS trust retry or TLS bypass was used. New Phase 2E browser journeys are unimplemented/pending, not skipped-as-passed: 192 additional executions and the >=552 cumulative gate are still mandatory before Phase 2E acceptance.

## Failed and superseded attempts

[Attempt history](e0/CI_ATTEMPT_HISTORY.json) preserves run/head/event/status/artifact identities at its recorded observation time; later terminal updates are retained privately and in the final PR receipt. Full original logs/ZIPs remain in ignored mode-restricted `artifacts/raw/phase2e-e0/hosted-attempts/`; successful and failed original evidence is not overwritten. Earlier source observations in [E0_PROGRESS.md](E0_PROGRESS.md) and the [historical report snapshot](e0/HISTORICAL_REPORT_SNAPSHOT.md) remain explicitly historical.

| Finding | Corrective action / disposition |
|---|---|
| Initial standard source preflight subprocess failures | Original Actions logs retained. The first workflow did not publish its captured internal build diagnostic after failure; that specific original diagnostic cannot be recovered and its exact root cause is not invented. Later failed attempts preserve full diagnostics. |
| PNG-off standard binding compile error, undefined `T` in upstream header | Diagnosed from actual compiler output; system PNG linked in the diagnostic profile, without patching pinned source. This broad profile is now superseded and cannot authorize acquisition. |
| JPEG-off standard binding import failure, unresolved `save_jpeg` | Diagnosed from actual loader output; fixed diagnostic linkage. Final minimal probe has no image-file binding and requires neither codec. |
| Old setuptools/wheel advisory findings | Four advisory entries/three distinct IDs preserved in the original audit. Patched versions were checked; subsequent minimal packaging uses the standard library and removes those unused build dependencies. The application lock was not changed. |
| Embedded HOG data missed by extension-only source selection | Material A1b policy failure recorded, original source retained, acquisition hard-disabled; corrected semantic/path exclusions and narrow binding, review still required. |
| Minimal probe referenced an uninstalled generated revision header | Version now comes from the pinned core's exported CMake metadata; actual compile flags exposed/asserted. Failed attempt/artifact retained. |
| Superseded/canceled regression attempts during genuine source fixes | Not counted as passing. No unchanged failed attempt was retried into a success claim; current exact-head full validation must complete separately. |

## Licensing, benchmark and approval distinctions

1. **Functional engineering:** 119 E0 controls and the actual source-only geometry/runtime probe are measured above. Current full application regression must satisfy the exact-head publication gate. Complete 54 Phase 2E scenario groups and all E1/E2 features remain pending in [TEST_MATRIX.md](TEST_MATRIX.md).
2. **Facial recognition demonstration:** no named neural weight acquired, no dataset image body downloaded, no CNN/landmark/encoder execution, descriptor, distance, candidate rank or actual matching result. The incidental HOG source payload is separately disclosed; it was never invoked. Do not treat a chip transform or compiled graph declaration as recognition.
3. **Independent biometric accuracy:** unapproved and unmeasured. No Recall@K, FPIR/FNIR, rare-error bound, demographic fairness, childhood age-gap/longitudinal performance or NGO workload claim is made. Source-linked CGI views cannot establish those properties.
4. **Operational approval:** absent. Production/research/private-child data and credentials are not mounted; no operational recognition, public search, automatic identity/exclusion, custody disclosure or child release is enabled.

Exact publisher grants, immutable weight/image references, training-data provenance gaps, code/weight/media license distinctions and restrictions remain in [LICENSING_AND_COMPATIBILITY.md](LICENSING_AND_COMPATIBILITY.md), the original licensing packet and blocked qualification registry. Fresh [primary permission text checks](e0/permission-text-revalidation.json) matched the accepted evidence. Model-specific compressed/decompressed SHA-256 values remain unknown; they were not fabricated or inserted into the original false-flag proposal. The 48 image HEAD checks verified reference metadata and delegated HTTPS host only; signed redirect URLs were not retained. Collection-derived metadata retains CC-BY-SA-4.0 attribution/share-alike separation; individual image permission is CC0. No extra corpus/generator/restricted model was imported.

## Acceptance blockers and next boundary

| Gate / deliverable | Current status |
|---|---|
| A0 bounded owner implementation scope | Authorized by the master directive; not later gate approval |
| A1 source/license locks | Exact primary text/reference evidence retained; unexpected bundled source component disclosed/excluded; revised complete worker/build review still needed |
| A1b revised data-free worker | Native source prototype validated; **blocked for design/manifest review and complete narrow real-model API**. Intake policy false. Read [MINIMAL_WORKER_REVIEW.md](e0/MINIMAL_WORKER_REVIEW.md) before continuation. |
| A2/A3 actual weight/image acquisition and independent byte review | Pending/unexecuted; no actual asset manifest can be approved yet |
| A4 bounded scan/unpack/decode, separately approved limits and actual decompressed manifest | Pending/unexecuted; unit bzip2 tests do not approve real decompression |
| A5 native safe parser/load qualification | Pending/unexecuted; no model loader in the current bridge |
| A6 independent blinded fictional image/linkage review | Pending; publisher metadata is not human validation |
| A7 scoped private-inference permit | Pending; no real trusted reviewer/signing authority or execution permit was fabricated |
| E1 real detector/aligner/128D descriptor/jobs/pgvector/exact authorized L2 | Unimplemented; no new migrations or live operations |
| E2 NGO native-provider integration/AR-EN/authorization/revocation/recovery/8 browser journeys | Unimplemented; existing fixture workflow/regression preserved |
| Final Phase 2E acceptance / A8 | Blocked; this draft is an E0 review checkpoint only |

The approved A1b text requires a reviewed preflight manifest and says “If incompatible, revise only the isolated worker design for review”. The broad binding could not meet the data-free contract; this is why the concrete replacement is submitted for review before dependent work. This is a technical source/gate blocker, not an institutional operational-approval prerequisite being imposed on synthetic development. Do not enable the policy simply because a prototype job is green.

The Phase 2D performance plan/targets remain unchanged: accepted-main database p95 1189.443731 ms missed 1000 ms, and previous queue/database variability remains unresolved. No source-only timing closes those misses or the proposed 8-core/16 GiB neural p95 <=5 s / 30 s ceiling. All [Phase 3 manual Arabic, real screen-reader and 1,000+ history gates](../phase3/MANUAL_ACCEPTANCE_GATES.md) remain pending. The public-repository/security-governance limitations and zero required independent GitHub approvals remain carried forward; no repository visibility/history/protection weakening was performed.

## Reproduction and source inventory

Commands executed/required are retained in progress/attempt receipts. Core reproduction on a clean checkout:

```sh
uv sync --locked
.venv/bin/ruff check tools/phase2e services/demo_recognition tests/phase2e
.venv/bin/python -m tools.phase2e.test_controls
# Native Linux x86_64 only, fresh private directory:
.venv/bin/python -m tools.phase2e.qualify /absolute/fresh/private/workdir
# Independent source artifact audit (metadata fetched separately from GitHub):
python3 -m tools.phase2e.verify_source_evidence META_JSON ARCHIVE_ZIP CHECKOUT_SHA GIT_DIR
```

Existing full regression commands remain `.venv/bin/python -m scripts.dev test`, reporting/research/qualification/workflow validation, `scripts.recovery`, web type/build, `scripts.dev browser`, real identity/BFF HTTP lanes, coverage, audit and the strict artifact gate, exactly as committed in the preserved required workflow. Actual CI source/commands/selected IDs are captured by that workflow; the above command list is not an execution claim.

Source groups: `services/demo_recognition/` (native CMake/C++ probe, wheel/runtime entry point, locked requirements/Dockerfile), `tools/phase2e/` (projection, qualification, packaging/SBOM, approval/integrity/intake/verifiers/strict test runner), `config/phase2e/` (locks, metadata-only transport policy and enforced block), `tests/phase2e/` / `e0-required-tests.json` (119 selectors), separate prototype Actions workflow, and this review/evidence packet. Every actual changed file is available in the draft PR diff; no accepted migration/API/browser source was deleted or replaced.

Stop for the A1b review. Do not merge as completed Phase 2E, acquire/parse assets under a fake approval, implement Phase 2F/3 or activate operational matching.
