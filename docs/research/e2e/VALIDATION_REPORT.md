# Phase 0 testing corrections — validation evidence

23 October 2026. Scope: documentation, traceability, framework dependency/configuration specimens. **No application implementation, application services, browser execution, test database, CI enforcement or application test results.**

Final observed results: original-package integrity checker **passed (271 structural checks)**; correction checker **passed (4954 structural/inventory checks)**. The registry covers **151 features, 630 planned cases, 32 declared API operations, 37 relation-boundary rows and 15 event contracts**. All application cases remain pending with no execution evidence. Seven tooling/configuration expectations were met, including deliberately nonzero no-tests and unsafe-configuration diagnostics; those are not seven passed application tests.

## Actual tooling evidence

Exact reviewed source commit and selected source content/hashes are in [source evidence](source-evidence.json) and [framework lock](framework-lock.json). Exact published e2e 0.21.3 + @e2e-dev/web 0.15.3, transitive playwright-core 1.64.1 and compiler/type versions are frozen in the research tool package lock. Source and npm package are separately identified; no source/package equivalence attestation performed.

Isolated install and clean npm ci used lifecycle scripts disabled. Node 24.18.0/npm 11.16.0 satisfy published framework requirements and the web-engine peer range accepts the runner. These checks do not establish browser binary/OS or application runtime compatibility. See [install](install.log) and [clean install](clean-install.log); npm's point-in-time audit output is not independent security evidence.

[tooling-checks.json](tooling-checks.json) records actual exit codes and expected diagnostic matches for CLI version, telemetry-off status, configuration type checking, no-test discovery and fail-closed configuration guards. Type checking uses skipLibCheck and verifies our config shape, not all upstream declarations. No browser or model was started. The default specimen contains no model provider; packet-level outbound traffic was not measured here.

The empty discovery check returns nonzero NO_TESTS and is deliberately **not successful application validation**. Missing telemetry opt-out, nonlocal target and nonsynthetic class each cause configuration failure. No pass-with-no-tests switch or dummy passing browser test was introduced.

## Documentation and traceability checks

The original validator still checks the original 16-document/source-evidence package. The corrections validator additionally checks four new documents, protected original-content hashes, all declared requirement/API/schema/event/threat inventories, planned executable IDs and pending evidence state, eleven safeguarding browser/state companions, exact source/package pins, safe configuration/TOML/environment policy and local links. Actual outputs: [base-phase0-checks.json](base-phase0-checks.json) and [documentation-checks.json](documentation-checks.json).

All application test targets in TEST_MATRIX are future implementation paths. Every feature/test is pending and execution_evidence=null. No discovery, planned command or documentary coverage count is a passed application test. Existing original REA/repository evidence and child-protection decisions remain preserved; original approval blockers still apply.

## Unresolved evidence and scope

Complete executable API/DDL contracts, full browser/OS installs, actual app/database smoke, application suite tools/runner/action release pins, CI jobs/hosting required checks, fixture provisioning, sanitizer and result reconciler, security/penetration/ML/performance/recovery/deployment evidence remain pending. Codex plugin/MCP registration was researched and shown as an inert specimen, not installed or invoked. Phase 0 is ready only for documentation review; no permission to start Phase 1 is implied.

The current workspace has no Git repository, remote or active PR/merge protection to configure; CI/CD requirements are a reviewed design target, not enforced host settings. No missing required document or fetched research category was found by these checks. Additional service-specific contracts and runtime evidence listed above remain intentionally unimplemented.
