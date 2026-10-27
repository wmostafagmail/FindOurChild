# Synthetic investigation demonstration runbook

Use an isolated local clone and existing exact locks. No model/image-dataset acquisition is needed or authorized. Never copy operational credentials, case databases, photographs or private research datasets into it.

1. Install the pinned Python/Node tools, run `uv sync --locked` and `npm ci --ignore-scripts`.
2. Run `.venv/bin/python -m scripts.dev init`, then `db` and `api`. These commands provision the synthetic database, migrations, private storage, ClamAV and Keycloak realm; secrets stay in ignored `.runtime` files.
3. Run `.venv/bin/python -m scripts.workflow_validate`. It provisions closed procedural cases/media through the real scanner, executes the exact required unit/PostgreSQL lane, and restores the actual bounded worker. Fixture grants expire; they are not operational NGO approval or guardian verification.
4. Build and run the web service using existing scripts. Staff enter `/en/investigation` or `/ar/investigation` using privately provisioned synthetic MFA accounts. Credential values must never enter reports, screenshots, commits or model calls.
5. Start a sealed scenario, open a candidate, inspect each authorized photograph and its independent chronology, and record structured human decisions. A separately authorized synthetic safeguarding person must complete the independent stage. Assignment never grants access; rejected evidence cannot be recycled into an identity conclusion.

Local browser TLS trust is an environment prerequisite, not a reason to bypass certificate verification. The owner selected hosted TLS validation; the required GitHub workflow configures trust only on disposable hosted runners and executes all Chromium/Firefox/WebKit targets. No further macOS keychain changes are part of this phase.

Full regression: hosted workflow `phase1a-required`, plus the separately reported local scripts. `workflow_test synthetic_workflow_http` requires the actual TLS BFF/Keycloak/API/worker. Tests use real services and synthetic fixtures. Private operator fault tools are CLI-only, enforce synthetic database identity and a closed account/action list, and always restore injected revocation/audit faults. They are not application endpoints or staff privileges.

Recovery uses a quarantined fresh restore, a new independent private activation epoch, then explicit current permission/revocation reconciliation before any controlled synthetic reissue. Do not restore an old backup over the running database and reuse activation/session configuration. The native drill verifies backup/schema/RLS preservation and default denial in the restored copy. It does not certify production erasure or automate institutional activation.

Rollback: stop synthetic entry/worker leases, retain applied migrations and immutable evidence, and use an explicitly compatible binary or quarantined restore. Do not drop the new journal or rewrite 0001–0024. Current schema changes do not enable the generic biometric, custody or release APIs. Phase 2E requires separate acceptance and authorization.
