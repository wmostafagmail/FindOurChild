# Phase 2A validation report

Status: implementation and validation in progress. No Phase 2A acceptance or real recognition qualification is claimed. [Architecture and limits](ARCHITECTURE.md), [licensing matrix](LICENSING_MATRIX.md), [required executable inventory](required-tests.json).

## Verified entry and scope

Phase 1C accepted only after PR #4 merged into main at `1f6af0e99a32c2002beac842790c4f56f6b7e1e0` and required hosted run `40227138621` succeeded on that exact commit. Independent artifact verification checked 126 Git blobs, 53 payload hashes, 332 Python tests, 168 TesterArmy executions (56/browser), 21 migrations and 93.47% coverage. [Acceptance proof](../phase1c/main-merge-validation.json). Archive SHA-256: `cd5602398f86fe92c798255932ce4774bdcf5d786ea017ec0d4f2ad12e908a6c`.

Dedicated branch: `codex/phase-2a-model-qualification-foundation`. Operational recognition, public biometric search, automatic identity confirmation, custody disclosure and Phase 2B remain disabled. Synthetic data only. The research role is not a runtime login and has no operational case/image access.

## Execution record

- Local synthetic research suite reached 113/113 passing, including real PostgreSQL/RLS, exact vector parity, authorization/revocation, historical metadata and adversarial checks. Current full regression and hosted validation remain pending until exact-source evidence is attached.
- Synthetic pipeline/evaluation smoke completed with zero real models benchmarked. It is not a child recognition benchmark or threshold qualification.
- Bounded connected REA inspection completed on two BFF source files as inert text; complete supplied-file inventory, unknown/partial semantics and 168 unknowns are retained in its evidence bundle.
- Phase 0 preservation/configuration checks passed after the 49-operation API contract update. Lint passed at the recorded local checkpoint.
- Local three-browser TLS execution is not claimed. The owner’s existing hosted-only TLS validation preference remains in force; no macOS keychain change or certificate bypass was attempted.

Exact final-source test counts, CI run/commit, artifact digest, migration/coverage/audit evidence and independent verification will be recorded after hosted completion. Pending/skipped/unexecuted checks never count as passed.

## Failures preserved and corrected

The first local research run passed 86/93 tests; seven actual SQL retrieval calls failed because the new NOLOGIN role lacked USAGE on the locked-down pgvector schema. An additive narrow grant in 0023 corrected this; no CREATE or operational-data privilege was granted and no applied migration was rewritten. A later expanded run passed 110/111 tests; one source-integrity check detected that the temporary execution-mirror copy omitted extensionless LICENSE files. The copy procedure was corrected and all 113 expanded tests subsequently passed. Original logs/results are retained privately in `artifacts/raw/phase2a-history/`; failed results are not counted as successful validation.

## Outstanding qualification and release limits

All real model candidates remain blocked before weight download/use: exact binary hashes and complete weights/training-data entitlement are unresolved. No real evaluation dataset or protocol was authorized. No upstream accuracy is adopted as local evidence. No neural inference, provider parity, GPU sizing, real no-face/quality assessment, demographic/longitudinal child validation, calibrated probability or operational threshold exists.

ANN/HNSW, operational queue/model workers, real biometric ingestion, federation, public matching, custody/release decisions and Phase 2B are unimplemented/disabled. The offline exact synthetic store and cleanup are not proof of production erasure, backup tombstone replay, lawful child processing, independent penetration testing, WORM retention or operational readiness. Preserve all existing Phase 0–1C legal, safeguarding, hosting, secret-custody and NGO approval gates.

## Reproducible commands

Use the locked environment: Node 24.18.0/npm 11.16.0, Python 3.13.13/uv 0.12.0; `uv sync --locked`, `npm ci --ignore-scripts`. Runtime/application dependency locks and Docker pins are retained from Phase 1C; no recognition framework dependency is added.

`python -m scripts.check_foundation`; `python -m scripts.dev init`; `python -m scripts.dev db`; `python -m scripts.dev api`; `python -m scripts.dev test`; `python -m scripts.reporting_validate`; `python -m scripts.research_validate`; `python -m scripts.recovery`; `python -m scripts.audit`; `npm run typecheck`; `npm run build`. In hosted CI install all pinned browser engines, configure ephemeral TLS trust, start actual services, then run `python -m scripts.dev browser`, `python -m scripts.identity_test`, `python -m scripts.reporting_http_test`, `python -m scripts.research_test research_http`, `python -m scripts.coverage_finish`, `python -m scripts.artifacts`. No model-assisted test steps, mandatory skips or retry passes are accepted.

The required check remains `phase1a-required` so existing main protection continues to enforce it. Sanitized artifacts contain allowlisted aggregate statuses, coverage, source hashes, migration/restore results, input-free foundation screenshots and minimized trace step names/statuses. No vectors, images from reporting flows, tokens, DOM dumps, case/subject manifests, locations or raw diagnostics are published.
