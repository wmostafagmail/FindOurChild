"""Protected readiness bootstrap/recovery. Campaign creation and asset execution are absent."""
import hmac
import json
import re
import secrets
from contextlib import contextmanager

import psycopg
from cryptography.fernet import Fernet
from psycopg.types.json import Jsonb

from tools.phase2e.owner_only_v3.confirmation import Clock
from tools.phase2e.owner_only_v3.records import digest, require, sha
from tools.phase2e.owner_only_v3.store import Store


class State:
    def __init__(self, config, private, checkpoint, identity):
        self.config, self.private, self.checkpoint, self.identity = config, private, checkpoint, identity
        self.cipher = Fernet(private['session_key'].encode())
        self.clock = Clock()

    def now(self):
        return self.clock.now()

    @contextmanager
    def connect(self, *, admin=False):
        url = self.private['admin_url' if admin else 'runtime_url']
        with psycopg.connect(url, connect_timeout=3) as conn:
            conn.execute("SET LOCAL statement_timeout='5s'")
            conn.execute("SET LOCAL lock_timeout='3s'")
            if not admin:
                require(conn.execute('SELECT rolsuper,rolbypassrls FROM pg_roles WHERE rolname=current_user').fetchone()
                        == (False, False), 'private_runtime_role')
            conn.execute("SELECT set_config('foc.v3_instance',%s,true)", (self.config['instance'],))
            conn.execute("SELECT set_config('foc.v3_tenant',%s,true)", (self.config['tenant'],))
            yield conn

    def _live(self, conn, session):
        r = conn.execute('SELECT expires,revoked,activation_epoch,authority_epoch FROM owner_deployment.sessions WHERE key=%s',
                         (sha(session.encode()),)).fetchone()
        epochs = self.checkpoint.current(self.config['instance'])[:2]
        return r is not None and r[0] > self.now() and r[1] is False and tuple(r[2:]) == epochs

    def live(self, session):
        with self.connect() as conn:
            return self._live(conn, session)

    def session(self, session):
        require(type(session) is str and len(session) == 43, 'deployment_session')
        with self.connect() as conn:
            row = conn.execute('SELECT encrypted_token,csrf FROM owner_deployment.sessions WHERE key=%s',
                               (sha(session.encode()),)).fetchone()
        require(row is not None and self.live(session), 'deployment_session_current')
        payload = json.loads(self.cipher.decrypt(row[0].encode(), ttl=1800))
        require(hmac.compare_digest(payload['session'], session), 'session_payload_binding')
        token = payload['token']
        owner = self.identity.owner(token, session, self.now(), self.live)
        return owner, row[1]

    def new_session(self, token):
        session, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        # Verify actual pinned JWT + fresh MFA + live IdP before creating a platform session.
        owner = self.identity.owner(token, session, self.now(), lambda _: True)
        epochs = self.checkpoint.current(self.config['instance'])[:2]
        with self.connect() as conn:
            conn.execute('INSERT INTO owner_deployment.sessions(instance,tenant,key,encrypted_token,csrf,expires,activation_epoch,authority_epoch) '
                         'VALUES(%s,%s,%s,%s,%s,%s,%s,%s)', (self.config['instance'], self.config['tenant'],
                         sha(session.encode()), self.cipher.encrypt(json.dumps({'token': token, 'session': session}).encode()).decode(), sha(csrf.encode()),
                         min(owner.expires_at, int(self.now()) + 1800), *epochs))
        return session, csrf

    def proof(self, session):
        self.session(session)
        code = secrets.token_hex(32)
        with self.connect() as conn:
            conn.execute('INSERT INTO owner_deployment.proofs(instance,tenant,key,session_key,config_digest,expires) '
                         'VALUES(%s,%s,%s,%s,%s,%s)', (self.config['instance'], self.config['tenant'], sha(code.encode()),
                         sha(session.encode()), digest(self.config), int(self.now()) + 300))
        return code

    def _proof(self, conn, code):
        require(type(code) is str and re.fullmatch('[a-f0-9]{64}', code), 'owner_proof_encoding')
        key = sha(code.encode())
        row = conn.execute('SELECT p.session_key,p.config_digest,p.expires,p.consumed,s.encrypted_token,s.revoked,s.expires '
            'FROM owner_deployment.proofs p JOIN owner_deployment.sessions s ON s.key=p.session_key '
            'WHERE p.key=%s AND p.instance=%s AND p.tenant=%s FOR UPDATE OF p,s',
            (key, self.config['instance'], self.config['tenant'])).fetchone()
        require(row is not None and row[1] == digest(self.config) and row[2] > self.now()
                and row[3] is False and row[5] is False and row[6] > self.now(), 'owner_proof_stale')
        payload = json.loads(self.cipher.decrypt(row[4].encode(), ttl=1800))
        require(sha(payload['session'].encode()) == row[0], 'proof_session_binding')
        self.identity.owner(payload['token'], payload['session'], self.now(), self.live)
        tombstone = 'owner-proof:' + key
        require(self.checkpoint.frozen(tombstone) is None, 'owner_proof_replay')
        self.checkpoint.seal(tombstone, digest({'config': digest(self.config), 'proof': key}))
        conn.execute('UPDATE owner_deployment.proofs SET consumed=true WHERE key=%s', (key,))
        return payload['token'], payload['session']

    def _authority(self, conn):
        rows = conn.execute('SELECT instance,tenant,enabled,activation_epoch,authority_epoch,revision,checkpoint '
                            'FROM owner_only_demo.authority FOR UPDATE').fetchall()
        require(len(rows) == 1 and str(rows[0][0]) == self.config['instance']
                and str(rows[0][1]) == self.config['tenant'], 'one_private_deployment')
        return rows[0]

    def activate(self, code, *, recovery=False):
        """Privileged local CLI only; a real fresh owner proof is necessary. No HTTP enable route."""
        with self.connect(admin=True) as conn:
            row = self._authority(conn)
            require(row[2] is False, 'already_enrolled_or_active')
            proof_token, proof_session = self._proof(conn, code)
            ext = self.checkpoint.current(self.config['instance'])
            if recovery:
                # Neither missing external seals nor a rolled-back DB can erase fixture history.
                exposure = dict(conn.execute('SELECT key,digest FROM owner_only_demo.fixture_exposure').fetchall())
                with self.checkpoint.locked():
                    states, _ = self.checkpoint._read()
                external = {k[7:]: v[3] for k, v in states.items() if re.fullmatch('freeze:[a-f0-9]{64}', k)}
                require(exposure == external, 'restore_fixture_history_missing')
            else:
                require(tuple(row[3:]) == ext and ext[:3] == (1, 1, 0), 'bootstrap_state_mismatch')
            new = (max(row[3], ext[0]) + 1, max(row[4], ext[1]) + 1, ext[2] + 1,
                   digest({'previous': ext[3], 'action': 'recover' if recovery else 'enroll',
                           'config': digest(self.config)}))
            # External-first reservation: SQL crash/mismatch denies; never roll back the external record.
            with self.checkpoint.locked():
                states, previous = self.checkpoint._read()
                require(states[self.config['instance']] == ext, 'admin_checkpoint_race')
                self.checkpoint._append(self.config['instance'], new, previous)
            conn.execute('UPDATE owner_only_demo.authority SET enabled=true,activation_epoch=%s,authority_epoch=%s,'
                         'revision=%s,checkpoint=%s WHERE instance=%s', (*new, self.config['instance']))
            conn.execute('UPDATE owner_deployment.sessions SET revoked=true WHERE key<>%s', (sha(proof_session.encode()),))
            conn.execute('UPDATE owner_deployment.sessions SET activation_epoch=%s,authority_epoch=%s WHERE key=%s',
                         (*new[:2], sha(proof_session.encode())))
            self._admin_audit(conn, 'deployment_recovered' if recovery else 'owner_enrolled_readiness_only', new)
            self.identity.owner(proof_token, proof_session, self.now(), lambda value: self._live(conn, value))

    def hold(self):
        # External-first epoch reservation prevents a restored DB from reviving revoked sessions.
        with self.connect(admin=True) as conn:
            self._authority(conn)
            old = self.checkpoint.current(self.config['instance'])
            new = (old[0] + 1, old[1] + 1, old[2] + 1,
                   digest({'previous': old[3], 'action': 'hold', 'config': digest(self.config)}))
            with self.checkpoint.locked():
                states, previous = self.checkpoint._read()
                require(states[self.config['instance']] == old, 'hold_checkpoint_race')
                self.checkpoint._append(self.config['instance'], new, previous)
            conn.execute('UPDATE owner_only_demo.authority SET enabled=false,activation_epoch=%s,authority_epoch=%s,'
                         'revision=%s,checkpoint=%s', new)
            conn.execute('UPDATE owner_deployment.sessions SET revoked=true')
            self._admin_audit(conn, 'deployment_held_all_sessions_revoked', new)

    def registry_current(self, head, epochs):
        with self.connect() as conn:
            row = conn.execute('SELECT config_digest,activation_epoch,authority_epoch FROM owner_deployment.registry_commits '
                               'WHERE key=%s', (head,)).fetchone()
        return row is not None and row[0] == digest(self.config) and tuple(row[1:]) == tuple(epochs)

    def _admin_audit(self, conn, action, state):
        value = {'action': action, 'scope': 'readiness_only_no_campaign', 'config': digest(self.config),
                 'state': list(state) if state else None}
        conn.execute('INSERT INTO owner_only_demo.journal(instance,tenant,kind,key,value,digest) VALUES(%s,%s,%s,%s,%s,%s)',
            (self.config['instance'], self.config['tenant'], 'event', secrets.token_hex(16), Jsonb(value), digest(value)))

    def readiness(self, session):
        owner, _ = self.session(session)
        with self.connect() as conn:
            row = conn.execute('SELECT enabled,activation_epoch,authority_epoch FROM owner_only_demo.authority '
                               'WHERE instance=%s AND tenant=%s',
                               (self.config['instance'], self.config['tenant'])).fetchone()
            campaigns=conn.execute("SELECT count(*) FROM owner_only_demo.journal WHERE kind='authorization'").fetchone()[0]
        require(row is not None and row[0] is True, 'deployment_inactive')
        require(campaigns==0,'unexpected_campaign_in_readiness_store')
        store = Store(self.private['runtime_url'], self.config['instance'], self.config['tenant'], self.checkpoint)
        with store.transaction(row[1], row[2]) as tx:
            tx.audit('deployment_readiness_read', digest(self.config))
            require(self.live(session), 'owner_session_revoked_during_audit')
        return {'readiness_only': True, 'owner_binding_verified': True, 'owner_event': owner.authentication_event_id,
                'activation_epoch': row[1], 'authority_epoch': row[2], 'campaign_authorizations': campaigns,
                'acquisition_enabled': False, 'unpacking_enabled': False, 'model_parsing_enabled': False,
                'inference_enabled': False, 'operational_enabled': False}
