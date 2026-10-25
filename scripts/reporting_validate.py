"""Host orchestration: actual worker/scanner lifecycle, no socket mounted into the application/tests."""

from scripts.dev import compose


def main():
    compose("stop", "worker")
    try:
        compose("run", "--rm", "--user", "0:0", "tester", "python", "-m", "scripts.reporting_test")
        compose("stop", "scanner")
        try:
            compose("run", "--rm", "--user", "0:0", "tester", "python", "-m", "scripts.resilience_test")
        finally:
            compose("up", "-d", "--wait", "scanner")
    finally:
        compose("up", "-d", "worker")


if __name__ == "__main__":
    main()
