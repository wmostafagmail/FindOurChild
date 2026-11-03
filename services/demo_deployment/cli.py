"""TTY-only local Linux setup. Never prints secrets; no acquisition or campaign commands."""
import base64
import getpass
import hashlib
import json
import os
import platform
import secrets
import sys
import time
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

import httpx
import jwt
import psycopg
from cryptography.exceptions import InvalidSignature
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from psycopg import sql

from tools.phase2e.owner_only_v3.records import canonical, digest, require

from .compose import topology
from .protected import ROOT, configuration, create_private, read_private

SOURCE = Path(__file__).resolve().parents[2]


def local_guard():
    require(platform.system() == 'Linux' and platform.machine() == 'x86_64' and os.geteuid() == 0,
            'local_linux_root_required')
    require(sys.stdin.isatty() and sys.stderr.isatty(), 'interactive_terminal_required')
    require(os.environ.get('GITHUB_ACTIONS') != 'true', 'no_real_setup_in_public_ci')
    os.umask(0o077)


def ask(label):
    value = getpass.getpass(label + ': ')
    require(0 < len(value) <= 4096 and not any(ord(c) < 32 for c in value), 'setup_input')
    return value


def private_dir(path, uid=0):
    path.mkdir(mode=0o700, parents=True, exist_ok=False)
    os.chown(path, uid, uid)


def write_all(fd, data):
    while data:
        size=os.write(fd,data)
        require(size>0,'setup_private_write')
        data=data[size:]


def prepare():
    # This performs local storage setup, not owner authentication or enrollment.
    require(not ROOT.exists(), 'deployment_already_prepared')
    source = SOURCE
    release = json.loads((source / 'release.json').read_text()) if (source / 'release.json').exists() else {
        'source_sha': __import__('subprocess').check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()}
    origin, issuer = ask('Private application HTTPS origin (no trailing slash)'), ask('IdP HTTPS issuer ending /realms/foc-private-demo')
    config = configuration({'domain': 'FOC-PHASE2E-DEPLOYMENT-READINESS-V1', 'instance': str(uuid4()),
        'tenant': str(uuid4()), 'origin': origin, 'issuer': issuer,
        'upstream': 'http://idp:8080/realms/foc-private-demo', 'client': 'foc-bff',
        'audiences': ['foc-api', 'foc-bff'], 'owner_subject': None, 'source_sha': release['source_sha'],
        'binding_expires': int(time.time()) + 30 * 86400, 'data_class': 'fictional_demo_only'})
    # Actual TLS certificate/key bytes are owner-supplied locally. No generated production identity.
    certificates = {}
    from cryptography import x509

    for name, host_url, uid in [('app', origin, 10001), ('idp', issuer, 1000)]:
        cert = Path(ask(name + ' full-chain PEM absolute path')).read_bytes()
        key = Path(ask(name + ' unencrypted PEM private-key absolute path')).read_bytes()
        parsed = x509.load_pem_x509_certificate(cert)
        private = serialization.load_pem_private_key(key, password=None)
        require(parsed.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
                == private.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo),
                'tls_key_mismatch')
        import datetime
        import ipaddress
        from urllib.parse import urlsplit

        require(parsed.not_valid_before_utc <= datetime.datetime.now(datetime.UTC)
                < parsed.not_valid_after_utc, 'tls_certificate_expired')
        sans = parsed.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
        host = urlsplit(host_url).hostname
        try:
            require(ipaddress.ip_address(host) in sans.get_values_for_type(x509.IPAddress), 'tls_ip_identity')
        except ValueError:
            require(host in sans.get_values_for_type(x509.DNSName), 'tls_dns_identity')
        certificates[name] = (cert, key, uid)
    client_secret = ask('Existing/new dedicated confidential OIDC client secret (stored locally only)')
    admin_username = ask('Temporary local Keycloak administrator username')
    require(admin_username.isascii() and admin_username.isalnum() and len(admin_username) <= 32, 'idp_admin_name')
    admin_password = ask('Temporary local Keycloak administrator password (minimum 20 characters)')
    require(len(admin_password) >= 20, 'idp_admin_password_strength')
    db_password, idp_admin_password, idp_password, runtime_password = [secrets.token_urlsafe(32) for _ in range(4)]
    config_private = {'client_secret': client_secret, 'session_key': Fernet.generate_key().decode(),
        'runtime_url': f'postgresql://foc_deployment:{quote(runtime_password)}@db:5432/postgres'}
    admin_private = {**config_private, 'admin_url': f'postgresql://postgres:{quote(db_password)}@db:5432/postgres',
        'idp_admin_url': f'postgresql://postgres:{quote(idp_admin_password)}@idp-db:5432/postgres',
        'idp_password': idp_password, 'runtime_password': runtime_password}
    private_dir(ROOT)
    for name, uid in [('runtime', 10001), ('admin', 0), ('checkpoint', 10001), ('quarantine', 0),
                      ('immutable-artifacts', 0), ('producer-secrets', 0), ('database', 999), ('identity-database', 999),
                      ('idp', 1000), ('tls', 0)]:
        private_dir(ROOT / name, uid)
    for name, value in [('config.json', config), ('private.json', config_private)]:
        create_private(ROOT / 'runtime' / name, value, owner=10001)
    create_private(ROOT / 'admin/private.json', admin_private)
    # No real producer is registered by prepare. Initial empty journal is sealed independently.
    registry = ROOT / 'runtime/producers.jsonl'
    fd = os.open(registry, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.fchown(fd, 10001, 10001);os.fsync(fd);os.close(fd)
    checkpoint_rows = []
    previous = '0' * 64
    for instance in [config['instance'], 'producer-registry:' + config['instance']]:
        row = {'instance': instance, 'previous': previous, 'state': [1, 1, 0, '0' * 64]}
        row['chain'] = digest(row);previous = row['chain'];checkpoint_rows.append(row)
    cp = ROOT / 'checkpoint/owner-only-v3.checkpoints'
    fd = os.open(cp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    data = b''.join(canonical(r) + b'\n' for r in checkpoint_rows)
    write_all(fd, data);os.fchown(fd, 10001, 10001);os.fsync(fd);os.close(fd)
    for name, password in [('database', db_password), ('identity-database', idp_admin_password)]:
        fd = os.open(ROOT / name / 'password', os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        write_all(fd, password.encode());os.fchown(fd, 999, 999);os.fsync(fd);os.close(fd)
        private_dir(ROOT / name / 'data', 999)
    realm = json.loads((SOURCE / 'config/keycloak/realm-template.json').read_text())
    realm.update(realm='foc-private-demo', sslRequired='external', users=[])
    realm['clients'][0]['secret'] = client_secret
    realm['clients'][0]['redirectUris'] = [origin + '/owner/callback']
    create_private(ROOT / 'idp/realm.json', realm, owner=1000)
    private_dir(ROOT / 'idp/data', 1000)
    private_dir(ROOT / 'idp/data/import', 1000)
    # Keycloak.conf is a private bind mount. Secrets do not enter Compose, process argv or public CI.
    escaped_admin = ''.join('\\' + c if c in '\\ :=#!' else c for c in admin_password)
    text = f'db-password={idp_password}\nbootstrap-admin-username={admin_username}\nbootstrap-admin-password={escaped_admin}\n'
    for name, data in [('keycloak.conf', text.encode()), ('entrypoint.sh', b'#!/bin/bash\nset -euo pipefail\nexec /opt/keycloak/bin/kc.sh start --optimized --import-realm\n'), ('secrets.json', b'{}')]:
        fd = os.open(ROOT / 'idp' / name, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        write_all(fd, data);os.fchown(fd, 1000, 1000);os.fsync(fd);os.close(fd)
    for name, (cert, key, uid) in certificates.items():
        private_dir(ROOT / 'tls' / name, uid)
        for filename, data in [('cert.pem', cert), ('key.pem', key)]:
            fd = os.open(ROOT / 'tls' / name / filename, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            write_all(fd, data);os.fchown(fd, uid, uid);os.fsync(fd);os.close(fd)
    create_private(ROOT / 'compose.json', topology(config, source=source, root=ROOT))
    print('Private configuration prepared; owner is unbound, all model actions unavailable.')


def init_db():
    p = read_private(ROOT / 'admin/private.json', owner=0)
    config = read_private(ROOT / 'runtime/config.json', owner=10001)
    with psycopg.connect(p['admin_url'], autocommit=True) as conn:
        conn.execute((SOURCE / 'database/owner_only_demo/0001_authority.sql').read_text())
        conn.execute((SOURCE / 'database/owner_deployment/0001_readiness.sql').read_text())
        conn.execute(sql.SQL('CREATE ROLE foc_deployment LOGIN NOSUPERUSER NOBYPASSRLS PASSWORD {}').format(sql.Literal(p['runtime_password'])))
        conn.execute('GRANT foc_v3_service TO foc_deployment')
        conn.execute('REVOKE CREATE ON SCHEMA public FROM PUBLIC')
        conn.execute('INSERT INTO owner_only_demo.authority(instance,tenant,activation_epoch,authority_epoch,checkpoint) '
                     'VALUES(%s,%s,1,1,%s)', (config['instance'], config['tenant'], '0' * 64))
    with psycopg.connect(p['idp_admin_url'], autocommit=True) as conn:
        conn.execute(sql.SQL('CREATE ROLE keycloak LOGIN NOSUPERUSER NOBYPASSRLS PASSWORD {}').format(sql.Literal(p['idp_password'])))
        conn.execute('CREATE DATABASE keycloak OWNER keycloak')
    print('Private schemas initialized inactive; no owner or campaign enrolled.')


def pin_idp():
    from .oidc import Identity

    config = read_private(ROOT / 'runtime/config.json', owner=10001)
    private = read_private(ROOT / 'admin/private.json', owner=0)
    identity = Identity(config, private, None)
    discovery = identity.request('/.well-known/openid-configuration')
    require(discovery['issuer'] == config['issuer'], 'discovery_issuer')
    rows = identity.request('/protocol/openid-connect/certs')['keys']
    fingerprints = []
    import jwt

    for row in rows:
        if row.get('kty') != 'RSA' or row.get('use') != 'sig':
            continue
        public = jwt.PyJWK.from_dict(row).key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
        fingerprints.append(hashlib.sha256(public).hexdigest())
    require(0 < len(fingerprints) <= 4, 'pin_key_inventory')
    # Public fingerprints only; owner must cross-check via trusted IdP administration.
    print('Observed public RSA SPKI SHA-256 fingerprints:', ','.join(fingerprints))
    confirmed = ask('Enter the exact independently checked signing-key fingerprint')
    require(confirmed in fingerprints, 'pin_confirmation')
    create_private(ROOT / 'runtime/idp-pin.json', {'issuer': config['issuer'], 'spki_sha256': [confirmed],
                   'expires_at': min(config['binding_expires'], int(time.time()) + 30 * 86400)}, owner=10001)
    print('IdP keys pinned; no owner or campaign enrolled.')


def bind_owner():
    config = read_private(ROOT / 'runtime/config.json', owner=10001)
    subject = ask('Exact real owner immutable IdP subject from protected IdP administration')
    require(0 < len(subject) <= 256, 'owner_subject_bound')
    create_private(ROOT / 'runtime/binding.json', {'subject': subject, 'config_digest': digest(config)}, owner=10001)
    print('Pending subject pinned; actual fresh owner MFA and terminal proof are still required.')


def register_producer(state):
    from .producers import append_registry

    code = ask('Fresh owner local-setup proof from the authenticated private page')
    path = Path(ask('Protected machine Ed25519 key JSON absolute path (local only)'))
    key_data = read_private(path, owner=0)
    private = Ed25519PrivateKey.from_private_bytes(base64.b64decode(key_data['private_key'], validate=True))
    public = private.public_key().public_bytes_raw()
    fingerprint = hashlib.sha256(public).hexdigest()
    print('Machine public-key fingerprint:', fingerprint)
    require(ask('Confirm exact machine public-key fingerprint') == fingerprint, 'producer_key_confirmation')
    challenge = secrets.token_bytes(32)
    private.public_key().verify(private.sign(challenge), challenge)
    name = ask('Producer stage: source/quarantine/bytes/processed/load')
    producer = {'public_key': base64.b64encode(public).decode(), 'source': ask('Measured producer source SHA-256'),
                'build': ask('Measured producer binary/build SHA-256'), 'tool': ask('Measured producer tool SHA-256'),
                'evidence_class': 'actual_isolated_measurement', 'resource_limits': [3000, 2000, 67108864], 'stages': [name]}
    fd = os.open(ROOT / 'runtime/producers.jsonl', os.O_RDWR | os.O_NOFOLLOW)
    try:
        with state.connect(admin=True) as conn:
            row = state._authority(conn)
            require(row[2] is True, 'producer_owner_not_enrolled')
            proof_token, proof_session = state._proof(conn, code)
            # Enrollment/recovery advances authority; registry epoch rollover is an explicit admin action.
            key = 'producer-registry:' + state.config['instance']
            with state.checkpoint.locked():
                states, previous = state.checkpoint._read();old = states[key]
                if old[:2] != tuple(row[3:5]):
                    state.checkpoint._append(key, (*row[3:5], old[2], old[3]), previous)
            value = append_registry(fd, state.checkpoint, state.config, name, producer,
                                   revoked=False, expires=int(time.time()) + 3600, epochs=row[3:5])
            conn.execute('INSERT INTO owner_deployment.registry_commits(key,instance,tenant,config_digest,activation_epoch,authority_epoch) '
                         'VALUES(%s,%s,%s,%s,%s,%s)', (value, state.config['instance'], state.config['tenant'], digest(state.config), *row[3:5]))
            state._admin_audit(conn, 'technical_producer_registered_readiness_only', row[3:])
            state.identity.owner(proof_token, proof_session, time.time(), state.live)
        print('Machine producer registered; no asset measurements or campaign authority issued.')
        return value
    finally:
        os.close(fd)


def revoke_producer(state):
    from .producers import append_registry, read_registry

    name = ask('Existing producer stage to revoke')
    fd = os.open(ROOT / 'runtime/producers.jsonl', os.O_RDWR | os.O_NOFOLLOW)
    try:
        with state.connect(admin=True) as conn:
            row = state._authority(conn)
            rows, epochs = read_registry(fd, state.checkpoint, state.config)
            require(name in rows, 'producer_missing')
            append_registry(fd, state.checkpoint, state.config, name, rows[name]['producer'], revoked=True,
                            expires=int(time.time()) + 3600, epochs=epochs[:2])
            state._admin_audit(conn, 'technical_producer_revoked', row[3:])
        print('Producer revoked. No replacement registration or authority created.')
    finally:
        os.close(fd)


def create_producer_key():
    from .producers import STAGES

    name = ask('Machine producer stage')
    require(name in STAGES, 'producer_stage')
    key = Ed25519PrivateKey.generate()
    create_private(ROOT / 'producer-secrets' / (name + '.json'),
                   {'private_key': base64.b64encode(key.private_bytes_raw()).decode()})
    print('Machine public-key SHA-256:', hashlib.sha256(key.public_key().public_bytes_raw()).hexdigest())
    print('Key stored locally. No trust registration or human signature created.')


def validate_storage():
    from .storage import provision_probe

    print(json.dumps(provision_probe(ROOT / 'immutable-artifacts')))


def main():
    local_guard()
    commands = {'prepare': prepare, 'init-db': init_db, 'pin-idp': pin_idp, 'bind-owner': bind_owner, 'validate-storage': validate_storage, 'create-producer-key': create_producer_key}
    require(len(sys.argv) == 2 and sys.argv[1] in {*commands, 'enroll', 'recover', 'hold', 'register-producer', 'revoke-producer'}, 'setup_command')
    if sys.argv[1] in commands:
        commands[sys.argv[1]]()
    else:
        from .runtime import load

        state = load(admin=True)
        try:
            if sys.argv[1] == 'hold':
                state.hold()
            elif sys.argv[1] == 'revoke-producer':
                revoke_producer(state)
            elif sys.argv[1] == 'register-producer':
                register_producer(state)
            else:
                code = ask('One-time local setup code from the freshly MFA-authenticated private owner page')
                state.activate(code, recovery=sys.argv[1] == 'recover')
                print('Readiness state activated; campaign authorization and all asset/model execution remain unavailable.')
        finally:
            state.checkpoint.close()


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, psycopg.Error, httpx.HTTPError, jwt.PyJWTError, InvalidToken, InvalidSignature):
        # No traceback/token/DSN/password/path in a terminal recording. Private state is retained fail-closed.
        print('Setup denied or incomplete. Keep state inactive; inspect protected local configuration.', file=sys.stderr)
        raise SystemExit(1) from None
