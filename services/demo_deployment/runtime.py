"""No implicit bootstrap, test principal, mutable environment override or policy fallback."""
import json
import os
from pathlib import Path

from tools.phase2e.owner_only_v3.checkpoint import Checkpoint
from tools.phase2e.owner_only_v3.records import require

from .oidc import Identity
from .protected import ROOT, configuration, read_private
from .state import State


def release_bound(config, release):
    require(type(release) is dict and set(release) == {'source_sha'}
            and release['source_sha'] == config['source_sha'], 'deployment_build_identity')


def load(*, admin=False):
    require(os.geteuid() == (0 if admin else 10001), 'deployment_process_identity')
    config = read_private(ROOT / 'runtime/config.json', owner=10001)
    binding_path = ROOT / 'runtime/binding.json'
    if binding_path.exists():
        binding = read_private(binding_path, owner=10001)
        require(set(binding) == {'subject', 'config_digest'}, 'binding_closed')
        from tools.phase2e.owner_only_v3.records import digest

        require(binding['config_digest'] == digest(config) and config['owner_subject'] is None, 'binding_config')
        config['owner_subject'] = binding['subject']
    config = configuration(config)
    release_bound(config, json.loads((Path(__file__).resolve().parents[2] / "release.json").read_bytes()))
    private = read_private(ROOT / ('admin/private.json' if admin else 'runtime/private.json'), owner=0 if admin else 10001)
    pin_path = ROOT / 'runtime/idp-pin.json'
    pin = read_private(pin_path, owner=10001) if pin_path.exists() else None
    directory = os.open(ROOT / 'checkpoint', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        checkpoint = Checkpoint(directory, owner=10001)
    finally:
        os.close(directory)
    identity = Identity(config, private, pin)
    return State(config, private, checkpoint, identity)


def evidence_root():
    # Fixed runtime path. No user path, assets, vectors, model or acquisition provider.
    path = Path(ROOT / 'quarantine')
    require(path.is_dir(), 'quarantine_unprovisioned')
    return {'quarantine_empty': not any(path.iterdir()), 'actual_processing_available': False}
