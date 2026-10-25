# Phase 2A validation report

Status: **synthetic Phase 2A foundation technically validated; awaiting owner review in [draft PR #5](https://github.com/wmostafagmail/FindOurChild/pull/5)**. No Phase 2A acceptance, real-model qualification or operational activation is claimed. [Architecture and limits](ARCHITECTURE.md), [licensing matrix](LICENSING_MATRIX.md), [required executable inventory](required-tests.json).

## Verified entry and scope

Phase 1C accepted only after PR #4 merged into main at `1f6af0e99a32c2002beac842790c4f56f6b7e1e0` and required hosted run `40227138621` succeeded on that exact commit. Independent artifact verification checked 126 Git blobs, 53 payload hashes, 332 Python tests, 168 TesterArmy executions (56/browser), 21 migrations and 93.47% coverage. [Acceptance proof](../phase1c/main-merge-validation.json). Archive SHA-256: `cd5602398f86fe92c798255932ce4774bdcf5d786ea017ec0d4f2ad12e908a6c`.

Dedicated branch: `codex/phase-2a-model-qualification-foundation`. Operational recognition, public biometric search, automatic identity confirmation, custody disclosure and Phase 2B remain disabled. Synthetic data only. The research role is not a runtime login and has no operational case/image access.

## Exact hosted validation

Implementation `975b1fa8f5fa12274dfaafdd51153540eca9c08a` passed [required PR run 40233614540](https://github.com/wmostafagmail/FindOurChild/actions/runs/40233614540) and [push run 40233611867](https://github.com/wmostafagmail/FindOurChild/actions/runs/40233611867). Every step succeeded. The PR merge checkout `30b06e974eafb52703bba33f726bb87e15145c7d` has the identical tree. [Run evidence](hosted-ci-verification.json), [artifact metadata](hosted-artifact-metadata.json), [independent verification](hosted-artifact-verification.json).

| Executed suite | Passed |
|---|---:|
| Foundation unit/API/real PostgreSQL/RLS/security/integration | 158 |
| Identity/MFA/authorization regression | 58 |
| Reporting/media/worker/safeguarding regression | 109 |
| Actual ClamAV outage/fail-closed regression | 1 |
| Actual reporting BFF/API HTTP regression | 6 |
| Research pipeline/evaluation/real PG/security/adversarial/evidence tests | 113 |
| Actual authenticated research capability/BFF HTTP tests | 2 |
| **Python total** | **447** |
| Official TesterArmy/e2e Chromium | 56 |
| Official TesterArmy/e2e Firefox | 56 |
| Official TesterArmy/e2e WebKit | 56 |
| **Official TesterArmy total** | **168** |

All seven browser titles execute in 24 targets: three engines × ar-EG/en-GB × widths 320/360/390/1280. The identity title additionally asserts anonymous denial, authenticated disabled flags and denial after real MFA-session logout. The running Next BFF/API/Keycloak/PostgreSQL services are used. Unit/analytic fixture tests remain identified separately. **Zero mandatory skips, retries or model-assisted steps; zero ordinary Playwright-only acceptance tests.** Exact runner/web/Playwright pins remain 0.21.3/0.15.3/1.64.1, with the accepted lockfiles unchanged and actual runner/web versions enforced by the results gate.

All 24 checksum-verified migrations, real RLS/tenant/authorization checks and actual nonempty pgvector/per-photo metadata backup/restore passed. The 41 application relations and four new research relations force RLS. The synthetic vector sentinel is removed after the drill; no raw vector is exported. Operational erasure/tombstone replay remains pending. API/migration Python coverage is **1139/1205 lines = 94.52282157676349%** (75% gate). Dependency audits found zero known npm/Python vulnerabilities at execution; this is not a container audit or independent penetration-test certification. Types, build and historical Phase 0/configuration checks passed.

Sanitized PR archive `12614004484` SHA-256: `e0867756c22cd456ee1d5ed264f12a18c3d35dcfda9374d7326862a085d1243c`. All **53 payload checksums**, **166 source blobs**, 48 input-free PNGs and 168 minimized traces were independently checked. [Versioned sanitized artifacts](../../artifacts/phase2a-sanitized/results.json). Execution-source fingerprint: `c20150475555b9c7c5684f2ed61dea8c7fd2f3425d57dcf11284cae8380c286b`. The independent tool imports no application validator. Source inventory includes the 22 pinned source/license texts read by integrity tests. No reporter/staff DOM, report photographs, raw vectors, manifest subjects, codes, tokens, locations or raw diagnostics are published.

[Traceability](TEST_TRACEABILITY.md) appends 118 passed foundation logical cases and six pending real-model/data qualifications. Registry: **185 features, 1096 cases; 464 passed and 632 future cases pending**. Every prior 178-feature/972-case row and the immutable 151/630 baseline remain unchanged. A synthetic test does not mark an operational ML feature passed.

[Local checkpoints](local-validation.json) retain their individual source digests: 381 local Python executions plus audits/types/build/recovery. Local browser/TLS and actual research HTTP validation are not claimed; hosted Ubuntu TLS was used under the owner's existing preference, with no macOS keychain change or certificate bypass.

The final evidence-only review commit must also pass the complete workflow; PR #5 records its exact final head/run and read-only artifact verification after completion. Its execution-source fingerprint must equal the implementation fingerprint above. The draft remains unmerged for owner review.

## Synthetic benchmark and research evidence

The weight-free smoke harness processed 32 geometric PNGs plus one analytic absent probe, repeated deterministic metric computation and passed the strict aggregate gate. **Zero recognition models were benchmarked or qualified.** [Model benchmark status](MODEL_BENCHMARK_STATUS.md) distinguishes the synthetic arithmetic output from unmeasured child recognition, age-gap, fairness, quality and neural-runtime performance. No operational threshold is set.

Connected REA inspected two BFF files as inert TypeScript, with 788 AST nodes and zero parse failures. Supplied-file inventory coverage is complete; semantic coverage is unknown/partial with 168 unknowns. [Full static Evidence](research/rea-evidence.json) is retained. This does not validate Python numerical behavior, live security or a model.

## Current branch protection

[Direct GitHub observation](main-protection.observed.json): strict/up-to-date `phase1a-required` from GitHub Actions app 15368 is required, including administrators; conversations must be resolved; force pushes and branch deletion are disabled. **Independent review is not required:** zero approving reviews, code-owner and latest-push approval disabled. Additional effective rules returned an empty list. No settings were changed; committed YAML is not the protection evidence.

## Failures preserved and corrected

The first local research run passed 86/93 tests; seven actual SQL retrieval calls failed because the new NOLOGIN role lacked USAGE on the locked-down pgvector schema. An additive narrow grant in 0023 corrected this; no CREATE or operational-data privilege was granted and no applied migration was rewritten. A later expanded run passed 110/111 tests; one source-integrity check detected that the temporary execution-mirror copy omitted extensionless LICENSE files. The copy procedure was corrected and all 113 expanded tests subsequently passed. Original logs/results are retained privately in `artifacts/raw/phase2a-history/`; failed results are not counted as successful validation.

The initial hosted PR run [40232842556](https://github.com/wmostafagmail/FindOurChild/actions/runs/40232842556) and push run [40232787794](https://github.com/wmostafagmail/FindOurChild/actions/runs/40232787794) failed on source `4facbec19c7dc33ef4ed223461114ca4fbe9aa58`. The first failure was `PermissionError` when container UID 10001 attempted to write the host runner-owned research report directory. Later real HTTP and coverage steps could not validate because web/TLS startup had not been reached. These are failed/incomplete runs, never counted as passes. Both original logs and the failed sanitized artifact are retained privately with checksums. `research_validate` now uses the host writer UID with unchanged dropped capabilities, matching existing baseline/reporting writers; the complete 113-test research suite and smoke harness passed locally after this correction. Both corrected hosted runs passed every step and their sanitized archives were independently verified; the failed attempts remain preserved.

## Outstanding qualification and release limits

All real model candidates remain blocked before weight download/use: exact binary hashes and complete weights/training-data entitlement are unresolved. No real evaluation dataset or protocol was authorized. No upstream accuracy is adopted as local evidence. No neural inference, provider parity, GPU sizing, real no-face/quality assessment, demographic/longitudinal child validation, calibrated probability or operational threshold exists.

ANN/HNSW, operational queue/model workers, real biometric ingestion, federation, public matching, custody/release decisions and Phase 2B are unimplemented/disabled. The offline exact synthetic store and cleanup are not proof of production erasure, backup tombstone replay, lawful child processing, independent penetration testing, WORM retention or operational readiness. Preserve all existing Phase 0–1C legal, safeguarding, hosting, secret-custody and NGO approval gates.

## Reproducible commands

Use the locked environment: Node 24.18.0/npm 11.16.0, Python 3.13.13/uv 0.12.0; `uv sync --locked`, `npm ci --ignore-scripts`. Runtime/application dependency locks and Docker pins are retained from Phase 1C; no recognition framework dependency is added.

`python -m scripts.check_foundation`; `python -m scripts.dev init`; `python -m scripts.dev db`; `python -m scripts.dev api`; `python -m scripts.dev test`; `python -m scripts.reporting_validate`; `python -m scripts.research_validate`; `python -m scripts.recovery`; `python -m scripts.audit`; `npm run typecheck`; `npm run build`. In hosted CI install all pinned browser engines, configure ephemeral TLS trust, start actual services, then run `python -m scripts.dev browser`, `python -m scripts.identity_test`, `python -m scripts.reporting_http_test`, `python -m scripts.research_test research_http`, `python -m scripts.coverage_finish`, `python -m scripts.artifacts`. No model-assisted test steps, mandatory skips or retry passes are accepted.

The required check remains `phase1a-required` so existing main protection continues to enforce it. Sanitized artifacts contain allowlisted aggregate statuses, coverage, source hashes, migration/restore results, input-free foundation screenshots and minimized trace step names/statuses. No vectors, images from reporting flows, tokens, DOM dumps, case/subject manifests, locations or raw diagnostics are published.
