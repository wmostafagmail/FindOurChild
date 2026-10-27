# Phase 2B qualification preparation — validation report

Status: **technical preparation validated; owner review pending**. Phase 2B is not accepted automatically. No real model is qualified, no real-child dataset is authorized, and operational recognition remains disabled. This report distinguishes executed engineering checks from pending scientific/legal/model qualification.

## Accepted entry gate

[PR #5](https://github.com/wmostafagmail/FindOurChild/pull/5) merged at `0d5abdaa713c504ef9bd90b7ec0fdd04e4a8accd`. [Required exact-main CI 40294754349](https://github.com/wmostafagmail/FindOurChild/actions/runs/40294754349) succeeded at that commit. Its tree matched reviewed head aff6420. Independent verification bound 166 execution-source files and 53 archive checksums to merged main (447 Python, 168 official browser executions, 24 migrations). [Phase 2A acceptance](../phase2a/ACCEPTANCE.md), [merge proof](../phase2a/main-merge-verification.json). Phase 2B began only after this gate passed.

## Delivered preparation

Branch: `codex/phase-2b-model-qualification`. Eight model/component profiles cover InsightFace/ArcFace, AdaFace, native SFace/YuNet, AuraFace and three relevant DeepFace ONNX backends. Publisher LFS/release identities are distinguished from actual binary verification and rights clearance. [Qualification matrix](MODEL_QUALIFICATION_MATRIX.md), [weight/data-provenance register](WEIGHT_PROVENANCE_REGISTER.md), [additional original-author provenance research](TRAINING_PROVENANCE_RESEARCH.md). Existing 22 source/license snapshots are preserved; 15 new pinned source/pointer/metadata records are hashed. No pretrained weight bytes, training dataset or portraits were downloaded, installed or executed. Source inspection did not import those modules.

[Dataset governance](DATASET_ACQUISITION_GOVERNANCE_PROTOCOL.md) defines independent identity verification, lawful authority, subject/family/event disjointness, historical per-image uncertainty, representative longitudinal cohorts, access, withdrawal, retention/deletion and independent approval. [Benchmark specification](INDEPENDENT_BENCHMARK_SPEC.md) defines Recall@1/10/50, FPIR/FNIR, open-set tasks, case/photo aggregation, infancy-through-adolescence strata, quality/pose/occlusion failures, confidence/power and NGO review burden. Age progression is a separately controlled future experiment. [Hardware/safe inference plan](HARDWARE_INFERENCE_PLAN.md), [security/privacy assessment](SECURITY_PRIVACY_ASSESSMENT.md), [blockers and approvals](BLOCKERS_APPROVAL_CHECKLIST.md).

Executable preparation adds closed model/source/publisher-identity checks, unconditional acquisition denial, fixed synthetic artifact integrity, allowlisted geometric dataset/independent-permission/leakage gates, bounded max-pair multi-photo arithmetic and independent-trial uncertainty calculations. A distinct disposable PostgreSQL cluster and internal-only network hold synthetic metadata, with four FORCE RLS relations, no case-service roles/schemas/credentials/storage or public ports, and native metadata recovery/revocation validation. The application API, browser flows, 49-operation contract, all 24 prior application migrations and seven accepted lock files are unchanged. Existing Phase 2A app-database research tables remain synthetic integration fixtures, never a child-data lab.

## Exact-source hosted execution

Implementation `ee7486c854b2052d61f797b6a381f0f9cb7d1522` passed every step of [full hosted run 40310140640](https://github.com/wmostafagmail/FindOurChild/actions/runs/40310140640). [Run metadata](hosted-ci-verification.json), [archive metadata](hosted-artifact-metadata.json), [independent verifier proof](hosted-artifact-verification.json), [sanitized results](../../artifacts/phase2b-sanitized/results.json).

| Executed suite | Passed |
|---|---:|
| Foundation unit/API/real PostgreSQL/RLS/security/integration | 158 |
| Identity/MFA/authorization regression | 58 |
| Reporting/media/worker/safeguarding regression | 109 |
| Actual scanner-outage/fail-closed regression | 1 |
| Actual reporting BFF/API HTTP regression | 6 |
| Research synthetic pipeline/evaluation/real PG/security/adversarial | 113 |
| Actual authenticated research capability/BFF HTTP | 2 |
| Qualification preparation, manifest/artifact/dataset negatives and separate real PG/RLS | 107 |
| **Python total** | **554** |
| Official TesterArmy Chromium | 56 |
| Official TesterArmy Firefox | 56 |
| Official TesterArmy WebKit | 56 |
| **Official TesterArmy total** | **168** |

All seven browser titles run against actual Next/API/Keycloak/PostgreSQL/scanner/storage/worker services across 24 targets: three engines × ar-EG/en-GB × widths 320/360/390/1280. Pinned official runner/web/Playwright: **0.21.3/0.15.3/1.64.1**. Zero test retries, mandatory skips, model-assisted steps or external testing-model tokens; zero ordinary Playwright-only acceptance tests. Synthetic unit checks do not substitute for the real-service integration assertions. All passing counts are actual executions; pending/failed/canceled/unexecuted cases are not passed.

All 24 checksum-verified application migrations, existing tenant/RLS/authorization tests, application backup/restore and vector/photograph cleanup checks passed. The separate lab's one initialization SQL created four forced-RLS metadata relations; actual cross-organization, missing-context, expiry, revocation, privilege-escalation, lineage and forbidden-real-class negatives passed. Native pg_dump/restore retained nonempty synthetic metadata, forced RLS and revoked access; subsequent revocation also denied reads. This is not real-photo deletion or old-backup tombstone certification.

Combined API/migration coverage: **1305/1384 lines = 94.29190751445087%**, above the 75% floor. Dependency audits found zero known npm/Python vulnerabilities at execution. Pinned Ruff checks, types/build, 179 structural/configuration checks and historical Phase 0 checks passed.

Archive `12645650250` SHA-256: `34f5fe6f8c47e477b065538c19f5fbdc4a73cf453d94b880fbd54760a407a053`. Independent verification checked **191 committed execution-source blobs**, **53 payload checksums**, 48 input-free PNGs and 168 minimized traces. Source fingerprint: `2513f3776af7a360d7c22acc864bd537435ecf7b959c7e2f33f031787baf27fa`. The verifier imports no application validation helper. Reports expose only allowlisted IDs/status/counts/coverage and closed recovery summaries; no child pixels, vectors, subject manifests, names, contacts, credentials, custody locations or raw DOM/process logs are published. Raw failure logs/dumps remain private.

The final evidence-only review head must also complete the full workflow. Its exact final push/PR CI, archive digest and read-only independent verification are recorded in the draft PR after completion; its execution fingerprint must equal this report's fingerprint. The PR remains draft and unmerged for owner review.

## Traceability and preservation

[Canonical traceability](../testing/test-matrix.json) preserves every original 185 feature row and the immutable Phase 0 151-feature/630-case baseline. Five QLF rows add all 107 executable selectors, one native lab recovery/isolation gate and 12 pending external real qualification/approval cases. Current registry: **190 features / 1216 logical cases; 572 passed, 644 future cases pending**. These logical cases are not a browser/Python execution count. Prior real-model qualification rows remain pending; no preparation test establishes actual child-identification accuracy. [Traceability details](TEST_TRACEABILITY.md), [required inventory](required-tests.json), [source inventory](SOURCE_INVENTORY.md), [dependency manifest](locked-dependency-manifest.json).

## Failures and corrective actions

[Attempt history](hosted-attempts.json) retains original failure/cancellation references; none is counted as passed. First source 3b44dd0 failed the pinned lint gate with 12 violations in new files; service setup was skipped, so later HTTP/cleanup stages also lacked services. Fixed unused/import/UTC/dictionary issues and explicit subprocess check=False, formatted only new files, and reran the exact full lint command and strict qualification suite.

Corrected-source run 40305567193 attempt 1 was canceled after over twenty minutes of slow Azure Ubuntu package transfers. Attempt 2 was superseded by a reproducible provisioning fix: only the ephemeral Linux runner's Azure mirror URI changes to Ubuntu's primary HTTPS archive, retaining suites/components/signing keys and adding 30-second APT HTTP/HTTPS timeouts with two package-transfer retries. Test retries remain zero; framework versions, engines and assertions are unchanged. On the fully passing source, browser dependencies/binaries installed in **39 seconds**. [Procedure and primary references](CI_TEST_GATES.md). No macOS keychain or OS storage setting was changed.

Initial local qualification stopped before tests when macOS canceled a source read. A scratch collection hook typo and initial reporter without timestamps were rejected; completed test bodies from that rejected run were not accepted as validation. The fixed strict 107-case suite and native restore passed in a verified-main execution mirror; [checkpoint evidence](local-validation.json) records its own source digest, not a claim of current-head browser execution. Foundation structural checks used the actual immutable baseline Git object store. Local Git reads also stalled on cloud-backed files: staged-tree commits and new objects were checksum-verified in the existing mirror and copied back without rewriting history or discarding files/index evidence. The working-tree check subsequently completed cleanly. Hosted execution uses a fresh Git checkout and supplies canonical full-suite evidence.

## Limits and readiness decision

**Zero real recognition models qualified or benchmarked; zero real child photographs processed.** Publisher-declared digests are not downloaded-byte verification. Exact weight/component grants, training-corpus editions/rights/subject authority/removals/overlap, legal/DPO/ethics approval and independently verified longitudinal ground truth remain unresolved. A related safetensors release does not clear training rights or remote custom code. No runtime/provider/CPU/GPU inference compatibility or minimum hardware requirement has been verified.

Synthetic ranks, age labels, confidence calculations and geometric embeddings verify engineering arithmetic. They do not establish child recognition, rare-error safety, demographic robustness, pose/occlusion quality, longitudinal generalization or an operational threshold. Full approved-data inference/cluster-bootstrap/fairness execution, provider parity, neural no-face/multiple-face failures, performance/ANN and generative age-progression experiments remain pending separate approval and measured evidence. Proposed hardware/retention/power numbers are planning inputs, not approvals or observed model results.

The container lab is not certification against a privileged host/Docker administrator. SQL context is trusted internal state, not authentication for arbitrary raw-SQL users. Revocation affects subsequent READ COMMITTED statements; cancellation, already-read bytes and old-backup tombstone/deletion verification require a separately approved real-data system. All earlier legal, safeguarding, hosting, key-custody and child-release gates remain. Current main protection retains strict/up-to-date phase1a-required including administrators, resolved conversations and no force-push/deletion; **independent code review is not required: zero approvals configured**. No rules changed; committed YAML alone is not protection evidence.

Preparation is ready for owner review when the final draft-PR head's full CI and source-bound archive verification complete. No acquisition, real evaluation, public facial search, automatic identity decision, custody disclosure or operational activation is authorized. Stop after Phase 2B preparation.
