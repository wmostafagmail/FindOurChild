import bz2
import os
from pathlib import Path

import pytest

from tools.phase2e.demo_governance.artifacts import (
    SEALS,
    ArtifactRegistry,
    _safe_open,
    disabled_assets,
    locked_inventory,
    snapshot_fd,
    verify_build,
)
from tools.phase2e.demo_governance.records import Denied, digest
from tools.phase2e.quarantine import IntegrityError, unpack_bzip2, verify_bytes


def test_dg_a01_no_gate_or_identity_before_io():
    with pytest.raises(Denied):
        disabled_assets()
    with pytest.raises(Denied):
        ArtifactRegistry("/does-not-exist", {})


def test_dg_a02_closed_51_inventory():
    rows = [
        {"source": f"synthetic-{i}", "size": 1, "sha256": "a" * 64, "git_blob": "b" * 40} for i in range(51)
    ]
    expected = {x["source"]: x for x in rows}
    assert locked_inventory(rows, expected)
    for wrong in [
        rows[:-1],
        rows + rows[:1],
        rows[:-1] + rows[:1],
        [dict(x, url="https://foreign.invalid") for x in rows],
    ]:
        with pytest.raises(Denied):
            locked_inventory(wrong, expected)


def test_dg_a03_exact_bytes_size_git_and_sha():
    for kwargs in [
        {"size": 2, "sha256": digest(b"x")},
        {"size": 1, "sha256": "a" * 64},
        {"size": 1, "git_blob": "0" * 40},
    ]:
        with pytest.raises(IntegrityError):
            verify_bytes(b"x", **kwargs)


def test_dg_a04_type_links_and_permissions_before_read():
    root = Path(os.environ["FOC_GOVERNANCE_ROOTED_FIXTURE"])
    for name in ["symlink", "hardlink", "fifo", "writable", "directory"]:
        with pytest.raises((Denied, OSError)):
            _safe_open(root / name, 0)


def test_dg_a05_no_pathname_reopen(tmp_path):
    p = tmp_path / "input"
    p.write_bytes(b"synthetic-original")
    with p.open("rb") as f:
        p.rename(tmp_path / "moved")
        p.write_bytes(b"wrong")
        with snapshot_fd(f.fileno(), size=18, sha256=digest(b"synthetic-original")) as fd:
            assert os.read(fd, 18) == b"synthetic-original"


def test_dg_a06_copy_mutation_denied_before_parser(tmp_path):
    p = tmp_path / "input"
    data = b"a" * 70000
    p.write_bytes(data)

    def mutate(_):
        p.write_bytes(b"b" * len(data))

    called = False
    with (
        p.open("rb") as f,
        pytest.raises(Denied),
        snapshot_fd(f.fileno(), size=len(data), sha256=digest(data), copy_observer=mutate),
    ):
        called = True
    assert not called


def test_dg_a07_kernel_seals_prevent_write_grow_shrink(tmp_path):
    import fcntl

    p = tmp_path / "input"
    p.write_bytes(b"original")
    with p.open("rb") as f, snapshot_fd(f.fileno(), size=8, sha256=digest(b"original")) as fd:
        p.write_bytes(b"new data")
        for action in [
            lambda: os.pwrite(fd, b"!", 0),
            lambda: os.ftruncate(fd, 9),
            lambda: os.ftruncate(fd, 1),
        ]:
            with pytest.raises(OSError):
                action()
        assert fcntl.fcntl(fd, getattr(fcntl, "F_GET_SEALS", 1034)) & SEALS == SEALS
        assert os.pread(fd, 8, 0) == b"original"


def test_dg_a08_sealing_failure_never_falls_back(tmp_path, monkeypatch):
    import fcntl

    p = tmp_path / "input"
    p.write_bytes(b"original")

    def fail(*_):
        raise OSError("synthetic unsupported seals")

    monkeypatch.setattr(fcntl, "fcntl", fail)
    with (
        p.open("rb") as f,
        pytest.raises(OSError),
        snapshot_fd(f.fileno(), size=8, sha256=digest(b"original")),
    ):
        pytest.fail("mutable fallback")


def test_dg_a09_malformed_concatenated_or_truncated_bzip():
    b = bz2.compress(b"synthetic buffer")
    for data in [b + b, b + b"x", b[:-1], b"BZh-bad"]:
        with pytest.raises(IntegrityError):
            unpack_bzip2(data, output_limit=1000, ratio_limit=128, time_limit=1)


def test_dg_a10_bounded_output_and_ratio():
    with pytest.raises(IntegrityError):
        unpack_bzip2(bz2.compress(b"a" * 100000), output_limit=100, ratio_limit=1, time_limit=1)


def test_dg_a14_quarantine_aad_tag_and_key():
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    key = AESGCM.generate_key(256)
    other = AESGCM.generate_key(256)
    nonce = os.urandom(12)
    encrypted = AESGCM(key).encrypt(nonce, b"synthetic", b"synthetic-aad")
    for k, body, aad in [
        (other, encrypted, b"synthetic-aad"),
        (key, encrypted + b"x", b"synthetic-aad"),
        (key, encrypted, b"foreign"),
    ]:
        with pytest.raises(InvalidTag):
            AESGCM(k).decrypt(nonce, body, aad)


def test_dg_a15_space_and_build_not_dimension_or_filename(tmp_path):
    manifest = {
        k: {"size": 1, "sha256": digest(b"x"), "build": "a" * 64, "space": "synthetic-v1"}
        for k in ["cnn_detector", "five_point_predictor", "resnet_128_encoder"]
    }
    registry = ArtifactRegistry(tmp_path, manifest)
    for build, space in [("b" * 64, "synthetic-v1"), ("a" * 64, "foreign-128D")]:
        with (
            pytest.raises(Denied),
            registry.open("resnet_128_encoder", build=build, space=space, authority=True),
        ):
            pytest.fail("space bypass")


def test_dg_a16_build_outputs_required_not_receipts():
    files = {
        k: b"synthetic-" + k.encode()
        for k in ["wheel", "extension", "test_binary", "sbom", "compiler", "source"]
    }
    expected = {k: digest(v) for k, v in files.items()}
    assert verify_build(files, expected)
    for kind in files:
        wrong = dict(files)
        wrong[kind] += b"tamper"
        with pytest.raises(Denied):
            verify_build(wrong, expected)
    with pytest.raises(Denied):
        verify_build({"sbom": b"receipt"}, {"sbom": digest(b"receipt")})


def test_actual_trusted_file_boundary_positive():
    root = Path(os.environ["FOC_GOVERNANCE_ROOTED_FIXTURE"])
    data = b"benign-interface-buffer"
    manifest = {
        k: {"size": len(data), "sha256": digest(data), "build": "a" * 64, "space": "synthetic-v1"}
        for k in ["cnn_detector", "five_point_predictor", "resnet_128_encoder"]
    }
    registry = ArtifactRegistry(root, manifest)
    with registry.open("cnn_detector", build="a" * 64, space="synthetic-v1", authority=True) as fd:
        assert os.read(fd, len(data)) == data


def receipt():
    from datetime import timedelta

    from tests.demo_governance.helpers import NOW
    from tools.phase2e.demo_governance.registry import utc

    r = {k: "a" * 64 for k in ["source", "derivative", "scanner", "decoder"]}
    r.update(
        definitions_expires=utc(NOW + timedelta(hours=1)),
        scan_status="clean",
        decode_status="clean",
        format="PNG",
        pixels=64,
        permission_epoch=1,
    )
    expected = {k: r[k] for k in ["source", "derivative", "scanner", "decoder", "permission_epoch"]}
    return r, expected, NOW


def test_dg_a11_scanner_missing_stale_dirty_or_timeout():
    from tools.phase2e.demo_governance.artifacts import processing_receipt

    r, e, now = receipt()
    assert processing_receipt(r, e, now)
    for field, value in [
        ("scan_status", "unavailable"),
        ("scan_status", "dirty"),
        ("scan_status", "timeout"),
        ("definitions_expires", "2000-01-01T00:00:00Z"),
    ]:
        wrong = dict(r)
        wrong[field] = value
        with pytest.raises(Denied):
            processing_receipt(wrong, e, now)
    with pytest.raises(Denied):
        processing_receipt({}, e, now)


def test_dg_a12_decoder_failure_or_format_and_pixels():
    from tools.phase2e.demo_governance.artifacts import processing_receipt

    r, e, now = receipt()
    for field, value in [
        ("decode_status", "crashed"),
        ("decode_status", "malformed"),
        ("format", "JPEG"),
        ("pixels", 2**32),
    ]:
        wrong = dict(r)
        wrong[field] = value
        with pytest.raises(Denied):
            processing_receipt(wrong, e, now)


def test_dg_a13_lineage_or_permission_changed():
    from tools.phase2e.demo_governance.artifacts import processing_receipt

    r, e, now = receipt()
    for field in e:
        wrong = dict(r)
        wrong[field] = 2 if field == "permission_epoch" else "b" * 64
        with pytest.raises(Denied):
            processing_receipt(wrong, e, now)


def test_atomic_no_replace_provisioning_from_benign_sealed_bytes(tmp_path):
    from tools.phase2e.demo_governance.artifacts import install_snapshot

    tmp_path.chmod(0o700)
    data = b"synthetic-not-model"
    source = tmp_path / "buffer"
    source.write_bytes(data)
    with source.open("rb") as f, snapshot_fd(f.fileno(), size=len(data), sha256=digest(data)) as fd:
        install_snapshot(tmp_path, "cnn_detector", fd, digest(data), len(data))
        assert (tmp_path / "cnn_detector").read_bytes() == data
        assert (tmp_path / "cnn_detector").stat().st_mode & 0o222 == 0
        assert (tmp_path / "cnn_detector").stat().st_nlink == 1
        with pytest.raises(FileExistsError):
            install_snapshot(tmp_path, "cnn_detector", fd, digest(data), len(data))
    assert not list(tmp_path.glob(".staging-*"))
