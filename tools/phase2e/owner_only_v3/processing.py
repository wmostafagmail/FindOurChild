"""Immutable artifact handoff reuses qualified V2 primitives without enabling asset effects."""

from tools.phase2e.demo_governance.artifacts import ArtifactRegistry, install_snapshot, snapshot_fd

from .records import require

__all__ = ["ArtifactRegistry", "install_snapshot", "process_assets", "snapshot_fd"]


def process_assets(*args, **kwargs):
    # No network, decompressor, scanner, decoder or native parser is invoked by V3 D1–D4.
    require(False, "v3_asset_processing_not_authorized")
