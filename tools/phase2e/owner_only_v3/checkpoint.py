"""Existing, separately provisioned protected checkpoint journal. No bootstrap or enrollment.

Reserve before SQL commit; a crash leaves a mismatch and requires offline recovery.
Accepted host/owner trust remains: this is not protection from a malicious root host.
"""

import fcntl
import os
import stat
from contextlib import contextmanager

from .records import canonical, decode, digest, require


class Checkpoint:
    def __init__(self, directory_fd, *, owner=0):
        parent = os.fstat(directory_fd)
        require(stat.S_ISDIR(parent.st_mode) and parent.st_uid == owner and parent.st_mode & 0o022 == 0,
                "checkpoint_parent")
        self.fd = os.open("owner-only-v3.checkpoints", os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
                          dir_fd=directory_fd)
        row = os.fstat(self.fd)
        require(stat.S_ISREG(row.st_mode) and row.st_uid == owner and row.st_nlink == 1
                and row.st_mode & 0o077 == 0, "checkpoint_file")

    @contextmanager
    def locked(self):
        fcntl.flock(self.fd, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(self.fd, fcntl.LOCK_UN)

    def _read(self):
        length = os.fstat(self.fd).st_size
        require(0 < length <= 64 * 1024 * 1024, "checkpoint_size")
        raw = os.pread(self.fd, length, 0)
        require(len(raw) == length and raw.endswith(b"\n"), "checkpoint_partial")
        states, previous = {}, "0" * 64
        for line in raw.splitlines():
            row = decode(line)
            require(set(row) == {"instance", "previous", "state", "chain"}
                    and row["previous"] == previous, "checkpoint_chain")
            require(row["chain"] == digest({k: v for k, v in row.items() if k != "chain"}), "checkpoint_digest")
            state = row["state"]
            require(type(state) is list and len(state) == 4 and all(type(v) is int and v >= 0 for v in state[:3])
                    and type(state[3]) is str and len(state[3]) == 64, "checkpoint_state")
            states[row["instance"]] = tuple(state)
            previous = row["chain"]
        return states, previous

    def current(self, instance):
        with self.locked():
            states, _ = self._read()
            require(instance in states, "checkpoint_unprovisioned")
            return states[instance]

    def advance(self, instance, expected, new):
        with self.locked():
            states, previous = self._read()
            require(states.get(instance) == expected and new[:2] == expected[:2]
                    and new[2] == expected[2] + 1, "checkpoint_cas")
            self._append(instance, new, previous)

    def frozen(self, key):
        with self.locked():
            states, _ = self._read()
            state = states.get("freeze:" + key)
            return state[3] if state else None

    def seal(self, key, value_digest):
        with self.locked():
            states, previous = self._read()
            state = (0, 0, 0, value_digest)
            prior = states.get("freeze:" + key)
            require(prior is None or prior == state, "external_fixture_freeze")
            if prior is None:
                self._append("freeze:" + key, state, previous)

    def _append(self, instance, state, previous):
        row = {"instance": instance, "previous": previous, "state": list(state)}
        row["chain"] = digest(row)
        data = canonical(row) + b"\n"
        os.lseek(self.fd, 0, os.SEEK_END)
        while data:
            size = os.write(self.fd, data)
            require(size > 0, "checkpoint_write")
            data = data[size:]
        os.fsync(self.fd)

    def close(self):
        os.close(self.fd)
