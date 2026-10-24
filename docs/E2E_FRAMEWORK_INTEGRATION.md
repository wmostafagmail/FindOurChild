# TesterArmy/e2e integration — Find Our Child

> Phase 1A execution update: the root lock/config/tests are active; `tools/e2e-plan` is preserved historical tooling evidence. Runner 0.21.3, web 0.15.3 and core 1.64.1 remain pinned, with a tested root Zod 4.6.6 security override. [Environment evidence](phase1a/environment-evidence.json) and [sanitized results](../artifacts/sanitized/results.json) record actual compatibility: Chromium/WebKit pass; Firefox launch fails on this macOS host. No Codex E2E MCP/plugin was activated; supported Codex integration research/specimens remain available below. Zero model usage was recorded, not a packet-capture claim.

Phase 0 correction, 23 October 2026. **Principal browser functional runner: the official [TesterArmy/e2e](https://github.com/tester-army/e2e).** Configuration specimens and tooling verification only; no application or application tests implemented. Existing product, model, privacy, RLS and safeguarding decisions remain in force.

## Reviewed identity and evidence

Repository commit: `69e123b17e04ed624df16d32f3b1ef95ce22c083`, committed 2026-10-23T19:31:37Z. [Selected source evidence](research/e2e/source-evidence.json), [framework lock](research/e2e/framework-lock.json) and [actual tooling check results](research/e2e/tooling-checks.json) distinguish documentation/source review, published packages, and commands executed here.

Read the official README/license, quickstart, Codex/coding-agent and MCP docs, web/config/expect/CLI/reporter references, security/telemetry docs, Next.js deterministic example, upstream examples CI and telemetry implementation/test source. All source links in the lock are immutable. Apache-2.0 applies to the reviewed framework; transitive dependencies retain their own licenses. External AI providers/hosted browsers would require separate terms and privacy review; none is selected.

| Component | Exact selected version | Compatibility evidence / limit |
|---|---|---|
| e2e | 0.21.3 | Published registry metadata, installed CLI/version, configuration load |
| @e2e-dev/web | 0.15.3 | Published peer requires e2e >=0.18.0 <1; exact selected pair installs and specimen type-checks |
| playwright-core | 1.64.1 | Exact web-engine dependency and lock; browser revisions recorded from installed browsers.json |
| Node.js | 24.18.0 | Observed host runtime; both framework packages declare ^22.22.3 or >=24.8.0 |
| npm | 11.16.0 | Observed installer, frozen package-lock |
| TypeScript | 7.0.2 | Official source dev-tool version; installed compiler accepts specimen |
| @types/node | 26.6.2 | Official source dev-tool pin; type-check aid, not an assertion that host is Node 26 |

The [package manifest](../tools/e2e-plan/package.json) and [transitive lock](../tools/e2e-plan/package-lock.json) freeze research/configuration verification. Install used `--ignore-scripts`; optional native/platform functionality beyond observed checks is not established. No browser binary was downloaded/launched and no cross-browser compatibility is claimed from type checking. Actual browser/full-stack smoke tests are a Phase 1 gate. Future upgrades must repeat peer/install/config/browser/telemetry/security checks and update lock plus source evidence; upstream is pre-1.0 and warns APIs may change.

## Official installation and selected adaptation

Official quickstart offers `npx e2e init`, engine Web and provider **None** for deterministic tests. Its `init --yes` setup prompt defaults to a gateway/provider example and writes project artifacts; do not blindly use that default here. **No init, app scaffolding, plugin installation or active e2e MCP registration was performed in this correction.**

Phase 1, after authorization: reproduce the pinned dependencies with `npm ci` in a dedicated test project, review dependency scripts, install only the pinned engine's required browsers with local `e2e-web install chromium --with-deps` (plus firefox/webkit where supported), and complete isolated full-stack readiness before running tests. Dependency/browser installation belongs to an authorized preparation job with network access; execution denies unapproved egress. Do not install a separate floating Playwright version or use an unpinned npx fetch in CI.

Use local lockfile-installed `./node_modules/.bin/e2e` for `list`, `run` and `mcp`. The [configuration specimen](../tools/e2e-plan/e2e.config.example.ts) has 24 planned browser/locale/width targets, retries 0, cache off, local browser engines, trace on for **synthetic-only** evidence, video off, list/JUnit reporters and no model/provider. It does not start an app; Phase 1 orchestration must start and verify the actual complete service stack first.

## Codex integration, separately from a test result

Official [coding-agent docs](https://github.com/tester-army/e2e/blob/69e123b17e04ed624df16d32f3b1ef95ce22c083/docs/coding-agents.mdx) describe a repository-provided Codex plugin and project skill. Plugin installs supply skills, not the npm package or MCP server. The reviewed plugin manifest version is 0.21.3. The official [MCP guide](https://github.com/tester-army/e2e/blob/69e123b17e04ed624df16d32f3b1ef95ce22c083/docs/mcp-server.mdx) documents a project `.codex/config.toml` entry, project trust and new session.

The [inert Codex specimen](testing/codex-e2e.example.toml) adapts that documented registration to a local pinned executable, explicit config and telemetry/synthetic guards. Placeholder paths intentionally prevent activation. Review real paths, project trust and access scope in Phase 1 before copying into active configuration. The user has requested an engineering/validation plan, so no active client configuration is changed now.

An MCP session can inspect live controls and produce candidate test lines. It is not a test run and produces no accepted test results. Codex is itself a model-backed client: expose only the isolated synthetic stack to it. Even though the MCP server needs no model, sending a real child screen to Codex would violate this testing boundary.

## Deterministic outcome policy

Use `test` from `@e2e-dev/web` and `expect` from `e2e`. Prefer semantic role/label/test-ID locators, explicit normalized values, response codes/schemas and authoritative SQL/storage/outbox observations. Poll observable conditions with bounded deadlines rather than fixed sleeps.

If an optional AI-assisted synthetic test is later approved, each `agent.act` atomic goal must be followed by deterministic assertions. `agent.assert`, generated natural-language confidence, screenshots alone and agent-reported success are insufficient acceptance oracles. A success toast cannot prove a persisted case, denied cross-tenant query, erased embedding or safe release. Browser journeys coordinate with independent API/DB/worker observers using separate read-only test credentials.

Mandatory regression is model-free and cache-off. A cached agent step can call a provider on a miss/hand-off; cache read-only is not an external-model prohibition. No external model is permitted to process real child data, even if a test operator has consent to use the data elsewhere. Lawful recognition evaluation occurs in its separate restricted ML harness.

## Real services and isolated database

Browser suites execute against actual Next.js/BFF, FastAPI, test Keycloak, PostgreSQL/pgvector, private test object storage, scanner path and job workers for enabled features. A route mock, in-memory database or UI-only fake backend cannot satisfy browser E2E. Component tests may mock; they are a different suite. External notification delivery goes to a test sink through the actual adapter; no messages go to real claimants.

Each CI run/shard gets a distinct database, database credentials, realm, buckets, queues and run identity. Apply real migrations and RLS to the test database; use actual non-owner API/worker roles. Preflight must independently inspect database identity/role, marker seed, service build digests and absence of production destinations before destructive setup. An environment flag alone is not proof of isolation. No fallback to an existing developer/staging/production database. Failed readiness blocks the suite.

Fixtures include unrelated organizations, suspended memberships, explicit case grants, both registries, safe synthetic photo objects, uncertain facts, independent approvers, wrong leads and revocation/deletion race barriers. Seed via a restricted test provisioner; browser operations use actual public/staff services. Read-only side-effect oracles have a separate test-only interface unavailable in deployed app networks.

## Telemetry, model traffic and artifacts

Every process (CLI, MCP, config, CI job and helper) gets `E2E_TELEMETRY_DISABLED=1` and `DO_NOT_TRACK=1`. Specimen import rejects missing opt-outs. Official telemetry is on by default; disabling it does not disable model calls, update checks, browser downloads or reporter integrations. Execution network policy permits only the isolated service network; pre-download packages/browsers in a separate trusted stage. Verify opt-out with local `e2e telemetry` and independently test outbound denial in Phase 1. The observed CLI status is not a packet-level proof of zero egress.

Official security docs state model-visible content can include accessibility trees, URLs, step history and requested screenshots; test/config/tools run with OS permissions and there is no built-in origin allowlist. Browser policy cannot substitute for an OS/container/network sandbox. No model keys, remote browser integrations, hosted artifact stores, feedback/repro uploads or public PR comment reporter in the mandatory lane.

Built-in secret redaction is incomplete: command.log is verbatim, video is unmasked, transformed values/downloads/cache may leak, and screenshots are not general PII redaction. Raw evidence stays ephemeral/restricted; sanitize screenshots/traces/logs/JUnit/SQL reports and scan canaries before publishing to the approved artifact store. Sanitization failure blocks acceptance and publication; publish only a safe failure manifest. Sensitive ML datasets do not enter browser evidence.

## CI adaptations and unresolved limits

Upstream examples.yml runs nightly/dispatch, not a PR gate, builds main, uses live models and retry semantics, and notes examples have no lockfiles. Its report upload and telemetry opt-out patterns are useful; its trigger/credential/retry/version policy is not our acceptance policy. Upstream CI docs allow clean skips, optional no-test success and rerun shortcuts. Here required-check policy rejects missing/zero/skipped/interrupted/flaky mandatory cases, retains original failures and uses explicit phase/target expected inventories. `failOnSkippedFailure: true` only covers skip-after-failure, so an independent result-inventory gate is necessary. No AI filter selects critical tests.

Outstanding: no app services or test database yet, no runnable matrix tests, complete API/DDL still pending, browser binaries/OS dependencies not exercised, other suite tools/release images not pinned yet, artifact sanitizer/result gate/CI workflows not implemented and branch protection not configured. These remain explicit Phase 1 validation deliverables, not passed checks. Browser E2E does not replace DB/RLS tests, adversarial testing, independent penetration testing or model evaluation.

