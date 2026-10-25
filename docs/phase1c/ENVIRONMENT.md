# Reproduce Phase 1C synthetic validation

Use Node 24.18.0/npm 11.16.0, Python 3.13.13/uv 0.12.0, the committed locks and pinned OCI images. No real child data, production credentials or external testing model is permitted.

```sh
uv sync --locked
npm ci --ignore-scripts
.venv/bin/ruff check services/api scripts tests
.venv/bin/python -m scripts.check_foundation
.venv/bin/python -m scripts.dev init
.venv/bin/python -m scripts.dev db
.venv/bin/python -m scripts.dev api
.venv/bin/python -m scripts.dev test
.venv/bin/python -m scripts.reporting_validate
.venv/bin/python -m scripts.recovery
.venv/bin/python -m scripts.audit
npm run typecheck
npm run build
```

`reporting_validate` stops the worker for isolated lease tests, runs the complete reviewed reporting inventory, stops the actual scanner for the outage inventory, then restores scanner health and the worker. Fixture mutations occur only after the isolated synthetic DB marker is verified. No Docker socket is mounted into API/worker/tests. Failed tests, unavailable required services, stale inventories and cleanup failures block progression.

The dev launcher retains `.runtime` secrets and existing volumes; it does not reset research or databases. The synthetic moderator and browser/HTTP users are explicitly provisioned fixtures. The local encrypted delivery sink is an operator-side development facility, not email/SMS. `scripts.reporting_code` reads one requested synthetic receipt from a private operator fixture file and never exposes codes as an application endpoint.

For the TLS browser/real-HTTP lanes, follow the existing ephemeral Ubuntu setup in [the required workflow](../../.github/workflows/phase1a.yml): generate a separate constrained CA/server leaf, verify strict TLS, install trust only in the disposable runner, configure supported Firefox policy/NSS, install all three pinned engines, and start actual Next/TLS services. Then run:

```sh
.venv/bin/python -m scripts.dev browser
.venv/bin/python -m scripts.identity_test
.venv/bin/python -m scripts.reporting_http_test
.venv/bin/python -m scripts.coverage_finish
.venv/bin/python -m scripts.artifacts
.venv/bin/python -m scripts.dev stop
```

The owner selected hosted validation after declining a macOS trust retry. No local keychain trust is added by Phase 1C, TLS verification is never disabled, and local browser acceptance is not claimed. The existing temporary mirror `/private/tmp/foc-phase1a-runtime` avoids observed macOS Documents/Docker I/O problems; source hashes must match the repository before its results can be attributed. Hosted execution uses a fresh checkout and isolated services.

Required suite definitions are frozen in `docs/phase1a/required-tests.json` (preserved baseline plus browser titles), `docs/phase1b/required-tests.json` (identity) and `docs/phase1c/required-tests.json` (reporting/outage/live HTTP). Do not regenerate inventories in CI to match observed discovery. No required skips, retries, missing results, model calls or unavailable engines count as passing. The final source-bound artifact gate requires every lane, combined API/migration Python coverage ≥75%, migration/restore evidence and zero known dependency audit findings.

Raw `.runtime`, `.e2e` and `artifacts/raw` remain private/ignored. Only the allowlist sanitizer output is uploaded. Browser console output and detailed Python assertions are captured privately to prevent credentials, receipt values or DOM content leaking into CI logs. Review [the report](VALIDATION_REPORT.md) for actual executions and limits; these commands alone are not passing evidence.
