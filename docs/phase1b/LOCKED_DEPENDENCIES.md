# Locked Phase 1B dependencies

Existing runtime/framework pins are preserved. New direct security dependencies: **PyJWT 2.15.0**, **cryptography 50.0.0**. Full transitive wheels and hashes remain in `uv.lock`; npm integrity/version locks remain in `package-lock.json`.

| npm package | Exact version |
|---|---|
| next | 16.4.3 |
| react | 19.3.1 |
| react-dom | 19.3.1 |
| @e2e-dev/web | 0.15.3 |
| @types/node | 26.6.2 |
| @types/react | 19.3.0 |
| @types/react-dom | 19.3.0 |
| axe-core | 4.14.0 |
| e2e | 0.21.3 |
| typescript | 7.0.2 |

Keycloak: `quay.io/keycloak/keycloak:26.7.0@sha256:0f198be292568439d700cdbfb893e69a6009bb43a94a06a945b1d3d506c76b13`. PostgreSQL/pgvector and Python image digest pins remain in compose/Dockerfile. No optional telemetry/model provider is enabled.

| Lock | SHA-256 |
|---|---|
| uv.lock | fe8c22879ce0d6012df568347b91710f5b7c4b049217711231b032fae653bb37 |
| package-lock.json | 7991f50bd233efa82d6195e999891a8106019fb005c73e5c072ba9bbf5c578ff |
| requirements-bootstrap.txt | 524c21e2a1cf273b13001b30f117affa2718978f0586846d1fc731a5d826d66e |
