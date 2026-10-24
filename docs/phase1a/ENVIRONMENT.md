# Phase 1A executable environment

Use Node **24.18.0**, npm **11.16.0**, Python **3.13.13**, uv **0.12.0** and Docker. Exact application/test dependency trees are in the root `package-lock.json` and `uv.lock`; `requirements-bootstrap.txt` hashes the uv installer. Container bases and GitHub actions are immutable digest/SHA pins. [Observed runtime evidence](environment-evidence.json) records actual commands and hashes.

```sh
make bootstrap
make db
make api
make web
# Another terminal; only synthetic data is permitted.
make test
E2E_TELEMETRY_DISABLED=1 DO_NOT_TRACK=1 ./node_modules/.bin/e2e-web install chromium firefox webkit
make browser
uv run python -m scripts.recovery
uv run python -m scripts.audit
uv run python -m scripts.artifacts
```

`make db` builds the locked Python image, starts the private PostgreSQL/pgvector service and applies checksum-verified forward migrations atomically. The schema contract release is `0001`; its migration ledger contains `0001_foundation` and `0002_contract_hardening`. Readiness requires the hardening migration as well as the release/instance identity and a non-superuser/non-BYPASSRLS role.

Database connections have no published host port. Provisioner/tests run on the internal-only network; the API alone bridges to an edge network and binds host port 8000 to loopback. The web server binds loopback port 3000. A separate existing host PostgreSQL instance was left untouched. Private generated credentials are in ignored `.runtime/local.json` with mode 0600; API, browser and web processes do not receive provisioner credentials. Model/provider credentials are removed from web/browser subprocess environments.

The actual API and migrated database ran in containers. Because repeated Documents filesystem reads stalled, a byte-equivalent temporary source/runtime at `/private/tmp/foc-phase1a-runtime` was used for web/browser execution. The workspace's dependency symlinks point to the verified temporary installations; bootstrap recreates dependencies from the locks after temporary storage is removed. The source fingerprint and file inventory make this location workaround reviewable. It is not a deployment architecture change.

Clean `npm ci --ignore-scripts` installed 74 host-selected packages with the final lock. TypeScript checks and the production Next.js build completed. The final container build used `uv sync --locked`; both forward migrations, replay, same-case/tenant checks and a real backup/restore drill executed. Raw local install/build/provision logs remain under ignored `artifacts/raw`; sanitized summaries are published separately.

TesterArmy e2e **0.21.3**, web engine **0.15.3**, Playwright core **1.64.1** remain pinned. The active root tree overrides Zod to **4.6.6** to address [GHSA-mrhx-c7xc-m3w5](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5), and the actual CLI/config/browser executions verify that selection. The original Phase 0 `tools/e2e-plan` lock remains unchanged as historical evidence and is not the active test runner. Root npm and Python audit reports record no known vulnerabilities at execution time; this does not certify archived research toolchains or constitute penetration testing.

Chromium 156.0.8078.4/revision 1248, Firefox 157.0/revision 1555 and WebKit 27.2/revision 2370 now execute successfully on macOS arm64: **24 passing executions per engine, 72 total**. The pinned Firefox initially failed because its macOS app-data lookup was inaccessible. `scripts/run-browser.mjs` creates disposable CoreFoundation app data through `CFFIXED_USER_HOME` on macOS, precreates Downloads to avoid its OS-added deny-delete ACL, and cleans up after the runner. It preserves HOME, original binaries, framework pins, assertions and all targets. No Full Disk Access or global permission change is required. See the [remediation report](REMEDIATION_REPORT.md) and [upstream issue](https://github.com/microsoft/playwright/issues/42768).

Reproduce the diagnostic with `node scripts/firefox-diagnostic.mjs` using pinned Node. It records a default-versus-isolated launch comparison under ignored `artifacts/raw/firefox-diagnostic.json`; these two low-level Playwright launch probes are diagnostics, not application acceptance tests. `make browser` then executes the complete TesterArmy suite with isolation applied automatically. Raw original failure logs remain under `artifacts/raw/baseline-add5cf7/`. Linux GitHub browser compatibility and remote merge enforcement remain unverified until a repository is provided.

Both E2E telemetry opt-outs are mandatory, Next telemetry is disabled by the web command wrapper, retries are zero and the browser suite has no model/provider/cache. Recorded browser model tokens/calls and downloads are zero. No network packet capture was performed; flags and zero model usage do not prove process-wide egress isolation.
