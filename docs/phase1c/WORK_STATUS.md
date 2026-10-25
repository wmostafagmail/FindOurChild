# Phase 1C engineering work in progress

Phase 1B acceptance is verified in ../phase1b/ACCEPTANCE.md. Current branch: codex/phase-1c-reporting-case-management. No Phase 2 authorization.

Implemented draft source: reporting.py/media.py/worker.py; migrations 0007–0014; private SeaweedFS 4.48, ClamAV Debian 1.5.4, Pillow 13.0.0; bilingual reporting page and fixed BFF routes; reporter contact verification into encrypted private local sink; staff moderation/notes/assertions/assignment; scoped media gateway and leases. Original 0001–0006 migrations and protected research are preserved.

Diagnostic reporting runs: 55/83, 64/85, then 85/85 passed against actual PostgreSQL/S3/ClamAV. Subsequent source changes require fresh full validation. Browser additions exist but are unexecuted. Phase 1C is not accepted or complete. Pending work includes hosted validation, live-HTTP reporting cases, outage/worker cleanup tests, CI/result-gate integration, final traceability/evidence/report and draft PR.

Known limitations to retain in final report: synthetic-only notice/contact restrictions; no external messaging provider; operational legal/NGO/retention/KMS approvals remain; no production facial recognition or custody/release/disclosure implementation. Typed public-command idempotency wrappers were added after the diagnostic runs and need regression. All local certificate trust restrictions remain: browser TLS validation hosted only.
