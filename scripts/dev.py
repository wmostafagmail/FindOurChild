"""Disposable, synthetic-only local service lifecycle. No production mode exists."""

import json
import os
import secrets
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".runtime"
ENV = STATE / "local.json"


def load():
    return json.loads(ENV.read_text())


def environment():
    data = load()
    from scripts.identity_setup import generate

    generate()
    identity = json.loads((STATE / "identity.json").read_text())
    data.update({k: v for k, v in identity.items() if k.startswith("FOC_")})
    data["FOC_CONTAINER_ADMIN_URL"] = data["FOC_DATABASE_ADMIN_URL"].replace("127.0.0.1:55439", "db:5432")
    data["FOC_CONTAINER_DATABASE_URL"] = data["FOC_DATABASE_URL"].replace("127.0.0.1:55439", "db:5432")
    return {
        **os.environ,
        **data,
        "PYTHONPATH": str(ROOT / "services/api"),
        "NEXT_TELEMETRY_DISABLED": "1",
        "E2E_TELEMETRY_DISABLED": "1",
        "DO_NOT_TRACK": "1",
        "FOC_E2E_DATA_CLASS": "synthetic",
        "FOC_E2E_ISOLATED": "1",
    }


def sanitize_environment(source):
    safe_foc = {"FOC_API_URL", "FOC_DATA_CLASS", "FOC_E2E_DATA_CLASS", "FOC_E2E_ISOLATED", "FOC_E2E_BASE_URL"}
    return {
        key: value
        for key, value in source.items()
        if not (key.startswith("FOC_") and key not in safe_foc)
        and not key.startswith(("AWS_", "OPENAI_", "ANTHROPIC_", "GOOGLE_API_"))
        and not key.endswith(("_API_KEY", "_TOKEN", "_SECRET", "_PASSWORD"))
    }


def compose(*args):
    subprocess.run(
        ["docker", "compose", "-f", str(ROOT / "compose.yaml"), *args],
        cwd=ROOT,
        env=environment(),
        check=True,
    )


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "help"
    if command == "init":
        STATE.mkdir(mode=0o700, exist_ok=True)
        if ENV.exists():
            print("Existing synthetic environment retained")
            return
        password, api_password = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        data = {
            "FOC_DATA_CLASS": "synthetic",
            "FOC_DB_ADMIN_PASSWORD": password,
            "FOC_DATABASE_ADMIN_URL": f"postgresql://postgres:{quote(password)}@127.0.0.1:55439/foc_synthetic",
            "FOC_DATABASE_URL": f"postgresql://foc_api:{quote(api_password)}@127.0.0.1:55439/foc_synthetic",
            "FOC_DB_API_PASSWORD": api_password,
            "FOC_API_URL": "http://127.0.0.1:8000",
        }
        descriptor = os.open(ENV, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w") as stream:
            json.dump(data, stream)
        print("Created private, synthetic-only credentials")
    elif command == "db":
        compose("up", "-d", "--wait", "db")
        compose("build", "api")
        compose("run", "--rm", "--user", "0:0", "migrate")
    elif command == "api":
        compose("stop", "api")
        compose(
            "run",
            "--rm",
            "--no-deps",
            "api",
            "python",
            "-c",
            "from pathlib import Path; [p.unlink() for p in Path('/coverage').glob('.coverage.*') if p.is_file()]",
        )
        compose("up", "-d", "api", "keycloak")
    elif command == "web":
        env = sanitize_environment(environment())
        os.execvpe("npm", ["npm", "run", "dev"], env)
    elif command == "test":
        compose("run", "--rm", "--user", f"{os.getuid()}:{os.getgid()}", "tester")
    elif command == "browser":
        compose(
            "run",
            "--rm",
            "--user",
            f"{os.getuid()}:{os.getgid()}",
            "tester",
            "python",
            "scripts/preflight.py",
        )
        from scripts.preflight import verify_services

        verify_services()
        env = sanitize_environment(environment())
        subprocess.run(["npm", "run", "test:browser"], env=env, check=True, cwd=ROOT)
    elif command == "stop":
        compose("stop")
    else:
        raise SystemExit("Use init | db | api | web | test | browser | stop. No destructive reset command.")


if __name__ == "__main__":
    main()
