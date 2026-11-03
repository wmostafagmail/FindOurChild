"""Root/instance-owned bounded records. No tokens/keys in command arguments or logs."""
import json
import os
import stat
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID

from tools.phase2e.owner_only_v3.records import canonical, require

DOMAIN = 'FOC-PHASE2E-DEPLOYMENT-READINESS-V1'
ROOT = Path('/var/lib/findourchild-demo')


def read_private(path, *, owner, maximum=65536):
    """Traverse each directory by FD; refuse symlinks, writable ancestors and aliases."""
    path = Path(path)
    require(path.is_absolute() and '..' not in path.parts, 'protected_path')
    directory = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:-1]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = next_fd
            st = os.fstat(directory)
            require(st.st_uid in (0, owner) and st.st_mode & 0o022 == 0, 'protected_ancestor')
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        try:
            st = os.fstat(fd)
            require(stat.S_ISREG(st.st_mode) and st.st_uid == owner and st.st_nlink == 1
                    and st.st_mode & 0o077 == 0 and 0 < st.st_size <= maximum, 'protected_file')
            data = os.read(fd, maximum + 1)
            require(len(data) == st.st_size, 'protected_size')
            return json.loads(data)
        finally:
            os.close(fd)
    finally:
        os.close(directory)


def create_private(path, value, *, owner=None):
    """No replacement. Parent must be separately provisioned and trusted."""
    path = Path(path)
    parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        st = os.fstat(parent)
        require(st.st_uid in (os.geteuid(), owner) and st.st_mode & 0o077 == 0, 'private_parent')
        fd = os.open(path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        try:
            data = canonical(value)
            while data:
                size = os.write(fd, data)
                require(size > 0, 'private_write')
                data = data[size:]
            if owner is not None:
                os.fchown(fd, owner, owner)
            os.fsync(fd)
        finally:
            os.close(fd)
        os.fsync(parent)
    finally:
        os.close(parent)


def https_origin(value):
    require(type(value) is str and len(value) <= 256, 'origin_type')
    u = urlsplit(value)
    require(u.scheme == 'https' and u.hostname and not u.username and not u.password
            and not u.query and not u.fragment and u.path in ('', '/') and value == value.rstrip('/'), 'https_origin')
    require(u.netloc == u.netloc.lower(), 'origin_canonical')
    return value


def configuration(row):
    expected = {'domain', 'instance', 'tenant', 'origin', 'issuer', 'upstream', 'client', 'audiences',
                'owner_subject', 'source_sha', 'binding_expires', 'data_class'}
    require(type(row) is dict and set(row) == expected and row['domain'] == DOMAIN, 'deployment_closed')
    require(row['data_class'] == 'fictional_demo_only', 'demo_data_only')
    https_origin(row['origin'])
    u = urlsplit(row['issuer'])
    require(u.scheme == 'https' and u.hostname and not u.username and not u.password
            and not u.query and not u.fragment and u.path == '/realms/foc-private-demo', 'issuer_pinned_path')
    require(row['upstream'] in (row['issuer'], 'http://idp:8080/realms/foc-private-demo'), 'fixed_upstream')
    require(row['client'] == 'foc-bff' and row['audiences'] == ['foc-api', 'foc-bff'], 'fixed_audiences')
    for key in ['instance', 'tenant']:
        require(type(row[key]) is str and str(UUID(row[key])) == row[key], 'deployment_uuid')
    require(row['owner_subject'] is None or type(row['owner_subject']) is str
            and 0 < len(row['owner_subject']) <= 256, 'owner_subject_type')
    require(type(row['binding_expires']) is int and row['binding_expires'] > 0, 'binding_expiry_type')
    require(type(row['source_sha']) is str and len(row['source_sha']) == 40
            and all(c in '0123456789abcdef' for c in row['source_sha']), 'deployment_source')
    return row
