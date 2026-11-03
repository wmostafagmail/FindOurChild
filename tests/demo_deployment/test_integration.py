"""Actual ephemeral TLS, Keycloak, PostgreSQL, protected files and supervisor; no real owner or assets."""
import json
from pathlib import Path

import pytest

from tests.demo_deployment.helpers import (
    BASE,
    admin,
    client,
    command,
    compose,
    headers,
    login,
    private,
    proof,
)
from tools.phase2e.demo_governance.isolation import run


@pytest.fixture(scope='module')
def authenticated():
    c, callback = login()
    assert callback.status_code == 302
    yield c
    c.close()


def test_real_tls_startup_and_nonowner_denial():
    with client() as c:
        r=c.get(BASE+'/health');assert r.status_code==200 and not r.json()['inference']
        assert c.get(BASE+'/owner/session').status_code==403
    c, callback=login('generated-readiness-nonowner')
    try:
        assert callback.status_code==403 and '__Host-foc-demo-session' not in c.cookies
    finally:c.close()


def test_actual_private_service_profiles():
    for name, uid, memory in [('api','10001:10001',268435456),('idp','1000:1000',1073741824),
                              ('db','999:999',536870912),('idp-db','999:999',536870912)]:
        cid=compose('ps','-q',name).decode().strip()
        info=json.loads(command('docker','inspect',cid))[0]
        h=info['HostConfig']
        assert info['State']['Running'] and info['Config']['User']==uid
        assert h['ReadonlyRootfs'] and not h['Privileged'] and h['CapDrop']==['ALL']
        assert 'no-new-privileges:true' in h['SecurityOpt'] and h['Memory']==h['MemorySwap']==memory
        assert not h.get('Devices') and h['PidsLimit']==128
        if name in ['db','idp-db']:
            assert not h['PortBindings']
            for network in info['NetworkSettings']['Networks']:
                assert json.loads(command('docker','network','inspect',network))[0]['Internal'] is True
        else:
            assert all(p['HostIp']=='127.0.0.1' for rows in h['PortBindings'].values() for p in rows)
        if name=='api':
            assert all('admin' not in m['Destination'] and 'docker.sock' not in m['Destination'] for m in info['Mounts'])
            assert next(m for m in info['Mounts'] if m['Destination'].endswith('/runtime'))['RW'] is False


def test_real_owner_mfa_immutable_enrollment_and_proof_replay(authenticated):
    c=authenticated
    assert c.get(BASE+'/owner/session').json()['mfa_verified'] is True
    assert c.get(BASE+'/owner/status').status_code==403
    code=proof(c)
    result=admin('import sys;from services.demo_deployment.runtime import load;s=load(admin=True);s.activate(sys.stdin.read());s.checkpoint.close()',data=code.encode())
    assert result==b''
    r=c.get(BASE+'/owner/status');assert r.status_code==200 and r.json()['readiness_only']
    assert r.json()['campaign_authorizations']==0 and not r.json()['model_parsing_enabled']
    # The interactive CLI rejects non-TTY/CI. A generated fixture cannot masquerade as human terminal setup.
    with pytest.raises(RuntimeError):
        compose('run','--rm','--no-TTY','admin','enroll')
    with pytest.raises(RuntimeError):
        admin('import sys;from services.demo_deployment.runtime import load;s=load(admin=True);s.activate(sys.stdin.read(),recovery=True)',data=code.encode())


def test_real_producer_registration_private_key_and_revocation(authenticated):
    c=authenticated;code=proof(c)
    public=json.loads(Path('.runtime/deployment-fixture/public.json').read_text())
    context=private()
    # Source/build/tool identities are actual bytes/image hashes of the generated measurement service, never model hashes.
    answers=[code,'/var/lib/findourchild-demo/producer-secrets/source.json',public['machine_fingerprint'],'source',
             context['source_digest'],context['api_image'].removeprefix('sha256:'),context['producer_tool_digest']]
    admin('import sys,json;from services.demo_deployment.runtime import load;from services.demo_deployment import cli;'
          'a=iter(json.loads(sys.stdin.read()));cli.ask=lambda _:next(a);s=load(admin=True);cli.register_producer(s);s.checkpoint.close()',
          data=json.dumps(answers).encode())
    raw=admin('import os,json;from services.demo_deployment.runtime import load;from services.demo_deployment.producers import read_registry;'
              's=load(admin=True);f=os.open("/var/lib/findourchild-demo/runtime/producers.jsonl",os.O_RDONLY);'
              'r,e=read_registry(f,s.checkpoint,s.config);assert len(r)==1 and not r["source"]["revoked"];'
              'os.close(f);s.checkpoint.close()')
    assert raw==b''
    admin('from services.demo_deployment.runtime import load;from services.demo_deployment import cli;'
          'cli.ask=lambda _:"source";s=load(admin=True);cli.revoke_producer(s);s.checkpoint.close()')


def test_real_csrf_closed_surface_and_no_artifact_routes(authenticated):
    c=authenticated
    for h in [{}, {'origin':'https://foreign.invalid','x-csrf-token':c.cookies['__Host-foc-demo-csrf']},
              {'origin':BASE,'x-csrf-token':'incorrect'}]:
        assert c.post(BASE+'/owner/enrollment-proof',headers=h,content=b'{}').status_code==403
    assert c.get(BASE+'/owner/status?owner=true').status_code==403
    for path in ['/demo-authorization/prepare','/model/load','/acquire','/biometric/search','/child-release']:
        assert c.post(BASE+path,headers=headers(c),content=b'{}').status_code==404
    assert c.post(BASE+'/owner/enrollment-proof',headers=headers(c),content=b'{"activate":true}').status_code==403


def test_real_forced_rls_runtime_cannot_enable_or_rewrite_history():
    admin('from services.demo_deployment.runtime import load;s=load(admin=True);'
          '\nwith s.connect() as c:\n'
          ' assert c.execute("SELECT count(*) FROM pg_class WHERE relnamespace IN '
          '(\'owner_only_demo\'::regnamespace,\'owner_deployment\'::regnamespace) AND relrowsecurity AND relforcerowsecurity").fetchone()[0]==6\n'
          ' try:c.execute("UPDATE owner_only_demo.authority SET enabled=true")\n'
          ' except __import__("psycopg").errors.InsufficientPrivilege:c.rollback()\n'
          ' else:raise AssertionError("runtime enabled authority")\n'
          '\ns.checkpoint.close()')


@pytest.mark.parametrize('scenario', ['tenant', 'registry-write', 'unrevoke', 'expired', 'proof-restore'])
def test_live_private_storage_negative_boundaries(authenticated, scenario):
    code=proof(authenticated)
    script = '''import sys
from services.demo_deployment.runtime import load
from tools.phase2e.owner_only_v3.records import Denied,sha
import psycopg
s=load(admin=True)
scenario,code=sys.stdin.read().split(':',1)
if scenario=='tenant':
 with s.connect() as c:
  c.execute("SELECT set_config('foc.v3_tenant','ffffffff-ffff-4fff-8fff-ffffffffffff',true)")
  assert c.execute('SELECT count(*) FROM owner_deployment.sessions').fetchone()[0]==0
elif scenario=='registry-write':
 try:
  with s.connect() as c:c.execute("INSERT INTO owner_deployment.registry_commits SELECT * FROM owner_deployment.registry_commits LIMIT 1")
 except psycopg.errors.InsufficientPrivilege:pass
 else:raise AssertionError('runtime registry write')
elif scenario=='unrevoke':
 try:
  with s.connect(admin=True) as c:
   c.execute('UPDATE owner_deployment.sessions SET revoked=true')
   c.execute('UPDATE owner_deployment.sessions SET revoked=false')
 except psycopg.errors.InsufficientPrivilege:pass
 else:raise AssertionError('revocation reversed')
elif scenario=='expired':
 with s.connect(admin=True) as c:
  c.execute('UPDATE owner_deployment.proofs SET expires=1 WHERE key=%s',(sha(code.encode()),))
  try:s._proof(c,code)
  except Denied as e:assert str(e)=='owner_proof_stale'
  else:raise AssertionError('expired proof')
  c.rollback()
elif scenario=='proof-restore':
 with s.connect(admin=True) as c:s._proof(c,code)
 with s.connect(admin=True) as c:
  c.execute('UPDATE owner_deployment.proofs SET consumed=false WHERE key=%s',(sha(code.encode()),))
  try:s._proof(c,code)
  except Denied as e:assert str(e)=='owner_proof_replay'
  else:raise AssertionError('restored proof replay')
  c.rollback()
s.checkpoint.close()
'''
    assert admin(script,data=(scenario+':'+code).encode())==b''


def test_real_generated_immutable_storage_and_no_replace():
    admin('from services.demo_deployment.cli import validate_storage;validate_storage()')
    with pytest.raises(RuntimeError):admin('from services.demo_deployment.cli import validate_storage;validate_storage()')


@pytest.mark.parametrize('mode', ['ok','sleep','network'])
def test_actual_nonroot_offline_worker_and_hard_deadline(mode):
    r=run(private()['worker_image'],mode)
    assert r['exit']==(124 if mode=='sleep' else 0) and r['native_metrics']['inference'] is False
    assert r['limits']['memory_bytes']==134217728 and r['limits']['deadline_ms']==3000


def test_real_hold_revocation_epoch_recovery_and_restored_proof_replay(authenticated):
    c=authenticated
    # Backup bytes are kept private; inactive restore is verified before any reactivation.
    dump=compose('exec','-T','db','pg_dump','-U','postgres','-d','postgres','--no-owner')
    Path('artifacts/raw/deployment/private-backup.sql').write_bytes(dump)
    admin('from services.demo_deployment.runtime import load;s=load(admin=True);s.hold();s.checkpoint.close()')
    assert c.get(BASE+'/owner/session').status_code==403 and c.get(BASE+'/owner/status').status_code==403
    fresh, callback=login();assert callback.status_code==302
    try:
        code=proof(fresh)
        admin('import sys;from services.demo_deployment.runtime import load;s=load(admin=True);s.activate(sys.stdin.read(),recovery=True);s.checkpoint.close()',data=code.encode())
        r=fresh.get(BASE+'/owner/status');assert r.status_code==200 and r.json()['activation_epoch']>=3
        # Restore into a new isolated database and force inactive; never replace the live private deployment.
        compose('exec','-T','db','createdb','-U','postgres','restored_readiness')
        command('docker','compose','-f',private()['compose'],'exec','-T','db','psql','-U','postgres','-d','restored_readiness','-v','ON_ERROR_STOP=1',data=dump)
        result=compose('exec','-T','db','psql','-XAt','-U','postgres','-d','restored_readiness','-c',
                       'UPDATE owner_only_demo.authority SET enabled=false;SELECT count(*) FROM owner_only_demo.authority WHERE enabled;')
        assert result.decode().strip().endswith('0')
    finally:fresh.close()
