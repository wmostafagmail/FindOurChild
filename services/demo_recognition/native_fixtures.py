"""Create tiny authored, non-model stream fixtures in the offline image build."""

import os
from pathlib import Path

root = Path('/opt/qualification/stream-fixtures')
root.mkdir()
for name in ['valid', 'hardlink-source', 'writable', 'unowned']:
    p = root / name
    p.write_bytes(b'fictional source-only stream\n')
    p.chmod(0o444 if name != 'writable' else 0o644)
os.chown(root / 'unowned', 10001, 10001)
os.link(root / 'hardlink-source', root / 'hardlink')
(root / 'symlink').symlink_to(root / 'valid')
(root / 'directory-link').symlink_to(root, target_is_directory=True)
(root / 'directory').mkdir()
os.mkfifo(root / 'fifo', 0o444)
