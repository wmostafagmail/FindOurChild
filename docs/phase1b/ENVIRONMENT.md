# Reproduce synthetic identity validation

Use the exact Node/Python/uv dependencies and existing foundation instructions. Run from the repository root:

```sh
uv sync --locked
npm ci --ignore-scripts
.venv/bin/python -m scripts.dev init
.venv/bin/python -m scripts.dev db
.venv/bin/python -m scripts.dev api
.venv/bin/python -m scripts.tls_setup
npm run typecheck
npm run build
npm run start
# Separate terminal, same workspace:
node scripts/tls.mjs
```

Application TLS: `https://127.0.0.1:3443/en/identity` or `/ar/identity`. The generated private `.runtime/identity.json` contains only synthetic credentials and maps each target to a separate synthetic account, so OTP replay prevention stays enabled. All test users have distinct IDs; browser and revocation cases do not share one user's OTP counter. This file, the generated realm, session key, CA private key, raw logs and dumps must remain untracked. Keep root `.runtime` private; only the synthetic generated import file is container-readable.

Run 157 regression cases inside the private DB network with `scripts.dev test`, then run 58 real identity/unit cases on the host with `scripts.identity_test`. The latter uses the explicit `.runtime/tls/cert.pem` CA for HTTPX, fixed loopback services and `docker exec` for synthetic revocation fixtures. No database host port is opened. Run `scripts.recovery` and `scripts.audit` with the pinned runtimes.

The required browser command remains `scripts.dev browser`: official e2e 0.21.3, web engine 0.15.3, Playwright 1.64.1; 24 targets, four titles, 96 executions; no ordinary Playwright-only acceptance suite. Telemetry off; deterministic assertions only; no model/provider calls. Password and computed OTP fills use the framework's Secret handles. Only fixed foundation screenshots are exported; identity DOM, cookies, form values, raw traces and errors are never published. Sanitized traces contain action names/status only.

The browser process must trust the generated test CA. The pinned engine has no custom per-context CA setting. CI config installs CA/NSS trust and the supported Firefox `Certificates.Install` policy only on a disposable Ubuntu runner ([Mozilla policy reference](https://mozilla.github.io/policy-templates/#certificates--install)); it does not disable certificate verification. On macOS, certificate trust needs explicit owner authorization and OS approval, followed by exact-fingerprint removal. For this review the owner chose hosted browser validation; local browser TLS acceptance is not claimed. Do not rerun certificate trust without new authorization.

After all executions, stop only the API gracefully so its instrumented process writes coverage, combine coverage and enforce the unchanged 75% threshold:

```sh
.venv/bin/python -m scripts.coverage_finish
.venv/bin/python -m scripts.artifacts
.venv/bin/python -m scripts.dev stop
```

`artifacts/sanitized` is the only upload directory. Required manifest updates are reviewed source changes, never generated during CI to make discovery match. Run the full regression after implementation changes; do not reuse old source digests or passing counts.

The API writes instrumentation only to its dedicated `/coverage` volume; it cannot modify the runner reports or manifests. The runner copies that data only after graceful shutdown. Test containers use the invoking host UID so host coverage can append without elevated filesystem access.
