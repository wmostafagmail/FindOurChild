"""CI-only generated deployment fixture preparation. Never imported by the deployed image."""
import base64
import hashlib
import json
import os
import re
import secrets
import sys
from pathlib import Path

from services.demo_deployment import cli
from services.demo_deployment.protected import create_private


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true' and os.geteuid() == 0
    plan = json.loads(Path(sys.argv[1]).read_text())
    root = Path(plan['directory'])
    assert root.parent == Path('/var/lib') and re.fullmatch('foc-deployment-ci-[a-f0-9]{32}', root.name)
    # Only generated test inputs, never an owner password, certificate or token.
    fixture_password, fixture_otp = secrets.token_urlsafe(24), base64.b32encode(secrets.token_bytes(20)).decode()
    answers = iter(['https://127.0.0.1:9443', 'https://127.0.0.1:9444/realms/foc-private-demo',
                    plan['cert'], plan['key'], plan['cert'], plan['key'], secrets.token_urlsafe(32),
                    'generatedadmin', secrets.token_urlsafe(32)])
    cli.ROOT = root
    cli.ask = lambda _: next(answers)
    cli.prepare()
    # Fixture enrollment is explicit test data. Production preparation always creates an empty realm.
    realm_path = root / 'idp/realm.json'
    realm = json.loads(realm_path.read_text())
    owner = '11000000-0000-4000-8000-000000000001'
    nonowner = '11000000-0000-4000-8000-000000000002'
    for uid, username in [(owner, 'generated-readiness-owner'), (nonowner, 'generated-readiness-nonowner')]:
        realm['users'].append({'id': uid, 'username': username, 'enabled': True, 'emailVerified': True,
            'firstName': 'Generated', 'lastName': 'CI fixture', 'email': username + '@synthetic.invalid',
            'credentials': [{'type': 'password', 'value': fixture_password, 'temporary': False},
                {'type': 'otp', 'secretData': json.dumps({'value': fixture_otp}),
                 'credentialData': json.dumps({'subType': 'totp', 'digits': 6, 'counter': 0,
                      'period': 30, 'algorithm': 'HmacSHA1', 'secretEncoding': 'BASE32'})}]})
    realm_path.write_text(json.dumps(realm));realm_path.chmod(0o600)
    config = json.loads((root / 'runtime/config.json').read_text())
    from tools.phase2e.owner_only_v3.records import digest

    create_private(root / 'runtime/binding.json', {'subject': owner, 'config_digest': digest(config)}, owner=10001)
    credentials = Path(plan['credentials'])
    credentials.write_text(json.dumps({'password': fixture_password, 'otp': fixture_otp,
                                      'data_class': 'generated_ci_only_not_real_owner'}))
    credentials.chmod(0o600);os.chown(credentials, plan['runner_uid'], plan['runner_uid'])
    # Install a root-only machine key fixture; no key is trusted until the actual enrollment path is tested.
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    key = Ed25519PrivateKey.generate()
    create_private(root / 'producer-secrets/source.json', {'private_key': base64.b64encode(key.private_bytes_raw()).decode()})
    public = hashlib.sha256(key.public_key().public_bytes_raw()).hexdigest()
    result = Path(plan['public'])
    result.write_text(json.dumps({'machine_fingerprint': public, 'owner': owner, 'nonowner': nonowner,
                                 'real_owner_provisioning': False}))
    os.chown(result, plan['runner_uid'], plan['runner_uid'])


if __name__ == '__main__':
    main()
