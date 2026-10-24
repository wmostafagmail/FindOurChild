# Phase 1A remediation report

Date: **2026-10-24 (Africa/Cairo)**. Project: **Find Our Child**. Starting revision: `add5cf75e80154567ee2188d00973bccbd18cd2e`, branch `codex/phase-1a-foundation`. Corrective runtime revision: **`ec99ac0c5200f83fffcb1bbbee9db1c8cfeaa89d`**.

**All required Phase 1A technical validation passes locally and in hosted CI; ready for owner acceptance review.** The private repository is [wmostafagmail/FindOurChild](https://github.com/wmostafagmail/FindOurChild), with [draft implementation PR #1](https://github.com/wmostafagmail/FindOurChild/pull/1). Main protection is App-bound and read back; an actual failing-check merge request received HTTP 405 on a disposable protected base. No external-blocker waiver was needed. No Phase 1B work or implementation merge was performed. See [hosted validation](HOSTED_VALIDATION.md).

## Root cause and corrective actions

All original 24 Firefox failures were engine initialization failures, before application assertions. Installed Playwright core 1.64.1 expects Firefox revision 1555 / version 157.0; that binary exists and starts with isolated app data. Its executable SHA-256 is `65f70a725a576763c36634d63407fad91d898d522f25a5ca9caf748b3e3be005`.

The same binary fails with default macOS app data and succeeds when `CFFIXED_USER_HOME` points to a fresh directory. This reproduces the macOS 27 app-data access problem in [Playwright issue 42768](https://github.com/microsoft/playwright/issues/42768). Firefox's temporary `-profile` alone does not isolate its separate app-data lookup. The controlled A/B result supports this cause; a local TCC audit was not performed. Binary absence, a revision mismatch and TesterArmy-only integration failure are ruled out by the unchanged binary succeeding in both the launch probe and full TesterArmy regression. These failures did not demonstrate application defects.

`scripts/run-browser.mjs` now creates disposable macOS app data, passes it only to the test-runner subprocess and removes it after completion. Precreating its Downloads directory prevents macOS from adding a deny-delete ACL that initially prevented cleanup. HOME, framework/browser versions, browser sandbox settings and all existing application assertions remain unchanged. No global permissions or Full Disk Access were granted. Linux follows the existing launch path.

`scripts/firefox-diagnostic.mjs` records the reproducible default/isolated comparison. The initial exploratory launch succeeded but its cleanup failed; a second cleanup attempt with retries also failed due to the Downloads ACL. Those exploratory commands are not counted as successful validation. The final committed diagnostic exits zero and cleans up its directories. Original raw failure evidence remains preserved.

## Framework and execution identity

The actual command is `e2e run --config e2e.config.ts --retries 0 --no-cache`, through `scripts/run-browser.mjs`. Tests import `test` from `@e2e-dev/web` and `expect` from `e2e`; the native report identifies runner **e2e 0.21.3**. Installed web engine is **0.15.3**, with transitive Playwright core **1.64.1**. The [approved framework source selection](../E2E_FRAMEWORK_INTEGRATION.md) remains commit `69e123b17e04ed624df16d32f3b1ef95ce22c083`; [official releases](https://github.com/tester-army/e2e/releases) confirm these pins and the engine's core dependency.

| Execution category | Chromium | Firefox | WebKit | Total |
|---|---:|---:|---:|---:|
| Local TesterArmy browser application tests, passed | 24 | 24 | 24 | **72** |
| Hosted PR TesterArmy browser application tests, passed | 24 | 24 | 24 | **72** |
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
| Hosted CI / protection / failing-check merge block | **Passed**: run 40079573659, App 15368 main readback and actual HTTP 405 rejection |

Negative regression includes every disabled domain operation with anonymous and forged credentials, cross-organization case reads and foreign keys, same-organization/wrong-case object references, missing/expired/revoked grants and membership, disabled principals, suspended organizations, forbidden sensitive tables, role elevation, wrong purpose and connection-context reuse. Four original disabled-feature safeguarding guards pass; operational identity/reporting/release/biometric workflows remain unimplemented and pending.

The accepted hosted PR run independently repeats the same 151 Python and 72 browser executions; all mandatory candidate results pass. The isolated negative probe instead has 150 passing Python tests and one intentional failure, with downstream browser/restore/audit steps unexecuted and never counted as passed. Its purpose is to demonstrate rejection.

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

This local check verifies integrity and source binding. The [hosted report](HOSTED_VALIDATION.md) separately verifies GitHub execution and its artifact archive. Independent reviewers can reproduce the full commands above with new synthetic data and query the recorded hosted run.

## Hosted execution and protected-branch evidence

The full [hosted validation report](HOSTED_VALIDATION.md), [hosted metadata](hosted-evidence.json), [artifact verification](hosted-artifact-verification.json), [job steps](hosted-job-steps.json) and [merge-block proof](negative-gate-proof.json) are reviewable evidence.

The owner supplied an empty private repository with admin/push access. Initial Git credentials failed; a command-scoped GitHub CLI helper authenticated without changing global Git settings. The initial atomic two-branch push was rejected because OAuth lacked workflow scope, leaving both branches absent. The owner completed GitHub device consent; scopes now include workflow. The owner also resolved the initial private-repository protection HTTP 403 by upgrading the account. No purchase, public-visibility change or credential publication was performed by the agent.

Main was published as the approved baseline. Engineering commit **dba2b79526b052ce3bd893998129f6c90932b30d** was then published and hosted PR workflow **40079573659** passed. PR checkout **de5371ab125c802ce5a282acd87712e170b395dd** and head dba2b79 have the same complete Git tree. The 54-file sanitized ZIP matches GitHub's SHA-256 digest; all 53 payload checksums, executed source hashes and 48 metadata-stripped PNGs were verified. A versioned copy is retained under `artifacts/hosted-sanitized/40079573659/`.

Main protection requires phase1a-required from observed GitHub Actions App **15368**, strict current-branch checks, administrator enforcement, one independent approval, stale-review dismissal, latest-push approval and resolved conversations, with force pushes/deletion disabled. [Requested](branch-protection.request.json) and [read-back settings](branch-protection.observed.json) match the enforced controls.

A one-assertion negative probe targeted a separate protected base with the same check/App/admin settings and no unrelated review gate. The PR was non-draft, conflict-free and up to date. Exactly one existing assertion deliberately expected 418; the unchanged application returned its correct 200. The workflow failed and the required-results gate blocked. An actual merge request constrained to the exact probe head returned HTTP **405**, `Required status check "phase1a-required" is failing.` The probe was closed unmerged and both temporary branches/test-only protection were removed. Main source and protection were verified unchanged afterward. No failing test or weakened main rule entered the implementation PR.

Temporary Git-object copying encountered filesystem stalls and incomplete intermediate copies; hash/fsck checks rejected incomplete mirrors before any successful publication. The final mirror verified complete original objects and preserved all commit identities. These diagnostics are not application tests or successful CI runs.

Hosted commands included command-scoped `git ... push`, `gh auth refresh --hostname github.com --scopes workflow`, protection PUT/GET operations using the versioned JSON requests, artifact download/verification, and the explicitly scoped negative `PUT /repos/wmostafagmail/FindOurChild/pulls/2/merge`. No credential/device-code value is stored in project files. Exact request/response fields, commits, run/PR URLs and cleanup are recorded in the linked evidence. The separate negative source is not an accepted regression candidate.

## Changed files and review gate

Runtime changes are limited to `scripts/run-browser.mjs` and new `scripts/firefox-diagnostic.mjs` (committed at `ec99ac0`). Review/docs, matrix generation/statuses, source inventory and sanitized execution artifacts are updated in the evidence commit; their exact inventory is recorded in [changed-files.json](changed-files.json) and is independently available through `git diff --name-status add5cf7..HEAD` after the evidence commit. Dependency manifests/locks, API behavior, migrations, RLS policies and accepted browser assertions are unchanged. Additional engineering configuration records main/probe protection; additional evidence contains verified hosted artifacts and negative enforcement results.

All Phase 1A technical validation blockers are resolved. The evidence changes are committed on the engineering branch and the final working tree is checked clean for review. Owner acceptance and independent PR review remain human gates. No Phase 1B entry is authorized; explicit approval remains required. Original legal, safeguarding, retention and model gates remain unchanged.
