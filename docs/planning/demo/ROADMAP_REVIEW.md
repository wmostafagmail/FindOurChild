# Revised roadmap review and validation

Date: 2026-10-27. Task scope is revised planning and public licensing research only. **No application implementation, weight/image acquisition, inference execution, actual child-data processing or operational approval process has started.**

## Deliverables and review state

[Phases 2D–3 roadmap](../../ROADMAP_PHASES_2D_3.md) supplies scope, dependencies, technical deliverables, tests, acceptance criteria, milestones and stop/review gates for each phase. It prioritizes an actual production-representative demonstration while keeping institutional operating approvals separate from permitted synthetic development. It preserves the original [Phase 2D proposal](../../phase2d/IMPLEMENTATION_SPEC.md), [Phase 2C readiness assessment](../../phase2c/READINESS_ASSESSMENT.md) and all earlier engineering/research decisions.

[Licensing assessment](DEMO_LICENSING_DECISION.md) identifies dlib v20.0 / three exact publisher public-domain model files and the separately licensed Syn-Vis-v0 individual images/curation. [Artifact proposal](DEMO_ASSET_PROPOSAL.json) records immutable refs and declared sizes/hashes for three weight files and 48 prospective images in 24 fictional groups, plus proposed preprocessing and split roles. No proposed artifact has `bytes_verified=true`, and all acquisition/integration/operational authorization fields remain false. A proposed filename/hash list is not an acquired/approved runtime fixture.

The model publisher's training sources, the dataset's nonrepresentative/stylized fictional content, generated-identity linkage, excluded demographic predictions, unknown binary SHA-256 and untested runtime suitability remain explicit limits. The code/model/image publisher grants are not claims of complete training-subject rights or real-child evaluation/operational qualification. Existing eight-profile blocked runtime configuration remains byte-identical.

The previous demonstration roadmap is retained verbatim after a dated pointer to the new phase roadmap. No history or old evidence is overwritten. PR #7 remains the unchanged six-file Phase 2C documentation PR at `aca8a2a`; this revised roadmap package is separate and does not alter its successful checks.

## Public research evidence

Eighteen exact primary source/metadata inputs are hashed in [source-lock.json](research/source-lock.json). They comprise pinned dlib source/model licenses, README and inert preprocessing example; publisher model Git blob/size metadata; Syn-Vis card, filename-only base/headshot links and image Git/LFS metadata; Qwen model card/license declarations; and canonical license texts. [Notices](research/NOTICE.md) retain attribution, exceptions and separate curation share-alike obligations. No image, dataset archive, model weight or inference package is in this evidence directory.

Research-service failures and omissions were not interpreted as permission. One metadata collector first assumed every generator listed a standalone license file; it stopped when Qwen-Image-Edit listed none. The corrected documentary collection preserves that absence and its model-card Apache declaration explicitly. No application test failed or passed through this research step, and the generator is not integrated. No public-data scrape, publisher/custodian contact, payment, account authorization or acceptance of gated terms occurred.

## Validation executed

Work was checked in an exact Git archive of `c4f623d0cd49c6d3ceca7724a30644038066c731` with only these documentary changes overlaid. The existing pinned Python environment executed:

```sh
FOC_GIT_DIR=/private/tmp/foc-phase1a-hosted-git \
  /private/tmp/foc-phase1a-runtime/.venv/bin/python -m scripts.check_foundation
```

Result: **180 foundation structural/configuration checks passed; both historical Phase 0 validators passed**. Separate documentary checks verified the new authored roadmap/assessment Markdown links (archived upstream README references retain their original repository context), new JSON parsing, all 18 exact evidence hashes/lengths, three selected model metadata refs, the excluded 68-point artifact, 48 image LFS refs/declared sizes, 24 disjoint fictional source groups and disabled authorization fields. These validate the proposed records, not model binaries, pixels, license compliance of a future build or inference quality.

Preservation checks compare all 191 accepted executable input hashes, all existing required inventories/locks/migrations, the prior Phase 2D proposal and the unchanged Phase 2C branch. The original 151-feature/630-case Phase 0 baseline and current 190-feature/1,216-case registry are unchanged. Previously passed 572 engineering cases and 644 pending future cases retain their statuses. No new phase test is implemented or marked passed.

The hosted 554 Python / 168 official TesterArmy executions belong to the previously verified Phase 2C head, documented in [its review](../../phase2d/SPECIFICATION_REVIEW.md). They are not a fresh hosted pass on this later planning commit. The revised package changes no executable source, dependency, schema or test configuration; no new application/model runtime suite is claimed executed here. All new 2D/2E/2F/3 suites and prospective 696 cumulative browser executions remain planning requirements.

Raw source research/proof remains separate from application artifacts; no child content, credentials, raw private browser captures or model vectors are exported. The previously recorded cloud-backed global working-tree read limitation is not represented as repaired; scoped documentary/index/source-preservation checks are used without replacing old evidence.

## Decision required before implementation

The package is ready for owner review. Approval must name the authorized phase(s) and exact demonstration acquisition scope before any download/build/integration. Recommended sequence is 2D, with 2E separately eligible for parallel approval, then 2F and Phase 3 review gates. An institutional operating decision is not requested as a prerequisite for fictional feature development.

Do not equate functional test success, synthetic neural results, independent authorized-data accuracy and operational approval. Those four report classes are defined separately in the roadmap. No scientifically validated missing-child accuracy, actual model compatibility, actual image suitability or operational permission has been established by this planning task. Stop after the roadmap and licensing assessment.
