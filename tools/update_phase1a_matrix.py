"""Extend the immutable Phase 0 baseline with actual, source-bound Phase 1A evidence."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'docs/testing/test-matrix-phase0.json'
if not BASE.exists(): BASE.write_bytes((ROOT/'docs/testing/test-matrix.json').read_bytes())
m=json.loads(BASE.read_text())
report=json.loads((ROOT/'artifacts/sanitized/results.json').read_text())
manifest=json.loads((ROOT/'docs/phase1a/required-tests.json').read_text())
proof='artifacts/sanitized/results.json'
passed={t['id'] for t in report.get('python',[]) if t['status']=='passed'}
for f in m['features']:
    for c in f['test_cases']:
        c['phase1a_required']=c['test_case_id'].endswith('_DISABLED_P1')
        node=c['planned_file']+'::'+c['planned_selector']
        if c['phase1a_required'] and node in passed:
            c.update(status='passed',execution_evidence={'path':proof,'selector':node,'source_digest':report['gate']['source_digest']})
            f['current_validation_status']='partial'
            f['execution_evidence']={'path':proof,'scope':'Disabled Phase 1 guard only; operational workflow remains pending'}
scopes={
 'FND-01':('Synthetic-only configuration and secret isolation','unit','Startup accepts only the isolated synthetic database; web/browser processes receive no database or model credentials.'),
 'FND-02':('Liveness, readiness and response security headers','api','Public health responses use no-store and generated request IDs; unavailable or untrusted database fails readiness.'),
 'FND-03':('Complete versioned OpenAPI and closed DTOs','api','All 32 domain contracts plus three foundation operations validate; domain behavior remains disabled.'),
 'FND-04':('Executable schema, migration replay and same-case integrity','database','Both immutable migrations apply/replay, tenant and same-case foreign keys reject mixed references, and all 41 domain relations force RLS.'),
 'FND-05':('Tenant/case/purpose/expiry database boundaries','database','Non-owner runtime reads only a granted active case; missing context, revocation, wrong purpose and sensitive classifications deny access.'),
 'FND-06':('Case/outbox transaction atomicity','database','Rollback removes both revision and outbox changes; no partial event escapes.'),
 'FND-07':('Disabled domain operations and sensitive routes','security','All 32 future operations reject both anonymous and forged credentials without mutation or sensitive echo.'),
 'FND-08':('Arabic/English foundation browser shell','browser','Real web/API/database render both locales without overflow, preserve HTML direction, support keyboard navigation, pass automated axe rules and expose no reporting inputs.'),
 'FND-09':('Required-result enforcement and artifact sanitization','unit','Missing/duplicated/skipped/retried/stale/model-assisted results fail the gate; PNG metadata and path escapes cannot be published.'),
 'FND-10':('Locked local environment and production web build','deployment','A clean exact npm install, locked Python container build, TypeScript check and production web build complete using the selected runtimes.'),
 'FND-11':('Closed event envelope and outbox metadata','integration','Only opaque IDs/revisions/policy metadata form a schema-valid event; arbitrary child payloads and unknown event types are rejected.'),
 'FND-12':('Current dependency security audits','security','The current application/test locks have no known npm or Python advisories in the recorded audit; historical research locks are excluded.'),
 'FND-13':('CI policy and remote enforcement','deployment','Pinned-action pull-request/full-regression workflow enforces required results and publishes only sanitized artifacts; remote run/protection must be independently verified.'),
 'FND-14':('Synthetic backup and restore validation','deployment','Restored schema retains both migration checksums, pgvector and 41 forced-RLS relations; runtime reads deny without context. Operational erasure remains pending.'),
 'DB-38':('idempotency_records','database','Tenant/principal/operation/key scope is unique, hashes have fixed length, response storage is ciphertext, and runtime access stays denied until reviewed Phase 1C policies.'),
}
features={}
for fid,(title,suite,outcome) in scopes.items():
 features[fid]={'feature_id':fid,'category':'database_boundary' if fid=='DB-38' else 'phase1a_foundation','source':'phase1a/REVIEW.md','title':title,'suite':suite,'phase_introduced':1,'phase1a_required':True,'positive_scenarios':outcome,'negative_scenarios':'Invalid, missing or unavailable inputs/dependencies reject rather than granting access or claiming validation.','security_authorization_scenarios':'Non-owner roles and forged/expired/missing authority cannot enable a sensitive operation; test artifacts contain only the synthetic shell.','edge_cases':'Isolation, tenant/case mixing, replay, rollback, missing results and platform-specific launch failure are checked where applicable; unimplemented operational scenarios remain pending in the original baseline.','fixture_ids':['FX-FOUNDATION'],'expected_outcomes':outcome,'test_cases':[],'current_validation_status':'pending','execution_evidence':None}
m['fixture_catalog']['FX-FOUNDATION']={'description':'Disposable internal-only PostgreSQL/pgvector, synthetic org/principal/case UUIDs, input-free bilingual shell, generated one-pixel sanitizer unit fixtures and synthetic validator reports. Validator unit fixtures never count as real browser/application evidence.'}
def feature_for(node):
 if 'idempotency' in node:return 'DB-38'
 if 'test_results_gate.py' in node:return 'FND-09'
 if 'tests/unit/' in node:return 'FND-01'
 if 'tests/api/' in node:return 'FND-03' if any(t in node for t in ['openapi','schema']) else 'FND-02'
 if 'test_fnd_outbox_atomic' in node:return 'FND-06'
 if 'outbox_reconstructs' in node or 'event_envelope' in node:return 'FND-11'
 if 'tests/database/' in node:return 'FND-04' if any(t in node for t in ['foreign_key','age_interval','all_domain_relations','wrong_case']) else 'FND-05'
 if 'migration_replay' in node:return 'FND-04'
 if 'tests/security/' in node:return 'FND-07'
 raise ValueError(node)
def append(fid,tid,selector,file,command,status,evidence,kind='positive',scenario=None):
 features[fid]['test_cases'].append({'test_case_id':tid,'kind':kind,'scenario':scenario or selector,'planned_file':file,'planned_selector':selector,'planned_command':command,'expected_outcome':features[fid]['expected_outcomes'],'required_from_phase':1,'phase1a_required':True,'status':status,'execution_evidence':evidence})
for node in manifest['python']:
 if '::test_tc_saf_' in node:continue
 file,selector=node.split('::',1);fid=feature_for(node)
 kind='security_authorization' if any(k in node for k in ['tenant','sensitive','principal','credential','permission','purpose','forged','disabled','role','idempotency','wrong_case']) else 'negative' if any(k in node for k in ['reject','invalid','unavailable','missing','revocation']) else 'edge' if any(k in node for k in ['rollback','reuse','replay','metadata']) else 'positive'
 tid='TC_FND_'+hashlib.sha256(node.encode()).hexdigest()[:12].upper()
 append(fid,tid,selector,file,'uv run python -m scripts.dev test', 'passed' if node in passed else 'pending', {'path':proof,'selector':node,'source_digest':report['gate']['source_digest']} if node in passed else None,kind,selector.replace('test_fnd_','').replace('_',' '))
for title in manifest['browser_titles']:
 observed=[r for r in report.get('browser_observed',[]) if r['id']==title]
 status='passed' if len(observed)==72//3 and all(r['status']=='passed' for r in observed) else 'failed' if observed else 'pending'
 append('FND-08',title,title,'tests/browser/foundation.e2e.ts','uv run python -m scripts.dev browser',status,{'path':proof,'source_digest':report['gate']['source_digest'],'target_results':observed},'security_authorization' if 'READY' in title else 'positive')
append('FND-10','TC_FND_INSTALL','clean-lock-and-build','package-lock.json','make bootstrap; npm run typecheck; npm run build','passed',{'path':'docs/phase1a/ENVIRONMENT.md','raw_local_logs':['artifacts/raw/npm-ci.log','artifacts/raw/typecheck.log','artifacts/raw/web-build.log','artifacts/raw/provision.log']})
for suite in ['npm','python']:
 append('FND-12','TC_FND_AUDIT_'+suite.upper(),suite+' current lock audit','scripts/audit.py','uv run python -m scripts.audit','passed' if report.get('dependency_audit',{}).get('status')=='passed' else 'pending',{'path':proof,'scope':suite+' current application/test lock only'})
config=ROOT/'docs/phase1a/configuration-checks.json'
append('FND-13','TC_FND_CI_CONFIG','immutable-pins-and-required-gate','.github/workflows/phase1a.yml','uv run python -m scripts.check_foundation','passed' if config.exists() and json.loads(config.read_text()).get('status')=='passed' else 'pending',{'path':'docs/phase1a/configuration-checks.json'} if config.exists() else None)
for item in ['REMOTE_RUN','BRANCH_PROTECTION']:
 append('FND-13','TC_FND_CI_'+item,item,'.github/workflows/phase1a.yml','Owner verifies GitHub required check and protected branch after repository selection','pending',None,'security_authorization','No remote repository is configured; remote enforcement has not executed.')
append('FND-14','TC_FND_RESTORE','synthetic-schema-and-rls-restore','scripts/recovery.py','uv run python -m scripts.recovery','passed' if report.get('migration_and_recovery',{}).get('status')=='passed' else 'pending',{'path':proof,'scope':'Foundation backup/restore only; operational erasure/tombstone replay pending'})
for f in features.values():
 states={c['status'] for c in f['test_cases']}
 f['current_validation_status']='passed' if states=={'passed'} else 'failed' if 'failed' in states else 'partial' if 'passed' in states else 'pending'
 f['execution_evidence']={'path':proof,'source_digest':report['gate']['source_digest']} if states-{'pending'} else None
m['features'].extend(features.values());m['schema_version']='2';m['scope']='Phase 0 baseline plus Phase 1A foundation; no Phase 1B/1C execution authorized';m['application_test_status']='phase1a_local_validated_external_gates_pending' if report['gate']['status']=='passed' else 'partially_validated_gate_blocked';m['baseline']={'commit':'40231be73ab9a5eb577ccf5308c86f6b7282976b','features':151,'planned_cases':630,'snapshot':'docs/testing/test-matrix-phase0.json'}
(ROOT/'docs/testing/test-matrix.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
all_cases=[c for f in m['features'] for c in f['test_cases']]
from collections import Counter
counts=Counter(c['status'] for c in all_cases)
lines=['# Find Our Child — test matrix','',f'Current traceability: **{len(m["features"])} features, {len(all_cases)} logical test cases**. Statuses: '+', '.join(f'{k}={v}' for k,v in sorted(counts.items()))+'.','', 'The immutable starting point is 151 features / 630 planned cases at commit `40231be73ab9a5eb577ccf5308c86f6b7282976b`. Four disabled-feature guards now have executed evidence; operational baseline scenarios remain pending. Foundation additions include idempotency storage, health contracts, result gates, and restore validation. Browser cases expand to 24 targets each; logical-case totals must not be confused with execution counts.','', ('Phase 1A local required-results gate: **'+report['gate']['status']+'**. Hosted CI and branch protection remain pending; owner acceptance of those external blockers has not been given. A passed foundation guard does not validate future authentication, reporting, approval, media or biometric workflows. The original whole-Phase-1 regression obligation remains unchanged.'),'', 'Machine-readable source: [test-matrix.json](testing/test-matrix.json). Original baseline: [test-matrix-phase0.json](testing/test-matrix-phase0.json). Evidence: [sanitized results](../artifacts/sanitized/results.json). Required Phase 1A inventory: [required-tests.json](phase1a/required-tests.json).','']
for f in m['features']:
 lines += [f'## {f["feature_id"]} — {f["title"]}','',f'Validation: **{f["current_validation_status"]}**. Suite: {f["suite"]}. Fixtures: '+', '.join(f['fixture_ids'])+'.','', 'Positive: '+f['positive_scenarios'],'','Negative: '+f['negative_scenarios'],'','Security/authorization: '+f['security_authorization_scenarios'],'','Edge cases: '+f['edge_cases'],'','Expected: '+f['expected_outcomes'],'','| Test case | Kind | Status | Executable / selector | Evidence |','|---|---|---|---|---|']
 for c in f['test_cases']:
  evidence='pending' if c['execution_evidence'] is None else (c['execution_evidence']['path'] if isinstance(c['execution_evidence'],dict) else str(c['execution_evidence']))
  lines.append('| '+c['test_case_id']+' | '+c['kind']+' | '+c['status']+' | `'+c['planned_file']+'` / `'+c['planned_selector'].replace('|','\\|')+'` | '+evidence+' |')
 lines += ['','Per-case scenarios, commands, expected outcomes, phase applicability and evidence selectors are recorded in the machine-readable matrix above.','']
(ROOT/'docs/TEST_MATRIX.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'features':len(m['features']),'cases':len(all_cases),'statuses':counts},indent=2))
