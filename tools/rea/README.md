# Pinned REA research tooling

Research-only npm project. Exact package rea-agents 6.7.0; package-lock pins transitive versions and integrity. MIT REA code; third-party dependency licenses recorded under docs/research/research-dependency-inventory.json.

Install in this directory with npm ci --ignore-scripts. Lifecycle scripts are deliberately disabled; optional native integrations are not established by this installation. Use the compatible runtime declared by the actual published package; reviewed source main has stricter requirements. Local verified runtime: Node 24.18.0, npm 11.16.0.

Codex registration was configured using the documented workflow:
1. node_modules/.bin/rea setup --client codex --skill=false --dry-run --json
2. Review the exact plan, scoped only to Codex.
3. node_modules/.bin/rea setup --client codex --skill=false --yes --json
4. node_modules/.bin/rea doctor --client codex --format json

Setup writes the user's Codex config with a backup. Do not apply these commands to another user's configuration without authorization. Restart Codex for MCP discovery. The final registration points to /Users/waleedmostafa/.codex/tools/find-our-child-rea-6.7.0/node_modules/.bin/rea. Workspace package/lock files reproduce the same installation; the durable runtime avoids observed workspace read instability.

Use static analyze-javascript-application against public/authorized local snapshots. Outputs can contain source/path information, so review retention. No child images, tokens or runtime sessions were used here.

The source evidence is not a full checkout, security audit or production dependency approval. Optional native providers/skill were not installed. See docs/REA_RESEARCH_REPORT.md for actual commands/results/limits.

