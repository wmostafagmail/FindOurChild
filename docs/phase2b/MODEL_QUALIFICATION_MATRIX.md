# Model qualification matrix

Preparation reviewed 2026-10-26. No real recognizer is qualified, downloaded or executed. Declared hashes identify publisher references; they do not verify bytes we have not lawfully acquired. Training rights and legal authority for child evaluation remain separate gates. [Full artifact/provenance register](WEIGHT_PROVENANCE_REGISTER.md), [machine-readable records](../../config/qualification-models.json), [hashed new source evidence](research/source-lock.json), [preserved Phase 2A sources](../phase2a/research/source-lock.json).

| Profile | Artifact identity | Decision |
|---|---|---|
| insightface-buffalo-l | `w600k_r50.onnx`; binary digest unknown | Blocked before acquisition, evaluation and operation |
| adaface-ir50-ms1mv2 | `adaface_ir50_ms1mv2.ckpt`; binary digest unknown | Blocked before acquisition, evaluation and operation |
| opencv-sface-fp32 | `face_recognition_sface_2021dec.onnx`; publisher digest declared; bytes unverified | Blocked before acquisition, evaluation and operation |
| opencv-yunet-2023mar | `face_detection_yunet_2023mar.onnx`; publisher digest declared; bytes unverified | Blocked before acquisition, evaluation and operation |
| auraface-r100 | `glintr100.onnx`; publisher digest declared; bytes unverified | Blocked before acquisition, evaluation and operation |
| deepface-arcface-onnx | `arcface_weights.onnx`; publisher digest declared; bytes unverified | Blocked before acquisition, evaluation and operation |
| deepface-sface-onnx | `face_recognition_sface_2021dec.onnx`; publisher digest declared; bytes unverified | Blocked before acquisition, evaluation and operation |
| deepface-facenet512-onnx | `facenet512_weights.onnx`; publisher digest declared; bytes unverified | Blocked before acquisition, evaluation and operation |

The eight profiles cover the five requested families and separately identify the YuNet detector and three relevant DeepFace ONNX backends. They are not eight independent model families. Method names such as ArcFace and wrapper licenses are not weight identities or grants. INT8, alternate YuNet dates, converted graphs, alternate providers, FaceNet128, TensorFlow/PyTorch exports and bundled attribute models are different qualification objects; none is silently substituted.

InsightFace's non-commercial research restriction is not treated as NGO permission. AdaFace's MIT source does not establish the checkpoint or MTCNN weight grant. OpenCV's model-directory licenses and AuraFace's publisher Apache declaration do not establish the complete rights chain of training images. DeepFace release hashes do not establish upstream conversion or dataset rights. No upstream benchmark is adopted as evidence of longitudinal-child identification accuracy. No candidate is selected for operational use.

Qualification needs model-specific legal/provenance approval, independent detector/aligner clearance, an exact artifact and dependency closure, safely pinned runtime/provider, numerical/preprocessing parity, and separately authorized independent evaluation. Every unresolved item is retained per profile; changing a configuration flag cannot enable downloads or loading. Reconsider only through a separately reviewed change after the approval checklist is completed.
