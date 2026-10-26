"""Append only qualification-preparation rows; never rewrite historical feature evidence."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'docs/testing/test-matrix.json';matrix=json.loads(p.read_text());required=json.loads((ROOT/'docs/phase2b/required-tests.json').read_text())['qualification']
proof=None
if '--verified-evidence' in sys.argv:
 proof=json.loads(Path(sys.argv[sys.argv.index('--verified-evidence')+1]).read_text())
 assert proof['status']=='passed' and proof['python_total']==554 and proof['browser_total']==168 and proof['counts']['qualification']==107
 results=json.loads((ROOT/'artifacts/phase2b-sanitized/results.json').read_text());assert results['gate']['status']=='passed' and results['gate']['source_digest']==proof['source_digest']
 assert {t['id'] for t in results['qualification']}==set(required)
 assert results['qualification_isolation']['metadata_backup_restore']=='passed'
matrix['features']=[f for f in matrix['features'] if not f['feature_id'].startswith('QLF-')]
matrix['fixture_catalog']['FX-QUAL']='32 allowlisted procedural geometric PNG hashes, a non-model artifact byte fixture, invented independent permission records and a separate disposable synthetic metadata PostgreSQL cluster; no real photographs or recognition weights.'
groups={1:[],2:[],3:[],4:[]}
for selector in required:
 name=selector.split('::')[1]
 group=3 if 'test_database.py' in selector else 2 if 'dataset' in name else 1 if any(x in name for x in ['registry','model_manifest','publisher_evidence','restricted_download','artifact']) else 4
 groups[group].append(selector)
groups[3].append('scripts.qualification_validate:isolated_native_recovery')
titles={1:'Model manifests, publisher-reference integrity and unconditional acquisition denial',2:'Synthetic dataset authorization, independent approval and evaluation leakage prevention',3:'Separate PostgreSQL cluster, tenant RLS, expiry/revocation and native metadata restore',4:'Reproducible rank/age/uncertainty arithmetic and bounded multi-photograph aggregation',5:'Real-model, private-data, hardware and independent evaluation approvals remain pending'}
for group in range(1,6):
 selectors=groups.get(group,[])
 if group==5:selectors=[m['id'] for m in json.loads((ROOT/'config/qualification-models.json').read_text())['models']]+['independent-private-dataset-approval','safe-inference-hardware-provider-qualification','independent-real-child-benchmark','separately-controlled-age-progression']
 cases=[]
 for i,selector in enumerate(selectors,1):
  passed=proof is not None and group!=5
  case={'test_case_id':f'TC_QLF_{group:02}_{i:03}','kind':'qualification_preparation' if group!=5 else 'external_qualification','scenario':selector,'planned_file':selector.split('::')[0] if group!=5 else 'not_authorized','planned_selector':selector,'planned_command':'python -m scripts.qualification_validate' if group!=5 else 'Separate approval and independent evaluation required; do not acquire or execute','expected_outcome':'Synthetic preparation invariants hold and sensitive requests fail closed' if group!=5 else 'Remain blocked until independent rights/data/technical approvals exist','required_from_phase':'2B preparation' if group!=5 else 'separately authorized real evaluation','status':'passed' if passed else 'pending','execution_evidence':None,'phase2b_required':group!=5}
  if selector.startswith('scripts.qualification_validate:'):case['planned_file']='scripts/qualification_validate.py'
  if passed:case['execution_evidence']={'run_url':proof['run_url'],'verified_head':proof['verified_head'],'source_digest':proof['source_digest'],'artifact_id':proof['artifact_id'],'archive_sha256':proof['archive_sha256'],'selector':selector}
  cases.append(case)
 matrix['features'].append({'feature_id':f'QLF-{group:02}','category':'qualification_preparation','source':'phase2b/VALIDATION_REPORT.md','title':titles[group],'suite':'model_evaluation' if group!=3 else 'database_security','phase_introduced':'2B preparation','positive_scenarios':'Only approved fixed synthetic fixtures and isolated metadata are admitted; future real qualification needs new authority','negative_scenarios':'Corrupt or unknown artifacts, restricted acquisition, claimed real-data permission, self-approval, stale or revoked grants and split leakage fail closed','security_authorization_scenarios':'No operational credentials, case data, public facial search, automated identity decision or custody disclosure','edge_cases':'Missing dates/age strata, rank 51, zero-event uncertainty, source hash mismatch, duplicate photographs, expired access and restore','fixture_ids':['FX-QUAL'],'expected_outcomes':'Engineering preparation only; no real recognition accuracy or lawful data clearance claimed','test_cases':cases})
matrix['application_test_status']='phase2b_preparation_hosted_validation_passed_awaiting_owner_review' if proof else 'phase2b_preparation_validation_pending'
p.write_text(json.dumps(matrix,ensure_ascii=False,indent=2)+'\n')
counts={s:sum(c['status']==s for f in matrix['features'] for c in f['test_cases']) for s in ['passed','pending']}
(ROOT/'docs/phase2b/TEST_TRACEABILITY.md').write_text('# Phase 2B feature/test traceability\n\nThe original 185 feature rows and immutable Phase 0 151-feature/630-case baseline are preserved exactly. Five QLF rows append all 107 strict qualification selectors, one real native lab recovery/isolation gate, and 12 pending real qualification/approval cases. [Canonical registry](../testing/test-matrix.json), [required inventory](required-tests.json). No prior pending real-model requirement is marked passed by synthetic preparation.\n\nCurrent registry: '+str(len(matrix['features']))+' features; '+str(sum(counts.values()))+' cases; '+str(counts['passed'])+' passed; '+str(counts['pending'])+' pending. Every row contains scenarios, security/edge cases, fixtures, expected outcomes, exact execution selector and evidence/status.\n')
print(counts)
