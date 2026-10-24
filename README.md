# Find Our Child

Phase **1A foundation only**. The acceptance gate remains **blocked** by the pinned Firefox launch failure; remote CI execution and branch protection are pending. Phase 1B and 1C have not started. All 32 domain operations return a fail-closed 503.

Start with the [Phase 1A review](docs/phase1a/REVIEW.md), [executable environment](docs/phase1a/ENVIRONMENT.md), [locked manifest](docs/phase1a/LOCKED_DEPENDENCIES.md), [source inventory](docs/phase1a/SOURCE_INVENTORY.md) and [test matrix](docs/TEST_MATRIX.md).

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

The original `tools/build_test_matrix.py` reproduces the Phase 0 pending baseline only. Current implementation traceability is updated by `tools/update_phase1a_matrix.py`; the original 151-feature/630-case baseline is retained separately. Never replace current execution evidence with generated pending/pass placeholders.
