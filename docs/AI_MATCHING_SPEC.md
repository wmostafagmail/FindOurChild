# AI matching specification

Proposed contract v0.1. No weights installed, no child photos processed, no calibrated thresholds approved.

## Versioned pipeline

| Stage | Input → output | Required gate/failure |
|---|---|---|
| 1. Intake | Upload intent → immutable quarantine object version/checksum | Authenticated capability, size/type/expiry limits |
| 2. Validate/scan | Raw bytes → verified decoded image record | Signature/MIME agreement, bounded dimensions/pixels, decompression limits, malware engine/signature version; fail closed on scanner outage |
| 3. EXIF handling | Original → access-restricted original + sanitized derivative | Preserve original encrypted; orientation applied before metadata removal; never expose GPS, device IDs or embedded thumbnails |
| 4. Detect | Sanitized oriented pixels → boxes/landmarks | Approved detector checksum; record no-face and detector failures |
| 5. Select subject | Multiple boxes → staff-confirmed face region | Never choose largest face automatically; no-face uses metadata-only investigation |
| 6. Align | Selected landmarks → model-specific crop | Record transform and template; no silent unaligned substitution |
| 7. Assess quality | Crop → resolution/blur/pose/occlusion warnings | Model-specific warning limits; poor images may be held or searched with warning |
| 8. Embed | Crop → finite vector, manifest, quality | Exact approved weights, dimension/dtype/normalization validation |
| 9. Index | Vector/provenance → space-specific index version | Legal basis active, case revision unchanged, subject approved |
| 10. Retrieve | Each query photo → compatible image candidates | Opposite registry and authorized case scope only |
| 11. Age-aware rank | Image pairs and capture/birth intervals → soft evidence | No hard age exclusion; no inferred exact birthday |
| 12. Fuse metadata | Independent candidate union → ranked case leads | Missing features neutral; contradiction/source confidence explicit |
| 13. Human review | Lead/evidence → hold/reject/investigate decision | No automated identity/custody decision |
| 14. Reprocess/audit | New model/policy/evidence → new run | Preserve previous run; deletion/revocation invalidates stale writes |

Worker adapters expose `detect`, `align`, `quality`, `embed` and `search` independently. Each returns a schema version, manifest checksum, input object version, warnings, timing and failure category. Image processors run without network egress with read-only models and bounded CPU/memory/time.

Every embedding stores source image and face IDs, organization/case ID, model identifier/version/checksum, dimension, preprocessing version, quality, processing timestamp, index version and source revision. Compatibility is an explicit immutable embedding-space identity, never dimension equality alone. RGB/BGR differences and alignment changes create distinct preprocessing identities.

## Multiple photographs and candidate union

For each usable query image retrieve top L image neighbors per compatible model, then map neighbors to case IDs. Cap photos per case per retrieval run with a documented sampling policy to prevent a case with hundreds of duplicates dominating retrieval; deduplicate identical images and near-duplicate captures. Record omitted photos and completeness.

Candidate universe = union(face retrieval, normalized-name retrieval, age/date/region retrieval, distinguishing-feature retrieval). Metadata-only cases remain eligible. Preserve a fixed review quota from each independent retrieval channel so metadata reranking cannot erase all face-only or metadata-only candidates. Quotas and L/K are evaluation parameters, not production defaults.

For a provisional single-model case score, let pair similarity be cosine only within its compatible space. Use the best valid pair as the primary retrieval score and report a bounded corroboration summary from additional independent good-quality captures. Do not average all photographs: one poor photo must not depress an otherwise strong lead. Max selection can inflate false matches when many photos exist; benchmark by photo count, cap independent corroboration, and report that selection effect.

Different models retain separate score components. Before validation, combine ranked lists by reciprocal rank rather than averaging raw cosine values:
`RRF(case) = Σ_channel w_channel / (k0 + rank_channel(case))`.
A missing channel contributes no vote and is explicitly unknown. Weights/k0/quota versions are frozen per experiment. Scores are lead priority signals; not identity probabilities.

## Metadata features

| Feature | Proposed representation |
|---|---|
| Age | Compare possible birth-date intervals derived from reported age at known dates; overlap supports compatibility, disjoint intervals create a soft warning scaled by source uncertainty |
| Names | Store submitted spelling; search-only Arabic Unicode normalization, remove tatweel/diacritics, normalize selected alef/ya variants with versioning; transliteration and edit distance as additional candidate channels |
| Dates | Missing/discovery/capture intervals with precision; impossible claimed chronology is a review flag, not automatic rejection |
| Geography | General regions and feasible travel-time ranges; unknown region neutral; do not use current shelter location in ranking output |
| Distinguishing marks | Structured location/type and staff-curated text evidence; contradictory testimony remains visible |
| Reliability | Source verification, evidence provenance and reporting quality; never infer trustworthiness from demographics |

Do not collapse ta marbuta to ha or every name variant into one irreversible string. Preserve original Arabic/English text for human inspection. Sex, when reliably reported, may be contextual evidence but is not a hard exclusion. Do not infer race, emotion or gender from faces.

## Age gaps and synthetic evidence

Compare historical photos separately across all observed age intervals; calculate actual elapsed capture time when dates are verified and label estimated gaps separately. Age-gap reranking starts as transparent soft compatibility and quality uncertainty; learned age adjustments require independent held-out longitudinal data.

Synthetic age progression is research-only, in a separate store/index namespace with immutable synthetic flags and source/model lineage. Synthetic outputs cannot become actual evidence, enter the default production index, establish identity or train on production children. Any experiment must test real-photo retrieval improvement and false-positive changes against the unmodified baseline at a fixed human-review budget.

## Output contract

A lead includes run ID, both case references subject to authorization, retrieval channels/ranks, per-model distance/metric and provenance, source image pairs, quality/age-gap warnings, supporting/contradictory/unknown features, policy/index version, calibration status, review state and a plain-language caution. No “97% match” field. Raw embeddings stay internal and never enter notifications.

Rejections bind a candidate pair, evidence revision and model/policy version. New evidence can reopen a rejected lead with a reason; old rejections must not silently suppress a newly justified investigation.

## Go/no-go

All model artifacts need explicit weights/data rights, hashes, preprocessing reproducibility and approved evaluation release. Licensed research use does not imply permission for NGO operational deployment. Production activation remains blocked until legal, technical and safeguarding owners approve measured thresholds and subgroup/age-gap limits.

