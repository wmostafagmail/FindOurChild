"""Host lifecycle: real scanner fixtures and isolated PostgreSQL tests, actual worker restored."""

import os

from scripts.dev import compose


def main():
    compose("stop", "worker")
    try:
        compose("run", "--rm", "--user", "0:0", "tester", "python", "-m", "scripts.synthetic_workflow_setup")
        compose(
            "run",
            "--rm",
            "--user",
            f"{os.getuid()}:{os.getgid()}",
            "tester",
            "python",
            "-m",
            "scripts.workflow_test",
        )
    finally:
        compose("up", "-d", "worker")


if __name__ == "__main__":
    main()
