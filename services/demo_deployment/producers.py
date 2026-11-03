"""Local-admin machine producer registry, separate from V2 human approval keys."""
import base64
import os
import stat
import time

from tools.phase2e.owner_only_v3.receipts import Producer, Verifier
from tools.phase2e.owner_only_v3.records import canonical, decode, digest, require

REGISTRY = 'FOC-DEPLOYMENT-TECHNICAL-PRODUCERS-V1'
STAGES = {'source', 'quarantine', 'bytes', 'processed', 'load'}


def read_registry(fd, checkpoint, config):
    st = os.fstat(fd)
    require(stat.S_ISREG(st.st_mode) and 0 <= st.st_size <= 65536 and st.st_nlink == 1 and st.st_mode & 0o077 == 0, 'registry_file')
    raw = os.pread(fd, st.st_size, 0)
    require(not raw or raw.endswith(b'\n'), 'registry_partial')
    rows, previous = {}, '0' * 64
    for number, line in enumerate(raw.splitlines(), 1):
        row = decode(line)
        require(set(row) == {'domain', 'config', 'name', 'producer', 'revoked', 'expires', 'epoch', 'previous', 'chain'}
                and row['domain'] == REGISTRY and row['config'] == digest(config)
                and row['previous'] == previous and row['chain'] == digest({k: v for k, v in row.items() if k != 'chain'}),
                'registry_chain')
        require(type(row['name']) is str and row['name'] in STAGES and type(row['revoked']) is bool
                and type(row['expires']) is int and type(row['epoch']) is list and len(row['epoch']) == 2,
                'registry_closed')
        p = row['producer']
        require(set(p) == {'public_key', 'source', 'build', 'tool', 'evidence_class', 'resource_limits', 'stages'}
                and p['evidence_class'] == 'actual_isolated_measurement'
                and type(p['stages']) is list and set(p['stages']) <= STAGES and p['stages'], 'producer_scope')
        for field in ['source', 'build', 'tool']:
            require(type(p[field]) is str and len(p[field]) == 64
                    and all(c in '0123456789abcdef' for c in p[field]), 'producer_digest')
        require(p['resource_limits'] == [3000, 2000, 67108864], 'readiness_profile_only')
        require(len(base64.b64decode(p['public_key'], validate=True)) == 32, 'producer_key')
        previous = row['chain']
        rows[row['name']] = row
    expected = checkpoint.current('producer-registry:' + config['instance'])
    require(expected[2:] == (len(raw.splitlines()), previous), 'registry_rollback')
    return rows, expected


class Producers:
    def __init__(self, fd, checkpoint, config, committed):
        self.fd, self.checkpoint, self.config = fd, checkpoint, config
        self.committed = committed

    def verify(self, raw, signature, *, epochs, **kwargs):
        rows, state = read_registry(self.fd, self.checkpoint, self.config)
        value = decode(raw)
        name = value.get('producer')
        require(name in rows and state[:2] == tuple(epochs)
                and self.committed(state[3], epochs) is True, 'producer_epoch_or_uncommitted')
        row, now = rows[name], time.time()
        require(not row['revoked'] and now < row['expires'] and row['epoch'] == list(epochs), 'producer_revoked_or_expired')
        p = row['producer']
        require(value.get('stage') in p['stages'], 'producer_stage')
        producer = Producer(base64.b64decode(p['public_key'], validate=True), p['source'], p['build'], p['tool'],
                            p['evidence_class'], tuple(p['resource_limits']))
        return Verifier({name: producer}).verify(raw, signature, **kwargs)


def append_registry(fd, checkpoint, config, name, producer, *, revoked, expires, epochs):
    """Invoked only inside a root-admin transaction after a consumed real-owner proof."""
    rows, old = read_registry(fd, checkpoint, config)
    require(name in STAGES and type(revoked) is bool and type(expires) is int
            and 0 < expires - time.time() <= 86400 and tuple(epochs) == old[:2], 'producer_registration')
    if revoked:
        require(name in rows and producer == rows[name]['producer'], 'revoke_existing_producer')
    row = {'domain': REGISTRY, 'config': digest(config), 'name': name, 'producer': producer, 'revoked': revoked,
           'expires': expires, 'epoch': list(epochs), 'previous': old[3]}
    row['chain'] = digest(row)
    data = canonical(row) + b'\n'
    require(os.fstat(fd).st_size + len(data) <= 65536, 'registry_capacity')
    with checkpoint.locked():
        states, previous = checkpoint._read()
        key = 'producer-registry:' + config['instance']
        require(states[key] == old, 'registry_cas')
        checkpoint._append(key, (*epochs, old[2] + 1, row['chain']), previous)
    os.lseek(fd, 0, os.SEEK_END)
    while data:
        size = os.write(fd, data)
        require(size > 0, 'registry_write')
        data = data[size:]
    os.fsync(fd)
    return row['chain']
