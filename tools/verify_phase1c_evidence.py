"""Independently verify a GitHub artifact against committed source and required inventories.

Usage: python3 tools/verify_phase1c_evidence.py ARTIFACT_METADATA_JSON ARCHIVE_ZIP HEAD_SHA [--no-copy]
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
    expected_sources.update(['.coveragerc','docs/phase1b/required-tests.json','docs/phase1c/required-tests.json','package.json','package-lock.json','pyproject.toml','uv.lock','compose.yaml','e2e.config.ts','docs/contracts/openapi.json','docs/contracts/event-envelope.schema.json','docs/phase1a/required-tests.json','services/api/Dockerfile','requirements-bootstrap.txt','.github/workflows/phase1a.yml'])
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
    baseline=git_json('docs/phase1a/required-tests.json');identity=git_json('docs/phase1b/required-tests.json');reporting=git_json('docs/phase1c/required-tests.json')
    results=json.loads(z.read('results.json'));source_digest=hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest()
    assert results['gate']=={'status':'passed','reasons':[],'source_digest':source_digest}
    counts={}
    for lane,expected in [('python',baseline['python']),('identity',identity['python']),('reporting',reporting['python']),('resilience',reporting['resilience']),('reporting_http',reporting['http'])]:
        assert Counter(t['id'] for t in results[lane])==Counter(expected)
        assert all(t=={'id':t['id'],'status':'passed'} for t in results[lane])
        counts[lane]=len(expected)
    targets={f'{b}-{l}-{w}' for b in ['chromium','firefox','webkit'] for l in ['ar-EG','en-GB'] for w in [320,360,390,1280]}
    expected={(title,target) for title in baseline['browser_titles'] for target in targets}
    assert set((t['id'],t['target']) for t in results['browser'])==expected
    assert len(results['browser'])==len(expected)==168
    assert all(t['status']=='passed' and set(t)=={'id','target','status'} for t in results['browser'])
    per_browser=Counter(t['target'].split('-')[0] for t in results['browser']);assert per_browser=={'chromium':56,'firefox':56,'webkit':56}
    migrations=results['migration_and_recovery']['all_migrations'];assert len(migrations)==21
    for name,digest in migrations.items():assert source['database/migrations/'+name+'.sql']==digest
    assert results['migration_and_recovery']['forced_rls']==41
    assert results['migration_and_recovery']['identity_session_rls']=='passed'
    assert results['migration_and_recovery']['reporting_metadata_rls']=='passed'
    assert results['migration_and_recovery']['operational_erasure']=='pending'
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
    traces=json.loads(z.read('traces.json'));assert len(traces)==168
    assert {(t['test'],t['target']) for t in traces}==expected
    assert all(set(t)=={'test','target','steps'} and all(set(s)=={'api','status'} for s in t['steps']) for t in traces)
    for name in names:assert b'SYNTHETIC_SECRET_CANARY' not in z.read(name)
    assert z.read('validation.log')==b'Phase 1C required gate: passed\n'
    proof={'verified_head':sha,'source_digest':source_digest,'source_files_verified_against_git_blobs':len(source),'artifact_id':meta['id'],'artifact_name':meta['name'],'archive_sha256':archive_hash,'verified_payload_checksums':len(checks),'counts':counts,'python_total':sum(counts.values()),'browser_total':len(results['browser']),'browser_counts':dict(per_browser),'migration_count':len(migrations),'coverage':results['coverage']['totals'],'screenshots':len(screenshots),'traces':len(traces),'status':'passed'}
    target=root/'artifacts/phase1c-sanitized'
    if '--no-copy' not in sys.argv:
        target.mkdir(parents=True,exist_ok=True)
        for name in names:
            path=target/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(z.read(name))
        (root/'docs/phase1c/hosted-artifact-verification.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof))
