# Find Our Child — testing-framework verification only

This private tooling package pins e2e 0.21.3, @e2e-dev/web 0.15.3, TypeScript 7.0.2 and @types/node 26.6.2; package-lock pins playwright-core 1.64.1 and transitive dependencies. Verified host: Node 24.18.0/npm 11.16.0. This is not an application package or implemented test suite.

Phase 0 checks used an isolated temporary npm install/clean npm ci with --ignore-scripts. No browser binary, app server, test database, model/provider, active Codex plugin or MCP registration was started. The config is an inert specimen for Phase 1; it may be type-checked after installing the exact lockfile but finds no tests in this package.

All e2e CLI/MCP/helper invocations require E2E_TELEMETRY_DISABLED=1 and DO_NOT_TRACK=1. The specimen additionally requires FOC_E2E_DATA_CLASS=synthetic and FOC_E2E_ISOLATED=1, accepts loopback targets only and has no model, cache or retries. Environment markers are not proof of actual database isolation; independent preflight is still required before Phase 1 execution.

Use the local lockfile-installed binary. Do not run init --yes, unpinned npx or remote model/browser integrations as a shortcut. A NO_TESTS diagnostic is a non-success and never a passed application test. Actual browser/OS and full-stack compatibility remain pending.

See docs/E2E_FRAMEWORK_INTEGRATION.md, docs/TEST_MATRIX.md, docs/CI_CD_TEST_GATES.md and docs/research/e2e/VALIDATION_REPORT.md from the workspace root for research, exact evidence and unresolved gates. Follow approved safeguarding/retention and fail-safe policies before implementation.
