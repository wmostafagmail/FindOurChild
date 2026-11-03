"""Pinned Linux/amd64 private demo topology. No model artifacts or Docker socket in API/worker."""
from pathlib import Path

PYTHON = 'python:3.13.13-slim-bookworm@sha256:355bfa66770995d7e9a0da4b3473b44d0cb451f6b56f5615ad9c39e3c4eca03f'
POSTGRES = 'pgvector/pgvector:0.8.7-pg17-bookworm@sha256:ac08538c6f8b9904c33c8224c5e5706dbe760aca29db1d096972b4052c22a75d'
KEYCLOAK = 'quay.io/keycloak/keycloak:26.7.0@sha256:0f198be292568439d700cdbfb893e69a6009bb43a94a06a945b1d3d506c76b13'


def topology(config, *, source, root):
    source, root = Path(source), Path(root)
    common = {'platform': 'linux/amd64', 'read_only': True, 'cap_drop': ['ALL'],
              'security_opt': ['no-new-privileges:true'], 'pids_limit': 128, 'cpus': 1,
              'logging': {'driver': 'local', 'options': {'max-size': '2m', 'max-file': '2'}}}

    def mount(folder, target, *, ro=True):
        return {'type': 'bind', 'source': str(root / folder), 'target': target, 'read_only': ro,
                'bind': {'create_host_path': False}}

    def db(name, network):
        return {**common, 'image': POSTGRES, 'user': '999:999', 'mem_limit': '512m', 'memswap_limit': '512m',
            'environment': {'POSTGRES_PASSWORD_FILE': '/run/password', 'POSTGRES_DB': 'postgres'},
            'volumes': [mount(name + '/password', '/run/password'),
                        mount(name + '/data', '/var/lib/postgresql/data', ro=False)],
            'tmpfs': ['/tmp:rw,nosuid,nodev,noexec,size=16m', '/var/run/postgresql:rw,nosuid,nodev,noexec,size=1m,uid=999'],
            'networks': [network], 'healthcheck': {'test': ['CMD', 'pg_isready', '-U', 'postgres'],
                'interval': '2s', 'timeout': '2s', 'retries': 30}}
    build = {'context': str(source), 'dockerfile': 'deployment/private-demo/Dockerfile',
             'args': {'SOURCE_SHA': config['source_sha']}}
    api_volumes = [mount('runtime', '/var/lib/findourchild-demo/runtime'),
                   mount('checkpoint', '/var/lib/findourchild-demo/checkpoint', ro=False),
                   mount('quarantine', '/var/lib/findourchild-demo/quarantine'),
                   mount('tls/app', '/run/tls')]
    app = {**common, 'build': build, 'image': 'foc-private-readiness:' + config['source_sha'],
           'user': '10001:10001', 'mem_limit': '256m', 'memswap_limit': '256m',
           'command': ['python', '-m', 'uvicorn', 'services.demo_deployment.app:app', '--factory',
                       '--host', '0.0.0.0', '--port', '8443', '--ssl-certfile', '/run/tls/cert.pem',
                       '--ssl-keyfile', '/run/tls/key.pem', '--no-access-log', '--log-level', 'critical'],
           'ports': ['127.0.0.1:' + str(__import__('urllib.parse', fromlist=['urlsplit']).urlsplit(config['origin']).port or 443) + ':8443'],
           'volumes': api_volumes, 'tmpfs': ['/tmp:rw,nosuid,nodev,noexec,size=8m'],
           'networks': ['edge', 'control', 'identity'], 'depends_on': {'db': {'condition': 'service_healthy'}}}
    idp_port = __import__('urllib.parse', fromlist=['urlsplit']).urlsplit(config['issuer']).port or 443
    idp = {**common, 'image': 'foc-private-idp:' + config['source_sha'],
        'build': {'context': str(source), 'dockerfile': 'deployment/private-demo/Keycloak.Dockerfile'}, 'user': '1000:1000', 'mem_limit': '1g', 'memswap_limit': '1g',
        'cpus': 2, 'entrypoint': ['/bin/bash', '/run/entrypoint.sh'],
        'environment': {'KC_HOSTNAME': config['issuer'].split('/realms/')[0], 'KC_HOSTNAME_STRICT': 'true',
                        'KC_DB': 'postgres', 'KC_DB_URL': 'jdbc:postgresql://idp-db:5432/keycloak',
                        'KC_DB_USERNAME': 'keycloak', 'KC_HTTP_ENABLED': 'true',
                        'KC_HTTPS_CERTIFICATE_FILE': '/run/tls/cert.pem', 'KC_HTTPS_CERTIFICATE_KEY_FILE': '/run/tls/key.pem'},
        'ports': [f'127.0.0.1:{idp_port}:8443'],
        'volumes': [mount('idp/entrypoint.sh', '/run/entrypoint.sh'), mount('idp/secrets.json', '/run/idp-secrets.json'),
                    mount('idp/keycloak.conf', '/opt/keycloak/conf/keycloak.conf'),
                    mount('idp/realm.json', '/opt/keycloak/data/import/realm.json'),
                    mount('tls/idp', '/run/tls'), mount('idp/data', '/opt/keycloak/data', ro=False)],
        'tmpfs': ['/tmp:rw,nosuid,nodev,noexec,size=64m'], 'networks': ['edge', 'identity'],
        'depends_on': {'idp-db': {'condition': 'service_healthy'}}}
    # Secrets are read by kc.sh from protected config, never embedded in Compose or argv.
    admin = {**common, 'image': app['image'], 'build': build, 'user': '0:0',
        'cap_add': ['DAC_OVERRIDE', 'CHOWN', 'FOWNER'], 'profiles': ['setup'],
        'stdin_open': True, 'tty': True, 'entrypoint': ['python', '-m', 'services.demo_deployment.cli'],
        'volumes': [mount('.', '/var/lib/findourchild-demo', ro=False)],
        'networks': ['control', 'identity'], 'mem_limit': '256m', 'memswap_limit': '256m',
        'tmpfs': ['/tmp:rw,nosuid,nodev,noexec,size=8m']}
    worker = {**common, 'image': 'foc-private-benign-worker:' + config['source_sha'],
        'build': {'context': str(source / 'services/demo_governance')}, 'profiles': ['benign-validation'],
        'user': '10001:10001', 'network_mode': 'none', 'mem_limit': '128m', 'memswap_limit': '128m',
        'pids_limit': 32, 'command': ['ok'], 'tmpfs': ['/tmp:rw,noexec,nosuid,nodev,size=1m,mode=1777']}
    return {'name': 'foc-private-demo', 'services': {'db': db('database', 'control'),
            'idp-db': db('identity-database', 'identity'), 'idp': idp, 'api': app, 'admin': admin, 'worker': worker},
            'networks': {'edge': {}, 'control': {'internal': True}, 'identity': {'internal': True}}}
