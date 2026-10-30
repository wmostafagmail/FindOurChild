# A1b closed native component interface — second review packet

Status: architecture continuation authorized by the owner on 2026-10-30 at checkpoint `3442923`; **full A1b, acquisition, model deserialization and inference are not authorized**. Preserve the approved [artifact gates](../ARTIFACT_ACQUISITION_GATES.md). This packet is source-only engineering for a second review, not completion of E0/E1/E2.

## Compiled surface and execution barrier

`foc-dlib-native==0.2.0`, interface `foc-dlib-closed-interface-v2`, retains the exact dlib v20.0 core at `2e0b3846b4dcd0953951a9c0172503c666975229`, CPython 3.13.13 ABI, CMake 3.31.6, NumPy 2.3.3 and both pinned Linux x86_64 base-image digests. Application dependencies and behavior are unchanged.

`model_backend.cpp` defines and compiles all six actual dlib parser/forward-call bodies, in a separate translation unit with LTO disabled. A build audit requires all six linked symbols. This improves on the old `sizeof` declarations; it does **not** execute a neural network. Every backend entry first calls the separately compiled execution guard. That guard always denies: compile-time capability is false, and actual-manifest authority is unprovisioned. Changing the Python attribute, environment, CLI arguments or an unreviewed manifest cannot enable it. Python model construction, pickle, arbitrary files/URLs, callbacks, dynamic providers and broad upstream bindings are absent.

| Private worker call | Typed input / prospective output | Source-only result now |
|---|---|---|
| `prepare_components()` | No arguments, fixed three-component session | `a1b_second_review_required`; no filesystem open or parser |
| `detect(rgb)` | Contiguous uint8 H×W×3, 1–512 each dimension; prospective <=32 bounded rectangles | Input rejection or review denial; no CNN call |
| `predict_five(rgb, rectangle)` | Same RGB bound; exactly four inclusive, ordered, in-bounds integer coordinates; prospective five in-bounds integer landmarks | Input rejection or review denial; no predictor call |
| `encode_128(chip)` | Exactly 150×150 RGB uint8; prospective 128 finite native float-to-double components | Input rejection or review denial; no encoder call |
| `validate_detection_input`, `validate_landmark_input`, `validate_encoder_input` | Same typed bounds, no model state | Executable validation only; no face/quality/identity claim |
| Preserved `align_chip`, `align_chip_batch` | Generated RGB, five authored nondegenerate points, max1600×1600 | Actual dlib transform at150×150/padding.25; no predicted landmarks |
| `boundary_counters()` | No arguments | Review denials and zero model-open/parser/inference attempts; no paths or descriptors |

The 512-pixel detection ceiling, no resize/upsample, one image, <=32 detections, one direct descriptor/no jitter averaging, finite output and unnormalized L2 semantics are proposed fixed interface bounds. They must be included in any later reviewed preprocessing/space manifest and validated on the entire frozen demo set; no difficult-image substitution or automatic selection is authorized. Limits do not establish actual CNN memory, speed or detectability. Out-of-image detections and malformed outputs fail explicitly rather than being silently clipped/filtered.

## Fixed loading and artifact boundary

Only these internal immutable paths exist: `/opt/foc-demo/models/mmod_human_face_detector.dat`, `/opt/foc-demo/models/shape_predictor_5_face_landmarks.dat`, `/opt/foc-demo/models/dlib_face_recognition_resnet_model_v1.dat`. None is an input to Python. No file or directory at those paths is provisioned. All three optional actual-byte identities are absent; no fabricated SHA/size can be enabled.

The compiled loader accepts a fixed component's independently reviewed identity only through a sealed, private provisioned registry. There is no runtime setter, browser JSON manifest or signature bypass. Its future provisioning must occur after A3/A4 actual-byte review and requires a new exact build/manifest review; this packet does not provision trusted identities or implement/approve A4/A5/A7 authority. Flipping the capability constant alone still hits the unprovisioned-authority denial.

The integrity stream uses OpenSSL EVP SHA-256, not a new hash implementation. It opens each path component with `openat`/`O_NOFOLLOW`, rejects untrusted/writable parent directories, symlinks, hardlinks, devices/FIFOs, non-root ownership, writable files, unknown/zero identities, oversized files, size/digest drift and trailing bytes. Reads use one held read-only descriptor and a 64 KiB buffer; file identity/stamps and full digest are checked before and after parsing. No arbitrary-path interface is registered with Python. Root/host administrators and changes to supposedly immutable mounts remain governance threats; inode checks alone do not defeat privileged concurrent mutation.

The 64 MiB/file engineering ceiling is **not** A4 approval of decompressed limits. Native deserializers may allocate based on hostile metadata before application postconditions. Future A5 must separately exercise actual approved parsers/corruptions under hard process limits, and A7 must approve actual authority/resource settings. No model parse, including benign corrupt-model parse, is permitted by this review checkpoint.

After future authorized loading, the predictor must report five parts and bounded feature count; detector outputs must be finite/bounded; the encoder must produce128 finite components with bounded nonzero norm and no normalization. All backend exceptions are reduced to a fixed failure code and fault the session. Such a session cannot silently retry or publish partial results. Those model-dependent postconditions are compiled but **unexecuted**.

## Isolation and evidence

Qualification remains native Linux x86_64 only; ARM/emulation cannot pass `qualify.py`. Offline build and runtime use no model/media/application credentials. Runtime: UID 10001, read-only root, no mounts/network/devices/capabilities, no-new-privileges,2 CPUs,1GiB memory/swap ceiling,64 PIDs,64MiB noexec tmpfs and60s external timeout. The source probe additionally sets CPU10s, zero core dumps,1MiB regular-file output and64 FDs, with one native thread. Actual source-only timing/RSS is measured; no neural p95 is inferred.

The build manifest records immutable code/dependency inputs, wheel/image/SBOM/notices, OpenSSL/system libraries, actual compiler-generated header/source dependencies, six linked component symbols, native-test executable hash and source-policy audit. Exact source fingerprints are independently checked against Git objects and the original source receipt.

The 52 new native cases comprise32 typed-interface/closed-boundary cases and20 benign byte-stream integrity cases. The stream test executable links OpenSSL and the integrity helper only, **not a dlib model parser**. Its tiny root-owned fixtures are authored text, not fake weights. Five earlier transform input denials and actual generated-array transforms remain. The 136 locked E0 Python controls preserve every original119 selector and add17 source/approval negatives. No skip/retry can count as passing. Final review-head evidence is recorded in PR #11 after independent verification.

Separate independent human/source/license approval is still required. Automated independent evidence checks are not that approval. Stop before acquisition, deserialization, inference, E1/E2, Phase 2F/3 or merge.

Two unchanged font declaration headers are required transitively by dlib DNN input/drawing declarations. They are retained as code only; the encoded font implementation remains excluded. `NO_MAKEFILE` is never enabled; compiler-input auditing rejects any excluded implementation. The failed missing-header syntax diagnostic is preserved.
