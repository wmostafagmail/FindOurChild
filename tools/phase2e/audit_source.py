"""Independent, stdlib-only review of actual source bytes; no acquisition/imports."""

import hashlib
import json
import re
import sys
from pathlib import Path


def audit(directory, lock):
    expected = {r['path']: r for r in lock['entries']}
    paths = list(directory.rglob('*'))
    if any(p.is_symlink() for p in paths):
        raise ValueError('Any source symlink is denied')
    actual = {str(p.relative_to(directory)) for p in paths if p.is_file()}
    if actual != set(expected):
        raise ValueError('Source closure mismatch')
    rows = []
    for name, row in expected.items():
        p = directory / name
        if p.is_symlink() or any(x.is_symlink() for x in p.parents):
            raise ValueError('Source symlink denied')
        data = p.read_bytes()
        if len(data) != row['bytes'] or hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() != row['git_blob']:
            raise ValueError('Source identity mismatch')
        checked_name = name if name not in {'dlib/gui_widgets/fonts.h', 'dlib/gui_widgets/fonts_abstract.h'} else 'reviewed_font_declaration_header'
        if b'\0' in data or any(x in checked_name for x in ['frontal_face_detector', 'dlib/gui_', 'dlib/python', 'tools/python', 'dlib/data_io/image_dataset_metadata.cpp']):
            raise ValueError('Source boundary violation')
        # Bounded heuristics, not a universal classifier for pretrained data.
        if any(x in data for x in [b'get_serialized_frontal_faces', b'get_decoded_string_with_default_font_data']):
            raise ValueError('Embedded serialized payload marker')
        literals = re.findall(rb'"([A-Za-z0-9+/=]{64,})"', data)
        if sum(map(len, literals)) >= 512:
            raise ValueError('Long encoded literal requires separate classification')
        rows.append({'path': name, 'sha256': hashlib.sha256(data).hexdigest(), 'git_blob': row['git_blob']})
    return {'scope': 'exact_source_closure_and_bounded_payload_heuristics',
            'files': rows, 'model_or_media_acquired': False, 'unresolved_heuristic_hits': 0,
            'universal_absence_claim': False, 'independent_human_review': 'pending'}


if __name__ == '__main__':
    print(json.dumps(audit(Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text())), indent=2))
