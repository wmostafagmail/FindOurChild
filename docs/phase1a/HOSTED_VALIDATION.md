# Phase 1A hosted validation and enforcement

Verified **24 October 2026, Africa/Cairo**. **All required technical gates pass; ready for owner acceptance review.** Phase 1B remains unapproved. The implementation PR is [#1](https://github.com/wmostafagmail/FindOurChild/pull/1), open as a draft and unmerged. The repository remains private.

## Committed source and positive CI

Primary accepted hosted evidence is [PR workflow run 40079573659](https://github.com/wmostafagmail/FindOurChild/actions/runs/40079573659), job `phase1a-required`, successful on the configured Ubuntu 24.04 runner. Published head is `dba2b79526b052ce3bd893998129f6c90932b30d`. GitHub checked out PR merge commit `de5371ab125c802ce5a282acd87712e170b395dd`; both have the identical complete Git tree `23a80c8dede7ebaa6b4770b4eb61f57d30616cb3`.

The executed application/test/config source digest is:

`cf3630cb45ee5115e8f02563661147a6fb658a272749d3f92cb1faf25152708d`

The digest covers 60 execution-relevant files, including application code, migrations, browser/Python tests, required inventory, contracts, dependency locks and CI workflow. Subsequent evidence/protection-document updates preserve this digest. They do not change application behavior or the test inventory. Full engineering-file hashes are in [source-files.json](source-files.json).

| Accepted hosted suite | Result |
|---|---|
| Unit | 41 passed |
| API | 6 passed |
| PostgreSQL schema/RLS/transaction | 34 passed |
| Security/authorization | 68 passed |
| Integration | 2 passed |
| Python total | **151 passed**, no required skips |
| TesterArmy Chromium | 24 passed |
| TesterArmy Firefox | 24 passed |
| TesterArmy WebKit | 24 passed |
| TesterArmy total | **72 passed**, zero failed/skipped/flaky/retried |
| API/migration Python coverage | 73/77 statements, **94.81%** |
| Migration replay and real restore | Both checksums, vector 0.8.7, 41 forced-RLS relations and denied-default reads verified |
| Current npm/Python audits | Zero known current-lock vulnerabilities |
| Typecheck, production build, result gate, sanitizer, artifact publication and service cleanup | Passed |

Tests use TesterArmy runner **0.21.3**, web **0.15.3**, Playwright core **1.64.1** with deterministic assertions against actual web/API/private PostgreSQL. No Playwright-only application suite substitutes for TesterArmy. The local Firefox launch probes are separate diagnostics. Model/telemetry restrictions and synthetic-only fixtures remain unchanged. See [allowlisted execution log lines](hosted-log-excerpt.json), [exact job steps](hosted-job-steps.json) and [artifact verification](hosted-artifact-verification.json). Local accepted results also pass 151 Python and 72 browser executions; repetitions do not add new feature coverage.

## Independent artifact verification

Artifact **12554692603**, named `phase1a-sanitized-de5371ab125c802ce5a282acd87712e170b395dd`, was downloaded and checked independently. Its archive SHA-256 matches GitHub's recorded digest:

`c9b3083c0e50d3081fe27cb5b242e44e0c5883e938a325df9b96f2329e51f832`

The ZIP contains **54 files**: 53 checksummed payloads and their checksum manifest. Validation rejects duplicate entries, symlinks, oversized archives and paths outside the fixed allowlist. All internal checksums match, the complete executed source manifest matches the workspace/committed source, every required result passes, and all **48 PNGs** already equal their metadata-stripped form. There are no raw screenshots, trace arguments, DOM, credentials, downloads or arbitrary page logs in this export.

The verified, already-sanitized contents are retained at [artifacts/hosted-sanitized/40079573659](../../artifacts/hosted-sanitized/40079573659/results.json), including results, coverage, normalized traces, source manifest, screenshots, validation log and checksums. The original ZIP stays in ignored local `artifacts/raw/hosted/positive-40079573659.zip`. GitHub artifact retention is seven days; the versioned evidence copy remains reviewable independently of that expiration. No general-purpose PII detector is claimed: the allowlist is limited to this fixed, input-free synthetic shell.

## Main protection and publisher identity

Protection was configured and independently read back from GitHub, rather than inferred from YAML. [Requested policy](branch-protection.request.json), [observed response](branch-protection.observed.json) and [hosted metadata](hosted-evidence.json) record:

- Required check `phase1a-required`, restricted to the observed **GitHub Actions App 15368**.
- The branch must be up to date; protection applies to administrators.
- One independent review, dismissal of stale reviews, approval after the latest push and resolved conversations.
- Force pushes and branch deletion disabled.

Main remains at the approved Phase 0 baseline `40231be73ab9a5eb577ccf5308c86f6b7282976b`. No implementation merge was performed. Required review is a human step, separate from passing technical tests.

## Actual failing-check merge rejection

[Closed probe PR #2](https://github.com/wmostafagmail/FindOurChild/pull/2) and [failed workflow 40079801282](https://github.com/wmostafagmail/FindOurChild/actions/runs/40079801282) demonstrate the negative path. A disposable base used the same App-bound required check, strict updates and administrator enforcement as main, with unrelated review requirements omitted only on that test base. Main's review requirements were never weakened.

Probe head `3c4457e3324149110babf5dcbd16f5981d49ccc0` changes one existing test to expect HTTP 418 while the unchanged application correctly returns 200. All 151 Python tests are still collected: **150 pass and one deliberately fails**. Subsequent browser/restore/audit steps do not execute; the result gate blocks, and none of those absent results count as passed. This deliberately invalid test revision is an enforcement probe, not an accepted application candidate. [Selected safe log lines](negative-log-excerpt.json) and [job steps](negative-job-steps.json) retain the exact failure.

The PR was non-draft, conflict-free and zero commits behind its base; the base had no review or conversation gate. With administrator enforcement active, an actual `PUT /repos/wmostafagmail/FindOurChild/pulls/2/merge`, constrained to the exact probe head, returned:

```text
HTTP 405
Required status check "phase1a-required" is failing.
```

[negative-gate-proof.json](negative-gate-proof.json) records the request, response, App identity, source revisions and causal preconditions. The PR was closed unmerged; both temporary branches and the test-only protection rule were removed. Main's SHA and complete App-bound protection were checked afterward. No probe change entered main, the implementation branch or local application source.

## Initial access issues resolved

The owner supplied an initially empty private repository and admin access. Initial protection/ruleset requests returned plan-level HTTP 403; the owner upgraded and the requests then succeeded. Initial atomic publication was rejected because the CLI OAuth token lacked `workflow`. The owner completed GitHub device consent; the observed scopes now include `repo` and `workflow`, and the engineering branch was published unchanged. No tokens, device codes or temporary download credentials are stored in project files.

Documents filesystem stalls required a byte-equivalent temporary Git-object mirror. Git object hashes and a complete `git fsck` were verified before the successful push. Incomplete intermediate copies were rejected by verification and never pushed. No commit identities or research history were rewritten. These access/environment failures are retained as resolved history, not reported as successful validation attempts.

## Recheck commands

These commands inspect existing GitHub evidence without merging or changing protection:

```sh
gh api repos/wmostafagmail/FindOurChild/actions/runs/40079573659
gh api repos/wmostafagmail/FindOurChild/branches/main/protection
gh api repos/wmostafagmail/FindOurChild/pulls/2
gh api repos/wmostafagmail/FindOurChild/actions/runs/40079801282
```

The [remediation report](REMEDIATION_REPORT.md) includes local reproduction and source/artifact hash checks. To check the versioned hosted evidence from this source tree:

```sh
.venv/bin/python - <<'PY'
from pathlib import Path
import hashlib, json
from scripts.fingerprint import fingerprint, inventory
p = Path('artifacts/hosted-sanitized/40079573659')
for name, digest in json.loads((p/'checksums.json').read_text()).items():
    assert hashlib.sha256((p/name).read_bytes()).hexdigest() == digest, name
assert inventory() == json.loads((p/'source-manifest.json').read_text())
r = json.loads((p/'results.json').read_text())
assert r['gate'] == {'status':'passed', 'reasons':[], 'source_digest':fingerprint()}
assert len(r['python']) == 151 and all(t['status']=='passed' for t in r['python'])
assert len(r['browser_observed']) == 72 and all(t['status']=='passed' for t in r['browser_observed'])
print('Hosted source and sanitized evidence verified')
PY
```

No outstanding Phase 1A technical validation blocker remains. Owner acceptance, independent PR review and explicit Phase 1B authorization remain separate decisions. Legal/safeguarding/data-protection approvals and all unimplemented operational/model workflows retain their original gates.
