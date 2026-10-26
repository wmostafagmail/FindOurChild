# Weight and training-data provenance register

All references observed 2026-10-26. No binary bytes were fetched. Publisher Git LFS pointers and release metadata are hashed as text/JSON; mutable release tags and main-branch URLs are not immutable transport approval. A future approved acquisition must hash the actual bytes and compare every component before parsing. Unknown means unresolved, never cleared.

## insightface-buffalo-l

Source revision: `c6c3af7bd2d0a0bf4b78c78437357f3521aa5d52`. Prospective filename: `w600k_r50.onnx`. Publisher SHA-256: `UNKNOWN`; declared bytes: `UNKNOWN`. Actual binary verification: **not performed**.

Code: MIT source declaration; component notices separate.

Weights: Non-commercial research restriction; NGO purpose not presumed permitted; no project-specific grant.

Training lineage: WebFace600K model-zoo lineage; exact training subjects/authority and overlap unknown. Exact dataset editions, source agreements, subject authority/withdrawals, redistribution permissions, geographic/purpose restrictions, training overlap and lawful child-domain evaluation authority remain unresolved.

Detector/alignment: buffalo_l det_10g.onnx plus five-point norm_crop; detector weights separately restricted/unverified.

Preprocessing: 112-pixel landmark-aligned crop; source RGB blob and conditional embedded graph normalization; exact graph contract/parity unverified. These are source-derived requirements or proposals, not graph/runtime parity results.

Decision: **blocked**. Unresolved: exact binary verification after lawful acquisition approval; model and every detector/aligner grant for NGO longitudinal-child evaluation; complete training-data identities, versions, rights and overlap review; independent evaluation dataset and protocol approval; safe serialization/provider/runtime pins and numerical preprocessing parity; independent age-gap/open-set/quality/demographic evaluation.

## adaface-ir50-ms1mv2

Source revision: `c60eaa786a42c03444f3df7096dbaf9d57ae010d`. Prospective filename: `adaface_ir50_ms1mv2.ckpt`. Publisher SHA-256: `UNKNOWN`; declared bytes: `UNKNOWN`. Actual binary verification: **not performed**.

Code: MIT code; third-party alignment terms separate.

Weights: Exact checkpoint grant unknown. README Drive reference is an identifier, not a license.

Training lineage: Named MS1MV2 checkpoint; MS-Celeb derivative provenance, exact subject rights, removals and overlap unresolved. Exact dataset editions, source agreements, subject authority/withdrawals, redistribution permissions, geographic/purpose restrictions, training overlap and lawful child-domain evaluation authority remain unresolved.

Detector/alignment: Provided MTCNN alignment; every bundled alignment checkpoint requires independent clearance.

Preprocessing: 112x112 BGR, image/255 then mean 0.5 and std 0.5. Output feature norm separated from cosine L2 normalization; checkpoint torch.load must not execute. These are source-derived requirements or proposals, not graph/runtime parity results.

Decision: **blocked**. Unresolved: exact binary verification after lawful acquisition approval; model and every detector/aligner grant for NGO longitudinal-child evaluation; complete training-data identities, versions, rights and overlap review; independent evaluation dataset and protocol approval; safe serialization/provider/runtime pins and numerical preprocessing parity; independent age-gap/open-set/quality/demographic evaluation.

## opencv-sface-fp32

Source revision: `48b10fa505aeb51fbd127fc60a5c660040e823b7`. Prospective filename: `face_recognition_sface_2021dec.onnx`. Publisher SHA-256: `0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79`; declared bytes: `38696353`. Actual binary verification: **not performed**.

Code: Directory Apache-2.0 declaration.

Weights: Publisher directory Apache-2.0; exact LFS identity declared, bytes not verified; training-data clearance missing.

Training lineage: Complete exact training corpus, versions, lawful subject authority and overlap not established. Exact dataset editions, source agreements, subject authority/withdrawals, redistribution permissions, geographic/purpose restrictions, training overlap and lawful child-domain evaluation authority remain unresolved.

Detector/alignment: Pin YuNet 2023mar separately; OpenCV FaceRecognizerSF.alignCrop with detected landmarks.

Preprocessing: Use native alignCrop/feature contract; input BGR and OpenCV internal graph preprocessing require pinned-runtime parity. Quantized variants are different models; example thresholds not adopted. These are source-derived requirements or proposals, not graph/runtime parity results.

Decision: **blocked**. Unresolved: exact binary verification after lawful acquisition approval; model and every detector/aligner grant for NGO longitudinal-child evaluation; complete training-data identities, versions, rights and overlap review; independent evaluation dataset and protocol approval; safe serialization/provider/runtime pins and numerical preprocessing parity; independent age-gap/open-set/quality/demographic evaluation.

## opencv-yunet-2023mar

Source revision: `48b10fa505aeb51fbd127fc60a5c660040e823b7`. Prospective filename: `face_detection_yunet_2023mar.onnx`. Publisher SHA-256: `8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4`; declared bytes: `232589`. Actual binary verification: **not performed**.

Code: YuNet directory MIT declaration.

Weights: MIT directory declaration; no inference/binary verification or full training provenance.

Training lineage: Exact detector training-data rights/provenance and child-domain failure behavior unresolved. Exact dataset editions, source agreements, subject authority/withdrawals, redistribution permissions, geographic/purpose restrictions, training overlap and lawful child-domain evaluation authority remain unresolved.

Detector/alignment: FaceDetectorYN detect outputs bounding box and five landmarks; frame scale and thresholds must be frozen.

Preprocessing: BGR image, configured detector input size, score/NMS/top-k from pinned wrapper; validate no-face/multi-face/small-face failures separately. 2026may and INT8 artifacts excluded. These are source-derived requirements or proposals, not graph/runtime parity results.

Decision: **blocked**. Unresolved: exact binary verification after lawful acquisition approval; model and every detector/aligner grant for NGO longitudinal-child evaluation; complete training-data identities, versions, rights and overlap review; independent evaluation dataset and protocol approval; safe serialization/provider/runtime pins and numerical preprocessing parity; independent age-gap/open-set/quality/demographic evaluation.

## auraface-r100

Source revision: `af6d057c9b0ec4071d4c49c80e3539258798b609`. Prospective filename: `glintr100.onnx`. Publisher SHA-256: `a7933ea5330113b01c9b60351d8f4c33003f145d8470ac5f0e52ee2effe25c60`; declared bytes: `260694151`. Actual binary verification: **not performed**.

Code: Inference would use separately licensed InsightFace code; none adopted.

Weights: Publisher Apache-2.0 model grant declaration; full rights chain not established.

Training lineage: Card describes commercially/publicly available sources, without exact datasets, licenses or subject authority. Exact dataset editions, source agreements, subject authority/withdrawals, redistribution permissions, geographic/purpose restrictions, training overlap and lawful child-domain evaluation authority remain unresolved.

Detector/alignment: Bundled scrfd_10g_bnkps.onnx has declared LFS identity but independent license/data chain unresolved. Attribute and 3D models excluded.

Preprocessing: 512-dimensional ArcFace-derived recognition expected from publisher; proposed InsightFace landmark alignment. Exact input color/normalization/graph contract and output parity remain unverified. These are source-derived requirements or proposals, not graph/runtime parity results.

Decision: **blocked**. Unresolved: exact binary verification after lawful acquisition approval; model and every detector/aligner grant for NGO longitudinal-child evaluation; complete training-data identities, versions, rights and overlap review; independent evaluation dataset and protocol approval; safe serialization/provider/runtime pins and numerical preprocessing parity; independent age-gap/open-set/quality/demographic evaluation.

## deepface-arcface-onnx

Source revision: `b748cb4e3622d3beaca9a3b60abcc2ee77617a8a`. Prospective filename: `arcface_weights.onnx`. Publisher SHA-256: `a897e00dcf6f15e99f7218f8ed081550ebd38c7115c434772faa7c488eb6ad40`; declared bytes: `136588094`. Actual binary verification: **not performed**.

Code: MIT wrapper, not blanket weights clearance.

Weights: Release asset declared digest; conversion chain and exact checkpoint grant unresolved.

Training lineage: Exact source checkpoint and original training corpus/rights unestablished for exported graph. Exact dataset editions, source agreements, subject authority/withdrawals, redistribution permissions, geographic/purpose restrictions, training overlap and lawful child-domain evaluation authority remain unresolved.

Detector/alignment: Every selected detector and alignment path needs separate clearance; do not use wrapper defaults.

Preprocessing: Pinned wrapper declares 112x112 and 512 output. ONNX export follows channels-last input; upstream normalization selection must be frozen and tested, not assumed equal to InsightFace. These are source-derived requirements or proposals, not graph/runtime parity results.

Decision: **blocked**. Unresolved: exact binary verification after lawful acquisition approval; model and every detector/aligner grant for NGO longitudinal-child evaluation; complete training-data identities, versions, rights and overlap review; independent evaluation dataset and protocol approval; safe serialization/provider/runtime pins and numerical preprocessing parity; independent age-gap/open-set/quality/demographic evaluation.

## deepface-sface-onnx

Source revision: `b748cb4e3622d3beaca9a3b60abcc2ee77617a8a`. Prospective filename: `face_recognition_sface_2021dec.onnx`. Publisher SHA-256: `0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79`; declared bytes: `38696353`. Actual binary verification: **not performed**.

Code: MIT wrapper plus separately licensed OpenCV artifact.

Weights: Mutable main URL is not accepted as an immutable artifact; expected pinned OpenCV LFS digest recorded only.

Training lineage: Same SFace training-provenance gap; wrapper does not clear it. Exact dataset editions, source agreements, subject authority/withdrawals, redistribution permissions, geographic/purpose restrictions, training overlap and lawful child-domain evaluation authority remain unresolved.

Detector/alignment: Wrapper detection/alignment is not automatically native OpenCV alignCrop; compare landmark geometry independently.

Preprocessing: Pinned wrapper takes BGR 112x112 [0,1], multiplies by 255, casts uint8, reverses to RGB, transposes NCHW float32; fixed graph batch 1. Separate preprocessing space from native path. These are source-derived requirements or proposals, not graph/runtime parity results.

Decision: **blocked**. Unresolved: exact binary verification after lawful acquisition approval; model and every detector/aligner grant for NGO longitudinal-child evaluation; complete training-data identities, versions, rights and overlap review; independent evaluation dataset and protocol approval; safe serialization/provider/runtime pins and numerical preprocessing parity; independent age-gap/open-set/quality/demographic evaluation.

## deepface-facenet512-onnx

Source revision: `b748cb4e3622d3beaca9a3b60abcc2ee77617a8a`. Prospective filename: `facenet512_weights.onnx`. Publisher SHA-256: `a7a4fbcc6af3175f5c4e91de0b92b4fa387e0e9f141efd59616337220363da33`; declared bytes: `93956456`. Actual binary verification: **not performed**.

Code: MIT wrapper only.

Weights: Release hash declared; upstream checkpoint/conversion/redistribution grant unresolved.

Training lineage: Source FaceNet512 training dataset and exact version/rights not established by wrapper. Exact dataset editions, source agreements, subject authority/withdrawals, redistribution permissions, geographic/purpose restrictions, training overlap and lawful child-domain evaluation authority remain unresolved.

Detector/alignment: Detector, face selection, alignment and resize/normalization variants require separate specification.

Preprocessing: Wrapper declares 160x160 and 512 output; ONNX base takes channels-last BGR after selected upstream normalization. Do not conflate 128d, PyTorch, TensorFlow and ONNX artifacts. These are source-derived requirements or proposals, not graph/runtime parity results.

Decision: **blocked**. Unresolved: exact binary verification after lawful acquisition approval; model and every detector/aligner grant for NGO longitudinal-child evaluation; complete training-data identities, versions, rights and overlap review; independent evaluation dataset and protocol approval; safe serialization/provider/runtime pins and numerical preprocessing parity; independent age-gap/open-set/quality/demographic evaluation.

## Additional component references

AdaFace R50/MS1MV2 README identifies Drive file `1eUaSHG4pGlIZK7hBkqjyp2fc2epKoBvI`; the exact checkpoint's binary digest and grant are unknown. The Drive target was not fetched. InsightFace buffalo_l additionally requires `det_10g.onnx`; the exact package/binary identity remains unresolved.

AuraFace's pinned publisher tree declares `scrfd_10g_bnkps.onnx` as SHA-256 `5838f7fe053675b1c7a08b633df49e7af5495cee0493c7dcf6697200b85b5b91`, 16,923,827 bytes. This is metadata, not binary verification or detector training-data clearance. Bundled landmark/attribute files are excluded. Recognition-file licensing is not blanket clearance for them.

DeepFace ArcFace/FaceNet512 release asset IDs are 601316846/601326180. The frozen observed metadata stores declared digest, size and modification date; a future replaced asset must fail identity verification. The SFace wrapper points to mutable upstream main; only the separately pinned OpenCV identity is a prospective expected reference, not proof of what a future mutable URL returns.

No legal entitlement is inferred from a public URL, repository popularity, publisher safety badge, code license, nonprofit purpose or an unverified third-party redistribution. Publisher contact and document exchange require separate authorization; no messages were sent. Obtain signed, purpose-specific documentation rather than downloading to investigate rights after the fact.
