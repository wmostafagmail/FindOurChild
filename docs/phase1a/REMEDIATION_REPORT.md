# Phase 1A remediation report

Date: **2026-10-24 (Africa/Cairo)**. Project: **Find Our Child**. Starting revision: `add5cf75e80154567ee2188d00973bccbd18cd2e`, branch `codex/phase-1a-foundation`. Corrective runtime revision: **`ec99ac0c5200f83fffcb1bbbee9db1c8cfeaa89d`**.

**Local validation passes. Phase 1A acceptance remains blocked by hosted CI and branch-protection verification.** No GitHub remote exists. The owner said a repository URL will be provided; this is not acceptance of the external blockers. No Phase 1B work was started.

## Root cause and corrective actions

All original 24 Firefox failures were engine initialization failures, before application assertions. Installed Playwright core 1.64.1 expects Firefox revision 1555 / version 157.0; that binary exists and starts with isolated app data. Its executable SHA-256 is `65f70a725a576763c36634d63407fad91d898d522f25a5ca9caf748b3e3be005`.

The same binary fails with default macOS app data and succeeds when `CFFIXED_USER_HOME` points to a fresh directory. This reproduces the macOS 27 app-data access problem in [Playwright issue 42768](https://github.com/microsoft/playwright/issues/42768). Firefox's temporary `-profile` alone does not isolate its separate app-data lookup. The controlled A/B result supports this cause; a local TCC audit was not performed. Binary absence, a revision mismatch and TesterArmy-only integration failure are ruled out by the unchanged binary succeeding in both the launch probe and full TesterArmy regression. These failures did not demonstrate application defects.

`scripts/run-browser.mjs` now creates disposable macOS app data, passes it only to the test-runner subprocess and removes it after completion. Precreating its Downloads directory prevents macOS from adding a deny-delete ACL that initially prevented cleanup. HOME, framework/browser versions, browser sandbox settings and all existing application assertions remain unchanged. No global permissions or Full Disk Access were granted. Linux follows the existing launch path.

`scripts/firefox-diagnostic.mjs` records the reproducible default/isolated comparison. The initial exploratory launch succeeded but its cleanup failed; a second cleanup attempt with retries also failed due to the Downloads ACL. Those exploratory commands are not counted as successful validation. The final committed diagnostic exits zero and cleans up its directories. Original raw failure evidence remains preserved.

## Framework and execution identity

The actual command is `e2e run --config e2e.config.ts --retries 0 --no-cache`, through `scripts/run-browser.mjs`. Tests import `test` from `@e2e-dev/web` and `expect` from `e2e`; the native report identifies runner **e2e 0.21.3**. Installed web engine is **0.15.3**, with transitive Playwright core **1.64.1**. The [approved framework source selection](../E2E_FRAMEWORK_INTEGRATION.md) remains commit `69e123b17e04ed624df16d32f3b1ef95ce22c083`; [official releases](https://github.com/tester-army/e2e/releases) confirm these pins and the engine's core dependency.

| Execution category | Chromium | Firefox | WebKit | Total |
|---|---:|---:|---:|---:|
| TesterArmy browser application tests, passed | 24 | 24 | 24 | **72** |
| TesterArmy failed / skipped / retried | 0 | 0 | 0 | **0** |
| Ordinary Playwright-only application acceptance tests | 0 | 0 | 0 | **0** |
| Final separate low-level launch diagnostics | 0 | 2 | 0 | **2 probes** |

The default Firefox diagnostic intentionally reproduces a launch failure; the isolated diagnostic passes. These final two probes, plus four earlier exploratory probes (six launch attempts in total), are separate from the 72 passing mandatory application executions. No `@playwright/test` suite is substituted for TesterArmy.

Three logical application cases expand across three engines, two browser locales and four widths (320, 360, 390, 1280): `TC_FND_BROWSER_AR_READY`, `TC_FND_BROWSER_EN_READY`, `TC_FND_BROWSER_LANGUAGE_SWITCH`. Assertions check real backend/database readiness, visible localized content, HTML language/direction, no overflow, no reporting inputs, keyboard skip navigation, axe accessibility violations and bilingual navigation. There is no API/browser mocking or model-assisted action. Preflight verifies the live web/API against the private database instance. Zero model tokens/calls, retries, flaky results, skips and downloads are recorded. Both telemetry opt-outs remain enforced.

## Executed validation

| Suite/check | Exact result |
|---|---|
| Python unit | **41 passed** |
| API | **6 passed** |
| Real PostgreSQL database/RLS | **34 passed** |
| Security/authorization | **68 passed** |
| Integration | **2 passed** |
| Python total | **151 passed**, zero skipped; one non-failing Starlette/httpx deprecation warning |
| API/migration Python line coverage | **94.81%**, 73/77 statements; no frontend/whole-repository claim |
| Complete TesterArmy regression | **72 passed**, 24 per engine; zero failed/skipped/flaky/retried |
| Both immutable migrations and replay | Passed, checksums preserved |
| Backup/restore | Passed: both ledger checksums, pgvector 0.8.7, 41 forced-RLS relations, default-denied runtime case reads |
| npm/Python vulnerability audits | Passed: zero known current-lock vulnerabilities at execution time |
| Clean npm lock install, TypeScript, production web build | Passed |
| Source-bound required-results and sanitized export | **Passed** |
| Documentation/configuration checks | See [configuration-checks.json](configuration-checks.json); historical validators test the preserved Phase 0 commit, not application behavior |
| Hosted CI / protection / failing-check merge block | **Pending**, no remote or hosted execution |

Negative regression includes every disabled domain operation with anonymous and forged credentials, cross-organization case reads and foreign keys, same-organization/wrong-case object references, missing/expired/revoked grants and membership, disabled principals, suspended organizations, forbidden sensitive tables, role elevation, wrong purpose and connection-context reuse. Four original disabled-feature safeguarding guards pass; operational identity/reporting/release/biometric workflows remain unimplemented and pending.

The current [matrix](../TEST_MATRIX.md) preserves the original 151-feature/630-case baseline and maps all delivered tests. Counts of baseline features and executed Python tests happen to match; they do not mean the full product baseline passed.

## Executed commands and reproduction

Commands below completed using Node 24.18.0/npm 11.16.0, Python 3.13.13 and the locked environment. Runtime execution used `/private/tmp/foc-phase1a-runtime`, byte-equivalent to committed application/test/config source, because Documents reads stalled. The source digest in [remediation-evidence.json](remediation-evidence.json) and the [source manifest](../../artifacts/sanitized/source-manifest.json) verify equivalence. `PATH=/opt/homebrew/opt/node@24/bin:$PATH` selected the pinned Node locally. No credentials are included in reports.

```sh
node scripts/firefox-diagnostic.mjs
.venv/bin/python -m scripts.dev db
.venv/bin/python -m scripts.dev api
.venv/bin/python -m scripts.dev test
.venv/bin/python -m scripts.recovery
.venv/bin/python -m scripts.audit
npm run typecheck
npm run build
npm ci --ignore-scripts
npm run start
# Separate terminal, after the actual service is listening:
.venv/bin/python -m scripts.wait_services
.venv/bin/python -m scripts.dev browser
.venv/bin/python -m scripts.artifacts
# Workspace checks:
.venv/bin/ruff check services/api scripts tests
.venv/bin/python -m scripts.check_foundation
python3 tools/update_phase1a_matrix.py
```

The normal `make browser` entry point applies the Firefox fix automatically. No manual editing of installed packages/binaries is required. Browser installation remains `E2E_TELEMETRY_DISABLED=1 DO_NOT_TRACK=1 ./node_modules/.bin/e2e-web install chromium firefox webkit` when pinned binaries are absent; binaries were already present and verified for this remediation, so reinstalling them was unnecessary.

## Evidence and independent verification

- [Exact execution metadata and raw checksums](remediation-evidence.json), [required inventory](required-tests.json), [results](../../artifacts/sanitized/results.json), [coverage](../../artifacts/sanitized/coverage.json), [normalized traces](../../artifacts/sanitized/traces.json), [source manifest](../../artifacts/sanitized/source-manifest.json) and [artifact checksums](../../artifacts/sanitized/checksums.json).
- **48** sanitized PNG screenshots contain only the fixed synthetic, input-free shell. Only metadata-stripped allowlisted images and normalized step names/statuses are published; raw errors/DOM/arguments and credentials are not exported. Negative sanitizer/path-traversal tests passed. This policy must be reviewed before any future reporting/photo/contact page.
- Ignored current raw evidence: `.e2e/report.json`, `.e2e/junit.xml`, `.e2e/results/`, `artifacts/raw/browser-console.log`, `browser-run.json`, `python-results.json`, `python.junit.xml`, `coverage.json`, `coverage.xml`, `provision.log`, `recovery.json`, `synthetic-backup.dump`, `audit-meta.json`, `npm-audit.json`, `python-audit.json`, `npm-ci.log`, `typecheck.log`, `web-build.log`, `web.log`, `firefox-diagnostic.json`.
- Original ignored evidence: `artifacts/raw/baseline-add5cf7/`; the temporary runtime's same archive includes `preservation-sha256.json` covering **472 original raw files**. The prior active browser report was also archived by the runner under `artifacts/raw/browser-attempt-*/report.json`. Original sanitized evidence remains in Git revision `add5cf7`; no original failure was relabeled as passing.

To independently verify the checked-in sanitized files and source without executing application tests, run this from the repository root using the locked Python environment:

```sh
.venv/bin/python - <<'PY'
import hashlib, json
from pathlib import Path
from scripts.fingerprint import fingerprint, inventory
p = Path('artifacts/sanitized')
for name, expected in json.loads((p/'checksums.json').read_text()).items():
    assert hashlib.sha256((p/name).read_bytes()).hexdigest() == expected, name
assert inventory() == json.loads((p/'source-manifest.json').read_text())
assert fingerprint() == json.loads((p/'results.json').read_text())['gate']['source_digest']
assert json.loads((p/'results.json').read_text())['gate']['status'] == 'passed'
print('Source and sanitized artifact hashes verified')
PY
```

This verifies integrity and source binding, not third-party execution attestation. Independent reviewers can reproduce the full commands above with new synthetic data; the hosted attestation is still pending.

## Hosted execution and protected-branch steps

`git remote -v` returned no entries. Therefore no repository-specific access denial, administrative permission result, hosted run ID or merge-block test exists. **Missing prerequisite:** owner-provided repository URL and access to it. Account permissions cannot be determined without that target; they are not assumed unavailable or sufficient.

Once supplied, inspect its existing branches/history before any push; do not overwrite them. Push the committed engineering branch with its original baseline ancestry, run `.github/workflows/phase1a.yml` and record the run URL, full head SHA, successful conclusion and sanitized artifact hashes. Confirm the complete 151-Python/72-browser inventory ran on the hosted OS. A YAML file or local macOS pass is insufficient.

A repository administrator should protect `main`: require pull requests and the actual GitHub Actions check name emitted by job `phase1a-required`, require the branch up to date, apply protection to administrators, disallow bypass/force pushes/deletion and require review/conversation resolution. Record the GET branch-protection response and the check's GitHub App identity. GitHub documents [protected-branch behavior](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) and [protection API permissions](https://docs.github.com/en/rest/branches/branch-protection): Administration read is required to inspect protection, Administration write to update it. Hosted execution also needs repository Contents write to push, Actions read to inspect and Actions write for manual dispatch, subject to organization policy and workflow-file permissions.

Use a disposable PR with a deliberate failing existing assertion. Record its failed required check and blocked merge state for a non-bypass actor; verify the required-check/rule identity applies to its base and commit. Restore the assertion and close the probe without merging it. Do not mark this merge-block test passed until observed. No remote mutations or disposable PR were performed during this no-remote run.

## Changed files and remaining gate

Runtime changes are limited to `scripts/run-browser.mjs` and new `scripts/firefox-diagnostic.mjs` (committed at `ec99ac0`). Review/docs, matrix generation/statuses, source inventory and sanitized execution artifacts are updated in the evidence commit; their exact inventory is recorded in [changed-files.json](changed-files.json) and is independently available through `git diff --name-status add5cf7..HEAD` after the evidence commit. Dependency manifests/locks, API behavior, migrations, RLS policies and browser assertions are unchanged.

Outstanding acceptance items are **hosted CI demonstration**, **verified branch protection and failing-check merge prevention**, or explicit project-owner acceptance of those external blockers. Such acceptance has not been given. All changes must be committed and the final tree clean before review. This remediation authorizes no Phase 1B entry; explicit approval remains required.
