"""Append Phase 1C traceability without replacing the immutable Phase 0 or accepted phase records."""
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
registry=ROOT/'docs/testing/test-matrix.json'
x=json.loads(registry.read_text());required=json.loads((ROOT/'docs/phase1c/required-tests.json').read_text())
evidence_file=ROOT/'artifacts/phase1c-sanitized/results.json'
evidence=None
if evidence_file.exists():
    import sys
    sys.path.insert(0,str(ROOT))
    from scripts.fingerprint import fingerprint
    evidence=json.loads(evidence_file.read_text())
    assert evidence['gate']['status']=='passed' and evidence['gate']['source_digest']==fingerprint(), 'Never publish stale/nonpassing traceability'
    for lane,key in [('reporting','python'),('resilience','resilience'),('reporting_http','http')]:assert sorted(t['id'] for t in evidence[lane])==sorted(required[key]) and all(t['status']=='passed' for t in evidence[lane])
    assert len(evidence['browser'])==168 and all(t['status']=='passed' for t in evidence['browser'])
status='passed' if evidence else 'pending'
groups=[
 ('RPTC-01','Intake, uncertain claims, contact verification, private drafts, receipt/session scope and relay','api_database_security',[n for n in required['python'] if '/test_intake.py::' in n],['FR-01','FR-02','FR-03','FR-04','FR-13','API-01','API-02','API-03','API-04','API-05','API-06','API-07','API-08','API-09']),
 ('RPTC-02','NGO moderation, scoped case access, assignments, evidence assertions, revisions and audit/outbox atomicity','api_database_security',[n for n in required['python'] if '/test_cases.py::' in n],['FR-03','FR-06','FR-12','FR-13','API-12','API-13','API-14','API-15','API-16','API-18','API-22']),
 ('RPTC-03','Actual ClamAV/S3 intake, encrypted versions, sanitization, publication authorization and crash/fencing recovery','media_worker_security',[n for n in required['python'] if '/test_media.py::' in n],['FR-05','FR-11','API-10','API-11','API-18','T05','T06','T07','T10']),
 ('RPTC-04','Orphan erasure acknowledgments, outbox recipient reauthorization, neutral notification dedup and dead letters','worker_database',[n for n in required['python'] if '/test_workers.py::' in n],['FR-09','FR-11','T10','T11','T13']),
 ('RPTC-05','Actual scanner service outage fails closed with bounded retries/dead letters','resilience',required['resilience'],['T05','T10','T17']),
 ('RPTC-06','Actual TLS Next/Keycloak/API/PG/S3/ClamAV/background-worker workflows','integration',required['http'],['FR-02','FR-04','FR-06','FR-12','T01','T02','T04','T05','T07']),
 ('RPTC-07','Official TesterArmy missing/found/reporter/moderation journeys, ar/en a11y, RTL, keyboard/zoom and all 24 targets','browser',required['browser_titles'],['FR-01','FR-02','FR-04','FR-14','T01','T02','T04','T05','T15']),
]
x['features']=[f for f in x['features'] if not f['feature_id'].startswith('RPTC-')]
x['fixture_catalog']['FX-REPORTING']='Only generated synthetic contacts/names/receipts, separate NGO/staff principals, encrypted operator sinks, solid-color PNG/JPEG/WebP, inert EICAR test string, immutable S3 versions, real ClamAV, real PG non-owner roles and controlled crash/outage barriers. No real child images or production information.'
all_nodes=[]
for fid,title,suite,nodes,related in groups:
    assert nodes
    cases=[]
    for i,node in enumerate(nodes,1):
        if suite=='browser':
            file='tests/browser/reporting.e2e.ts';command='.venv/bin/python -m scripts.dev browser'
        else:file=node.split('::')[0];command='.venv/bin/python -m scripts.reporting_http_test' if suite=='integration' else '.venv/bin/python -m scripts.reporting_validate'
        cases.append({'test_case_id':f'TC_{fid.replace("-","_")}_{i:03}','kind':'positive_negative_security_edge','scenario':node,'planned_file':file,'planned_selector':node,'planned_command':command,'expected_outcome':'Exact DTO/state/absence/authorization assertions in the executable; no unauthorized disclosure, unsafe ready image, duplicate committed action or unexecuted mandatory target.','required_from_phase':'1C','phase1c_required':True,'status':status,'execution_evidence':{'artifact':'artifacts/phase1c-sanitized/results.json','source_digest':evidence['gate']['source_digest']} if evidence else None})
        all_nodes.append(node)
    x['features'].append({'feature_id':fid,'category':suite,'source':'phase1c/ARCHITECTURE.md','title':title,'suite':suite,'phase_introduced':'1C','related_requirements':related,'positive_scenarios':'Unknown/no-photo missing/found intake; verified own-submission access; clean multi-image evidence; authorized human case operations and recoverable private drafts.','negative_scenarios':'Malformed/oversize/forged/replayed requests, wrong contacts, expired/revoked capabilities, unapproved notices, invalid media/scanner outage and stale revisions deny without unsafe effects.','security_authorization_scenarios':'Cross-org/case/no-grant/forged-CSRF/original-media access denied; claimed parent/guardian never gains staff/custody; current access rechecked before publication/delivery; audit failures roll back.','edge_cases':'Offset ordering/unknown dates, literal text, concurrent revision writes, process loss before/after each object write, stale fencing, unbound uploads, quotas, orphan cleanup acknowledgments and source/result reconciliation.','fixture_ids':['FX-REPORTING','FX-BASE','FX-IDP','FX-MEDIA','FX-EVENT','FX-DB','FX-FAILURE'],'expected_outcomes':'Deterministic current-source assertions pass in every required lane/target. Synthetic data and sanitized artifacts only; disabled matching/disclosure/release remain denied.','test_cases':cases})
assert len(all_nodes)==len(set(all_nodes))==sum(len(required[k]) for k in ['python','resilience','http','browser_titles'])
x['application_test_status']='phase1c_hosted_technical_validation_passed_awaiting_owner_review' if evidence else 'phase1b_accepted_phase1c_validation_pending'
registry.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
counts=Counter(c['status'] for f in x['features'] for c in f['test_cases'])
lines=['# Phase 1C feature and execution traceability','',f'Current status: **{status}**. New cases remain pending until the full current-source hosted artifact passes and is independently verified. The Phase 0 151-feature/630-test snapshot and all accepted Phase 1A–1B entries are preserved.','',f'Master registry: {len(x["features"])} features, {sum(counts.values())} logical cases; '+', '.join(f'{n} {s}' for s,n in sorted(counts.items()))+'. Logical mappings are not browser execution counts.','',f'Phase 1C inventory: {len(required["python"])} reporting cases, {len(required["resilience"])} real scanner-outage case, {len(required["http"])} actual TLS/BFF cases and {len(required["browser_titles"])} browser titles ×24 targets. Together with preserved 158 baseline/58 identity and four prior browser titles, full required execution is {158+58+len(required['python'])+len(required['resilience'])+len(required['http'])} Python and 168 TesterArmy cases.','', 'Identity-boundary doubles in test_cases.py are explicitly scoped API/SQL tests; actual MFA/HTTP/browser lanes remain independently mandatory.','']
for fid,title,suite,nodes,related in groups:
    lines += [f'## {fid} — {title}','',f'Related requirements: {", ".join(related)}. Fixtures and positive/negative/security/edge expectations are in the [machine registry](../testing/test-matrix.json). Evidence: '+('[verified sanitized results](../../artifacts/phase1c-sanitized/results.json).' if evidence else '**pending**.'),'','| Case ID | Executable selector | Status |','|---|---|---|']
    lines += [f'| TC_{fid.replace("-","_")}_{i:03} | `{node}` | {status} |' for i,node in enumerate(nodes,1)]
    lines += ['']
lines+=['## API, jobs, database and safeguarding crosswalk','','| Boundary | Executable coverage / status |','|---|---|']
contract=json.loads((ROOT/'docs/contracts/openapi.json').read_text())
for path,item in contract['paths'].items():
    for method,o in item.items():
        if path.startswith('/identity'):link='Preserved 58-case identity inventory and MFA browser regression'
        elif not path.startswith('/v1'):link='Preserved baseline API/contract/readiness suite'
        elif o.get('x-implementation-status')=='implemented-phase-1c':link='RPTC-01–07; exact positive/negative selectors above and immutable required inventory'
        else:link='Preserved 64 anonymous/forged domain guards and SAF-04/07/08/09 disabled-capability denial; future positive behavior pending'
        lines.append(f'| `{method.upper()} {path}` ({o["operationId"]}) | {link} |')
lines += ['| media.scan, lease/retry/dead-letter/publication | RPTC-03/05: actual scanner, worker roles, crash checkpoints, fences and deletion-generation negatives |','| outbox/notification delivery | RPTC-04: neutral payload, current grants, idempotent private sink, exhausted lease |','| quarantine/orphan/draft expiry | RPTC-01/04: expiry, actual immutable version erasure and acknowledgment; whole-case/backup erasure remains pending |','| cases/grants/memberships/org/principal | Preserved DB/RLS/identity regression plus RPTC-02 current grant/tenant/role/transaction tests |','| claims/codes/sessions/commands/restricted intake/journals | RPTC-01/02: hashed capabilities, replay/expiry, no direct runtime reads/writes, closed projections, custody exclusion |','| objects/intents/photos/derivatives/evidence | RPTC-03: immutable key/version/hash, quota, MIME/bomb/EICAR, metadata stripping, exact-owner scope and current media grants |','| audit/outbox | RPTC-02/04: same-transaction rollback, non-sensitive envelopes, role separation; operational WORM export remains a release gate |','| fraudulent parent/guardian, found location, original media, tenant leaks | RPTC-01/02/06/07 and permanent security guards; exact denials/no-effects |','| biometric search, self-approval, release/custody bypass | Existing permanent disabled-route guards plus RPTC-02/06/07; no positive production capability implemented |','| model accuracy, federation, operational custody/reunion/deletion/legal hold | Original future cases remain pending; browser tests cannot validate those unimplemented capabilities |','']
(ROOT/'docs/phase1c/TEST_TRACEABILITY.md').write_text('\n'.join(lines))
print({'features':len(x['features']),'cases':sum(counts.values()),'status_counts':dict(counts)})
