"""Generate planned test traceability. This does not create or execute application tests."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
features = []
FIXTURES = {
    'FX-BASE': 'Synthetic organizations A/B, unrelated cases, named requester/reviewer/authority/auditor/operator, same-role different principals, explicit grants; no real identities.',
    'FX-UNCERTAIN': 'Original Arabic/English spellings, Arabic digits, NULL/approximate/disputed intervals, no-photo reports, impossible chronology and multiple revisions.',
    'FX-MEDIA': 'Generated non-child drawings and consent-free geometric test images, EXIF/GPS canaries, multiple face-region adapter outputs, malformed/MIME/polyglot/decompression fixtures; no real child photos.',
    'FX-IDP': 'Local test Keycloak realm, synthetic users, fresh/stale MFA, wrong issuer/audience, expired/revoked sessions and pooled connection contexts; disposable credentials.',
    'FX-MATCH': 'Synthetic case/score/vector manifests, incompatible spaces, deliberate wrong leads, no-mate cases and human rejection; synthetic vectors cannot demonstrate recognition accuracy.',
    'FX-APPROVAL': 'Synthetic claimant, missing/found pair, independently verified-authority fixture, distinct actors, same actor with two roles, revision/expiry/conflict variants.',
    'FX-EVENT': 'Closed event envelopes with duplicate/reordered IDs, lease expiry, crash checkpoints, tombstone generations, provider stub receipts and deterministic clock.',
    'FX-PURGE': 'Synthetic original/derivative/object versions, vector partitions, grants, exports, cache markers, queues and backup copies; scoped legal-hold variants.',
    'FX-DB': 'Fresh/previous synthetic schema snapshots, actual non-owner DB roles, deliberate cross-org FK links, empty/missing tenant contexts, rollback/fault barriers.',
    'FX-FAILURE': 'Isolated scanner/IdP/KMS/storage/audit/provider outages, latency/network partitions and process kills; no production failure injection.',
    'FX-A11Y': 'Approved Arabic/English synthetic UI strings, mixed-direction IDs, 320/360/390/1280px viewports, keyboard/screen-reader scripts, 200% zoom/reduced motion.',
    'FX-EVAL': 'Separately authorized subject-disjoint evaluation manifest with independent identity ground truth and rights record, restricted data store; never external testing models.',
    'FX-DEPLOY': 'Immutable candidate/previous release digests, synthetic staging topology, migrations/WAL/object backups, independent deletion ledger and rollback approval fixture.'
}


def add(fid, category, source, title, suite, positive, negative, security, edge, fixtures, outcome, phase=1):
    base = fid.lower().replace('-', '_')
    browser = suite in ['browser', 'accessibility']
    component = suite == 'components'
    file = (f'tests/browser/{base}.e2e.ts' if browser else
            f'tests/components/{base}.test.ts' if component else f'tests/{suite}/test_{base}.py')
    cases = []
    for suffix, kind, scenario in [('P', 'positive', positive), ('N', 'negative', negative),
                                   ('S', 'security_authorization', security), ('E', 'edge', edge)]:
        tid = 'TC_' + fid.replace('-', '_') + '_' + suffix
        selector = tid if browser or component else 'test_' + tid.lower()
        cmd = (f'./node_modules/.bin/e2e run {file} --grep {tid} --retries 0 --no-cache'
               if browser else f'vitest run {file} -t {tid}' if component else f'pytest {file}::{selector}')
        expected = (outcome if suffix == 'P' else
                    'The specified negative scenario is handled according to the completed contract (neutral response where existence protection requires it): ' + scenario + '; no unauthorized mutation, disclosure or delivery' if suffix == 'N' else
                    'Current exact-purpose authorization and all listed security constraints hold: ' + scenario + '; unauthorized access/effects denied or safely held' if suffix == 'S' else
                    'Under '+scenario+', supported success preserves: '+outcome+'; any failure remains safely held/denied without an unauthorized partial effect')
        cases.append({'test_case_id': tid, 'kind': kind, 'scenario': scenario,
                      'planned_file': file, 'planned_selector': selector, 'planned_command': cmd,
                      'expected_outcome': expected,
                      'required_from_phase': phase, 'status': 'pending', 'execution_evidence': None})
    features.append({'feature_id': fid, 'category': category, 'source': source, 'title': title,
                     'suite': suite, 'phase_introduced': phase, 'positive_scenarios': positive,
                     'negative_scenarios': negative, 'security_authorization_scenarios': security,
                     'edge_cases': edge, 'fixture_ids': fixtures, 'expected_outcomes': outcome,
                     'test_cases': cases, 'execution_evidence': None, 'current_validation_status': 'pending'})


FR_DETAILS = [
 ('Switch locale mid-form and submit each registry flow', 'Invalid locale or script payload is escaped', 'Reporter sees no staff fields during locale switch', 'Arabic digits, long labels, interrupted connection and draft recovery', ['FX-BASE','FX-UNCERTAIN','FX-A11Y'], 'Correct registry, preserved original values, RTL/LTR semantics, one neutral receipt'),
 ('Submit unknown name/age and no photo', 'Invalid ordered interval rejected without inventing values', 'Unverified source cannot mark claims verified', 'Unknown vs zero age, estimated capture dates, individual finder', ['FX-UNCERTAIN'], 'Claims retain uncertainty and a restricted triage task is created'),
 ('Add evidence-backed verified assertion preserving original claim', 'Missing verifier/evidence cannot produce verified fact', 'Unassigned user cannot change assertion provenance', 'Concurrent contradictory revisions and disputed evidence', ['FX-BASE','FX-UNCERTAIN'], 'Immutable claim history plus independently attributed verification'),
 ('Verified reporter adds own supplement and views redacted receipt', 'Guess or replay receipt/code fails without revealing existence', 'Own-report capability cannot read staff notes/counterpart case/custody', 'Revocation/expiry during supplement and safe recovery', ['FX-BASE','FX-IDP'], 'Only own submitted facts accessible, no found-child disclosure'),
 ('Select correct subject among multiple photo regions and record capture interval', 'No-face/ambiguous subject remains held', 'Unauthorized user cannot select another case photo', 'Historical photos, low quality and multiple children', ['FX-MEDIA','FX-UNCERTAIN'], 'Approved subject selection and original photo provenance; no silent largest-face choice'),
 ('Moderate, assign and transition with valid purpose/revision', 'Illegal lifecycle jump and stale revision rejected', 'Org admin without case grant cannot assign sensitive content to self', 'Audit sink outage and concurrent assignment/revocation', ['FX-BASE','FX-DB','FX-FAILURE'], 'Authorized transition, assignment, audit and outbox commit atomically'),
 ('Confirm/reverse duplicate link with both case grants', 'Wrong pair or unreviewed merge request rejected', 'Cross-org link cannot disclose records', 'New evidence after duplicate rejection and repeated requests', ['FX-BASE','FX-UNCERTAIN'], 'Reversible link with full independent provenance, no destructive merge'),
 ('Review wrong lead and reject/hold/escalate with reason', 'Model score alone cannot resolve case', 'Unassigned reviewer cannot access lead or approve own request', 'New evidence after rejection and competing reviews', ['FX-MATCH','FX-APPROVAL'], 'Lead decision retained, no automatic identity/custody action'),
 ('Authorized staff receives neutral task notification once', 'Invalid destination or provider error retried/dead-lettered', 'Revoked recipient and claimant receive no identifying message', 'Duplicate event and grant revoked at send boundary', ['FX-EVENT','FX-BASE'], 'Neutral payload only, current permission rechecked and delivery audit retained'),
 ('Distinct safeguarding/authority actors approve scoped disclosure then supervised reunion', 'Missing authority, fraud concern or changed evidence holds release', 'Requester/self-approval/admin bypass denied', 'Approval expiry/revocation races and actor with two roles', ['FX-APPROVAL','FX-FAILURE'], 'No identifying disclosure or custody transfer until every independent gate holds'),
 ('Approve deletion and verify every store/index/queue is purged', 'Active legal hold prevents only scoped erasure', 'Revoked capability cannot serve image during purge', 'Delete during embedding insertion and restore from old backup', ['FX-PURGE','FX-EVENT'], 'Tombstone first, all permitted purge acknowledgments recorded, no resurrection'),
 ('Same-org authorized search and approved bilateral federation workflow', 'Unilateral/expired federation agreement yields no results', 'Other organization sees no names/media/counts/vectors/custody', 'Opt-out during matching and disclosure expiry', ['FX-BASE','FX-MATCH','FX-APPROVAL'], 'Explicit scope and bilateral approvals enforced; federation off by default'),
 ('Append supplement/note/abuse report and inspect permitted history', 'Tampered evidence reference or history edit rejected', 'Abuse report hidden from implicated user; audit reader sees minimized data', 'Conflicting notes, unverified evidence and pagination', ['FX-BASE','FX-UNCERTAIN'], 'Authorship/revisions retained; privileged notes never in reporter DTO'),
 ('Complete workflows using keyboard and screen reader in both languages', 'Hidden error or overflowing action fails acceptance', 'Disabled controls do not replace backend authorization', 'All target widths, mixed bidi text, focus restoration, zoom/reduced motion', ['FX-A11Y'], 'Accessible labels/order/status/errors and responsive layout verified')
]
prd = (ROOT/'docs/PRODUCT_REQUIREMENTS.md').read_text()
for (fid, title), detail in zip(re.findall(r'^\| (FR-\d+) \| ([^\n]+?) \|$', prd, re.M), FR_DETAILS, strict=True):
    add(fid,'functional','PRODUCT_REQUIREMENTS.md#'+fid,title,'browser',*detail,
        phase=2 if fid == 'FR-08' else 4 if fid == 'FR-10' else 1)

API_SCENARIOS = [
 ('Submit a missing report with uncertain data', 'Reject invalid interval/oversized payload', 'Bound intake challenge, rate limit and idempotency; no search', 'Retry identical key and changed body', ['FX-BASE','FX-UNCERTAIN'], '202 neutral receipt, attributed missing claims and triage event'),
 ('Submit individual/organization found report safely', 'Reject malformed welfare/discovery inputs', 'No shelter or identity disclosed to claimant', 'Unknown name, no photo and finder without organization', ['FX-BASE','FX-UNCERTAIN'], '202 found intake receipt; restricted custody follow-up'),
 ('Request recovery through verified safe channel', 'Malformed contact handled without existence leak', 'Known and unknown contacts return indistinguishable neutral 202', 'Flood/shared IP and expired code', ['FX-IDP'], 'No case existence revealed; attempts bounded'),
 ('Exchange valid one-time code for own submission session', 'Invalid/reused code denied', 'Cannot bind code to another receipt or privilege', 'Concurrent redemption and expiry boundary', ['FX-IDP'], 'Single use, submission-scoped access only'),
 ('Read own submission', 'Unknown/deleted receipt denied', 'No counterpart, staff notes, exact custody or vectors', 'Expired/revoked reporter session', ['FX-BASE','FX-IDP'], 'Redacted own claims only'),
 ('Append new reported information', 'Bad evidence reference denied', 'Cannot write verified facts or another case', 'Duplicate supplement and stale revision', ['FX-UNCERTAIN'], 'Attributed immutable supplement; no verified fact overwrite'),
 ('Send safe NGO relay message', 'Malformed/oversized/XSS payload rejected or escaped', 'No shelter/staff private contacts returned', 'Retry/provider outage and safe-channel changes', ['FX-BASE','FX-EVENT'], '202 neutral relay acknowledgment with no private recipients'),
 ('Submit safeguarding concern', 'Malformed reference gets neutral handling', 'Implicated staff/claimant cannot read allegation', 'Anonymous/incomplete concern and duplicate attempts', ['FX-BASE'], 'Restricted abuse queue without lookup response'),
 ('Read approved ar/en safety text', 'Unknown locale follows defined fallback', 'No case data in public/cacheable response', 'Stale guidance version and accessibility alternative', ['FX-A11Y'], 'Public approved locale/version text only'),
 ('Create bounded quarantine upload intent', 'Disallowed type/size/quota rejected', 'Capability bound to exact case/key and no public ACL', 'Intent expiry/orphan upload and replay', ['FX-MEDIA'], 'Expiring restricted upload permission'),
 ('Finalize immutable uploaded version/checksum', 'Mismatch/missing object denied', 'Cannot retarget case, key or mutable object version', 'Duplicate completion, scan outage and deletion race', ['FX-MEDIA','FX-EVENT'], '202 scan job; image not served before acceptance'),
 ('List granted cases using cursor', 'Bad cursor/filter rejected', 'No inaccessible counts or cross-org rows', 'Grant revoke between pages and empty scope', ['FX-BASE','FX-DB'], 'Only permitted case summaries and pagination'),
 ('Read assigned case with ETag', 'Missing/deleted case returns neutral inaccessible response', 'No grant, wrong org and restricted custody denied', 'Membership expiry during pooled transaction', ['FX-BASE','FX-DB'], 'Authorized DTO plus revision; no generic database serialization'),
 ('Perform legal case transition', 'Illegal jump/missing evidence rejected', 'No automatic score-triggered resolution or admin bypass', 'If-Match stale and concurrent transition', ['FX-APPROVAL','FX-DB'], 'Only guarded new state and atomic audit/outbox'),
 ('Assign case/team and grant appropriately', 'Invalid/suspended member rejected', 'Supervisor scope and least privilege enforced', 'Self-assignment privilege escalation and concurrent revocation', ['FX-BASE','FX-IDP'], 'Audited authorized assignment'),
 ('Record claimed or evidence-verified assertion', 'Missing provenance/invalid interval denied', 'Verification requires reviewer and evidence permissions', 'Conflicting revisions/disputed source', ['FX-UNCERTAIN'], 'Immutable assertion; original remains preserved'),
 ('Approve selected face region', 'Unknown region/ambiguous face held', 'Only authorized case media reviewer selects', 'Two children, zero faces, stale detector revision', ['FX-MEDIA'], 'Explicit subject and source revision recorded'),
 ('Stream permitted sanitized image', 'Unsafe/quarantined/deleted object denied', 'Other org/expired/revoked token/original privilege denied', 'Range/cache request and revoke during streaming', ['FX-MEDIA','FX-IDP'], 'Authorized content with no-store/no-referrer, no GPS metadata leak'),
 ('Queue matching with approved manifest/purpose', 'Uncleared model/missing subject denied', 'No public biometric route or cross-org search grant', 'No photos, incompatible space and deleted revision', ['FX-MATCH'], '202 internal scoped job; no raw vectors returned'),
 ('Read authorized case leads with reasons', 'Unknown lead/run denied', 'Require both case scopes and federation disclosure policy', 'Rejected/stale lead and missing metadata', ['FX-MATCH','FX-BASE'], 'Permitted candidate DTO and uncertainty; no identity probability'),
 ('Hold/reject/escalate lead with evidence', 'No rationale/invalid outcome denied', 'Assigned independent reviewer scope enforced', 'Stale review and new evidence after rejection', ['FX-MATCH','FX-APPROVAL'], 'Immutable review, no automatic confirmation'),
 ('Append investigation note', 'Oversized/unsafe text handled', 'Reporter/other org cannot read or modify notes', 'Concurrent versions and malicious Arabic text', ['FX-BASE'], 'Attributed restricted revision'),
 ('Create/confirm reversible duplicate link', 'Same-case/invalid pair rejected', 'Both grants and confirmation role required', 'Repeated link/reversal/concurrent update', ['FX-BASE'], 'Reversible reviewed link with independent reports intact'),
 ('Request recipient/field-scoped disclosure', 'Missing purpose/mask/expiry denied', 'Request grants no access; recipient identity verified independently', 'Expired agreement and snapshot changes', ['FX-APPROVAL'], 'Pending restricted request only'),
 ('Independent bilateral disclosure approval', 'Missing side/authority/evidence holds disclosure', 'Self-approval or same principal in two roles denied', 'Expiry/revocation/snapshot race', ['FX-APPROVAL'], 'Expiring field mask only after all required approvals'),
 ('Propose safe reunion after identity review', 'Unconfirmed identity/fraud concern prevents readiness', 'Claimant cannot create or approve own handover', 'Disputed custody and child objection', ['FX-APPROVAL'], 'Pending safeguarded plan, not release'),
 ('Record distinct safeguarding and authority decisions', 'Missing/stale verification blocks', 'Two-person identities and recent MFA enforced', 'Approver disabled or evidence revised after signing', ['FX-APPROVAL','FX-IDP'], 'Scope/snapshot-bound approval only'),
 ('Record supervised authorized handover', 'Incomplete/expired approvals deny child release', 'No admin/worker/claimant bypass or duplicate transfer', 'Concurrent replay/revocation and witness failure', ['FX-APPROVAL','FX-EVENT'], 'Only complete independent gates permit witnessed transition'),
 ('Request authorized erasure', 'Legal hold scoped/reviewed', 'Request itself cannot reveal child existence or bypass privacy authority', 'Purge racing indexing and backups', ['FX-PURGE'], 'Tombstone/revocation then verifiable purge workflow'),
 ('Read permitted minimized audit events', 'Invalid cursor denied', 'Audit mandate does not grant media/custody or cross-org data', 'Hash-chain break and pagination boundary', ['FX-DB'], 'Minimized scoped audit stream, no payload secrets'),
 ('Read approved aggregate analytics', 'Unsupported drilldown rejected', 'Suppress small cells and cross-org differencing', 'Overlapping queries and zero/small samples', ['FX-BASE'], 'Nonidentifying approved aggregates only'),
 ('Manage organization membership with permission', 'Invalid role/suspended organization rejected', 'No automatic case/custody grant for org admin', 'Role change/session revoke and last-admin policy', ['FX-IDP','FX-BASE'], 'Audited membership lifecycle with current grant enforcement')
]
api_text = (ROOT/'docs/API_CONTRACTS.md').read_text()
operations = re.findall(r'^\| ((?:GET|POST|PUT|PATCH|DELETE) /[^|]+?) \|', api_text, re.M)
for n, (operation, data) in enumerate(zip(operations, API_SCENARIOS, strict=True), 1):
    phase = 2 if any(s in operation for s in ['matching-runs','/leads']) else 4 if any(s in operation for s in ['disclosure','reunification','analytics']) else 1
    add(f'API-{n:03}', 'api_operation', 'API_CONTRACTS.md', operation, 'api', *data, phase=phase)

schema_text = (ROOT/'docs/DATABASE_SCHEMA.md').read_text()
relations = re.findall(r'^\| ([a-z_]+(?: / [a-z_]+)?) \|',schema_text,re.M)
for n, relation in enumerate(relations,1):
    control = relation in ['model_manifests','embedding_spaces']
    broker = relation in ['federation_agreements','broker_candidate_edges','disclosure_grants']
    restricted = relation in ['restricted_custody','approvals','handovers','report_access','reporters']
    append_only = relation in ['assertions','human_reviews','investigations / notes','audit_events']
    positive = ('Authorized signed/versioned control metadata read; administrator performs approved append' if control else
                'Broker/approval actor performs only agreement-and-purpose-scoped access' if broker else
                'Explicit restricted-purpose grant permits only needed fields' if restricted else
                'API/worker non-owner role performs authorized same-org case-scoped operation')
    negative = ('Reject incompatible dimension/manifest mutation and invalid version' if control else 'Deny missing tenant/purpose/context, invalid FK or unauthorized table action')
    security = ('Deny ordinary principal mutation; no embedded child payload in global control metadata' if control else
                'Tenant roles cannot read broker-only edges; unilateral agreement cannot authorize disclosure' if broker else
                'FORCE RLS for tenant-owned rows; no BYPASSRLS; own-org admin still needs case/restricted grant')
    edge = ('Attempt UPDATE/DELETE as application role; preserve immutable history' if append_only else
            'Revoke/expire grant or legal basis during transaction; connection pool reused for another org')
    outcome = f'{relation}: only authorized operations commit; unauthorized reads return no rows and writes are denied, no partial sensitive side effect'
    phase = 2 if relation in ['model_manifests','embedding_spaces','embeddings','matching_runs','candidate_leads','face_regions'] else 4 if broker else 1
    add(f'DB-{n:03}','database_boundary','DATABASE_SCHEMA.md',relation,'database',positive,negative,security,edge,['FX-DB','FX-BASE'],outcome,phase)

DB_EXTRA=[
 ('Tenant pool/context isolation','Use transaction-local server-set principal/organization','Missing context fails closed','Forged user-supplied organization cannot set DB identity','Reuse pooled connection after rollback and session revoke','No residual tenant/purpose context or leaked rows'),
 ('Composite cross-organization foreign keys','Insert same-org case/evidence relation','Reject other-org parent with guessed ID','No deferred FK bypass through worker or bulk path','Concurrent parent deletion and reused readable identifiers','Composite ownership enforced at DB boundary'),
 ('Audit/outbox/domain atomic commit','Commit authorized mutation with one audit/outbox record','Inject failure before each commit boundary','Unprivileged actor cannot suppress audit','Crash before/after commit and retried idempotency key','All three commit or none; no unlogged side effect'),
 ('Approval/revocation race','Approve valid independent plan transaction','Revoke approval or change snapshot before release','Same signer in two roles still cannot approve own release','Concurrent handover/revoke at deterministic barrier','Release denied when any current gate invalid'),
 ('Deletion/index race','Tombstone then purge all model partitions','Stale embedding completion cannot resurrect row','Worker must recheck legal basis and generation','Crash/retry between object deletion and vector write','No reachable vector/media after deletion; purge audit remains'),
 ('Schema install/upgrade/restore','Apply migrations to empty and prior synthetic release','Fail interrupted/incompatible backfill safely','Migration role separated from API roles','Large resumable backfill and restore tombstones','Constraints/RLS preserved and rollback path demonstrated')
]
for n,(title,p,neg,s,e,o) in enumerate(DB_EXTRA,1):
    add(f'TXN-{n:02}','transaction','DATABASE_SCHEMA.md',title,'database',p,neg,s,e,['FX-DB','FX-EVENT','FX-PURGE'],o)

EVENT_BEHAVIOR={
 'report.submitted':('Create restricted triage/assignment task','No child data in event; unverified source cannot self-approve'),
 'media.uploaded':('Lease malware/validation job against immutable object version','No serve/embed until valid scan; outage keeps quarantine'),
 'media.ready':('Schedule approved-subject processing or staff selection','No automatic subject choice for multiple faces'),
 'media.quarantined':('Hold processing and create authorized moderation task','No image URL/raw bytes in notification'),
 'subject.selected':('Queue selected-region alignment/quality/embedding','Deny unapproved or stale source revision'),
 'embedding.ready':('Insert compatible-space vector and schedule retrieval','Never compare equal-sized incompatible model vectors'),
 'matching.requested':('Run scoped face and independent metadata retrieval','Reject unlicensed model, absent purpose or unauthorized federation'),
 'matching.completed':('Persist lead run and neutral review task','No auto identity resolution or claimant message'),
 'lead.reviewed':('Persist rejection/hold/escalation effect and follow-up','No automatic child release'),
 'disclosure.approved':('Prepare expiring field-scoped permitted package','Recheck both sides, signer and snapshot before release'),
 'approval.revoked':('Invalidate dependent package/plan before next use','No stale send/release from queued worker'),
 'reunification.recorded':('Create supervised welfare follow-up and history','No public reunion story or exact location exposure'),
 'deletion.requested':('Tombstone/revoke, cancel jobs, purge media/vectors/provider artifacts','Scoped legal hold; no reinsertion from stale jobs'),
 'deletion.completed':('Verify negative retrieval and purge acknowledgments','Retain only legally approved minimized audit'),
 'notification.requested':('Deduplicate neutral alert to currently permitted recipient','No claimant identity/location/image/vector leak')
}
events=json.loads((ROOT/'docs/contracts/event-envelope.schema.json').read_text())['properties']['event_type']['enum']
for n,event in enumerate(events,1):
    p,s=EVENT_BEHAVIOR[event]
    add(f'JOB-{n:03}','background_event','contracts/event-envelope.schema.json',event,'workers',p,
        'Malformed/unknown version goes to dead-letter review with no sensitive processing',s,
        'Duplicate/out-of-order delivery, expired lease, crash-after-effect, stale case revision and revoked legal basis',
        ['FX-EVENT','FX-BASE','FX-FAILURE'],p+' exactly within current permissions; retry is idempotent and audit/dedup retained',
        phase=2 if event.startswith(('embedding','matching','subject')) else 1)

JOB_EXTRA=[
 ('media_sanitize','Produce orientation-correct sanitized derivative and encrypted preserved original','Reject unsafe decode and fail closed on scanner/metadata tool outage','Separate original/EXIF access permission','GPS embedded thumbnail and image-size bomb','Safe derivative only; originals remain restricted'),
 ('lease_retry_dead_letter','Recover orphaned lease and retry transient error','No blind retry of permanent auth/model-license failure','Recheck permission and deletion generation on every effect','Clock skew, duplicate lease and exhaustion','No double external effect; actionable dead-letter'),
 ('orphan_upload_cleanup','Expire bounded unused intent and orphan object','Do not erase finalized legitimate evidence','Only owning organization/quarantine scope','Finalize racing cleanup','No orphan storage leak or wrongful evidence deletion'),
 ('audit_export','Export chained events to independent signed-root sink','Detect gap/tamper/sink outage','Exporter cannot read media/vector payloads','Crash between export and acknowledgment','Verifiable root/sequence and durable backlog; sensitive decisions hold when required'),
 ('retention_hold_review','Apply approved purpose/TTL and review expiring legal hold','No invented production retention schedule','Only privacy authority changes holds','Withdrawal/closure racing retention timer','Scoped hold and approved erasure; no indefinite silent reuse'),
 ('index_reprocess_reconcile','Reprocess manifest-versioned vectors and reconcile object/index tombstones','Never switch incompatible spaces silently','No worker privilege escalation or cleared-license bypass','Partial migration, rollback, deletion and ANN filtered-shortfall','Versioned reproducible indexes with no deleted-case resurrection')
]
for n,(title,p,neg,s,e,o) in enumerate(JOB_EXTRA,1):
    add(f'WORK-{n:02}','background_job','ENGINEERING_ARCHITECTURE.md / DEPLOYMENT_OPERATIONS.md',title,'workers',p,neg,s,e,['FX-EVENT','FX-MEDIA','FX-PURGE','FX-FAILURE'],o)

SAFE=[
 ('Fraudulent guardian','Verify safe contact separately from independently established relationship','Forged/stolen relationship evidence is held','No child identity/location revealed during fraud inquiry','Actual guardian may still be unsafe; child objection/conflict','Only qualified independent review advances claim'),
 ('Found-child location discovery','Authorized safeguarding reader sees only approved fields','Guess URLs, search/filter/export/analytics to locate shelter','Unverified claimant sees no existence/count/location hints','Same missing-report owner and mixed federation grants','No shelter/custody leak via response, cache, logs or notifications'),
 ('Unauthorized image access','Case/media grant permits sanitized derivative','Direct object key/original/GPS request denied','Cross-org and expired/revoked session denied at request boundary','Range/read cache, stale presigned URL and revocation race','No private image access outside exact scope'),
 ('Unauthorized biometric search','Authorized internal job uses compatible-space scope','Public, reporter or arbitrary query vectors denied','No embedding array or public identity-to-location endpoint','Raw SQL vector path and federation worker credentials','Internal scoped lead retrieval only'),
 ('Cross-organization leakage','Authorized same-org and approved bilateral disclosure works','Wrong-org case ID, vectors, cursor and object key denied','Both tenant RLS and application permission checks enforced','Pooled connection reuse and opt-out during in-flight job','No private row/media/count leak'),
 ('Expired and revoked access','Current valid purpose-specific grants work','Expired receipt/MFA/session/grant/approval denied','Revoked actor cannot send notification or stream image','Expiry at use time and stale outbox task','Fail closed and revoke pending dependent effects'),
 ('Incorrect match and human rejection','Reviewer rejects deliberately wrong synthetic candidate','High score cannot confirm identity automatically','Unauthorized reviewer cannot see/act on lead','New evidence after rejection and missing metadata','Audited rejection, no claimant message or case resolution'),
 ('Two-person approval','Two distinct competent principals approve current snapshot','Same principal with two roles or requester approval denied','Org admin cannot override independent-actor requirement','Account sharing, approver suspension and concurrent signing','Distinct identity/action/scope enforced at API and DB transition'),
 ('Child-release bypass','Supervised plan with all current approvals proceeds','Direct lifecycle call, handover replay, missing authority or service outage denied','Requester/admin/worker cannot bypass custody gate','Changed evidence, expiry, legal dispute or audit failure','No child-release state or disclosure when any verification incomplete'),
 ('Deletion and biometric cleanup','Erase permitted original/derivative/all embedding spaces and queues','Stale worker and old backup cannot restore reachability','Removed grants deny image/vector read before purge completes','Legal hold, object versions, crash/retry and index race','Verified tombstone-first purge with minimal lawful audit'),
 ('Notification information leakage','Neutral task link reaches authorized staff once','Template containing identifying/location/image/vector data fails','Revoke recipient between enqueue and send; claimant gets no lead','Lock-screen preview, provider retry, log and URL leakage','Neutral/redacted delivery with current authorization and dedup')
]
for n,(title,p,neg,s,e,o) in enumerate(SAFE,1):
    add(f'SAF-{n:02}','safeguarding','CHILD_SAFEGUARDING_POLICY.md / user correction',title,'security',p,neg,s,e,
        ['FX-BASE','FX-IDP','FX-APPROVAL','FX-MATCH','FX-PURGE','FX-FAILURE'],o,
        phase=2 if n in [4,7] else 4 if n in [8,9] else 1)
    feature = features[-1]
    fid = feature['feature_id']
    for layer in ['BROWSER', 'STATE']:
        tid = 'TC_' + fid.replace('-', '_') + '_' + layer
        file = (f'tests/browser/{fid.lower().replace("-", "_")}.e2e.ts' if layer == 'BROWSER'
                else feature['test_cases'][0]['planned_file'])
        selector = tid if layer == 'BROWSER' else 'test_' + tid.lower()
        command = (f'./node_modules/.bin/e2e run {file} --grep {tid} --retries 0 --no-cache'
                   if layer == 'BROWSER' else f'pytest {file}::{selector}')
        feature['test_cases'].append({'test_case_id': tid, 'kind': 'companion_' + layer.lower(),
            'scenario': ('Run the real-service safeguarding journey with deterministic UI/HTTP and no-leak assertions' if layer == 'BROWSER'
                         else 'Verify actual non-owner SQL/storage/outbox/worker effects for every allowed and denied variant'),
            'planned_file': file, 'planned_selector': selector, 'planned_command': command,
            'expected_outcome': o, 'required_from_phase': feature['phase_introduced'],
            'status': 'pending', 'execution_evidence': None})
    if feature['phase_introduced'] > 1:
        tid = 'TC_' + fid.replace('-', '_') + '_DISABLED_P1'
        file = feature['test_cases'][0]['planned_file']
        selector = 'test_' + tid.lower()
        feature['test_cases'].append({'test_case_id': tid, 'kind': 'disabled_capability_guard',
            'scenario': 'Before this capability is implemented, attempt direct API/worker/lifecycle bypass and verify no private disclosure, biometric lookup, automatic identity confirmation or custody transfer',
            'planned_file': file, 'planned_selector': selector,
            'planned_command': f'pytest {file}::{selector}',
            'expected_outcome': 'Unavailable capability fails closed (absent route/explicit denial); no sensitive state/outbox/object effect; future positive cases remain pending',
            'required_from_phase': 1, 'status': 'pending', 'execution_evidence': None})

threat_text=(ROOT/'docs/SECURITY_THREAT_MODEL.md').read_text()
for tid,title,control,required in re.findall(r'^\| (T\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$',threat_text,re.M):
    add('SEC-'+tid,'security_threat','SECURITY_THREAT_MODEL.md#'+tid,title,'security',
        'Demonstrate legitimate flow with control enabled: '+control,
        'Inject the named attack/failure and require denial/hold: '+title,
        'Probe API, worker, DB and artifact privileges using unrelated org, missing case grant and restricted data canaries',
        'Concurrent revocation/outage/retry and alternate read/export/cache path',
        ['FX-BASE','FX-DB','FX-FAILURE'],required+'; preserve safe care/intake and prevent unauthorized sensitive effect')

EXTRA=[
 ('UNIT-01','unit_component','Domain/unit and rendered component invariants','unit','Pure interval/name normalization and form/verification-state rendering','Malformed intervals/unknown vs contradiction','No hidden verified state or unsafe HTML rendering','Arabic diacritics, Unicode variants and component event reordering',['FX-UNCERTAIN','FX-A11Y'],'Original claims preserved; deterministic domain and component assertions',1),
 ('UNIT-02','unit_component','React form and review components','components','Render forms/review controls and dispatch validated input events','Missing labels, invalid errors and unsafe HTML fail','Sensitive fields absent without granted projection; hidden button is not authorization','Locale switch, keyboard focus, long Arabic text and loading states',['FX-UNCERTAIN','FX-A11Y'],'Deterministic rendered component assertions independent of browser E2E',1),
 ('AUTH-01','authentication','OIDC/MFA/session lifecycle','auth','Actual test Keycloak login, correct issuer/audience and fresh step-up','Wrong JWT claims, stale MFA, logout/revocation denied','CSRF/cookie/session fixation/account deprovisioning protection','IdP/JWKS rotation outage and membership update mid-session',['FX-IDP','FX-BASE'],'Authenticated current purpose/grants enforced; no fallback anonymous access',1),
 ('A11Y-01','accessibility','Arabic/English responsive/accessibility journeys','accessibility','Keyboard/labels/focus/status/zoom/manual screen-reader review','Missing names, focus traps and clipped actionable text fail','Private content absent from accessible tree and page title','3 browsers × 2 locales × 4 widths; reduced motion, bidi and low bandwidth',['FX-A11Y'],'WCAG acceptance evidence plus deterministic layout/DOM checks; manual results separate',1),
 ('ML-01','model_evaluation','Lawful longitudinal identification benchmark','ml','Frozen independent ground-truth subject/family-disjoint evaluation','Leakage, missing provenance/license or synthetic-only accuracy claims rejected','Restricted lawful images never exported to testing model/logs','Age gaps, quality/occlusion, demographic uncertainty, no-mate probes',['FX-EVAL'],'Recall@1/10/50, false leads/FPIR, workload and confidence intervals; unset go/no-go pending NGO approval',2),
 ('ML-02','model_regression','Embedding/fusion/reprocessing regression','ml','Compatible deterministic embeddings/ranking with independent retrieval','RGB/BGR/dimension/weight/metric mismatch fails','Uncleared manifest or production-data training denied','Photo count max-score inflation, missing metadata and age uncertainty',['FX-MATCH','FX-MEDIA'],'Versioned provenance, no incompatible vector comparison or auto-confirmation',2),
 ('PERF-01','performance','Pilot capacity/load and filtered search','performance','Measure proposed workload with controls enabled','Resource saturation/queue overload fails capacity gate','No rate-limit/authorization bypass for benchmark','50k cases × five synthetic photos, 30 staff, 100 reports/hour; scoped ANN vs exact',['FX-BASE','FX-MATCH','FX-FAILURE'],'Observed p50/p95/p99/error/resources and review workload; provisional SLOs not assumed passed',1),
 ('RES-01','resilience','Failure, concurrency and recovery','resilience','Recover scanner/IdP/DB/storage/KMS/audit/worker failures','Unavailable sensitive gate blocks serve/disclose/release','No plaintext/admin/anonymous fallback','Kill before/after commits, partitions, race barriers and at-least-once events',['FX-FAILURE','FX-EVENT','FX-DB'],'Fail-safe sensitive paths, bounded retries, no double effect; measured recovery evidence',1),
 ('DEP-01','deployment','Clean installation and release candidate validation','deployment','Build locked candidate and install fresh isolated full stack','Missing lock/digest/signature/schema guard blocks promotion','No PR secrets, floating images or production data','Clean and upgrade paths, browser binaries/platform mismatch',['FX-DEPLOY','FX-DB'],'Candidate health, migrations and full mandatory regression evidence tied to digests',1),
 ('DEP-02','deployment','Rollback and backup/deletion recovery','deployment','Restore/rollback to compatible approved release','Destructive incompatible downgrade or tombstone loss blocks','No resurrection of deleted case, revoked approval or model','Coherent DB/object cut, key recovery and incomplete backfill',['FX-DEPLOY','FX-PURGE'],'Verified RPO/RTO, revocation/deletion replay and permission-safe reopening',5),
 ('TOOL-01','testing_policy','TesterArmy telemetry/model/artifact boundaries','security','Model-free local browser runner with both opt-out flags and isolated DB','Telemetry unset, production target, external model with real data denied','Egress policy plus synthetic canaries and independent artifact redaction','Cache miss, automatic browser install, malicious page link and raw command.log',['FX-BASE','FX-FAILURE'],'No optional telemetry or real child data to external testing model; artifacts sanitized before publishing',1)
]
for fid,category,title,suite,p,n,s,e,fx,o,phase in EXTRA:
    add(fid,category,'TEST_STRATEGY.md / CI_CD_TEST_GATES.md',title,suite,p,n,s,e,fx,o,phase)

out={'schema_version':'1','scope':'Phase 0 planned test architecture only; application not implemented',
     'application_test_status':'pending','fixture_catalog':FIXTURES,'features':features}
(ROOT/'docs/testing/test-matrix.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
md=['# Find Our Child — test traceability matrix','',
    '**Every application test below is pending and unimplemented. No execution evidence exists.** A planned file/selector/command is an implementation target, not an existing executable test. This matrix makes future executables traceable without claiming they run before the application exists.','',
    'Machine-readable source: [test-matrix.json](testing/test-matrix.json). Regenerate with `python3 tools/build_test_matrix.py`. Phase 0 checks validate inventory/coverage/status consistency only.','',
    'Scope: all 14 numbered functional requirements, all 32 API operations in API_CONTRACTS, every schema relation security boundary (composite relation rows explicitly cover both named tables), all 15 event contracts, additional worker/timer jobs, transaction races, 11 requested safeguarding workflows, 19 original threats and the independent testing suites. New requirements/routes/jobs/tables must extend this inventory in the same PR.','',
    'Status vocabulary: pending = not implemented; implemented-not-run = executable exists without accepted evidence; blocked/failed/skipped/interrupted/flaky = not accepted; passed = exact executable/target/fixture result accepted with artifact ID. Current status is pending for every feature and test case.','',
    'Each ID has four separately planned cases: `_P` positive, `_N` negative, `_S` security/authorization, `_E` edge. SAF IDs additionally have `_BROWSER` and `_STATE` companion cases. Future-phase SAF capabilities also have `_DISABLED_P1` denial cases required from Phase 1; full positive cases stay pending until their required_from_phase. This explicit applicability is not a runtime skip. Expected success for a browser case additionally requires actual API/database side-effect oracles, not merely a visible success toast. UI selectors are authored against live synthetic services in Phase 1. API exact status/DTOs beyond the existing outline are contract-completion gates, not invented here.','',
    'Python selectors below target planned pytest suites; rendered components target Vitest. Browser/accessibility selectors target TesterArmy/e2e tests; Playwright supplies its engine only. Frameworks/versions for other future suites require their own release locks before implementation. No file is generated under application test directories by this tool.','',
    'Evidence for every future accepted result: source/build/contract/lock/model versions, test ID, target, fixture hash, timestamps, exit, status/counts, sanitized artifact hashes/location, migration/SQL oracles where relevant and reviewer. No mandatory skip or absent test may count as passed. Critical safeguarding scenarios run as browser + API/DB/worker checks; companion layers are specified in [security catalog](SECURITY_TEST_CATALOG.md).','',
    '## Synthetic and restricted fixture catalog','']
for key,value in FIXTURES.items(): md.append(f'- **{key}:** {value}')
current=None
for f in features:
    if f['category']!=current:
        current=f['category'];md+=['',f'## {current.replace("_"," ").title()}','']
    md += [f'### {f["feature_id"]} — {f["title"]}','',
           f'- **Source / phase / suite:** {f["source"]}; phase {f["phase_introduced"]}; {f["suite"]}.',
           f'- **Positive:** {f["positive_scenarios"]}.',f'- **Negative:** {f["negative_scenarios"]}.',
           f'- **Security and authorization:** {f["security_authorization_scenarios"]}.',f'- **Edge cases:** {f["edge_cases"]}.',
           f'- **Fixtures:** {", ".join(f["fixture_ids"])}.',f'- **Expected outcomes:** {f["expected_outcomes"]}.',
           '- **Planned test IDs:** '+', '.join(c['test_case_id'] for c in f['test_cases'])+'.',
           '- **Planned executable targets:** '+', '.join('`'+p+'`' for p in dict.fromkeys(c['planned_file'] for c in f['test_cases']))+'; exact selectors/commands in the JSON record.',
           '- **Execution evidence:** none (not run). **Current validation status: pending.**','']
(ROOT/'docs/TEST_MATRIX.md').write_text('\n'.join(md)+'\n')
print(json.dumps({'features':len(features),'planned_cases':sum(len(f['test_cases']) for f in features),
                  'api_operations':len(operations),'database_relation_boundaries':len(relations),
                  'events':len(events),'all_application_tests':'pending'},indent=2))
