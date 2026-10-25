# Find Our Child

> Phase 1C is accepted after verified PR #4 merge and exact-main hosted CI. Phase 2A is in progress: [research scope, licensing and validation](docs/phase2a/VALIDATION_REPORT.md). Synthetic data only; operational recognition and Phase 2B remain disabled.

Phase 1B is accepted after PR #3 merged and required CI passed on exact main `9fcb6ef`. [Acceptance evidence](docs/phase1b/ACCEPTANCE.md).

Phase 1C reporting and case management is implemented and technically validated in [draft PR #4](https://github.com/wmostafagmail/FindOurChild/pull/4), awaiting owner review. [Validation report](docs/phase1c/VALIDATION_REPORT.md), [reproducible environment](docs/phase1c/ENVIRONMENT.md), [architecture](docs/phase1c/ARCHITECTURE.md), [locks](docs/phase1c/LOCKED_DEPENDENCIES.md), [source inventory](docs/phase1c/SOURCE_INVENTORY.md) and [traceability](docs/phase1c/TEST_TRACEABILITY.md).

Required hosted validation passed: **332 Python tests, 168 official TesterArmy browser executions (56 each Chromium/Firefox/WebKit), all 21 migrations and restore/RLS, security audits and sanitized artifact gates**. Synthetic data only. No production facial recognition, operational child release or Phase 2 work.

## Historical phase records

Earlier status statements and commands below describe their recorded phase. Current Phase 1C instructions and limits are linked above.

Phase 1A is accepted after PR #1 and hosted CI on merged main `683180e`. **Phase 1B identity/security is implemented and technically validated in [draft PR #3](https://github.com/wmostafagmail/FindOurChild/pull/3), awaiting owner review.** Phase 1C has not begun; all 32 reporting/media/matching/safeguarding domain operations remain fail-closed with 503.

Start with the [Phase 1B validation report](docs/phase1b/VALIDATION_REPORT.md), [current environment](docs/phase1b/ENVIRONMENT.md), [locks](docs/phase1b/LOCKED_DEPENDENCIES.md), [architecture](docs/phase1b/ARCHITECTURE.md), [source inventory](docs/phase1b/SOURCE_INVENTORY.md) and [test matrix](docs/TEST_MATRIX.md). Full required hosted validation executes 216 Python and 96 TesterArmy browser cases. Existing foundation commands remain available; identity/browser testing also requires the TLS/IdP steps in the current environment guide.

```sh
make bootstrap
make db
make api
make web
# Separate terminal
make test
make browser
```

The browser binaries must first be installed with the locked `e2e-web` command and both telemetry flags; see the environment guide. Only synthetic data is permitted. Private credentials/raw artifacts are ignored; CI publishes the allowlisted sanitized evidence. Database migration/test credentials are never passed to the web/browser or API runtime.

The approved Phase 0 package is preserved at Git commit `40231be73ab9a5eb577ccf5308c86f6b7282976b`. [Research](docs/REA_RESEARCH_REPORT.md), [architecture](docs/ENGINEERING_ARCHITECTURE.md), [safeguarding](docs/CHILD_SAFEGUARDING_POLICY.md), [privacy](docs/PRIVACY_AND_RETENTION.md), [test strategy](docs/TEST_STRATEGY.md) and [phase gates](docs/IMPLEMENTATION_PHASES.md) remain governing documents. Current machine-readable contracts are under `docs/contracts` and executable schema migrations under `database/migrations`.

The original `tools/build_test_matrix.py` reproduces the Phase 0 pending baseline only. Current Phase 1B traceability is updated by `tools/update_phase1b_matrix.py` from verified current-source evidence; the Phase 1A updater reproduces only its historical scope; the original 151-feature/630-case baseline is retained separately. Never replace current execution evidence with generated pending/pass placeholders.
