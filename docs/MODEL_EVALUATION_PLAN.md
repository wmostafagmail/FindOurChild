# Model evaluation plan

Design only. The reproducible harness is specified here for phase 2 implementation; it has not been built or run during Phase 0.

## Data governance and identity ground truth

Evaluation uses synthetic fixtures for engineering behavior and separately consented/lawfully obtained real images for recognition metrics. Synthetic identities cannot establish real-child recognition performance. Require documented image provenance, identity verification independent of the model, authorized processing purpose, dataset license, retention expiry and permitted demographic annotations.

An independent custodian assigns pseudonymous subject/family groups and adjudicates disputed labels. Split train/development/calibration/test by subject, and group relatives/duplicates/capture sessions as needed to prevent leakage. Same child never appears across folds under aliases; use provenance review and duplicate checks. Temporal longitudinal probe/gallery images from the same subject belong within one evaluation fold. Freeze test access and keep model-training overlap uncertainty explicit; if training membership is unknowable, document rather than claiming leakage-free validation.

Production child photos cannot be used for training or benchmark development without a separately approved legal protocol. Public scraping of missing-child reports is excluded.

## Reproducible harness contract

Input manifest rows: pseudonymous subject/family IDs, image content hash, authorized dataset reference, partition, capture date/precision, birth/age interval, quality/occlusion labels, ground-truth verification method, permitted demographic strata and expiry. Sensitive mapping kept outside experiment artifacts.

Run manifest: code SHA, locked dependency set and OS/container digest, model/weights hashes, detector/aligner/preprocessing versions, seed, exact gallery/probe hashes, search parameters, aggregation/photo caps, feature/fusion version, thresholds, hardware/driver/runtime provider, thread/batch settings and timing protocol. Disable network access while executing. Export CSV/JSON metrics and privacy-reviewed aggregate plots; restricted failure examples remain access-controlled.

Proposed executable stages for phase 2:
`validate_manifest → enforce_splits → preprocess → embed → exact_search → optional_ANN_search → aggregate → rerank → evaluate → bootstrap → render_report`.
Cache only content-addressed compatible outputs with manifest checks; never silently reuse another model space. Deterministic ties use opaque case ID order after score, and are reported.

## Metrics and denominators

| Metric | Definition and required report |
|---|---|
| Recall@1/10/50 | Fraction of mate-present query cases with a true candidate case in first K; report macro per subject and query-level values, gallery size and number of true mates |
| False leads/query | Wrong cases returned above a review threshold, averaged over all probes; separate mate-present and mate-absent probes and top-K workload |
| FPIR | Fraction of mate-absent probes returning at least one candidate above fixed identification threshold |
| FNIR / TPIR | Mate-present identification misses/hits at thresholds and rank constraints; separate from pairwise FAR/TAR |
| Threshold sensitivity | Full development curves and frozen test operating points; subgroup values at the same global threshold |
| Lead review burden | Number of leads actually reviewed before finding a verified true lead; unsuccessful queries right-censored and reported separately |
| Calibration | Only if probability output is justified: held-out Brier/log loss/reliability bins with population/prior assumptions; otherwise mark uncalibrated |
| Retrieval approximation | ANN Recall@K relative to exact scoped search and true-label recall; include tenant/case-grant filter selectivity |
| Availability/performance | No-face/quality-reject rates, queue time, image processing p50/p95, memory/VRAM, throughput at fixed hardware and concurrency |

Prespecify age strata (e.g. 0–2, 3–5, 6–9, 10–13, 14–17), actual capture-gap strata (0–1, >1–3, >3–5, >5 years), quality, occlusion and consented population demographics. These are proposed bins, not claims of sufficient sample sizes. Unknown dates and uncollected demographics get explicit unknown rows. Small sample suppression and restricted disaggregated access preserve privacy without hiding known evaluation gaps.

Use subject-clustered bootstrap (proposed 2,000 resamples, fixed seed) for 95% intervals, preserving longitudinal dependence; compare models with paired subject resamples. For rare false events, add an appropriate exact/binomial interval at the independent probe unit. Zero observed false matches does not prove zero risk; determine sample size/power from NGO-approved tolerable harm and desired interval width before data collection.

## Experiments and controls

Same lawful gallery/probe manifests and review budget for each model. Compare individual image vs case aggregation, photo-count caps, quality warnings, metadata-only, face-only, fusion and age-aware variants. Keep blinded holdout and forbid threshold tuning on the test set. Test different photo counts to detect max-score false-match inflation. Include wrong chronology, similar names, relatives, lookalikes, replayed/edited photos, no-face and no-mate probes.

Ablate normalization, RGB/BGR, alignment, ONNX export/quantization and provider parity with tolerant numerical checks and retrieval-equivalence limits. Any quantized model gets a new manifest and full evaluation. Actual demographic fairness requires lawful labeled data and uncertainty; skin-tone heuristics are not ground truth.

## Human factors and release decision

Run a blinded staff pilot comparing reviewer decisions with/without ranking and explanations. Measure false-confirmation behavior, review burden, fatigue, accessibility and anchoring. Reviewer acceptance is not ground-truth identity.

Go/no-go requires a signed artifact listing target population/gallery size, Recall@K/FPIR/workload limits, subgroup/age-gap minimum evidence, confidence intervals, operational cost, failure examples and rollback plan. Numerical thresholds remain **unset** until evidence and NGO approval. Release cannot bypass a failing subgroup by labeling a model generally accurate. Restrict supported scope or remain manual.

Re-evaluate after model, weights, preprocessing, gallery growth, index, fusion, data-quality or population changes. Drift alerts create review tasks and can disable AI ranking; they never trigger claimant disclosure.

