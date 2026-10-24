"""Developer-only inventory update. CI compares this checked-in manifest, never regenerates it."""

import json
from pathlib import Path

import pytest


class Inventory:
    def pytest_collection_finish(self, session):
        tests = [item.nodeid for item in session.items]
        Path("docs/phase1a/required-tests.json").write_text(
            json.dumps(
                {
                    "scope": "phase1a-only",
                    "python": tests,
                    "browser_titles": [
                        "TC_FND_BROWSER_AR_READY",
                        "TC_FND_BROWSER_EN_READY",
                        "TC_FND_BROWSER_LANGUAGE_SWITCH",
                        "TC_ID_BROWSER_MFA_TENANT_LOGOUT",
                    ],
                    "browser_targets": 24,
                },
                indent=2,
            )
            + "\n"
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main(["tests/unit", "tests/api", "tests/database", "tests/security", "tests/integration", "--collect-only", "-q"], plugins=[Inventory()]))
