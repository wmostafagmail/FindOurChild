"""Exact-source generated deployment validation. No real owner, asset or model operation."""
import hashlib
import io
import json
import os
import secrets
import shutil
import ssl
import subprocess
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives import serialization

from scripts.artifacts import clean_png
from scripts.dev import sanitize_environment
from tests.demo_deployment.helpers import admin, command
from tools.phase2e.demo_governance.run_checks import Results

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/phase2e-deployment-readiness'
PRIVATE = ROOT / '.runtime/deployment-fixture'


def sources():
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', 'HEAD'], cwd=ROOT, text=True).splitlines()
    selected = [p for p in paths if p.startswith(('services/demo_deployment/', 'tests/demo_deployment/',
        'tests/demo_deployment_browser/', 'deployment/private-demo/', 'database/owner_deployment/',
        'tools/phase2e/owner_only_v3/', 'tools/phase2e/demo_governance/', 'services/demo_governance/'))
        or p in ['e2e.deployment.config.ts', '.github/workflows/phase2e-deployment-readiness.yml',
                 'scripts/deployment_validate.py', 'scripts/deployment_credentials.py', 'pyproject.toml', 'uv.lock',
                 'package-lock.json', 'requirements-bootstrap.txt', 'docs/phase2e/deployment-required-tests.json']]
    return {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in selected}


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true' and sys.platform == 'linux'
    OUT.mkdir(parents=True, exist_ok=False);PRIVATE.mkdir(parents=True, exist_ok=False)
    rawdir = ROOT/'artifacts/raw/deployment';rawdir.mkdir(parents=True, exist_ok=True)
    rawdir.chmod(0o700)
    before=sources();required=json.loads((ROOT/'docs/phase2e/deployment-required-tests.json').read_text())
    head=command('git','rev-parse','HEAD').decode().strip()
    # Fixture-only release identity consumed by the same production preparation logic.
    release=ROOT/'release.json';assert not release.exists();release.write_text(json.dumps({'source_sha':head}))
    plan={'directory':'/var/lib/foc-deployment-ci-'+secrets.token_hex(16),'runner_uid':os.getuid(),
          'cert':str(ROOT/'.runtime/tls/server.pem'),'key':str(ROOT/'.runtime/tls/key.pem'),
          'credentials':str(PRIVATE/'credentials.json'),'public':str(PRIVATE/'public.json')}
    (PRIVATE/'plan.json').write_text(json.dumps(plan));(PRIVATE/'plan.json').chmod(0o600)
    compose_path=plan['directory']+'/compose.json'
    logs=io.StringIO();result=Results();context={'compose':str(PRIVATE/'compose.json')}
    phase='fixture_preparation'
    try:
        command('sudo','-E',sys.executable,'-m','tests.demo_deployment.fixture',str(PRIVATE/'plan.json'))
        command('sudo','cp',compose_path,str(PRIVATE/'compose.json'))
        command('sudo','chown',str(os.getuid()),str(PRIVATE/'compose.json'))
        (PRIVATE/'context.json').write_text(json.dumps(context))
        def compose(*args,timeout=600):
            return command('docker','compose','-f',context['compose'],*args,timeout=timeout)
        # Full build logs stay private, and no secret enters build args/context.
        phase='locked_image_build'
        (rawdir/'build.log').write_bytes(compose('build','api','idp','worker',timeout=1200))
        phase='private_database_initialization'
        compose('up','-d','--wait','db','idp-db',timeout=120)
        admin('from services.demo_deployment.cli import init_db;init_db()')
        phase='actual_idp_tls_startup'
        compose('up','-d','idp')
        transport=httpx.Client(verify=ssl.create_default_context(cafile=str(ROOT/'.runtime/tls/cert.pem')),
                               trust_env=False,timeout=5)
        deadline=time.monotonic()+180
        while True:
            try:
                discovery=transport.get('https://127.0.0.1:9444/realms/foc-private-demo/.well-known/openid-configuration')
                if discovery.status_code==200:
                    assert discovery.json()['issuer']=='https://127.0.0.1:9444/realms/foc-private-demo';break
            except httpx.HTTPError:pass
            assert time.monotonic()<deadline,'Actual generated IdP did not become ready'
            time.sleep(.5)
        jwks=transport.get('https://127.0.0.1:9444/realms/foc-private-demo/protocol/openid-connect/certs').json()['keys']
        fingerprints=[]
        for row in jwks:
            if row.get('kty')=='RSA' and row.get('use')=='sig':
                key=jwt.PyJWK.from_dict(row).key.public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
                fingerprints.append(hashlib.sha256(key).hexdigest())
        assert len(fingerprints)==1
        # Generated fixture pin, never a real owner/admin trust enrollment.
        pin={'issuer':'https://127.0.0.1:9444/realms/foc-private-demo','spki_sha256':fingerprints,'expires_at':int(time.time())+3600}
        admin('import sys,json;from services.demo_deployment.protected import ROOT,create_private;'
              'create_private(ROOT/"runtime/idp-pin.json",json.loads(sys.stdin.read()),owner=10001)',data=json.dumps(pin).encode())
        phase='actual_readiness_tls_startup'
        compose('up','-d','api')
        deadline=time.monotonic()+60
        while True:
            try:
                r=transport.get('https://127.0.0.1:9443/health')
                if r.status_code==200:break
            except httpx.HTTPError:pass
            assert time.monotonic()<deadline,'Actual readiness HTTPS service did not start';time.sleep(.2)
        api_image=compose('images','-q','api').decode().strip();worker_image='foc-private-benign-worker:'+head
        def image_id(image):return json.loads(command('docker','inspect',image))[0]['Id']
        context.update(api_image=image_id(api_image),worker_image=image_id(worker_image),
            idp_image=image_id(compose('images','-q','idp').decode().strip()),
            db_image=image_id(compose('images','-q','db').decode().strip()),
            source_digest=hashlib.sha256(json.dumps(before,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            producer_tool_digest=hashlib.sha256((ROOT/'services/demo_deployment/producers.py').read_bytes()).hexdigest())
        (PRIVATE/'context.json').write_text(json.dumps(context))
        probe_dir=rawdir/'worker-probes';probe_dir.mkdir();os.environ['FOC_GOVERNANCE_PROBE_EVIDENCE']=str(probe_dir)
        phase='actual_private_storage_authorization_recovery_and_worker_tests'
        with redirect_stdout(logs),redirect_stderr(logs):
            code=pytest.main(['--confcutdir=tests/demo_deployment','tests/demo_deployment','-q','--tb=short'],plugins=[result])
        assert result.nodes==required['python'] and len(result.nodes)==len(set(result.nodes))
        assert code==0 and all(v=={'setup':'passed','call':'passed','teardown':'passed'} for v in result.stages.values())
        (OUT/'python-results.json').write_text(json.dumps({'tests':result.stages,'mandatory_skips':0,'real_owner_provisioned':False},indent=2)+'\n')
        browser_env={**sanitize_environment(os.environ),'GITHUB_ACTIONS':'true','E2E_TELEMETRY_DISABLED':'1','DO_NOT_TRACK':'1',
                     'FOC_E2E_DATA_CLASS':'synthetic','FOC_E2E_ISOLATED':'1'}
        phase='official_three_browser_readiness'
        browser=subprocess.run(['./node_modules/.bin/e2e','run','--config','e2e.deployment.config.ts','--retries','0','--no-cache'],
                               cwd=ROOT,env=browser_env,capture_output=True,timeout=2400,check=False)
        (rawdir/'browser.log').write_bytes(browser.stdout+browser.stderr)
        report=json.loads((ROOT/'.e2e-deployment-readiness/report.json').read_text())['run']['results']
        targets={f'{b}-{l}-{w}' for b in ['chromium','firefox','webkit'] for l in ['ar-EG','en-GB'] for w in [320,360,390,1280]}
        assert len(report)==24 and {r['targetId'] for r in report}==targets
        traces=[];screens={}
        for row in report:
            assert row['titlePath'][-1]=='DR-B01-real-private-readiness-without-campaign' and len(row['attempts'])==1
            traces.append({'case':row['titlePath'][-1],'target':row['targetId'],'status':row['status'],
                           'steps':[{'api':s['api'] if s['api'].startswith(('app.','browser.','expect.')) else 'other',
                                     'status':s['status']} for s in row['attempts'][0].get('steps',[])]})
            if row['status']=='passed':
                images=[a for a in row['attempts'][0].get('artifacts',[]) if a.get('kind')=='screenshot'
                        and 'deployment-readiness-signed-out-shell' in a['path']]
                assert len(images)==1
                path=(ROOT/'.e2e-deployment-readiness/results'/images[0]['path']).resolve()
                assert path.is_relative_to((ROOT/'.e2e-deployment-readiness/results').resolve())
                data=clean_png(path.read_bytes());name=hashlib.sha256(row['targetId'].encode()).hexdigest()+'.png'
                (OUT/'screenshots').mkdir(exist_ok=True);(OUT/'screenshots'/name).write_bytes(data);screens[name]=hashlib.sha256(data).hexdigest()
        (OUT/'browser-results.json').write_text(json.dumps({'framework':'TesterArmy/e2e','e2e':'0.21.3','web':'0.15.3',
            'executed':24,'passed':sum(r['status']=='passed' for r in report),'mandatory_skips':sum(r['status']=='skipped' for r in report),
            'screenshots':screens,'traces':traces},indent=2)+'\n')
        assert browser.returncode==0 and all(r['status']=='passed' for r in report) and len(screens)==24
        assert before==sources(),'Source changed during deployment verification'
        shutil.copytree(probe_dir,OUT/'benign-worker-probes')
        (OUT/'manifest.json').write_text(json.dumps({'checkout':head,'tree':command('git','rev-parse','HEAD^{tree}').decode().strip(),
            'source_manifest':before,'source_digest':context['source_digest'],'image_identities':{k:v for k,v in context.items() if k.endswith('_image')},
            'python_tests':len(result.nodes),'official_new_browser_executions':24,'original_browser_executions_required_elsewhere':504,
            'fixture_url':'https://127.0.0.1:9443','fixture_url_scope':'ephemeral_CI_only_not_owner_hosting',
            'actual_owner_provisioning':False,'actual_campaign_authorizations':0,'model_assets':0,'image_assets':0,'model_parses':0,'inference':False,
            'runtime':'actual_TLS_Keycloak_private_PostgreSQL_checkpoint_and_benign_Linux_worker',
            'performance_gate':'unchanged_database_demo_exception_queue_separate',
            'payload_sha256':{str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file()}},indent=2)+'\n')
    except BaseException as error:
        (OUT/'failure.json').write_text(json.dumps({'checkout':head,'error_class':type(error).__name__,'phase':phase,'source_manifest':before,
            'tests':result.stages,'diagnostics':result.diagnostics,'scope':'generated_source_only_no_real_owner_no_assets_no_inference'},indent=2)+'\n')
        print(json.dumps({'deployment_failed':True,'phase':phase,'error_class':type(error).__name__,'diagnostics':result.diagnostics}))
        raise
    finally:
        (rawdir/'pytest.log').write_text(logs.getvalue());(rawdir/'pytest.log').chmod(0o600)
        prior_error=sys.exc_info()[0]
        try:
            if Path(context['compose']).exists():
                command('docker','compose','-f',context['compose'],'down','--remove-orphans',timeout=90)
        except RuntimeError:
            (OUT/'cleanup-failure.json').write_text(json.dumps({'cleanup_passed':False,'checkout':head})+'\n')
            if prior_error is None:raise
        finally:
            release.unlink(missing_ok=True)
    manifest=json.loads((OUT/'manifest.json').read_text());manifest['containers_disposed']=True
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'deployment_python_passed':len(result.nodes),'official_new_browser_passed':24,'real_owner_provisioned':False,'assets':0,'inference':False,'containers_disposed':True}))


if __name__=='__main__':main()
