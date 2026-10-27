"""Independently verify a GitHub artifact against committed source and required inventories.

Usage: python3 tools/verify_phase2d_evidence.py ARTIFACT_METADATA_JSON ARCHIVE_ZIP HEAD_SHA [--no-copy]
The metadata is the single artifact object returned by GitHub's artifact API.
No application validation helper is imported. --no-copy performs a read-only audit.
"""
import hashlib,io,json,re,shutil,struct,subprocess,sys,zipfile,zlib
from collections import Counter
from pathlib import Path

root=Path(__file__).resolve().parents[1]
meta=json.loads(Path(sys.argv[1]).read_text());archive=Path(sys.argv[2]);sha=sys.argv[3]
assert re.fullmatch('[a-f0-9]{40}',sha)
raw=archive.read_bytes();archive_hash=hashlib.sha256(raw).hexdigest();assert meta['digest']=='sha256:'+archive_hash
with zipfile.ZipFile(io.BytesIO(raw)) as z:
    names=[n for n in z.namelist() if not n.endswith('/')];assert len(names)==len(set(names))
    fixed={'checksums.json','coverage.json','results.json','source-manifest.json','traces.json','validation.log'}
    assert all(n in fixed or re.fullmatch(r'screenshots/[a-f0-9]{24}\.png',n) for n in names)
    checks=json.loads(z.read('checksums.json'));assert set(checks)==set(names)-{'checksums.json'}
    for name,digest in checks.items():assert re.fullmatch('[a-f0-9]{64}',digest) and hashlib.sha256(z.read(name)).hexdigest()==digest
    source=json.loads(z.read('source-manifest.json'))
    tracked=subprocess.check_output(['git','ls-tree','-r','--name-only',sha],cwd=root,text=True).splitlines()
    bases={'apps/web','services/api','scripts','database','tests','config'}
    extensions={'.ts','.tsx','.css','.py','.sql','.mjs','.json','.png'}
    expected_sources={n for n in tracked if any(n.startswith(b+'/') for b in bases) and Path(n).suffix in extensions and Path(n).name!='next-env.d.ts' and not any(p in {'.next','__pycache__','node_modules'} for p in Path(n).parts)}
    expected_sources.update(['.coveragerc','docs/phase1b/required-tests.json','docs/phase1c/required-tests.json','docs/phase2a/required-tests.json','docs/phase2a/research/source-lock.json','docs/phase2b/required-tests.json','docs/phase2d/required-tests.json','docs/phase2b/research/source-lock.json','compose.qualification.yaml','package.json','package-lock.json','pyproject.toml','uv.lock','compose.yaml','e2e.config.ts','docs/contracts/openapi.json','docs/contracts/event-envelope.schema.json','docs/contracts/synthetic-candidate-source-v1.schema.json','docs/phase1a/required-tests.json','services/api/Dockerfile','requirements-bootstrap.txt','.github/workflows/phase1a.yml'])
    research_lock=json.loads(subprocess.check_output(['git','show',sha+':docs/phase2a/research/source-lock.json'],cwd=root))
    for entry in research_lock['sources']:
        path='docs/phase2a/research/'+entry['local']
        assert '..' not in Path(path).parts and not Path(entry['local']).is_absolute()
        expected_sources.add(path)
        assert source[path]==entry['sha256']
    qualification_lock=json.loads(subprocess.check_output(['git','show',sha+':docs/phase2b/research/source-lock.json'],cwd=root))
    for entry in qualification_lock['sources']:
        path='docs/phase2b/research/'+entry['local']
        assert '..' not in Path(path).parts and not Path(entry['local']).is_absolute()
        expected_sources.add(path);assert source[path]==entry['sha256']
    assert set(source)==expected_sources, 'Incomplete or unexpected source inventory'
    assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in source)
    specs=''.join(sha+':'+name+'\n' for name in source).encode()
    process=subprocess.run(['git','cat-file','--batch'],input=specs,cwd=root,capture_output=True,check=True)
    data=process.stdout;pos=0
    for name,expected in source.items():
        end=data.index(b'\n',pos);header=data[pos:end].decode().split();assert len(header)==3 and header[1]=='blob'
        size=int(header[2]);payload=data[end+1:end+1+size];assert hashlib.sha256(payload).hexdigest()==expected,name
        pos=end+size+2
    assert pos==len(data)
    def git_json(path):return json.loads(subprocess.check_output(['git','show',sha+':'+path],cwd=root))
    baseline=git_json('docs/phase1a/required-tests.json');identity=git_json('docs/phase1b/required-tests.json');reporting=git_json('docs/phase1c/required-tests.json');research=git_json('docs/phase2a/required-tests.json')
    results=json.loads(z.read('results.json'));source_digest=hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest()
    assert results['gate']=={'status':'passed','reasons':[],'source_digest':source_digest}
    counts={}
    for lane,expected in [('python',baseline['python']),('identity',identity['python']),('reporting',reporting['python']),('resilience',reporting['resilience']),('reporting_http',reporting['http']),('research',research['research']),('research_http',research['research_http'])]:
        assert Counter(t['id'] for t in results[lane])==Counter(expected)
        assert all(t=={'id':t['id'],'status':'passed'} for t in results[lane])
        counts[lane]=len(expected)
    targets={f'{b}-{l}-{w}' for b in ['chromium','firefox','webkit'] for l in ['ar-EG','en-GB'] for w in [320,360,390,1280]}
    expected={(title,target) for title in baseline['browser_titles'] for target in targets}
    assert set((t['id'],t['target']) for t in results['browser'])==expected
    assert len(results['browser'])==len(expected)==360
    assert all(t['status']=='passed' and set(t)=={'id','target','status'} for t in results['browser'])
    per_browser=Counter(t['target'].split('-')[0] for t in results['browser']);assert per_browser=={'chromium':120,'firefox':120,'webkit':120}
    migrations=results['migration_and_recovery']['all_migrations'];assert len(migrations)==29
    for name,digest in migrations.items():assert source['database/migrations/'+name+'.sql']==digest
    assert results['migration_and_recovery']['forced_rls']==46
    assert results['migration_and_recovery']['identity_session_rls']=='passed'
    assert results['migration_and_recovery']['reporting_metadata_rls']=='passed'
    assert results['migration_and_recovery']['operational_erasure']=='pending'
    assert results['migration_and_recovery']['research_vector_restore']=={'status':'passed','vectors_verified':1,'forced_research_tables':4,'raw_vector_exported':False}
    smoke=results['synthetic_model_smoke']
    assert smoke['status']=='synthetic_smoke_only' and smoke['real_models_benchmarked']==0 and smoke['pipeline_images']==32
    assert smoke['recognition_accuracy_claim'] is False and smoke['operational_threshold']=='unset'
    assert smoke['denominators']=={'gallery_images':16,'probes':17,'mate_present':16,'mate_absent':1,'subjects':16}
    assert sum(counts.values())==447 and counts['research']==113 and counts['research_http']==2
    qualification=git_json('docs/phase2b/required-tests.json')['qualification']
    assert len(qualification)==107 and Counter(t['id'] for t in results['qualification'])==Counter(qualification)
    assert all(t=={'id':t['id'],'status':'passed'} for t in results['qualification'])
    counts['qualification']=len(qualification)
    assert sum(counts.values())==554
    workflow=git_json('docs/phase2d/required-tests.json')
    for lane in ['synthetic_workflow','synthetic_workflow_http']:
        required=workflow[lane]
        assert Counter(t['id'] for t in results[lane])==Counter(required)
        assert all(t=={'id':t['id'],'status':'passed'} for t in results[lane])
        counts[lane]=len(required)
    assert len(workflow['synthetic_workflow'])>=84 and len(workflow['synthetic_workflow_http'])>=52
    assert results['migration_and_recovery']['synthetic_workflow_restore']=={'forced_rls_tables':8,'quarantined_restore_denies_access':True,'activation_epoch_reissue_required':True,'operational_erasure':'pending'}
    assert results['qualification_isolation']=={'separate_database':True,'network_internal':True,'published_ports':0,'operational_credentials_mounted':False,'forced_rls_tables':4,'metadata_backup_restore':'passed','restored_revocation':'passed','real_data_authorized':False}
    registry=git_json('config/qualification-models.json');assert registry['real_models_qualified']==0 and len(registry['models'])==8
    assert all(m['decision']=='blocked' and m['artifact']['bytes_verified'] is False and all(m[k] is False for k in ['download_allowed','execution_allowed','operational_allowed']) for m in registry['models'])
    assert results['coverage']['totals']['percent_covered']>=75
    assert results['dependency_audit']=={'status':'passed','npm_known_vulnerabilities':0,'python_known_vulnerabilities':0}
    screenshots=[n for n in names if n.startswith('screenshots/')];assert len(screenshots)==48
    for name in screenshots:
        image=z.read(name);assert image.startswith(b'\x89PNG\r\n\x1a\n');p=8;chunks=[]
        while p<len(image):
            size=struct.unpack('>I',image[p:p+4])[0];kind=image[p+4:p+8];payload=image[p+8:p+8+size];crc=struct.unpack('>I',image[p+8+size:p+12+size])[0]
            assert kind in {b'IHDR',b'PLTE',b'IDAT',b'IEND'} and zlib.crc32(kind+payload)&0xffffffff==crc
            chunks.append(kind);p+=size+12
        assert p==len(image) and chunks[0]==b'IHDR' and chunks[-1]==b'IEND' and b'IDAT' in chunks
    traces=json.loads(z.read('traces.json'));assert len(traces)==360
    assert {(t['test'],t['target']) for t in traces}==expected
    assert all(set(t)=={'test','target','steps'} and all(set(s)=={'api','status'} for s in t['steps']) for t in traces)
    for name in names:assert b'SYNTHETIC_SECRET_CANARY' not in z.read(name)
    assert z.read('validation.log')==b'Phase 2D synthetic investigation required gate: passed\n'
    proof={'verified_head':sha,'source_digest':source_digest,'source_files_verified_against_git_blobs':len(source),'artifact_id':meta['id'],'artifact_name':meta['name'],'archive_sha256':archive_hash,'verified_payload_checksums':len(checks),'counts':counts,'python_total':sum(counts.values()),'browser_total':len(results['browser']),'browser_counts':dict(per_browser),'migration_count':len(migrations),'coverage':results['coverage']['totals'],'screenshots':len(screenshots),'traces':len(traces),'status':'passed'}
    proof['qualification_isolation']=results['qualification_isolation']
    proof['real_models_qualified']=0
    proof['synthetic_workflow_only']=True
    capacity=results['synthetic_workflow_capacity']
    assert capacity['scope']=='synthetic_database_retrieval_only' and capacity['model_inference'] is False and capacity['status']=='measured'
    assert (capacity['sessions'],capacity['queries'],capacity['candidates_per_query'])==(20,100,50)
    assert 0<=capacity['p50_ms']<=capacity['p95_ms']<=capacity['p99_ms']
    assert capacity['database_p95_within_planning_1000ms']==(capacity['p95_ms']<=1000)
    proof['synthetic_workflow_capacity']=capacity
    for name in migrations:
        if name[:4]<='0024':
            old=subprocess.check_output(['git','show','6e793b424c5e3c6eabe9bfc8b819404cf2cfeeed:database/migrations/'+name+'.sql'],cwd=root)
            assert hashlib.sha256(old).hexdigest()==migrations[name]

    target=root/'artifacts/phase2d-sanitized'
    if '--no-copy' not in sys.argv:
        target.mkdir(parents=True,exist_ok=True)
        for name in names:
            path=target/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(z.read(name))
        (root/'docs/phase2d/hosted-artifact-verification.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof))
