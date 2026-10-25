# Phase 1C validation report — in progress

Phase 1B is accepted based on actual merged main `9fcb6ef` and passing required run `40144238603`; see [acceptance and checksum evidence](../phase1b/ACCEPTANCE.md). Phase 1C is implemented on `codex/phase-1c-reporting-case-management` and remains under technical validation. Phase 2 has not begun.

The frozen inventory currently requires 158 preserved baseline Python cases, 58 identity cases, 107 reporting/media/worker cases, one actual scanner-outage case, six real reporting HTTP cases, and 168 official TesterArmy executions (56 each Chromium/Firefox/WebKit). These are requirements, not a claim that the current revision has passed every lane. Required cases may not be skipped.

Current diagnostic evidence: the baseline reached 158/158; reporting reached 96/96 plus the real scanner-outage pass, then 103/106 with three cleanup failures caused by stale storage IAM. IAM reload is now reproducible and narrowly scoped version enumeration was verified. New boundary/recovery/claim-projection changes require a fresh full run. Hosted browser/live-HTTP evidence is pending. Tests are not marked passed in new traceability until current source-bound sanitized evidence is independently verified.

Historical corrections include scanner architecture compatibility (official Debian multi-arch image), non-root storage startup, volume allocation/readiness, SQL search path, duplicate OpenAPI parameter, closed claim projection bounds, retry idempotency and stale-worker orphan cleanup. Original Phase 0–1B evidence is preserved. Private diagnostics are retained outside published artifacts; no sensitive assertion values are included here.

[Architecture](ARCHITECTURE.md) and [reproduction](ENVIRONMENT.md) define delivered scope. This remains synthetic engineering: external messaging, production KMS/IdP/hosting/signature-update operations, legal/retention/NGO approvals, independent penetration/manual accessibility/load acceptance and whole-case/backup erasure remain separate release requirements. No production face recognition, automated identity decision, disclosure authorization or child release is implemented. Case evidence supports image documents; PDF/Office/SVG imports are rejected. Capture metadata can be set per upload via API; the UI applies capture-year metadata to a selected batch. Summary/journal quotas are explicit.

A final immutable CI/artifact verification, exact results, source inventory, dependency manifest, updated traceability and draft PR will replace this in-progress assessment before the turn completes.
