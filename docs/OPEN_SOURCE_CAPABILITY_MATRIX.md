# Open-source capability matrix

Reviewed 23 October 2026. **Decisions below are architecture recommendations, not permission to deploy.** Source facts have high confidence only within inspected files; capabilities described in upstream docs have not been independently runtime-tested. No repository demonstrates validated Egyptian longitudinal child identification in this review.

Exact SHAs, local content hashes, source URLs and examined files are in [repository-lock.json](research/repository-lock.json) and [source-evidence.json](research/source-evidence.json). Every link below is commit-pinned. Source snapshots are retained solely as research evidence; no application dependency is approved by copying a snapshot.

| Repository | Decision | Code license | Weights/data clearance |
|---|---|---|---|
| morluto/rea | Adopt for bounded research only | MIT for REA-authored code; third-party notices/tool licenses separate. | No face weights/data included or approved; commercial native tools require separate licenses. |
| exadel-inc/CompreFace | Study only; optional isolated comparator after license review | Apache-2.0 root license. | FaceNet/InsightFace plugin choices do not inherit a universal weights/data clearance. Approve each exact model, detector and dataset separately. |
| deepinsight/insightface | Adapt an adapter for evaluation only after artifact rights clearance | README states MIT code; no root LICENSE file identified in reviewed tree, so preserve actual component notices before copying. | README explicitly restricts provided training annotations/models to non-commercial research, including auto-downloads; separate recognition-model licensing contact offered. NGO status alone is not clearance. |
| serengil/deepface | Adapt for evaluation harness only | MIT library. | README explicitly delegates detector/recognizer/attribute licensing to their original projects. Each exact weight and source dataset needs its own assessment. |
| mk-minchul/adaface | Study and evaluate quality-aware candidate, pending weights/data rights | MIT source, plus separate third-party notices under face_alignment. | Checkpoint links identify CASIA-WebFace, VGGFace2, MS1MV2/MS1MV3 and WebFace training sources; root MIT does not establish dataset/biometric deployment rights. |
| immich-app/immich | Study only; no product fork or copied code authorized by recommendation | AGPL-3.0 root license; obtain counsel interpretation before copying or modifications/network deployment. | Recognition source explicitly declares INSIGHTFACE; upstream weight/model-source terms need independent clearance beyond AGPL. |
| photoprism/photoprism | Study only; adopt provenance concepts through original implementation | AGPL-3.0 root source license. | Guide lists SFace/AuraFace as Apache-2.0 and InsightFace ArcFace as non-free/gated. Those are upstream declarations; verify original publishers' exact weights/data provenance before selection. |
| raigaurav26/FindTrace | Reject as production base; study failure modes only | No LICENSE file found in complete five-file tree; README has no reuse grant. Public visibility is not permission to incorporate code. | face-api.js library, TF/model artifacts and training-data rights must be reviewed separately; none cleared here. |
| pgvector/pgvector | Adopt initial vector storage/search, conditional on phase tests | PostgreSQL license in root LICENSE. | No weights or child data shipped as part of adoption; embedding artifacts governed separately. |
| qdrant/qdrant | Defer; alternate only after measured database limits | Apache-2.0 root source license. | No recognition weights; indexed production vectors remain sensitive personal data. |
| fastapi/fastapi | Adopt backend framework | MIT root source license. | No pretrained weights/data included in this adoption. |
| keycloak/keycloak | Adopt for staff identity, subject to operational ownership | Apache-2.0 LICENSE.txt. | No biometric face weights or datasets required. |
| temporalio/temporal | Defer initially; consider phase 4 durable operations | MIT server source; SDK/UI dependencies require separate inventory if adopted. | No recognition weights required. |
| minio/minio | Defer production selection; conditional local/provider candidate | AGPL-3.0 source; docs CC BY 4.0 per README; commercial AIStor is a separate licensing/support decision. | No face weights; stored media and vectors still require lawful basis. |

## morluto/rea

Reviewed commit: `9fd78a74f84a8e924bd58e7deaf5934bfb24f53c` (2026-10-23T19:14:34Z).

**1. Capabilities and limits:** CLI/MCP static JavaScript/TypeScript/HTML artifact graphs, evidence identities and explicit unknowns; native/runtime adapters require additional authorized targets and tools. Not a face recognizer or a security certification.

**2. Architecture:** Node CLI and stdio MCP share application workflows; isolated static source analysis, content-addressed evidence and graph projections.

**3. Reusable components:** Use CLI/MCP diagnostics, source relationship inspection and retained evidence. Never use speculative relationships as verified runtime behavior.

**4. Data/API contracts:** analyze-javascript-application accepts directory/ASAR; JSON Evidence has subject digest, graph, coverage, limitations and statistics. Codex setup/doctor explicitly select client.

**5. Runtime/hardware:** Published 6.7.0 accepts local Node 24.18.0; reviewed main has stricter engines. Native providers not configured; static JavaScript works without them.

**6. Performance evidence:** This run recorded static outputs and exit codes, not benchmark throughput. Successful exits still produced partial coverage.

**7. Security:** Static targets never executed; no live sessions, browser credentials or child records inspected. Setup changes only REA Codex registration; restart needed for discovery.

**8a. Code license:** MIT for REA-authored code; third-party notices/tool licenses separate.

**8b. Weights/data license:** No face weights/data included or approved; commercial native tools require separate licenses.

**9. Integration difficulty:** Low for CLI, medium for MCP client lifecycle and platform dependencies.

**10. Recommendation:** Adopt for bounded research only

**Evidence confidence and limitations:** High for inspected contracts and observed CLI; runtime integrations untested.

Sources inspected: [README.md](https://github.com/morluto/rea/blob/9fd78a74f84a8e924bd58e7deaf5934bfb24f53c/README.md), [docs/installation.md](https://github.com/morluto/rea/blob/9fd78a74f84a8e924bd58e7deaf5934bfb24f53c/docs/installation.md), [docs/client-configuration.md](https://github.com/morluto/rea/blob/9fd78a74f84a8e924bd58e7deaf5934bfb24f53c/docs/client-configuration.md), [docs/javascript-application-workflows.md](https://github.com/morluto/rea/blob/9fd78a74f84a8e924bd58e7deaf5934bfb24f53c/docs/javascript-application-workflows.md), [package.json](https://github.com/morluto/rea/blob/9fd78a74f84a8e924bd58e7deaf5934bfb24f53c/package.json).

## exadel-inc/CompreFace

Reviewed commit: `ddf32da8245e2e6688c3ab6f60587fd3e31538c2` (2023-11-14T08:13:44Z).

**1. Capabilities and limits:** Self-hosted face detection, verification and recognition services with subject examples; does not implement child safeguarding, longitudinal validation or custody review.

**2. Architecture:** Nginx/Angular frontend, Spring Boot admin/API, Python embedding core and PostgreSQL; API performs classification with ND4J, core runs stateless neural inference.

**3. Reusable components:** Study service abstraction, subject/example management and multiple-photo API patterns; avoid an entire parallel identity database initially.

**4. Data/API contracts:** REST recognition subjects/examples and recognition/verify/detection operations, x-api-key authentication, multipart/base64 image forms and similarity/bounding-box responses. These service keys are not our user/case authorization.

**5. Runtime/hardware:** Docker Compose on CPU/GPU variants; embedding core is the heavy component. Hardware must be measured against selected model and concurrency.

**6. Performance evidence:** README/architecture give scaling guidance; no reproducible child age-gap measurements collected. Reviewed latest commit is dated 2023-11-14; that is an observation, not proof of current security support.

**7. Security:** Keep behind internal service auth; tenant isolation, quotas, model artifacts, stale dependencies and media retention need independent review.

**8a. Code license:** Apache-2.0 root license.

**8b. Weights/data license:** FaceNet/InsightFace plugin choices do not inherit a universal weights/data clearance. Approve each exact model, detector and dataset separately.

**9. Integration difficulty:** Medium-high: additional Java/Python services and identity mapping.

**10. Recommendation:** Study only; optional isolated comparator after license review

**Evidence confidence and limitations:** High for source/docs architecture; low for operational suitability until tested.

Sources inspected: [README.md](https://github.com/exadel-inc/CompreFace/blob/ddf32da8245e2e6688c3ab6f60587fd3e31538c2/README.md), [LICENSE](https://github.com/exadel-inc/CompreFace/blob/ddf32da8245e2e6688c3ab6f60587fd3e31538c2/LICENSE), [docs/Architecture-and-scalability.md](https://github.com/exadel-inc/CompreFace/blob/ddf32da8245e2e6688c3ab6f60587fd3e31538c2/docs/Architecture-and-scalability.md), [docs/Rest-API-description.md](https://github.com/exadel-inc/CompreFace/blob/ddf32da8245e2e6688c3ab6f60587fd3e31538c2/docs/Rest-API-description.md), [embedding-calculator/src/services/facescan/plugins/insightface/insightface.py](https://github.com/exadel-inc/CompreFace/blob/ddf32da8245e2e6688c3ab6f60587fd3e31538c2/embedding-calculator/src/services/facescan/plugins/insightface/insightface.py).

## deepinsight/insightface

Reviewed commit: `c6c3af7bd2d0a0bf4b78c78437357f3521aa5d52` (2026-10-19T07:54:01Z).

**1. Capabilities and limits:** Detection, alignment and face embedding APIs; current README additionally advertises server/person-analysis/video features. None establishes safe child identification.

**2. Architecture:** Python FaceAnalysis orchestrates model packages and ONNX Runtime execution providers; larger repository includes training and detection implementations.

**3. Reusable components:** Evaluate fixed ArcFace-compatible recognition/detection pipeline and manifest checks, without person tracking or automatic reference updates.

**4. Data/API contracts:** FaceAnalysis prepares model/detector runtime and get(image) returns face records; exact fields follow chosen model package. Model identity and preprocessing must travel with vectors.

**5. Runtime/hardware:** CPU/CUDA/CoreML provider paths described upstream; installed provider/model/hardware compatibility is untested here. GPU may improve batching but is not assumed mandatory.

**6. Performance evidence:** Upstream accuracy, INT8 and large-scale search claims are not independently replicated and cannot be transferred to Egyptian children or age gaps.

**7. Security:** Disable automatic Internet model downloads in workers; verify weight hashes and explicit allowed tasks. No liveness requirement can be satisfied from a historical still image.

**8a. Code license:** README states MIT code; no root LICENSE file identified in reviewed tree, so preserve actual component notices before copying.

**8b. Weights/data license:** README explicitly restricts provided training annotations/models to non-commercial research, including auto-downloads; separate recognition-model licensing contact offered. NGO status alone is not clearance.

**9. Integration difficulty:** Medium engineering; high legal/data validation dependency.

**10. Recommendation:** Adapt an adapter for evaluation only after artifact rights clearance

**Evidence confidence and limitations:** High for stated license restrictions and inspected API orchestration; operational weight permissions unresolved.

Sources inspected: [README.md](https://github.com/deepinsight/insightface/blob/c6c3af7bd2d0a0bf4b78c78437357f3521aa5d52/README.md), [python-package/README.md](https://github.com/deepinsight/insightface/blob/c6c3af7bd2d0a0bf4b78c78437357f3521aa5d52/python-package/README.md), [python-package/insightface/app/face_analysis.py](https://github.com/deepinsight/insightface/blob/c6c3af7bd2d0a0bf4b78c78437357f3521aa5d52/python-package/insightface/app/face_analysis.py).

## serengil/deepface

Reviewed commit: `9749010f9950daf2cec20a1c5f054e2c0e312983` (2026-10-23T16:22:17Z).

**1. Capabilities and limits:** Multi-model verification, representation and search; optional demographic/streaming functions are unnecessary and excluded.

**2. Architecture:** Python facade delegates to detection, preprocessing, representation, verification, recognition and storage modules; inspected package now supports backend extras.

**3. Reusable components:** Convenient independent model wrappers and preprocessing comparisons; use explicit configurations, not implicit defaults.

**4. Data/API contracts:** DeepFace.verify/find/represent entry points; represent returns embeddings and facial-region data. Different wrapped models/detectors produce different contracts and score scales.

**5. Runtime/hardware:** Python and backend-dependent ONNX/TensorFlow/PyTorch dependencies. Source setup.py and version module inspected; no backend installed or CPU/GPU timing measured.

**6. Performance evidence:** Upstream benchmark tables do not establish longitudinal open-set child performance; no framework-level accuracy claim adopted.

**7. Security:** No arbitrary file/URL model endpoints; isolate image decoding, model downloads and unsafe serialized caches; API optional module not exposed publicly.

**8a. Code license:** MIT library.

**8b. Weights/data license:** README explicitly delegates detector/recognizer/attribute licensing to their original projects. Each exact weight and source dataset needs its own assessment.

**9. Integration difficulty:** Low-medium evaluation integration; medium-high production restriction surface.

**10. Recommendation:** Adapt for evaluation harness only

**Evidence confidence and limitations:** High for facade/source and license separation; no independent model result.

Sources inspected: [README.md](https://github.com/serengil/deepface/blob/9749010f9950daf2cec20a1c5f054e2c0e312983/README.md), [LICENSE](https://github.com/serengil/deepface/blob/9749010f9950daf2cec20a1c5f054e2c0e312983/LICENSE), [setup.py](https://github.com/serengil/deepface/blob/9749010f9950daf2cec20a1c5f054e2c0e312983/setup.py), [deepface/DeepFace.py](https://github.com/serengil/deepface/blob/9749010f9950daf2cec20a1c5f054e2c0e312983/deepface/DeepFace.py), [deepface/__init__.py](https://github.com/serengil/deepface/blob/9749010f9950daf2cec20a1c5f054e2c0e312983/deepface/__init__.py).

## mk-minchul/adaface

Reviewed commit: `c60eaa786a42c03444f3df7096dbaf9d57ae010d` (2024-06-10T14:47:39Z).

**1. Capabilities and limits:** Quality-adaptive recognition training loss and inference; paper benchmarks low-quality datasets. Quality adaptation is not evidence of age invariance.

**2. Architecture:** PyTorch backbone and adaptive margin loss; inference loads checkpoint state_dict and aligns faces.

**3. Reusable components:** Independent quality-aware embedding baseline, low-quality evaluation methodology; do not transplant legacy training environment into production.

**4. Data/API contracts:** inference.py converts PIL RGB to BGR tensor normalized to [-1,1], 112×112 input; model returns feature and norm. README commonly uses 512-dimensional features.

**5. Runtime/hardware:** Legacy README conda/PyTorch/CUDA instructions differ from requirements constraints; pinned requirements include Lightning 1.8.6 and a PyTorch upper bound. Modern port/ONNX parity needs testing.

**6. Performance evidence:** IJB/TinyFace and HQ validation results are upstream experiments, not Egyptian child age-gap validation.

**7. Security:** torch.load checkpoint deserialization requires trusted, hash-verified artifacts; avoid executing untrusted checkpoints and use safe supported loading/export workflows.

**8a. Code license:** MIT source, plus separate third-party notices under face_alignment.

**8b. Weights/data license:** Checkpoint links identify CASIA-WebFace, VGGFace2, MS1MV2/MS1MV3 and WebFace training sources; root MIT does not establish dataset/biometric deployment rights.

**9. Integration difficulty:** Medium-high due to old stack, export parity and provenance.

**10. Recommendation:** Study and evaluate quality-aware candidate, pending weights/data rights

**Evidence confidence and limitations:** High for explicit channel/crop implementation; weights/data approval and modern-runtime compatibility unresolved.

Sources inspected: [README.md](https://github.com/mk-minchul/adaface/blob/c60eaa786a42c03444f3df7096dbaf9d57ae010d/README.md), [LICENSE](https://github.com/mk-minchul/adaface/blob/c60eaa786a42c03444f3df7096dbaf9d57ae010d/LICENSE), [inference.py](https://github.com/mk-minchul/adaface/blob/c60eaa786a42c03444f3df7096dbaf9d57ae010d/inference.py), [requirements.txt](https://github.com/mk-minchul/adaface/blob/c60eaa786a42c03444f3df7096dbaf9d57ae010d/requirements.txt).

## immich-app/immich

Reviewed commit: `9666eadc5bbf81b91d2f5c10fb2630685dea8be7` (2026-10-23T12:27:22Z).

**1. Capabilities and limits:** Photo backup/search, metadata, faces and people, sharing; not a child-protection registry. Current recognition source explicitly names InsightFace model source.

**2. Architecture:** TypeScript/NestJS service with PostgreSQL, job infrastructure and Python ML service; web/mobile clients. Architecture prose may lag current source: confirm actual release topology before deployment.

**3. Reusable components:** Study ML boundary, detection-to-recognition dependency, photo/face association, reprocessing and UI subject correction.

**4. Data/API contracts:** FaceController has guarded CRUD/reassignment operations. ML repository defines multipart predict requests with facial-recognition detector/recognizer options; responses include image dimensions, boundingBox, serialized embedding and score.

**5. Runtime/hardware:** Inspected ML manifest requires Python >=3.12,<4.0 and ONNX/OpenCV dependencies; source version 3.3.0rc0 is not an approved stable deployment release.

**6. Performance evidence:** No application install or throughput measurement; image-library clustering benchmarks cannot substitute for authorized case retrieval.

**7. Security:** Sharing/map/EXIF capabilities are inappropriate defaults here. Face API permissions are not evidence that our tenant/case/federation safeguards already exist.

**8a. Code license:** AGPL-3.0 root license; obtain counsel interpretation before copying or modifications/network deployment.

**8b. Weights/data license:** Recognition source explicitly declares INSIGHTFACE; upstream weight/model-source terms need independent clearance beyond AGPL.

**9. Integration difficulty:** High as a base; low-medium as design reference.

**10. Recommendation:** Study only; no product fork or copied code authorized by recommendation

**Evidence confidence and limitations:** High for selected source interfaces; REA scope is two files only with unresolved imports.

Sources inspected: [README.md](https://github.com/immich-app/immich/blob/9666eadc5bbf81b91d2f5c10fb2630685dea8be7/README.md), [LICENSE](https://github.com/immich-app/immich/blob/9666eadc5bbf81b91d2f5c10fb2630685dea8be7/LICENSE), [docs/docs/developer/architecture.mdx](https://github.com/immich-app/immich/blob/9666eadc5bbf81b91d2f5c10fb2630685dea8be7/docs/docs/developer/architecture.mdx), [machine-learning/pyproject.toml](https://github.com/immich-app/immich/blob/9666eadc5bbf81b91d2f5c10fb2630685dea8be7/machine-learning/pyproject.toml), [server/src/controllers/face.controller.ts](https://github.com/immich-app/immich/blob/9666eadc5bbf81b91d2f5c10fb2630685dea8be7/server/src/controllers/face.controller.ts), [server/src/repositories/machine-learning.repository.ts](https://github.com/immich-app/immich/blob/9666eadc5bbf81b91d2f5c10fb2630685dea8be7/server/src/repositories/machine-learning.repository.ts), [machine-learning/immich_ml/models/facial_recognition/recognition.py](https://github.com/immich-app/immich/blob/9666eadc5bbf81b91d2f5c10fb2630685dea8be7/machine-learning/immich_ml/models/facial_recognition/recognition.py).

## photoprism/photoprism

Reviewed commit: `f0a4f41e5585aab070f3f688b8d4c0d6b5a10481` (2026-10-23T18:19:21Z).

**1. Capabilities and limits:** Photo indexing, face detection/embedding/clustering and model migrations; not identity or custody confirmation.

**2. Architecture:** Go backend and web frontend. Inspected face entity persists EmbedModel; SetEmbeddings rejects incompatible models/dimensions. Current docs describe ONNX SFace/AuraFace/ArcFace options and detector pairing.

**3. Reusable components:** Study model-space guards, artifact checksums, license gates and migration/audit patterns. Reimplement our domain requirements independently unless reuse terms approved.

**4. Data/API contracts:** Face entity stores model-specific embeddings; model/weight configuration affects geometry, dimensions and thresholds. Current guide explicitly separates detector provenance, embedding provenance and model migration.

**5. Runtime/hardware:** Go with optional ONNX shared library/TensorFlow configuration depending model; current docs warn binding/runtime version parity. Host-specific build/test not performed.

**6. Performance evidence:** Guide contains operator-library calibration and benchmarks with limitations; they are not child identity ground truth or our thresholds.

**7. Security:** Inspect EXIF/location exposure, model license acceptance and debug media. Setting an acceptance variable is not a substitute for obtaining legal permission.

**8a. Code license:** AGPL-3.0 root source license.

**8b. Weights/data license:** Guide lists SFace/AuraFace as Apache-2.0 and InsightFace ArcFace as non-free/gated. Those are upstream declarations; verify original publishers' exact weights/data provenance before selection.

**9. Integration difficulty:** Medium study, high fork/reuse due to different domain and license review.

**10. Recommendation:** Study only; adopt provenance concepts through original implementation

**Evidence confidence and limitations:** High for inspected model guards; original permissive weight provenance remains an additional review.

Sources inspected: [README.md](https://github.com/photoprism/photoprism/blob/f0a4f41e5585aab070f3f688b8d4c0d6b5a10481/README.md), [LICENSE](https://github.com/photoprism/photoprism/blob/f0a4f41e5585aab070f3f688b8d4c0d6b5a10481/LICENSE), [internal/ai/face/README.md](https://github.com/photoprism/photoprism/blob/f0a4f41e5585aab070f3f688b8d4c0d6b5a10481/internal/ai/face/README.md), [internal/ai/face/license.go](https://github.com/photoprism/photoprism/blob/f0a4f41e5585aab070f3f688b8d4c0d6b5a10481/internal/ai/face/license.go), [internal/entity/face.go](https://github.com/photoprism/photoprism/blob/f0a4f41e5585aab070f3f688b8d4c0d6b5a10481/internal/entity/face.go).

## raigaurav26/FindTrace

Reviewed commit: `f30bbf5e1d13670d42b7fa7ebaf8c6d4e6fd2295` (2026-07-16T14:44:12Z).

**1. Capabilities and limits:** Single HTML application with face-api.js embeddings, local case storage, camera loop, alerts and canvas aging effects. No verified evidence of reliable child age progression or secure NGO workflows.

**2. Architecture:** Inline browser JavaScript, localStorage, external CDN/model scripts, geolocation and IP fallback; no server authority boundary in supplied repository.

**3. Reusable components:** No code reuse proposed. Useful negative examples: score-to-confidence conversion, client-side sensitive records, location-linked alerts and synthetic images conflated with investigative value.

**4. Data/API contracts:** index.html uses face-api.js 0.22.2, descriptor distances, localStorage case/settings keys and fetch/geolocation calls. REA HTML result misses inline script semantics; derived-script analysis still partial.

**5. Runtime/hardware:** Modern browser/WebGL/camera permissions per README; not executed here. Model CDN assets not fetched or licensed by this review.

**6. Performance evidence:** README latency/FPS numbers are unreplicated without hardware/dataset methodology. IEEE publication claim not independently verified; repository LaTeX is not publication evidence.

**7. Security:** Source includes localStorage, external model URLs, IP geolocation, HTML interpolation and match-triggered location workflow. No runtime exploit assessment performed; not suitable for sensitive child deployment as supplied.

**8a. Code license:** No LICENSE file found in complete five-file tree; README has no reuse grant. Public visibility is not permission to incorporate code.

**8b. Weights/data license:** face-api.js library, TF/model artifacts and training-data rights must be reviewed separately; none cleared here.

**9. Integration difficulty:** Reject: rebuilding security/domain would replace most architecture.

**10. Recommendation:** Reject as production base; study failure modes only

**Evidence confidence and limitations:** High for source observations; runtime behavior, accuracy and publication claims unverified.

Sources inspected: [README.md](https://github.com/raigaurav26/FindTrace/blob/f30bbf5e1d13670d42b7fa7ebaf8c6d4e6fd2295/README.md), [index.html](https://github.com/raigaurav26/FindTrace/blob/f30bbf5e1d13670d42b7fa7ebaf8c6d4e6fd2295/index.html).

## pgvector/pgvector

Reviewed commit: `c82c81e22e48d32698e8d637442628f90ed84b8a` (2026-10-23T10:09:23Z).

**1. Capabilities and limits:** PostgreSQL vectors, exact nearest-neighbor queries, HNSW/IVFFlat approximate indexes, multiple distance operators; not a biometric model or authorization system.

**2. Architecture:** PostgreSQL C extension, SQL types/operators and index access methods.

**3. Reusable components:** Case-associated vector rows, exact-search baseline, versioned-space partitions and measured ANN migration.

**4. Data/API contracts:** CREATE EXTENSION vector; SQL vector types and distance operators including cosine distance. vector.control records 0.8.7 at reviewed SHA; enforce model space in our schema.

**5. Runtime/hardware:** README supports PostgreSQL 13+; source build needs server headers/toolchain or verified packaged extension. Memory/index sizing depends on corpus and dimensions.

**6. Performance evidence:** README documents HNSW memory/build tradeoffs and post-scan filtering; restricted queries may return too few results. Compare scoped ANN Recall@K with exact oracle before enabling.

**7. Security:** Database extension is privileged code; deployment allowlist and supply-chain review. RLS/grants are our responsibility and must be tested with actual query plans.

**8a. Code license:** PostgreSQL license in root LICENSE.

**8b. Weights/data license:** No weights or child data shipped as part of adoption; embedding artifacts governed separately.

**9. Integration difficulty:** Low-medium; medium for authorization-aware ANN tuning.

**10. Recommendation:** Adopt initial vector storage/search, conditional on phase tests

**Evidence confidence and limitations:** High for source SQL/control and documented filter limitation; actual scale unmeasured.

Sources inspected: [README.md](https://github.com/pgvector/pgvector/blob/c82c81e22e48d32698e8d637442628f90ed84b8a/README.md), [LICENSE](https://github.com/pgvector/pgvector/blob/c82c81e22e48d32698e8d637442628f90ed84b8a/LICENSE), [vector.control](https://github.com/pgvector/pgvector/blob/c82c81e22e48d32698e8d637442628f90ed84b8a/vector.control), [sql/vector.sql](https://github.com/pgvector/pgvector/blob/c82c81e22e48d32698e8d637442628f90ed84b8a/sql/vector.sql).

## qdrant/qdrant

Reviewed commit: `222b2e44ab1c3f17e8246396ead6558e45041df7` (2026-10-21T17:45:09Z).

**1. Capabilities and limits:** Vector search, filtering/payloads and REST/gRPC interfaces; cannot replace source-of-truth case grants or human review.

**2. Architecture:** Rust service, HTTP/tonic gRPC frontends, collection/segment storage and distributed consensus code.

**3. Reusable components:** Potential filtered vector search engine with tenant/model-space payloads; requires outbox-index synchronization and deletion reconciliation.

**4. Data/API contracts:** Collections/points/vectors/payload filters over REST/gRPC; OpenAPI inventory exists. Exact wire schema not fully reviewed in this phase; pin a release schema before implementation.

**5. Runtime/hardware:** Inspected Cargo.toml version 1.20.0, edition 2024, rust-version 1.98; release binary/container compatibility must be checked separately. CPU/RAM/SSD sizing measured by dataset.

**6. Performance evidence:** No benchmark reproduced. Vendor throughput claims and ANN settings depend on recall, filters, quantization and hardware.

**7. Security:** Private network, explicit API auth/TLS, no browser access. App enforces grants on retrieval and final hydration; index revocation lag can leak unless fail-closed.

**8a. Code license:** Apache-2.0 root source license.

**8b. Weights/data license:** No recognition weights; indexed production vectors remain sensitive personal data.

**9. Integration difficulty:** Medium-high: extra service and consistency/backup/security boundary.

**10. Recommendation:** Defer; alternate only after measured database limits

**Evidence confidence and limitations:** High for manifest/startup code; detailed API/runtime not validated.

Sources inspected: [README.md](https://github.com/qdrant/qdrant/blob/222b2e44ab1c3f17e8246396ead6558e45041df7/README.md), [LICENSE](https://github.com/qdrant/qdrant/blob/222b2e44ab1c3f17e8246396ead6558e45041df7/LICENSE), [Cargo.toml](https://github.com/qdrant/qdrant/blob/222b2e44ab1c3f17e8246396ead6558e45041df7/Cargo.toml), [src/main.rs](https://github.com/qdrant/qdrant/blob/222b2e44ab1c3f17e8246396ead6558e45041df7/src/main.rs).

## fastapi/fastapi

Reviewed commit: `7a0a3f0b286c6c865cf4398ea0e957a87b8bffa4` (2026-10-23T18:45:33Z).

**1. Capabilities and limits:** Typed Python API routing, validation, dependencies and OpenAPI generation; does not provide tenant isolation or secure workflows automatically.

**2. Architecture:** ASGI application over Starlette with Pydantic-oriented schema/validation integration; applications.py exposes routes, OpenAPI and dependency configuration.

**3. Reusable components:** Internal/public DTO separation, request validation, staff auth dependency, generated contract and structured errors.

**4. Data/API contracts:** HTTP JSON/multipart API, explicit response models and generated OpenAPI; disable public interactive internal docs in deployed sensitive environments.

**5. Runtime/hardware:** Inspected pyproject requires Python >=3.10; source version module 0.162.0. Pin a compatible release and full transitive lock in phase 1, not an untested source main.

**6. Performance evidence:** No benchmark replicated; asynchronous I/O does not accelerate CPU/GPU inference. Heavy processing belongs in bounded workers.

**7. Security:** Authentication/authorization, rate limits, safe uploads and redaction are application requirements; exception and validation responses must not echo sensitive values.

**8a. Code license:** MIT root source license.

**8b. Weights/data license:** No pretrained weights/data included in this adoption.

**9. Integration difficulty:** Low-medium, mainly domain controls and dependency compatibility.

**10. Recommendation:** Adopt backend framework

**Evidence confidence and limitations:** High for source API framework contracts; no installed application validated.

Sources inspected: [README.md](https://github.com/fastapi/fastapi/blob/7a0a3f0b286c6c865cf4398ea0e957a87b8bffa4/README.md), [LICENSE](https://github.com/fastapi/fastapi/blob/7a0a3f0b286c6c865cf4398ea0e957a87b8bffa4/LICENSE), [pyproject.toml](https://github.com/fastapi/fastapi/blob/7a0a3f0b286c6c865cf4398ea0e957a87b8bffa4/pyproject.toml), [fastapi/applications.py](https://github.com/fastapi/fastapi/blob/7a0a3f0b286c6c865cf4398ea0e957a87b8bffa4/fastapi/applications.py), [fastapi/__init__.py](https://github.com/fastapi/fastapi/blob/7a0a3f0b286c6c865cf4398ea0e957a87b8bffa4/fastapi/__init__.py).

## keycloak/keycloak

Reviewed commit: `ebaf01d2d794294a369416587e7afc490e1d7bbe` (2026-10-23T19:12:43Z).

**1. Capabilities and limits:** Identity/access management with OIDC/OAuth2 and SAML capabilities; organizations/case authorization must remain application controlled.

**2. Architecture:** Java/Quarkus server with realms, users, authentication flows, persistence and administrative APIs; source pom at reviewed head is 999.0.0-SNAPSHOT.

**3. Reusable components:** Staff OIDC login, mandatory MFA flow, logout/revocation and membership lifecycle integration; choose actual tested release rather than SNAPSHOT.

**4. Data/API contracts:** OIDC discovery, authorization-code flow with PKCE, JWKS and token/logout interfaces. Exact realm export/admin configuration and WebAuthn/OTP flow need phase 1 integration validation.

**5. Runtime/hardware:** JVM/container plus database; reviewed pom pins Quarkus 3.40.1.1. Released Java requirements and memory sizing not established by this source-only pass.

**6. Performance evidence:** No login/load or failover benchmark run; identity-provider availability is an operational dependency.

**7. Security:** Protected admin plane, strict redirect URIs, MFA/step-up, short sessions and no role claim as sole case-access authority. Keycloak admin is not automatically an application case reader.

**8a. Code license:** Apache-2.0 LICENSE.txt.

**8b. Weights/data license:** No biometric face weights or datasets required.

**9. Integration difficulty:** Medium-high operationally; medium integration.

**10. Recommendation:** Adopt for staff identity, subject to operational ownership

**Evidence confidence and limitations:** High for source manifest/license; MFA enforcement and release operation remain proposed/test-required.

Sources inspected: [README.md](https://github.com/keycloak/keycloak/blob/ebaf01d2d794294a369416587e7afc490e1d7bbe/README.md), [LICENSE.txt](https://github.com/keycloak/keycloak/blob/ebaf01d2d794294a369416587e7afc490e1d7bbe/LICENSE.txt), [pom.xml](https://github.com/keycloak/keycloak/blob/ebaf01d2d794294a369416587e7afc490e1d7bbe/pom.xml).

## temporalio/temporal

Reviewed commit: `7a98c28e70ec062b1a7f68c7bdebe07ca89ac32a` (2026-10-23T19:37:29Z).

**1. Capabilities and limits:** Durable workflow histories, timers and retried activities; does not make external effects exactly-once or grant business approval.

**2. Architecture:** Go frontend/history/matching/internal-worker services with persistent histories; SDK workers run application workflows/activities.

**3. Reusable components:** Potential long-running investigation reminders, delivery retries, approval expiry and reprocessing orchestration.

**4. Data/API contracts:** Workflow/activity interfaces via separately versioned SDK and server RPC. Event payloads should contain opaque IDs only; keep child details out of workflow histories.

**5. Runtime/hardware:** Reviewed go.mod requires Go 1.27.0 and retracts specified versions; source main is not a stable deployment pin. Requires persistence and worker fleet, local dev server not production topology.

**6. Performance evidence:** No workload replay, history growth or worker failure test run. Operational overhead is not justified by a measured pilot need yet.

**7. Security:** TLS/auth and namespace policy, history retention, encrypted payload handling and deterministic replay discipline required; retries recheck grants before effects.

**8a. Code license:** MIT server source; SDK/UI dependencies require separate inventory if adopted.

**8b. Weights/data license:** No recognition weights required.

**9. Integration difficulty:** High relative to initial leased jobs; useful once durable complexity warrants it.

**10. Recommendation:** Defer initially; consider phase 4 durable operations

**Evidence confidence and limitations:** High for documented architecture/source manifest; no operational verification.

Sources inspected: [README.md](https://github.com/temporalio/temporal/blob/7a98c28e70ec062b1a7f68c7bdebe07ca89ac32a/README.md), [LICENSE](https://github.com/temporalio/temporal/blob/7a98c28e70ec062b1a7f68c7bdebe07ca89ac32a/LICENSE), [docs/architecture/README.md](https://github.com/temporalio/temporal/blob/7a98c28e70ec062b1a7f68c7bdebe07ca89ac32a/docs/architecture/README.md), [go.mod](https://github.com/temporalio/temporal/blob/7a98c28e70ec062b1a7f68c7bdebe07ca89ac32a/go.mod).

## minio/minio

Reviewed commit: `7aac2a2c5b7c882e68c1ce017d8256be2feea27f` (2026-02-12T20:18:48Z).

**1. Capabilities and limits:** S3-compatible object storage with lifecycle/versioning/retention facilities in repository; does not by itself establish compliant secure child-data storage.

**2. Architecture:** Go object server and storage backends; object-layer interface supports put/get/delete and metadata operations.

**3. Reusable components:** S3 adapter compatibility, quarantine/original/derivative separation; prefer provider portability while support and legal review are unresolved.

**4. Data/API contracts:** S3 object operations and versioned keys behind our internal object IDs; presigned links are bearer capabilities and need application authorization/revocation strategy.

**5. Runtime/hardware:** go.mod Go 1.24.0/toolchain 1.24.8; README warns legacy precompiled binaries will not receive updates and describes source builds. Do not deploy an old floating Docker quickstart.

**6. Performance evidence:** No durability, hardware-failure or S3 load experiment reproduced; disk layout/redundancy and KMS integration must be tested.

**7. Security:** Private buckets, network-isolated admin plane, no default credentials, TLS, KMS, backup and object-version purge. WORM retention conflicts with erasure unless legally scoped.

**8a. Code license:** AGPL-3.0 source; docs CC BY 4.0 per README; commercial AIStor is a separate licensing/support decision.

**8b. Weights/data license:** No face weights; stored media and vectors still require lawful basis.

**9. Integration difficulty:** Medium-high: ongoing patch/support posture, key management and storage operations.

**10. Recommendation:** Defer production selection; conditional local/provider candidate

**Evidence confidence and limitations:** High for source/license/README maintenance warning; no deployed security or durability verification.

Sources inspected: [README.md](https://github.com/minio/minio/blob/7aac2a2c5b7c882e68c1ce017d8256be2feea27f/README.md), [LICENSE](https://github.com/minio/minio/blob/7aac2a2c5b7c882e68c1ce017d8256be2feea27f/LICENSE), [go.mod](https://github.com/minio/minio/blob/7aac2a2c5b7c882e68c1ce017d8256be2feea27f/go.mod), [cmd/object-api-interface.go](https://github.com/minio/minio/blob/7aac2a2c5b7c882e68c1ce017d8256be2feea27f/cmd/object-api-interface.go).

