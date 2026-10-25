# Model benchmark status

**Zero recognition models have run or been qualified.** All real candidates are blocked before download/use for missing exact artifact/data clearance, and no real evaluation dataset/protocol is authorized. [Licensing decisions](LICENSING_MATRIX.md) distinguish code, weights and training data for every candidate. Upstream benchmark claims are not Find Our Child measurements.

| Candidate | Recognition benchmark | Exact checkpoint/runtime compatibility | Child age-gap/open-set/fairness qualification |
|---|---|---|---|
| InsightFace / ArcFace buffalo pack | Not run | Not installed; hashes/entitlement unresolved | Pending |
| AdaFace IR50/MS1MV2 | Not run | Not installed; safe checkpoint loading/runtime and rights unresolved | Pending |
| DeepFace ONNX ArcFace/SFace wrapper candidates | Not run | No backend/weights installed; per-backend terms unresolved | Pending |
| OpenCV SFace / YuNet | Not run | No ONNX binary installed; exact provenance/rights unresolved | Pending |
| AuraFace-v1 | Not run | No weights installed; exact training provenance/rights unresolved | Pending |

The executable engineering harness processes 32 geometric PNGs with a weight-free pixel-grid adapter and one separate analytic open-set vector. [Local smoke checkpoint](synthetic-smoke-checkpoint.json) records 16 gallery images, 17 probes, 16 mate-present probes, one mate-absent probe and 16 pseudonymous subjects. Its Recall@1/10/50 values are 0.0625/0.625/1, FPIR 0 on one synthetic absent probe and FNIR 0.9375 at the arbitrary frozen synthetic threshold. These figures validate accounting and reproducibility; they do not measure face recognition, age invariance, fairness, child-safety risk or a usable threshold. Zero observed false events on one fixture establishes no real-world risk bound.

Synthetic capture metadata places these fixtures in an over-five-year capture-gap bin and a 10–13-year probe capture-age bin. Those are invented fixture labels, not longitudinal photographs. Unknown/cross-bin inputs and split leakage are tested separately. Other age/demographic/quality strata, statistical power, independent ground truth, real model-training overlap and deployment-gallery behavior remain unmeasured. The subject-clustered bootstrap exercises an implementation path; a tiny artificial corpus cannot provide a scientific confidence claim.

Exact PostgreSQL retrieval is checked against independent Python search under photo caps and authorization filters. ANN/HNSW approximation parity is not run and no ANN index is enabled. Timing describes only bounded synthetic Python image processing; no neural CPU/GPU throughput, provider parity, memory/queue capacity or operational SLO is established.

The required hosted artifact will bind the smoke aggregate to the committed source and locks; it must retain `synthetic_smoke_only`, `recognition_accuracy_claim=false`, `real_models_benchmarked=0` and `operational_threshold=unset`. Qualification needs separately approved exact artifacts and a lawful real dataset/protocol, independent review, population/age-gap evidence and release approvals. Phase 2B and operational recognition remain disabled.
