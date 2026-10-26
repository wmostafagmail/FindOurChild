# Independent benchmark specification

Version: qualification-preparation-1. Status: reproducible specification and synthetic arithmetic checks; real benchmarks **not run**. The sealed protocol, candidate artifacts, preprocessing, embedding-space identity, gallery composition, aggregation, random seeds and threshold/calibration rules must be signed before any approved real test. The independent evaluator controls truth and test unblinding; model developers cannot tune against test outcomes.

## Tasks and denominators

Primary task: missing-child probe against a private found-child gallery; secondary task: found-child probe against a missing-child gallery. Both remain research-only and disabled for operational cases. Report subject/case/image counts separately. Genuine-enrolled probes and genuinely absent open-set probes have separate denominators. Verify absence from the whole gallery, including aliases and all photographs, independently of model scores.

Recall@1/@10/@50 is the fraction of mate-present queries returning a genuine case within K, without a threshold. For a gallery smaller than K use all available cases; do not divide by K or exclude the query. Macro-average per child as primary, micro-query rates as supplementary. FNIR(T,K) is the fraction of mate-present queries failing to return a genuine case within K at or above frozen threshold T. FPIR(T,K) is the fraction of mate-absent queries returning any case above T. TPIR=1−FNIR on the same declared denominator. A wrong lead on a mate-present query is separately counted as reviewer burden, not hidden by FPIR. Similarity is not an identity probability.

These definitions follow [NIST 1:N evaluation](https://pages.nist.gov/frvt/html/frvt1N.html) and [NIST identification definitions](https://www.nist.gov/system/files/documents/2017/11/20/frvt_1n_api_v1.0.pdf). NIST's datasets, thresholds and reported scores are not child-domain validation or permission to obtain its images. Investigative ranked lists and research threshold curves remain distinct from automatic identity decisions, which are forbidden.

Report failure-to-acquire/enroll, no-face, multiple-face, invalid crop, quality rejection, inference timeout and missing metadata. Count eligible mate-present pipeline failures as misses in the primary intention-to-evaluate denominator. Conditional-on-success rates are supplementary and cannot replace it. An absent probe rejected before search must be reported as a processing failure as well as no returned false lead; it is not evidence of a safe high-accuracy recognizer. The current geometric adapter cannot measure these neural failure modes.

## Multiple photographs and case ranking

Baseline uses deterministic pre-score content-hash selection of at most three gallery photographs per case. One scheduled probe photograph is primary; a separately pre-registered three-probe/three-gallery max-pair arm measures multi-photo aggregation. Score a case by its highest approved pair score, return each case once, sort ties by stable case ID and cap lists at 50. Freeze photo budgets before scores are visible; reject duplicate query-gallery content and incompatible spaces. More photos inflate max scores, so calibrate each aggregation/gallery-size arm separately and report omitted photographs and unequal photo availability. Never apply a single-photo threshold to a multi-photo arm by assumption.

Synthetic tests cover fixed ranks 1/10/50/51, max-pair aggregation, stable three-photo budgets, tie/order behavior, duplicate/split/context denials and missed-threshold versus retrieved-hit distinctions. Actual child performance of these operators remains unmeasured. Alternative mean/quality-weighted aggregation is a separate registered ablation; do not select it from sealed test results.

## Longitudinal, quality and population experiments

Use the independent per-image age/date intervals and cohort plan in the governance protocol. Evaluate both directions of age gap and infancy-to-adolescence coverage, reporting known, unknown and cross-bin intervals. Include genuine positives with large age gaps and unrelated/sibling/twin hard negatives where separately authorized. Keep families in one partition and account for their correlation. No image generation or age estimation fills missing longitudinal evidence.

Pre-register source/resolution/lighting/blur/compression, pose yaw/pitch/roll and occlusion categories with annotation methods and reviewer agreement. Freeze quality/rejection thresholds on development/calibration only. Include natural difficult inputs and approved bounded corruptions as distinct arms; adversarial transformations do not establish real-world robustness. Report detector/alignment/quality and recognizer failures separately. No neural quality, pose, occlusion or demographic performance is measured by synthetic color-grid fixtures.

Report authorized demographic strata and intersections, unknowns, worst-group performance, uncertainty and coverage gaps. Do not infer protected traits from faces. Independent privacy review must approve aggregate cell release and prevent reconstruction from totals; suppressed cells are not replaced with zero. Address source/selection/verification bias and calibration transportability. Comparisons and multiple subgroup claims need a registered family-wise or false-discovery procedure and a statistician's approval.

## Calibration, uncertainty and sample power

Select any research threshold from calibration data only for a pre-approved FPIR target, and freeze it per artifact/provider/space/gallery/aggregation arm. Preserve score orientation, cohort eligibility and candidate budgets. No threshold is an operational activation decision. Keep test sealed; version and re-register any change that requires a new test. Training-overlap uncertainty blocks model qualification.

Use seeded subject/family-cluster bootstrap intervals for all Recall@K, FNIR, FPIR and workload estimates; report sampling unit, cluster weights, seed, replicates and denominators. At least 2,000 replicates is the proposed starting procedure, subject to independent statistical approval. Paired model comparisons resample the same clusters and retain covariance. Repeated images/pairs are not independent sample-size inflation. For truly independent one-trial-per-subject open-set samples, [NIST binomial interval methods](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm) provide a separate reference calculation; a bootstrap with zero events alone is not a rare-error guarantee.

For zero false-positive events among n independent absent-subject trials, the one-sided 95% exact binomial upper bound is 1−0.05^(1/n). At least 2,995 independent trials are needed to put that bound at or below 0.001; 29,956 for 0.0001. These are arithmetic planning examples, not approved targets, observed rates or authority to acquire that many subjects. Correlation, stratification, multiple testing and nonzero failures require a full revised power/interval plan. If evidence is insufficient, report the achieved bound or unavailable result and withhold the safety claim.

## NGO review workload and reproducibility

Report cases/photographs shown per query, genuine case rank, false leads for mate-present and absent queries, review burden at K=1/10/50, and an independently approved blinded human-review study using synthetic cases until separately authorized. Pilot review time assumptions are planning inputs, not measured staff performance. Include all-rejected lists and incorrect-match/human-rejection outcomes. Review never confirms identity, discloses custody or bypasses the existing two-person release controls.

An independent rerun must bind dataset/protocol/label/split hashes, artifact/component hashes, container/runtime/provider/hardware/precision pins, preprocessing/crop/quality/space versions, SQL/index settings, case/photo sampling and tie rules, seeds, calibration records and exclusion/failure logs. Verify exact-search recall first; future ANN loss and gallery-size dependence require separate measurement. Publish only approved aggregates and sanitized execution artifacts, never images, embeddings, identity linkages or raw score lists for children.

## Separately controlled age-progression experiment

No age-progression model or generated child image is used now. Any future arm needs independent generative-model/weight/training-data rights, child-data authority, explicit owner/ethics/DPO approval and a new protocol. Keep originals as controls, subject/family-disjoint generation and evaluation, provenance labels on all generated images, identical photo/review budgets, and paired real-ground-truth endpoints. Generated likeness is not evidence of identity or a replacement for longitudinal ground truth. No generated image enters an operational case gallery or release decision.
