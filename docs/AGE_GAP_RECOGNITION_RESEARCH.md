# Age-gap recognition research

Phase 0 literature and source review, 23 October 2026. No research images downloaded and no experiment executed. “Age-aware” is a proposed evidence-handling approach; **age-invariant child recognition has not been demonstrated for this platform**.

## Evidence ledger

| Source | Evidence actually inspected | Finding | Confidence / limitations |
|---|---|---|---|
| [Deb, Nain & Jain, arXiv:1711.03990v1](https://arxiv.org/abs/1711.03990v1), ICB 2018 DOI 10.1109/ICB2018.2018.00042 | Author abstract and author-hosted paper search excerpt | CLF covers 919 subjects, ages 2–18, with repeated images over up to six years; compares FaceNet, a commercial matcher and fusion | High for paper description, no replication; access rights and identity provenance not established for our use |
| [Bahmani & Schuckers, arXiv:2204.01760v1](https://arxiv.org/abs/2204.01760v1), 2022 | Author abstract | YFA analysis reports age-gap-related score decay across tested matchers even over short intervals; studies quality-aware MagFace | High for authors' reported finding, no independent measurements; controlled acquisition and short gaps limit missing-child transfer |
| [Longitudinal Evaluation of Child Face Recognition and the Impact of Underlying Age, IJCB 2024](https://ieeexplore.ieee.org/document/10744505), DOI 10.1109/IJCB62174.2024.10744505 | Indexed publisher abstract; direct publisher page returned robot/JavaScript challenge | Describes evaluation over longer time gaps and age-group dependence | Medium: indexed abstract only; do not treat reported numbers as independently reviewed full-paper evidence |
| [Kim, Jain & Liu, AdaFace, arXiv:2204.00964v2](https://arxiv.org/abs/2204.00964v2) | Author abstract plus pinned repository README/inference.py | Quality-adaptive margin uses feature norms; low-quality benchmarks motivate evaluation | High for method description; neither age-invariance nor Egyptian child accuracy follows |
| [FindTrace pinned source](https://github.com/raigaurav26/FindTrace/blob/f30bbf5e1d13670d42b7fa7ebaf8c6d4e6fd2295/index.html) | Direct source and REA static outputs | Procedural canvas aging and descriptive prediction requests; no validated longitudinal retrieval protocol found in inspected source | High for source mechanisms; publication and performance claims unverified |

Paper summaries are evidence about specific experiments, not a promised accuracy level. Verification TAR/FAR at a chosen threshold cannot be substituted for open-set identification FPIR or Recall@K in a large operational gallery.

## Proposed evaluation candidates

1. Licensed InsightFace/ArcFace recognition with pinned detector/aligner; research permissions explicitly verified before use and distinct operational license before deployment.
2. AdaFace quality-aware embeddings as an independent model family; verify checkpoint/training-data rights, BGR input and safe checkpoint handling.
3. A DeepFace-wrapped independently licensed comparator (e.g. a specific FaceNet or SFace artifact after original-source review); a wrapper is not an independent model if it loads the same weights as candidate 1.
4. SFace and AuraFace are leads for additional original-publisher license/provenance assessment because the inspected PhotoPrism guide lists permissive weight licenses. They are **not yet cleared model choices**.
5. MagFace is a literature-motivated follow-up comparator, outside the required repository set; code/weights/data due diligence has not been performed here.

No artifact is selected for production. A manifest must pin weights and preprocessing hashes, source commit, license text and data-provenance assessment before any lawful evaluation.

## Experiments to pre-register

Baseline A: real photos only, each capture searched independently, case aggregation at a fixed photo budget. Baseline B: same model with transparent age/date intervals and metadata candidate union. Compare with quality-only and metadata-only ablations. Baseline C: independent model family, same split/gallery and preprocessing parity checks.

Evaluate actual photo age gaps, not only time missing. Report unknown/estimated gaps separately and stratify by youngest photo age. Include low quality, occlusion, siblings/relatives and no-mate probes; lawful representation of intended Egyptian population is required. Do not use names or case identifiers to leak identity into benchmark labels or split selection.

Any synthetic progression experiment remains isolated: compare original-only against original-plus-synthetic at the same review budget and gallery size; measure false-positive inflation and identity drift, with generator/version lineage. Generated images remain watermarked/labeled research artifacts, never “updated real photo” evidence. Production remains disabled absent measurable held-out benefit, no unacceptable harm, legal basis and safeguarding approval.

## Explicit unresolved gaps

- Lawful access to enough independently verified longitudinal Egyptian child identities, especially infants and large multi-year gaps.
- Whether candidate weights' training populations/provenance permit ethical deployment and overlap with evaluation subjects.
- Open-set identification performance under actual photo quality, gallery size, siblings and uncertain chronology.
- Reproducible age-gap calibration with confidence intervals rather than imported adult pairwise thresholds.
- Effect of missing/incorrect capture dates, low-resolution historical images and scanning artifacts.
- Whether any progression method improves real target retrieval rather than perceived resemblance; no validated method established here.
- Reviewer anchoring, workload and possible harm from convincing false leads.
- Model independence, export/runtime numerical parity and long-term drift monitoring.

Owner of closure: ML lead with NGO safeguarding and privacy/legal owners. Lack of sufficient lawful evaluation data is a blocker to phase 2/3 operational activation, not a reason to reuse public missing-child photographs.

