"""Collect only dedicated API instrumentation after shutdown; API cannot write runner reports."""

import subprocess
import sys
from pathlib import Path

from scripts.dev import compose


def main():
    compose("stop", "api")
    output = Path("artifacts/raw")
    for file in output.glob(".coverage.api*"):
        if file.is_file():
            file.unlink()
    subprocess.run(["docker", "cp", "foc-phase1a-api-1:/coverage/.", str(output)], check=True)
    if not any(output.glob(".coverage.api*")):
        raise SystemExit("API-process coverage missing")
    for arguments in [
        ["combine", "--append", "--keep", str(output)],
        ["report", "--fail-under=75"],
        ["json", "-o", str(output / "coverage.json")],
        ["xml", "-o", str(output / "coverage.xml")],
    ]:
        subprocess.run([sys.executable, "-m", "coverage", *arguments], check=True)


if __name__ == "__main__":
    main()
