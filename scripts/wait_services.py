import time

import httpx

from scripts.preflight import verify_services

for attempt in range(30):
    try:
        verify_services()
        break
    except (httpx.HTTPError, RuntimeError, ValueError, OSError):
        if attempt == 29:
            raise SystemExit("Actual services did not become ready") from None
        time.sleep(1)
