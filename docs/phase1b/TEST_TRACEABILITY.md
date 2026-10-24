# Phase 1B executable traceability

The immutable 151-feature/630-test Phase 0 baseline and existing 1A mappings remain preserved in the master matrix. Original future operations remain pending; the new identity routes do not activate the 32 Phase 1C/domain endpoints. Each IDN entry in the JSON matrix records positive/negative/security/edge scenarios, fixture IDs, outcomes, exact executable selectors, evidence and current status. Browser count is 24 executions for each logical title.

| Feature | Executable cases | Current evidence |
|---|---:|---|
| IDN-01: JWT issuer/audience/signature/MFA/time/nonce and IdP failure boundaries | 32 | pending final hosted gate |
| IDN-02: Anonymous, forged, callback state and Secure-cookie boundaries | 14 | pending final hosted gate |
| IDN-03: Real Keycloak MFA, BFF/API, organizations, case grants, CSRF, audit and live revocation | 12 | pending final hosted gate |
| IDN-04: Real PostgreSQL session ACLs, role elevation denial, context isolation and audit integrity | 6 | pending final hosted gate |
| IDN-05: TesterArmy real TLS MFA/tenant/CSRF/logout, Arabic switch, every configured browser | 1 | pending final hosted gate |

| API operation | Executable coverage |
|---|---|
| GET /identity/login, GET /identity/callback, GET /identity/me | IDN-02, IDN-03, IDN-05 |
| POST /identity/logout | IDN-03, IDN-05; CSRF and revoked-session negatives |
| POST /identity/organizations/{org}/memberships | IDN-03 admin flow; IDN-04 sensitive-role/self-elevation negatives |
| GET /identity/organizations/{org}/cases/{case}/permission | IDN-03 cross-org/unknown/grant/membership expiry and revocation; IDN-04 context |
| GET /identity/organizations/{org}/audit | IDN-03 role/tenant/token-leak negatives; IDN-04 chain and mutation denial |

Platform sessions and all new SQL functions: IDN-04 plus IDN-03 real API/session flows. No background worker is delivered in 1B; worker/event/safeguarding cases remain pending in the master matrix. Separate unit doubles in IDN-01 do not count as real IdP/browser/database execution.
