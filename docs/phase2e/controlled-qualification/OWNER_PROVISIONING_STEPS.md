# Historical b9e161f4 checkpoint — retained evidence

The following is the original pre-implementation owner-boundary packet. For the subsequently authorized executable Step 2 adapter, use [PRIVATE_DEPLOYMENT_GUIDE.md](PRIVATE_DEPLOYMENT_GUIDE.md). Its earlier missing-adapter statements describe b9e161f4 and do not mean the current source is documentation-only. No actual owner has been provisioned.

# Secure real-owner provisioning and confirmation steps

**STOP boundary:** no real owner has authenticated or been enrolled. The current
checkout is not a provisioned demo environment. No ready-to-use enrollment URL,
bootstrap command or campaign digest exists yet; do not substitute a test route.
This procedure separates required owner actions from pending engineering work.
One real project owner is sufficient under V3; no second human or human
Ed25519-signing process is introduced.

## 1. Owner supplies the protected deployment destination

Choose a private synthetic-only Linux x86_64 demo host/environment and a verified
HTTPS application origin. Identify its real IdP issuer, application client ID,
exact allowed audience set and the account that will be the sole demo owner.
Use the existing IdP's administrative interface to create/identify that real
account and enroll MFA yourself. Keep recovery material under your control.
Do not reuse fictional CI users, their TOTP seeds, a GitHub identity claim or
`.runtime/identity.json`. Do not send passwords, OTPs, session cookies, client
secrets, private producer keys or recovery keys in chat, Git or public CI.

Handoff non-secret deployment details through the approved private configuration
channel. The owner subject is an immutable IdP identifier obtained and checked
from actual authentication/administration, not an arbitrary `owner=true` field.
Record the following as a **pending deployment proposal**, not trusted enrollment:

| Required item | Who controls it / how verified |
|---|---|
| Private deployment destination, HTTPS origin, instance and synthetic tenant | Owner selects; engineering checks host isolation and TLS identity |
| Real IdP issuer, client and exact audiences | Owner/IdP administration; independently check discovery and pinned signing keys |
| Real owner immutable subject/principal mapping | Owner authenticates with fresh MFA; server verifies signed issuer/audience/subject and platform mapping |
| Client secret and storage-encryption credentials | Owner-controlled secret store or protected host-local provisioning session; never a public record |
| Checkpoint custody and backup/restore destination | Owner-controlled private storage outside authorization DB rollback scope |
| Service producer key custody and intended receipts | Dedicated technical services, not human reviewer identities or CI fixture keys |

These inputs are missing today. Stop here until the owner can supply/configure
them securely. Existing chat authorization permits engineering work; it does
not constitute the later authenticated campaign confirmation.

## 2. Engineering installs and validates D5 before asking for scope consent

After the destination/identity handoff, implement/review a separate protected
bootstrap/deployment adapter for the existing V3 primitives. This adapter is not
installed by this packet. Do not patch production to import the CI test factory
or enable a registry by editing a boolean. Preserve V1/V2 and operational policy.

1. Deploy the reviewed exact build with no operational credentials, case data or
   networks mounted. Keep owner authority inactive and acquisition/parser/inference
   closed. Establish TLS, trusted wall/monotonic time, bounded logs and private
   audit storage. Document administrative access and rollback trust assumptions.
2. Initialize the separate private V3 PostgreSQL schema from its unchanged
   migration. Use a dedicated non-superuser/NOBYPASSRLS runtime identity;
   migration/administrative credentials must not enter API/worker environments.
   Verify tenant/instance isolation and append-only journal/audit/outbox denial.
3. Provision the protected external checkpoint with its own custody and
   append-only durability. Bootstrap matching instance/authority epochs under
   the authenticated ceremony; never invent current cursors from an old backup.
   Keep an unmatched, corrupt or unavailable checkpoint inactive.
4. Bind the real owner through the validated IdP/platform mapping and live
   session checks. Require actual password/OTP assurance and authentication age
   no greater than 300 seconds, pinned signature/issuer/audiences, origin/CSRF
   and same-session confirmation. Capture only sanitized success/failure evidence.
5. Register actual technical-service producer public keys through protected
   administration. Pin service source/build/tool identities, allowed receipt
   classes, deployment scope, validity, epochs and revocation. Generate/retain
   private service keys inside their protected service custody, never for an
   invented human. Verify proof of possession and reject CI/generated-buffer
   producers as real asset qualification authorities.
6. Provision encrypted private quarantine and immutable, closed-path registry
   roots using reviewed directory FDs/ownership. Validate no symlink/hardlink/
   writable-alias substitution, no pathname reopening after snapshot, sealed
   byte rehashing, no replace and read-only consumer mounts. Acquire no bodies.
7. Validate resource-isolated Linux worker deployment using generated benign
   fixtures only: non-root, offline, read-only, dropped capabilities, hard cgroups/
   CPU/AS/PID/FD/output/temp limits, independent supervisor/deadline, descendant
   reaping, cancellation and stale-publication fencing. The source-only profile
   does not qualify real dlib loading. No model parser may run at this step.
8. Execute real deployment negative tests for wrong owner/tenant/purpose, stale
   MFA, revoked sessions, expired authority/receipts, wrong producer/build/epoch,
   checkpoint corruption, control-plane loss and inactive restore. Restore must
   reconcile authority and permanent fixture history before reactivation.

Retain exact deployed source/binary hashes and actual test outcomes. Do not
claim these steps passed from hosted synthetic tests. Any failure stops dependent
work; no automatic epoch reconciliation, profile widening or success override.

## 3. Prepare the actual load-only campaign after D5 passes

Reverify the frozen upstream source identities, current code/weight/image license
texts, provenance restrictions, immutable URLs and exact sizes **without asset
body acquisition**. Preserve original and current observations. Reject changes
or unavailable evidence; do not select replacements. Use exactly the original
three models and 48 images/24 pairings, independent capture-date/age uncertainty,
explicit synthetic provenance and no score-informed replacement.

Construct the closed V3 record from actual deployment identities and exact
source/build, models/images/fixtures/processing/resources/rights plan digests.
Freeze per-stage CPU/wall/RSS/AS/PID/FD/output/temp limits, quarantine and evidence
retention/deletion policy, scanner/decoder/native versions, audit, epoch and
expiry rules. Only acquisition, byte verification, bounded processing and
load-only qualification may be in scope. Inference and all sensitive operational
actions remain absent and disabled. A complete immutable scope is not available
yet; a draft JSON object with placeholders is not authority.

## 4. Owner performs actual confirmation in the private application

Engineering first demonstrates that the real owner session reaches the deployed
private page at the validated origin and `/en/demo-authorization` or
`/ar/demo-authorization`. These routes exist in source but are unprovisioned
today; no local CI hostname or invented URL is an enrolled destination.

The owner signs in with fresh MFA in their own browser, selects Prepare, reviews
the complete server-held scope, all 51 source references, 48/24 immutable fixture
plan, uncertainty, processing/resource/retention limits and loss-of-independent-
review disclosures, then checks the explicit confirmation and confirms the exact
displayed campaign digest within the five-minute challenge. Read back the
immutable private record/audit and expiry (at most four hours); test renewal and
revocation without extending or mutating the old scope. No chat reply, copied
token, schema-valid document, screenshot or synthetic record substitutes for
this event. Keep bearer tokens and complete private records out of public reports.

## 5. Only then acquire and qualify, stopping at A5

With live valid acquisition authority and all actual prerequisites, fetch only
the closed approved assets to encrypted quarantine. Record pinned upstream
identity, measured size and SHA-256, redirect/source chain and all failures.
A3 verifies actual bytes. A4 performs bounded single-stream decompression, real
malware scanning, sandboxed decoding and immutable derivative lineage. A5
performs only fixed-component isolated model parsing/load qualification with
actual binary/model hashes and measured hard limits. No image inference, face
detection on fixtures, landmarks, descriptors or similarity search may run.
Each stage needs actual trusted technical receipts and all previous successful
dependencies. Reject failure, mismatch or unavailable state; retain originals
and never substitute assets or silently increase resource caps.

Run every affected security/database/recovery/native/governance suite and the
complete existing application and official three-browser regressions. Publish
an exact-head draft PR and actual outcome/limit/receipt evidence; pending A3/A4/A5
steps never count as passed. Keep database and queue/resource/security misses
separate. Stop for owner review at A5, without merging or starting Phase 2F/3.
