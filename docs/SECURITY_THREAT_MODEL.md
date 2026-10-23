# Security threat model

Phase 0 design assessment. Controls are requirements, not implemented or penetration-tested security claims.

## Protected assets and boundaries

Highest-risk assets: child identities/photos, biometric vectors, exact shelter/custody, guardian contacts, authority evidence, legal-basis records, access grants and disclosure approvals. Also protect session tokens, encryption keys, audit roots, backups and notifications. Embeddings remain sensitive biometric data, not anonymized records.

Threat actors: fraudulent relatives/traffickers, abusive guardians, curious or compromised staff, malicious organization admins, upload attackers/bots, supply-chain attackers and infrastructure insiders. Model failures and reviewer anchoring are safety threats even without a malicious actor.

Trust boundaries: public browser/edge; BFF/API; identity provider; organization and case scopes; broker federation; quarantine/media worker; inference process/model artifacts; object store/KMS; audit sink; notification provider; backups/operator access.

## Threat/control/verification register

| ID | Attack or failure | Required control | Evidence required before pilot |
|---|---|---|---|
| T01 | IDOR, forged org ID, pooled tenant leakage | Server-validated principal/org, FORCE RLS, case grants, composite FKs, non-owner API role | Cross-tenant API+SQL negative tests, pooled connection race tests |
| T02 | Fraudulent claimant obtains identity/location | Separate contact vs relationship vs custody verification; no candidate disclosure; independent scoped approvals | Adversarial claimant journeys and safeguarding review |
| T03 | Insider enumerates/export cases | Purpose-based grants, explicit media permission, no bulk export by default, audit/anomaly review | Role matrix, export abuse tests, access-review drill |
| T04 | Session theft, phishing or shared staff account | Named users, MFA, short sessions, recent step-up for disclosure, secure cookies/CSRF, logout/revocation | IdP/BFF integration and session replay tests |
| T05 | Malware, polyglot files, decompression bombs | Quarantine, content validation, versioned malware scan, decode sandbox and resource ceilings | Adversarial files and scanner-down failure tests |
| T06 | EXIF GPS/shelter leaks | Private original, sanitized derivative, metadata/thumbnail stripping and separate custody table | Byte-level EXIF/thumbnail checks and DTO snapshots |
| T07 | Link leakage/cache/search indexing | Reauthorizing media gateway, no-store/no-referrer, no public buckets, restrictive CSP | Header, cache, CDN and bucket-policy tests |
| T08 | Model/vector leak or malicious weights | No public inference/vector endpoints; approved hashes, trusted serialization, no worker egress | Egress denial, weight-tamper and incompatible-space tests |
| T09 | False leads or adversarial image edits | Independent models/evaluation, uncertainty, human review, no automatic resolution | Open-set benchmark and staff false-lead exercises |
| T10 | Replay/race bypass of approval or deletion | Revision-bound approvals, unique actors, expiry, serializable/locked transition, tombstone checks | Concurrent approval/revocation/deletion tests |
| T11 | Notification leaks or spam | Neutral template, authorized recipient at send time, dedup/quota/retries and delivery audit | Provider stub tests, duplicate/out-of-order/revoked grant cases |
| T12 | Audit alteration or sensitive logs | Append-only role, chained hashes and external signed roots; allowlisted fields | Tamper detection, denied UPDATE/DELETE and log leakage scans |
| T13 | Lost keys/ransomware/backups restore deleted children | Separate KMS custody, encrypted backups, offline/immutable copies, tombstone replay | Measured recovery/erasure drills |
| T14 | Cross-NGO metadata inference | Disabled-default federation, bilateral purpose grants, broker-only edges, no hidden counts | Unauthorized-count/timing tests, opt-out race and bilateral disclosure tests |
| T15 | XSS from notes/names/generated output | Escaped text rendering, sanitized limited markup, strict CSP, no inline executable remote content | Stored-XSS cases in Arabic/English, rich-text and evidence previews |
| T16 | SSRF through URL image/report import | Do not accept remote image URLs initially; safe resolver/egress restrictions if added | Loopback/private/redirect/metadata-target tests |
| T17 | Bot flooding and storage exhaustion | Limits by contact/session/org/IP, accessible challenges, quotas, orphan cleanup | Load/abuse test without denying all shared-network users |
| T18 | Compromised dependency or stale service | Exact locks/digests, SBOM, license/CVE checks, signatures/provenance review and patch owner | Clean install, reproducible build and patch drill |
| T19 | Unauthorized aggregate inference | Small-cell suppression, fixed approved reports, no row drilldown | Differencing and low-count analytics tests |

## Cryptography and secrets

TLS on external and internal untrusted boundaries, private DB/object networks, managed envelope encryption with separated key permissions and rotation. Sensitive contact/custody/evidence fields encrypted with purpose-scoped keys; keys not in database backups. Passwords/tokens/API keys stay out of repository and logs. Store capability/verifier hashes with short expiry and bounded attempts. Never log request bodies or vector values by default.

Presigned media URLs are bearer access; the default gateway rechecks permissions per request. Revoke account, case and purpose grants centrally; background effects check again at use time. Strong admin authentication alone does not protect database owner credentials; operator access is break-glass with independent audit and time-limited approval.

## Incident handling and residual risks

Incident commander can freeze media/disclosure, disable matching and revoke sessions while preserving essential safe intake. Preserve evidence under a restricted legal hold, assess affected children and notify through counsel-approved procedures. No fixed statutory deadline is assumed without current Egyptian legal review.

Residual risks: facial resemblance among relatives, poor longitudinal coverage, insider screenshots, authorized-recipient misuse, identity-provider outage, incomplete model-training provenance and backup erasure lag. No software control alone establishes safe custody. Risk owners and acceptance must be recorded in the Phase 0 decision log; no acceptance is implied by this document.

