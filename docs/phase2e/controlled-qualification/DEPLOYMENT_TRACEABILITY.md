# Private readiness feature-to-execution traceability

All exact selectors are frozen in `../deployment-required-tests.json`; current hosted status is pending, local unit status 52 passed. This adds source-only readiness features without replacing existing TEST_MATRIX/V3 governance scenarios.

| ID | Components | Executable coverage | Expected outcome |
|---|---|---|---|
| DR-01 | protected.py, cli.py | closed_configuration (18); local_setup; protected_file_negative | Unknown fields/paths, CI and non-TTY setup denied; no seeded owner |
| DR-02 | oidc.py, app.py | actual_signature_owner_mfa_and_live_session (19); real_tls_startup; real_owner_mfa | Real RS256+SPKI+exact subject/auds/MFA+introspection; foreign/stale/untrusted denied |
| DR-03 | state.py, SQL | real_owner_mfa; live_private_storage_negative_boundaries (5); real_forced_rls | Proof exact config/session/expiry, consumed once externally; tenant isolation and irreversible session revocation |
| DR-04 | producers.py, cli.py | producer_registry_rollback; real_producer_registration | Actual local machine PoP; fixed measurement source/build/tool, expiry/epochs, external journal+SQL commit; revoke/rollback/uncommitted denied |
| DR-05 | storage.py | real_generated_immutable_storage | Fixed benign bytes only, real sealed FD, no replace; actual assets unavailable |
| DR-06 | compose.py, Dockerfiles, unchanged supervisor | runtime_topology; actual_nonroot_offline_worker (3) | Linux amd64, private databases/no runtime admin secret, offline non-root bounded helper, hard deadline |
| DR-07 | checkpoint/state/SQL | real_hold_revocation_epoch_recovery_and_restored_proof_replay | Hold advances external epochs; restore isolated/inactive, fresh proof recovery, prior sessions denied |
| DR-08 | app.py, owner.js/css | private_http_closed_surface (11); real_csrf; DR-B01 ×24 | Private bilingual/RTL responsive WCAG assertions, CSRF/owner-claim denial, no campaign/model/public-search routes, signed-out clean shell |
| DR-09 | deployment_validate.py, required CI | exact inventory/source/payload checks, all-stage assertions | No mandatory green skip; frozen original suites remain required; private logs never published |

Fixtures are exclusively generated credentials, fictional immutable subjects, ephemeral TLS identities, generated machine keys and fixed benign text. No image/model data or human consent is represented. Evidence path: hosted artifact `phase2e-deployment-readiness-<checkout SHA>`; no passing hosted result is claimed until independently verified.
