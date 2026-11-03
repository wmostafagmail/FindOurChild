import hashlib
import html
import json
import re
import ssl
import subprocess
from pathlib import Path

import httpx

BASE = 'https://127.0.0.1:9443'


def private():
    return json.loads(Path('.runtime/deployment-fixture/context.json').read_text())


def command(*args, data=None, timeout=60):
    p = subprocess.run(list(args), input=data, capture_output=True, timeout=timeout, check=False)
    if p.returncode:
        # Raw outputs remain private; exceptions contain no DSN/token/secret.
        Path('artifacts/raw/deployment').mkdir(parents=True, exist_ok=True)
        Path('artifacts/raw/deployment/last-command.log').write_bytes(p.stdout + p.stderr)
        raw=p.stdout+p.stderr
        codes=re.findall(rb'(?:Denied|PermissionError|OperationalError|InvalidTextRepresentation|UndefinedTable|SyntaxError|AssertionError): ([a-z_]{1,64})(?:\r?\n|$)',raw)
        diagnostic={'command':args[0],'exit':p.returncode,'private_sha256':hashlib.sha256(raw).hexdigest(),
                    'fixed_codes':[v.decode() for v in codes]}
        print(json.dumps({'private_command_failure':diagnostic}))
        raise RuntimeError('Private deployment test command failed; diagnostic retained privately')
    return p.stdout


def compose(*args):
    return command('docker', 'compose', '-f', private()['compose'], *args, timeout=120)


def admin(code, *arguments, data=None):
    # Source-only generated CI fixture invokes the same protected implementation, not the interactive human CLI.
    args = ['docker', 'compose', '-f', private()['compose'], 'run', '--rm', '--no-TTY', '--entrypoint', 'python', 'admin',
            '-c', code, *arguments]
    return command(*args, data=data, timeout=120)


def client():
    return httpx.Client(follow_redirects=False, timeout=30, trust_env=False,
                       verify=ssl.create_default_context(cafile='.runtime/tls/cert.pem'))


def login(username='generated-readiness-owner'):
    c = client()
    r = c.get(BASE + '/owner/login');assert r.status_code == 302
    r = c.get(r.headers['location'])

    def action(response):
        return html.unescape(re.search(r'<form[^>]*action="([^"]+)"', response.text)[1])

    credential = command('.venv/bin/python', '-m', 'scripts.deployment_credentials', 'password').decode().strip()
    r = c.post(action(r), data={'username': username, 'password': credential})
    assert 'id="otp"' in r.text
    value = command('.venv/bin/python', '-m', 'scripts.deployment_credentials', 'otp').decode().strip()
    r = c.post(action(r), data={'otp': value});assert r.status_code == 302
    callback = c.get(r.headers['location'])
    return c, callback


def headers(c):
    return {'origin': BASE, 'x-csrf-token': c.cookies['__Host-foc-demo-csrf'], 'content-type': 'application/json'}


def proof(c):
    r = c.post(BASE + '/owner/enrollment-proof', headers=headers(c), content=b'{}')
    assert r.status_code == 200
    return r.json()['local_setup_code']
