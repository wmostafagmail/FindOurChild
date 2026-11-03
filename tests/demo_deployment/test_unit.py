"""Generated unit fixtures; never real owner enrollment, permits or asset authority."""
import base64
import hashlib
import json
import os
import time
from uuid import uuid4

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from fastapi.testclient import TestClient

from services.demo_deployment import cli
from services.demo_deployment.app import SESSION, build
from services.demo_deployment.compose import topology
from services.demo_deployment.oidc import Identity
from services.demo_deployment.producers import Producers, append_registry, read_registry
from services.demo_deployment.protected import configuration, read_private
from tools.phase2e.owner_only_v3.checkpoint import Checkpoint
from tools.phase2e.owner_only_v3.records import Denied, canonical, digest, sha


def config():
    return {'domain': 'FOC-PHASE2E-DEPLOYMENT-READINESS-V1', 'instance': str(uuid4()), 'tenant': str(uuid4()),
            'origin': 'https://private.example.invalid:9443',
            'issuer': 'https://identity.example.invalid:9444/realms/foc-private-demo',
            'upstream': 'http://idp:8080/realms/foc-private-demo', 'client': 'foc-bff',
            'audiences': ['foc-api', 'foc-bff'], 'owner_subject': 'generated-unit-subject',
            'source_sha': 'a' * 40, 'binding_expires': int(time.time()) + 3600, 'data_class': 'fictional_demo_only'}


@pytest.mark.parametrize('case', ['positive', 'unknown', 'origin_http', 'origin_query', 'origin_userinfo',
    'issuer_http', 'issuer_realm', 'upstream_remote', 'wrong_audience', 'duplicate_audience', 'wrong_client',
    'wrong_domain', 'real_data', 'source_short', 'source_not_hex', 'bool_expiry', 'foreign_instance', 'owner_bool'])
def test_closed_configuration(case):
    row = config()
    change = {'unknown': {'activate': True}, 'origin_http': {'origin': 'http://private.invalid'},
        'origin_query': {'origin': row['origin'] + '?activate=1'}, 'origin_userinfo': {'origin': 'https://user:pass@private.invalid'},
        'issuer_http': {'issuer': 'http://identity.invalid/realms/foc-private-demo'},
        'issuer_realm': {'issuer': row['issuer'].replace('foc-private-demo', 'master')},
        'upstream_remote': {'upstream': 'https://untrusted.invalid'}, 'wrong_audience': {'audiences': ['foreign']},
        'duplicate_audience': {'audiences': ['foc-api', 'foc-bff', 'foc-bff']}, 'wrong_client': {'client': 'public'},
        'wrong_domain': {'domain': 'V2'}, 'real_data': {'data_class': 'operational'}, 'source_short': {'source_sha': 'a'},
        'source_not_hex': {'source_sha': 'X' * 40}, 'bool_expiry': {'binding_expires': True},
        'foreign_instance': {'instance': '../../owner'}, 'owner_bool': {'owner_subject': True}}
    if case == 'positive':
        assert configuration(row) is row
    else:
        row.update(change[case])
        with pytest.raises((Denied, ValueError)):
            configuration(row)


def oidc_fixture():
    c = config();key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = key.public_key();der = public.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(public));jwk.update(kid='generated-test-key', use='sig')
    active = {'active': True, 'sub': c['owner_subject']}

    def transport(request):
        if request.url.path.endswith('/certs'):
            return httpx.Response(200, json={'keys': [jwk]})
        if request.url.path.endswith('/introspect'):
            return httpx.Response(200, json=active)
        return httpx.Response(404)

    identity = Identity(c, {'client_secret': 'untrusted-unit-fixture-only'},
        {'issuer': c['issuer'], 'spki_sha256': [hashlib.sha256(der).hexdigest()], 'expires_at': int(time.time()) + 60},
        transport=httpx.MockTransport(transport))
    now = int(time.time())
    claims = {'iss': c['issuer'], 'aud': c['audiences'], 'sub': c['owner_subject'], 'sid': 'opaque-fixture-session',
              'iat': now, 'auth_time': now, 'exp': now + 120, 'amr': ['pwd', 'otp']}
    return identity, key, claims, active


@pytest.mark.parametrize('case', ['positive', 'bad_signature', 'bad_algorithm', 'foreign_owner', 'foreign_issuer',
    'foreign_audience', 'missing_otp', 'amr_string', 'future_auth', 'stale_mfa', 'bool_auth', 'opaque_sid_missing',
    'untrusted_key', 'expired_pin', 'wrong_pin_issuer', 'unbound_owner', 'expired_binding', 'revoked_idp', 'revoked_platform'])
def test_actual_signature_owner_mfa_and_live_session(case):
    identity, key, claims, active = oidc_fixture()
    now = time.time()
    changes = {'foreign_owner': {'sub': 'another-fixture'}, 'foreign_issuer': {'iss': 'https://foreign.invalid'},
        'foreign_audience': {'aud': ['foreign']}, 'missing_otp': {'amr': ['pwd']}, 'amr_string': {'amr': 'pwd,otp'},
        'future_auth': {'auth_time': int(now) + 2}, 'stale_mfa': {'auth_time': int(now) - 301},
        'bool_auth': {'auth_time': True}, 'opaque_sid_missing': {'sid': None}}
    claims.update(changes.get(case, {}))
    if case == 'untrusted_key': identity.pin['spki_sha256'] = ['b' * 64]
    if case == 'expired_pin': identity.pin['expires_at'] = int(now) - 1
    if case == 'wrong_pin_issuer': identity.pin['issuer'] = 'https://foreign.invalid'
    if case == 'unbound_owner': identity.config['owner_subject'] = None
    if case == 'expired_binding': identity.config['binding_expires'] = int(now) - 1
    if case == 'revoked_idp': active['active'] = False
    token = jwt.encode(claims, key, algorithm='RS256', headers={'kid': 'generated-test-key'})
    if case == 'bad_signature': token += 'x'
    if case == 'bad_algorithm': token = jwt.encode(claims, b'untrusted-unit-secret-only-32bytes', algorithm='HS256', headers={'kid': 'generated-test-key'})
    operation = lambda: identity.owner(token, 'generated-unit-session-' + 's' * 32, now,
                                       lambda _: case != 'revoked_platform')
    if case == 'positive':
        assert operation().subject == claims['sub']
    else:
        with pytest.raises((Denied, jwt.PyJWTError)):
            operation()


def test_runtime_topology_and_no_secret_interpolation():
    c = config();t = topology(c, source='/reviewed/source', root='/var/lib/findourchild-demo')
    assert t['networks']['control']['internal'] is True and t['networks']['identity']['internal'] is True
    for name in ['db', 'idp-db']:
        assert 'ports' not in t['services'][name] and t['services'][name]['user'] == '999:999'
    worker = t['services']['worker']
    assert worker['network_mode'] == 'none' and worker['user'] == '10001:10001' and worker['read_only']
    assert worker['cap_drop'] == ['ALL'] and 'volumes' not in worker and worker['mem_limit'] == '128m'
    assert t['services']['api']['user'] == '10001:10001' and t['services']['api']['read_only']
    assert not any('admin' in v['source'] for v in t['services']['api']['volumes'])
    assert 'docker.sock' not in json.dumps(t) and all('PASSWORD' not in k or (k.endswith('_FILE') and v.startswith('/run/'))
        for service in t['services'].values() for k, v in service.get('environment', {}).items())
    assert all(v['platform'] == 'linux/amd64' for v in t['services'].values())


def test_local_setup_denies_noninteractive_and_ci(monkeypatch):
    monkeypatch.setattr(cli.platform, 'system', lambda: 'Linux');monkeypatch.setattr(cli.platform, 'machine', lambda: 'x86_64')
    monkeypatch.setattr(cli.os, 'geteuid', lambda: 0);monkeypatch.setattr(cli.sys.stdin, 'isatty', lambda: False)
    with pytest.raises(Denied): cli.local_guard()
    monkeypatch.setattr(cli.sys.stdin, 'isatty', lambda: True);monkeypatch.setattr(cli.sys.stderr, 'isatty', lambda: True)
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    with pytest.raises(Denied): cli.local_guard()


def test_protected_file_negative_before_any_secret_read(tmp_path):
    # Writable /tmp ancestry is intentionally not accepted as deployed protected storage.
    path = tmp_path / 'key.json';path.write_text('{"secret":"generated-unit-only"}')
    with pytest.raises(Denied): read_private(path, owner=os.getuid())
    path.unlink();path.symlink_to('/etc/passwd')
    with pytest.raises((Denied, OSError)): read_private(path, owner=os.getuid())


def checkpoint(tmp_path):
    parent = tmp_path / 'private';parent.mkdir(mode=0o700)
    c = config();rows=[];previous='0' * 64
    for key in [c['instance'], 'producer-registry:' + c['instance']]:
        row={'instance':key,'previous':previous,'state':[1,1,0,'0'*64]};row['chain']=digest(row);rows.append(row);previous=row['chain']
    (parent/'owner-only-v3.checkpoints').write_bytes(b''.join(canonical(r)+b'\n' for r in rows));(parent/'owner-only-v3.checkpoints').chmod(0o600)
    directory=os.open(parent,os.O_RDONLY|os.O_DIRECTORY)
    cp=Checkpoint(directory,owner=os.getuid());os.close(directory)
    path=parent/'registry';path.touch(mode=0o600);fd=os.open(path,os.O_RDWR)
    return cp,fd,c


def test_producer_registry_rollback_revoke_and_no_generated_evidence_trust(tmp_path):
    cp,fd,c=checkpoint(tmp_path)
    key=ed25519.Ed25519PrivateKey.generate()
    producer={'public_key':base64.b64encode(key.public_key().public_bytes_raw()).decode(),'source':'a'*64,'build':'b'*64,
              'tool':'c'*64,'evidence_class':'actual_isolated_measurement','resource_limits':[3000,2000,67108864],'stages':['source']}
    try:
        append_registry(fd,cp,c,'source',producer,revoked=False,expires=int(time.time())+60,epochs=(1,1))
        rows,_=read_registry(fd,cp,c);assert rows['source']['revoked'] is False
        with pytest.raises(Denied,match='producer_epoch_or_uncommitted'):
            Producers(fd,cp,c,lambda *_:False).verify(canonical({'producer':'source'}),b'',epochs=(1,1))
        old=os.pread(fd,65536,0)
        append_registry(fd,cp,c,'source',producer,revoked=True,expires=int(time.time())+60,epochs=(1,1))
        assert read_registry(fd,cp,c)[0]['source']['revoked'] is True
        os.ftruncate(fd,0);os.pwrite(fd,old,0)
        with pytest.raises(Denied):read_registry(fd,cp,c)
    finally:os.close(fd);cp.close()


class UnitState:
    def __init__(self): self.config=config();self.valid=True
    def session(self, session):
        if not self.valid or session!='s'*43:raise Denied('fixture_session')
        return None,sha(b'fixture-csrf')
    def proof(self, session): return 'a'*64
    def readiness(self, session): return {'readiness_only':True,'inference_enabled':False}


@pytest.mark.parametrize('case', ['ar','en','no_cookie','wrong_csrf','cross_origin','owner_claim','bearer','oversized','campaign','model','public_search'])
def test_private_http_closed_surface(case):
    s=UnitState();client=TestClient(build(s),base_url=s.config['origin'])
    if case in ['ar','en']:
        r=client.get('/owner/'+case);assert r.status_code==200
        assert ('dir="rtl"' if case=='ar' else 'dir="ltr"') in r.text
        assert "frame-ancestors 'none'" in r.headers['content-security-policy'] and 'no-store' in r.headers['cache-control']
        assert "connect-src 'self'" in r.headers['content-security-policy']
        assert 'generated-unit-subject' not in r.text
        return
    client.cookies.set(SESSION,'s'*43)
    headers={'origin':s.config['origin'],'x-csrf-token':'fixture-csrf'}
    if case=='no_cookie':client.cookies.clear();r=client.get('/owner/session')
    elif case=='owner_claim':r=client.get('/owner/session?owner=true')
    elif case=='bearer':r=client.get('/owner/session',headers={'authorization':'Bearer invented'})
    elif case in ['campaign','model','public_search']:
        path={'campaign':'/demo-authorization/prepare','model':'/model/load','public_search':'/biometric/search'}[case]
        r=client.post(path,headers=headers,content=b'{}');assert r.status_code==404;return
    else:
        if case=='wrong_csrf':headers['x-csrf-token']='wrong'
        if case=='cross_origin':headers['origin']='https://foreign.invalid'
        r=client.post('/owner/enrollment-proof',headers=headers,content=b'x'*5000 if case=='oversized' else b'{}')
    assert r.status_code==403


@pytest.mark.parametrize('scenario', ['positive','stale','unknown','missing'])
def test_immutable_build_release_identity(scenario):
    from services.demo_deployment.runtime import release_bound
    c=config();release={'source_sha':c['source_sha']}
    if scenario=='stale':release['source_sha']='b'*40
    if scenario=='unknown':release['activate']=True
    if scenario=='missing':release={}
    if scenario=='positive':release_bound(c,release)
    else:
        with pytest.raises(Denied,match='deployment_build_identity'):release_bound(c,release)


@pytest.mark.parametrize('scenario',['unknown','key','evidence','limits','hash'])
def test_invalid_registration_does_not_mutate_external_checkpoint(tmp_path,scenario):
    cp,fd,c=checkpoint(tmp_path)
    p={'public_key':base64.b64encode(b'p'*32).decode(),'source':'a'*64,'build':'b'*64,'tool':'c'*64,
       'evidence_class':'actual_isolated_measurement','resource_limits':[3000,2000,67108864],'stages':['source']}
    if scenario=='unknown':p['approved']=True
    if scenario=='key':p['public_key']='invalid'
    if scenario=='evidence':p['evidence_class']='generated_fixture'
    if scenario=='limits':p['resource_limits']=[300000,200000,6710886400]
    if scenario=='hash':p['source']='not-a-measured-hash'
    before=cp.current('producer-registry:'+c['instance'])
    try:
        with pytest.raises((Denied,ValueError)):
            append_registry(fd,cp,c,'source',p,revoked=False,expires=int(time.time())+60,epochs=(1,1))
        assert cp.current('producer-registry:'+c['instance'])==before and os.fstat(fd).st_size==0
    finally:os.close(fd);cp.close()
