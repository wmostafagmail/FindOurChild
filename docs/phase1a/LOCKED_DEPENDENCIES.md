# Locked dependency manifest

The complete resolved versions and integrity hashes are [package-lock.json](../../package-lock.json), [uv.lock](../../uv.lock) and [requirements-bootstrap.txt](../../requirements-bootstrap.txt). Their SHA-256 values and observed runtime/image identities are in [environment-evidence.json](environment-evidence.json). The direct npm/Python manifests are [package.json](../../package.json) and [pyproject.toml](../../pyproject.toml).

| Component | Selected pin |
|---|---|
| Node / npm | 24.18.0 / 11.16.0 |
| Python / uv | 3.13.13 / 0.12.0 |
| Next / React / React DOM | 16.4.3 / 19.3.1 / 19.3.1 |
| TypeScript | 7.0.2 |
| TesterArmy runner / web / Playwright core | 0.21.3 / 0.15.3 / 1.64.1 |
| Active Zod security override | 4.6.6 |
| axe-core | 4.14.0 |
| FastAPI / Uvicorn / psycopg | 0.162.0 / 0.54.0 / 3.3.6 |
| pytest / pytest-cov / Ruff / pip-audit | 9.1.1 / 7.1.0 / 0.17.2 / 2.10.1 |
| PostgreSQL / pgvector runtime | 17.11 / 0.8.7 |

PostgreSQL image: `pgvector/pgvector:0.8.7-pg17-bookworm@sha256:ac08538c6f8b9904c33c8224c5e5706dbe760aca29db1d096972b4052c22a75d`.

Python base: `python:3.13.13-slim-bookworm@sha256:355bfa66770995d7e9a0da4b3473b44d0cb451f6b56f5615ad9c39e3c4eca03f`.

All additional direct/transitive packages, optional-platform packages and wheel hashes are recorded by the locks. The database image digest, not the moving `pg17` family label, fixes its actual patch release. Source-to-published-package equivalence is not attested by these version locks. No facial model/weights are selected or enabled.
