"""Append research-only traceability; retain accepted historical rows and pending operational ML cases."""
import hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'docs/testing/test-matrix.json';matrix=json.loads(p.read_text());required=json.loads((ROOT/'docs/phase2a/required-tests.json').read_text())
verified=None
if '--verified-evidence' in sys.argv:
 verified=json.loads(Path(sys.argv[sys.argv.index('--verified-evidence')+1]).read_text())
 assert verified['status']=='passed' and verified['python_total']==447 and verified['browser_total']==168
 assert verified['counts']['research']==len(required['research']) and verified['counts']['research_http']==len(required['research_http'])
 results=json.loads((ROOT/'artifacts/phase2a-sanitized/results.json').read_text())
 assert results['gate']['status']=='passed' and results['gate']['source_digest']==verified['source_digest']
# Remove only this generator's rows so reruns cannot duplicate/rewrite historical acceptance.
matrix['features']=[f for f in matrix['features'] if not f['feature_id'].startswith('RSC-')]
groups=[('RSC-01','Versioned synthetic adapter and fail-closed model loading','test_pipeline.py'),('RSC-02','Reproducible open-set and capture-age/gap evaluation','test_evaluation.py'),('RSC-03','Private pgvector exact retrieval, per-photo metadata and RLS','test_database.py'),('RSC-04','Licensing evidence integrity and privacy-safe artifact gates','test_evidence.py'),('RSC-05','Authenticated capability API and actual BFF regression','research_http'),('RSC-06','Three-engine deterministic disabled-capability regression','browser')]
for fid,title,key in groups:
 if key=='research_http': selectors=required['research_http']
 elif key=='browser': selectors=['TC_ID_BROWSER_MFA_TENANT_LOGOUT']
 else: selectors=[t for t in required['research'] if key in t]
 if fid=='RSC-03':selectors+=['scripts.recovery:research_vector_restore']
 if fid=='RSC-04':selectors+=['scripts.research_benchmark:synthetic_model_smoke']
 cases=[]
 for i,selector in enumerate(selectors,1):
  cases.append({'test_case_id':f'TC_{fid.replace("-","_")}_{i:03}','kind':'research_validation','scenario':selector,'planned_file':selector.split('::')[0],'planned_selector':selector,'planned_command':'python -m scripts.research_validate' if key not in {'browser','research_http'} else 'python -m scripts.dev browser' if key=='browser' else 'python -m scripts.research_test research_http','expected_outcome':'Synthetic foundation invariants hold; unauthorized or incompatible operations fail closed; no real model is qualified','required_from_phase':'2A','status':'pending','execution_evidence':None,'phase2a_required':True})
 for case in cases:
  selector=case['planned_selector']
  if key=='browser':case['planned_file']='tests/browser/identity.e2e.ts'
  if selector=='scripts.recovery:research_vector_restore':
   case['planned_file']='scripts/recovery.py';case['planned_command']='python -m scripts.recovery'
  if selector=='scripts.research_benchmark:synthetic_model_smoke':
   case['planned_file']='scripts/research_benchmark.py';case['planned_command']='python -m scripts.research_validate'
  if verified:
   case['status']='passed'
   case['execution_evidence']={'head_sha':verified['verified_head'],'source_digest':verified['source_digest'],'artifact_id':verified['artifact_id'],'archive_sha256':verified['archive_sha256'],'verification':'docs/phase2a/hosted-artifact-verification.json','run_url':verified.get('run_url','https://github.com/wmostafagmail/FindOurChild/actions/runs/40233614540'),'scope':'synthetic engineering only; zero real recognition models'}
 matrix['features'].append({'feature_id':fid,'category':'research_foundation','source':'phase2a/ARCHITECTURE.md','title':title,'suite':key,'phase_introduced':'2A','positive_scenarios':'Authorized synthetic processing, deterministic metrics and exact scoped retrieval','negative_scenarios':'Invalid manifests, nonfinite vectors, missing/expired/revoked authority or evidence are rejected','security_authorization_scenarios':'API/worker cannot access research; research cannot access operational data; no activation or disclosure','edge_cases':'Unknown dates/ages, ties, duplicate captures, stale revisions, no-mate denominators, cross-bin uncertainty','fixture_ids':['FX-2A-GEOMETRIC','FX-2A-ANALYTIC','FX-2A-PG'],'expected_outcomes':'Reviewable engineering evidence only; real recognition/production qualifications remain pending','test_cases':cases})
future=[]
for i,candidate in enumerate(['insightface','adaface','deepface','opencv_zoo','auraface','authorized_real_dataset_protocol'],1):
 future.append({'test_case_id':f'TC_RSC_07_{i:03}','kind':'qualification','scenario':'Exact artifact/data clearance and independent real evaluation: '+candidate,'planned_file':'not_authorized','planned_selector':candidate,'planned_command':'Pending separate authorization and rights clearance; no download or execution','expected_outcome':'Fail closed until exact weights/data/protocol and measured qualification approvals exist','required_from_phase':'2B','status':'pending','execution_evidence':None,'phase2a_required':False})
matrix['features'].append({'feature_id':'RSC-07','category':'model_qualification','source':'phase2a/LICENSING_MATRIX.md','title':'Real artifact rights, lawful corpus and child-recognition qualification remain blocked','suite':'model_evaluation','phase_introduced':'2A','positive_scenarios':'Only separately approved artifacts and data enter future evaluation','negative_scenarios':'Missing provenance/entitlement blocks download and use','security_authorization_scenarios':'No synthetic result can enable operational recognition or identity/custody decisions','edge_cases':'Different bundled detector licenses, training overlap uncertainty and insufficient age-gap evidence','fixture_ids':[],'expected_outcomes':'All real model qualification cases pending','test_cases':future})
matrix['application_test_status']='phase2a_hosted_technical_validation_passed_awaiting_owner_review' if verified else 'phase2a_implementation_validation_pending'
matrix['fixture_catalog']['FX-2A-GEOMETRIC']={'description':'32 local geometric PNGs; no faces, weights or child data'}
matrix['fixture_catalog']['FX-2A-ANALYTIC']={'description':'Hand-constructed normalized vectors and pseudonymous metric ground truth'}
matrix['fixture_catalog']['FX-2A-PG']={'description':'Isolated real PostgreSQL research grants/datasets/photographs/vector rows; cleanup after each test'}
p.write_text(json.dumps(matrix,indent=2)+'\n')
features=[f for f in matrix['features'] if f['feature_id'].startswith('RSC-')]
cases=[c for f in features for c in f['test_cases']]
(ROOT/'docs/phase2a/TEST_TRACEABILITY.md').write_text('# Phase 2A executable traceability\n\nPhase 0–1C records are preserved. All new rows are pending until independently verified hosted current-source evidence is attached. The existing 151-feature / 630-case Phase 0 baseline remains immutable. Research rows do not mark operational ML requirements passed.\n\n'+''.join(f'- {f["feature_id"]}: {f["title"]}; {len(f["test_cases"])} logical cases.\n' for f in features)+'\n113 research Python tests, two actual HTTP tests, one extended logical browser scenario across all 24 targets, one nonempty vector restore and one synthetic smoke gate. Full accepted regression remains mandatory. Exact selectors, scenarios, authorization negatives, fixtures, expected outcomes, execution evidence and statuses are in [test-matrix.json](../testing/test-matrix.json) and [required-tests.json](required-tests.json).\n')
if verified:
 q=ROOT/'docs/phase2a/TEST_TRACEABILITY.md';text=q.read_text().replace('All new rows are pending until independently verified hosted current-source evidence is attached.','118 research foundation cases passed on independently verified hosted current-source evidence; six real model/data qualification cases remain pending.');q.write_text(text)
print({'features':len(matrix['features']),'cases':sum(len(f['test_cases']) for f in matrix['features']),'new_cases':len(cases),'verified':bool(verified)})
