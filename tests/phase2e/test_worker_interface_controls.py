"""New A1b source-policy negatives; never import a native model parser."""

import hashlib
import json

import pytest

from tools.phase2e.audit_source import audit
from tools.phase2e.source_projection import ROOT, allowed_path, validate_lock


def tree(tmp_path, data=b'// authored synthetic code\n', name='dlib/math.h'):
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    lock = {'entries': [{'path': name, 'bytes': len(data),
                        'git_blob': hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()}]}
    return lock


def test_independent_source_audit_hashes_actual_synthetic_bytes(tmp_path):
    lock = tree(tmp_path)
    report = audit(tmp_path, lock)
    assert report['universal_absence_claim'] is False and report['unresolved_heuristic_hits'] == 0
    assert report['files'][0]['sha256'] == hashlib.sha256(b'// authored synthetic code\n').hexdigest()


@pytest.mark.parametrize('data', [b'get_serialized_frontal_faces', b'get_decoded_string_with_default_font_data',
                                b'"'+b'A'*512+b'"', b'\0hidden binary'])
def test_source_policy_catches_more_than_filename_extensions(tmp_path, data):
    lock = tree(tmp_path, data)
    with pytest.raises(ValueError):
        audit(tmp_path, lock)


@pytest.mark.parametrize('change', ['extra_file', 'missing_file', 'wrong_hash', 'changed_size', 'symlink'])
def test_independent_actual_source_closure_denials(tmp_path, change):
    lock = tree(tmp_path)
    p = tmp_path / 'dlib/math.h'
    if change == 'extra_file':
        (tmp_path / 'extra.h').write_text('unapproved')
    elif change == 'missing_file':
        p.unlink()
    elif change == 'wrong_hash':
        lock['entries'][0]['git_blob'] = '0'*40
    elif change == 'changed_size':
        lock['entries'][0]['bytes'] += 1
    else:
        target = tmp_path.parent / (tmp_path.name+'-synthetic-target')
        target.write_bytes(p.read_bytes())
        p.unlink()
        p.symlink_to(target)
    with pytest.raises(ValueError):
        audit(tmp_path, lock)


@pytest.mark.parametrize('path', ['dlib/gui_widgets/fonts.cpp', 'dlib/gui_widgets.h', 'dlib/gui_core.h',
                                'dlib/gui_core/gui_core_kernel_1.cpp'])
def test_unused_gui_and_embedded_font_are_outside_projection(path):
    assert allowed_path(path) is False


def test_v3_projection_has_no_new_or_substituted_upstream_blob():
    lock = json.loads((ROOT / 'config/phase2e/source-projection.json').read_text())
    assert len(validate_lock(lock)) == 1114
    disposition = json.loads((ROOT / 'docs/phase2e/e0/ADDITIONAL_SOURCE_AUDIT.json').read_text())
    assert disposition['remaining_blobs'] == 1114 and len(disposition['excluded']) == 27
    assert all(not allowed_path(r['path']) for r in disposition['excluded'])


def test_architecture_approval_cannot_enable_any_acquisition_or_execution():
    policy = json.loads((ROOT / 'config/phase2e/qualification-policy.json').read_text())
    for name in ['acquisition_enabled', 'native_model_loading_enabled', 'image_decoding_enabled',
                 'inference_enabled', 'operational_enabled']:
        assert policy[name] is False
    assert policy['status'] == 'A1b_engineering_approved_second_review_pending'


def test_closed_native_test_inventory_cannot_be_confused_with_inference():
    inventory = json.loads((ROOT / 'config/phase2e/native-test-inventory.json').read_text())
    assert inventory['model_deserializations_allowed'] == 0
    assert inventory['inference_executions_allowed'] == 0
    assert inventory['interface_cases'] == [f'INTERFACE-{i}' for i in range(1, 33)]
    assert inventory['stream_cases'] == [f'STREAM-{i}' for i in range(1, 21)]
