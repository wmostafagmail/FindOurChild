"""Separate private deployment OIDC adapter. Existing V1/V2 application identity is unchanged."""
import hashlib
import time
from uuid import NAMESPACE_URL, uuid5

import httpx
import jwt
from cryptography.hazmat.primitives import serialization

from tools.phase2e.owner_only_v3.identity import Binding, authenticate_token
from tools.phase2e.owner_only_v3.records import require


class Identity:
    def __init__(self, config, secrets, pin, *, transport=None):
        self.config, self.secrets, self.pin = config, secrets, pin
        self.transport = transport  # Explicit injected transport only in tests, never from HTTP/config.

    def request(self, path, data=None):
        require(path in {'/.well-known/openid-configuration', '/protocol/openid-connect/certs',
                        '/protocol/openid-connect/token', '/protocol/openid-connect/token/introspect'}, 'idp_fixed_path')
        with httpx.Client(verify=True, trust_env=False, timeout=5, follow_redirects=False,
                          transport=self.transport) as client, client.stream('GET' if data is None else 'POST', self.config['upstream'] + path,
                    data=None if data is None else {**data, 'client_id': self.config['client'],
                                                  'client_secret': self.secrets['client_secret']}) as response:
            response.raise_for_status()
            raw = bytearray()
            for block in response.iter_bytes(8192):
                raw.extend(block)
                require(len(raw) <= 65536, 'idp_response_bound')
            import json

            return json.loads(raw)

    def public_key(self, token):
        require(type(token) is str and len(token) <= 16384 and self.pin is not None, 'idp_pin_required')
        header = jwt.get_unverified_header(token)
        require(header.get('alg') == 'RS256' and type(header.get('kid')) is str
                and len(header['kid']) <= 256, 'idp_algorithm')
        require(self.pin['issuer'] == self.config['issuer'] and time.time() < self.pin['expires_at'], 'idp_pin_expired')
        rows = self.request('/protocol/openid-connect/certs')['keys']
        require(type(rows) is list and len(rows) <= 8, 'idp_key_inventory')
        found = [k for k in rows if k.get('kid') == header['kid'] and k.get('kty') == 'RSA' and k.get('use') == 'sig']
        require(len(found) == 1, 'idp_key_identity')
        key = jwt.PyJWK.from_dict(found[0]).key
        der = key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
        require(hashlib.sha256(der).hexdigest() in self.pin['spki_sha256'], 'idp_key_not_pinned')
        return key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)

    def owner(self, token, session, now, live):
        require(self.config['owner_subject'] is not None and now < self.config['binding_expires'], 'owner_binding_expired')
        binding = Binding(self.config['issuer'], 'foc-api', self.config['owner_subject'],
            str(uuid5(NAMESPACE_URL, self.config['issuer'] + '/' + self.config['owner_subject'])),
            self.public_key(token), token_audiences=tuple(self.config['audiences']))

        def current(b, value):
            active = self.request('/protocol/openid-connect/token/introspect', {'token': token})
            return active.get('active') is True and active.get('sub') == b.subject and live(value) is True

        return authenticate_token(token, binding, session, now, current)

    def id_token(self, token, nonce):
        row = jwt.decode(token, self.public_key(token), algorithms=['RS256'], audience=self.config['client'],
            issuer=self.config['issuer'], options={'require': ['exp', 'iat', 'sub', 'iss', 'aud', 'nonce', 'auth_time', 'amr']})
        require(row['nonce'] == nonce and row['sub'] == self.config['owner_subject'], 'id_token_binding')
        require(type(row['auth_time']) is int and 0 <= time.time() - row['auth_time'] <= 300
                and type(row['amr']) is list and all(type(v) is str for v in row['amr'])
                and {'pwd', 'otp'} <= set(row['amr']), 'id_token_mfa')
        return row
