"""Generated CI secrets only. Production setup never imports this provider."""
import fcntl
import json
import os
import sys
import time
from pathlib import Path

from tests.identity.helpers import otp


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true' and sys.argv[1:] in (['otp'], ['password'])
    root = Path('.runtime/deployment-fixture')
    data = json.loads((root / 'credentials.json').read_text())
    assert data['data_class'] == 'generated_ci_only_not_real_owner'
    if sys.argv[1] == 'password':
        print(data['password'])
        return
    # Keep the provider's replay protection. Every login uses a new 30-second counter.
    with (root / 'last-otp-counter').open('a+') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        stream.seek(0);last = int(stream.read() or '0')
        while int(time.time()) // 30 <= last or int(time.time()) % 30 > 20:
            time.sleep(.2)
        counter = int(time.time()) // 30
        stream.seek(0);stream.truncate();stream.write(str(counter));stream.flush();os.fsync(stream.fileno())
        print(otp(data['otp']))


if __name__ == '__main__':
    main()
