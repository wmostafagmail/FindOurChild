"""Closed immutable artifact projection. Benign source-only tests; no acquisition.

A Linux sealed memfd, not a hash of a mutable file, is the parser handoff.
Unsupported sealing denies. Actual model identities remain unprovisioned.
"""

import fcntl
import hashlib
import json
import os
import stat
from contextlib import contextmanager
from pathlib import Path

from .records import canonical, digest, require, sha

MAX_BYTES = 64 * 1024 * 1024  # engineering cap, NOT an approved model unpack bound
SEALS = 0x0001 | 0x0002 | 0x0004 | 0x0008  # SEAL, SHRINK, GROW, WRITE
COMPONENTS = {"cnn_detector", "five_point_predictor", "resnet_128_encoder"}


def locked_inventory(rows, expected):
    require(type(rows) is list and len(rows) == len(expected) == 51, "closed_inventory")
    require(
        all(type(x) is dict and set(x) == {"source", "size", "sha256", "git_blob"} for x in rows),
        "inventory_fields",
    )
    names = [x["source"] for x in rows]
    require(len(set(names)) == 51 and set(names) == set(expected), "inventory_membership")
    require(all(x == expected[x["source"]] for x in rows), "inventory_identity")
    for row in rows:
        require(
            type(row["size"]) is int and 0 < row["size"] <= MAX_BYTES and sha(row["sha256"]),
            "inventory_identity",
        )
    return digest(canonical(rows))


def verify_build(files, expected):
    require(
        set(files) == set(expected)
        and {"wheel", "extension", "test_binary", "sbom", "compiler", "source"} <= set(files),
        "build_inventory",
    )
    for kind, data in files.items():
        require(type(data) is bytes and digest(data) == expected[kind], "build_integrity")
    require(
        b"scan_fhog_pyramid" not in files["source"] and b"python_bindings" not in files["source"],
        "source_exclusion",
    )
    return digest(canonical(expected))


def _safe_open(path, owner):
    path = Path(path)
    require(path.is_absolute() and ".." not in path.parts, "absolute_fixed_path")
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for part in path.parts[1:-1]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
            os.close(fd)
            fd = next_fd
            st = os.fstat(fd)
            require(st.st_uid == owner and st.st_mode & 0o022 == 0, "parent_permissions")
        result = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=fd)
    finally:
        os.close(fd)
    st = os.fstat(result)
    try:
        require(
            stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and st.st_uid == owner and st.st_mode & 0o222 == 0,
            "artifact_permissions",
        )
    except BaseException:
        os.close(result)
        raise
    return result


def _identity(st):
    return st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns


@contextmanager
def snapshot_fd(source_fd, *, size, sha256, copy_observer=None):
    """Caller owns source-FD provenance. Parser receives ONLY sealed result.

    fstat before/after copy rejects observed races. Post-seal digest is decisive
    even when an attacker changes and restores timestamps. Privileged kernel/
    host compromise remains outside this boundary.
    """
    require(type(size) is int and 0 < size <= MAX_BYTES and sha(sha256), "snapshot_identity")
    require(hasattr(os, "memfd_create"), "sealing_unavailable")
    before = os.fstat(source_fd)
    require(stat.S_ISREG(before.st_mode) and before.st_size == size, "snapshot_size")
    fd = os.memfd_create("foc-demo-immutable", os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
    try:
        position = 0
        while position < size:
            block = os.pread(source_fd, min(65536, size - position), position)
            require(block, "snapshot_truncated")
            view = memoryview(block)
            while view:
                n = os.write(fd, view)
                require(n > 0, "snapshot_write")
                view = view[n:]
            position += len(block)
            if copy_observer:
                copy_observer(position)
        require(_identity(before) == _identity(os.fstat(source_fd)), "snapshot_race")
        fcntl.fcntl(fd, fcntl.F_ADD_SEALS, SEALS)
        require(fcntl.fcntl(fd, fcntl.F_GET_SEALS) & SEALS == SEALS, "sealing_failed")
        h = hashlib.sha256()
        for position in range(0, size, 65536):
            h.update(os.pread(fd, min(65536, size - position), position))
        require(os.fstat(fd).st_size == size and h.hexdigest() == sha256, "snapshot_digest")
        os.lseek(fd, 0, os.SEEK_SET)
        yield fd
    finally:
        os.close(fd)


class ArtifactRegistry:
    """Privileged provisioner supplies fixed projection once, never a browser.

    There is no downloader, decompressor, scanner, image decoder or model parser
    in this class. A read cannot mint authority; callers need a current chain.
    """

    def __init__(self, directory, manifest, *, owner=0):
        self.directory, self.manifest, self.owner = Path(directory), manifest, owner
        require(set(manifest) == COMPONENTS, "fixed_components")
        require(
            all(
                set(x) == {"size", "sha256", "build", "space"} and sha(x["sha256"]) and sha(x["build"])
                for x in manifest.values()
            ),
            "closed_component_manifest",
        )

    @contextmanager
    def open(self, component, *, build, space, authority):
        require(component in COMPONENTS and authority is True, "artifact_authority")
        row = self.manifest[component]
        require(row["build"] == build and row["space"] == space, "artifact_space")
        # Paths cannot be selected by an untrusted request, nor by the manifest.
        fd = _safe_open(self.directory / component, self.owner)
        try:
            with snapshot_fd(fd, size=row["size"], sha256=row["sha256"]) as sealed:
                yield sealed
        finally:
            os.close(fd)


def disabled_assets():
    config = json.loads(
        (Path(__file__).resolve().parents[3] / "config/phase2e/demo-governance.json").read_text()
    )
    require(config["provisioning_enabled"] is True, "provisioning_disabled")
    require(False, "actual_artifact_identities_unprovisioned")


def processing_receipt(receipt, expected, now):
    """Validate exact technical receipt; no scanner/decode execution or approval.

    The authenticated review record binds the digest of this entire receipt.
    An arbitrary receipt without that signature is never processing authority.
    """
    from .records import time_value

    require(
        set(receipt)
        == {
            "source",
            "derivative",
            "scanner",
            "definitions_expires",
            "scan_status",
            "decoder",
            "format",
            "pixels",
            "decode_status",
            "permission_epoch",
        },
        "receipt_fields",
    )
    require(
        set(expected) == {"source", "derivative", "scanner", "decoder", "permission_epoch"}, "receipt_binding"
    )
    require(all(receipt[k] == v for k, v in expected.items()), "lineage")
    require(all(sha(receipt[k]) for k in ["source", "derivative", "scanner", "decoder"]), "lineage_digest")
    require(
        receipt["scan_status"] == "clean" and time_value(receipt["definitions_expires"]) > now, "scan_failed"
    )
    require(
        receipt["decode_status"] == "clean"
        and receipt["format"] == "PNG"
        and type(receipt["pixels"]) is int
        and 0 < receipt["pixels"] <= 4096 * 4096,
        "decode_failed",
    )
    return digest(canonical(receipt))


def install_snapshot(directory, component, sealed_fd, expected_digest, size):
    """Atomic no-replace immutable file installation by privileged provisioner.

    No model parser and no asset acquisition. The caller's signed gate must bind
    component, bytes, build, space and current authority before invoking this.
    Production calls remain unreachable behind disabled_assets().
    """
    require(component in COMPONENTS and sha(expected_digest) and 0 < size <= MAX_BYTES, "install_identity")
    require(fcntl.fcntl(sealed_fd, fcntl.F_GET_SEALS) & SEALS == SEALS, "immutable_required")
    fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    staging = ".staging-" + os.urandom(16).hex()
    output = None
    try:
        st = os.fstat(fd)
        require(st.st_uid == os.geteuid() and st.st_mode & 0o077 == 0, "private_install_directory")
        output = os.open(staging, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600, dir_fd=fd)
        h = hashlib.sha256()
        for offset in range(0, size, 65536):
            data = os.pread(sealed_fd, min(65536, size - offset), offset)
            require(data, "install_truncated")
            h.update(data)
            view = memoryview(data)
            while view:
                count = os.write(output, view)
                require(count > 0, "install_write")
                view = view[count:]
        require(os.fstat(sealed_fd).st_size == size and h.hexdigest() == expected_digest, "install_digest")
        os.fchmod(output, 0o444)
        os.fsync(output)
        os.link(staging, component, src_dir_fd=fd, dst_dir_fd=fd, follow_symlinks=False)
        os.unlink(staging, dir_fd=fd)
        os.fsync(fd)
    finally:
        if output is not None:
            os.close(output)
        try:
            os.unlink(staging, dir_fd=fd)
        except FileNotFoundError:
            pass
        os.close(fd)
