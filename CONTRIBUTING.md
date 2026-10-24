# Engineering workflow

Use `main` for reviewed work and `codex/<scope>` or `feature/<scope>` for small branches. Open a pull request; do not commit directly to main. Every change includes affected tests, contract/migration changes and the traceability update. Full accepted regression runs on pull requests, main, merge queue and phase review.

The `Phase 1A required validation / phase1a-required` check must be required by repository rules, with stale approvals dismissed and direct pushes blocked. Local workflow files cannot establish remote branch protection. The private origin is wmostafagmail/FindOurChild. Main protection is configured/read back and bound to GitHub Actions App 15368; hosted regression and actual failing-check merge rejection are verified. PR review remains required. See docs/phase1a/hosted-evidence.json for current observed status.

Use `make bootstrap`, `make db`, `make api`, then `make web` in another terminal. `make test` runs actual PostgreSQL tests inside the private network. Install browser binaries with the locked `e2e-web` executable and both telemetry flags, then `make browser`. Use synthetic records exclusively. See docs/phase1a/REVIEW.md for the exact review state and remaining approvals.

Migrations are atomic and checksum-verified. Never alter an applied migration; add the next numbered migration. Use expand/contract changes and recovery validation. Database administrator credentials are confined to setup/tests; the API receives only `foc_api` credentials. The database has no published port. SQL context is trusted server context, never an API parameter; Phase 1B must validate identity before setting it. Raw SQL access as the API role is outside that trust boundary.

Phase 1B and 1C require separate user approval. No domain operation, biometric search, disclosure, approval or child handover is enabled in Phase 1A. No optional model/provider or remote-browser integration is configured.
