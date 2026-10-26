import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inventory():
    paths = []
    for base in ["apps/web", "services/api", "scripts", "database", "tests", "config"]:
        paths.extend(
            p
            for p in (ROOT / base).rglob("*")
            if p.is_file()
            and p.name != "next-env.d.ts"
            and p.suffix in {".ts", ".tsx", ".css", ".py", ".sql", ".mjs", ".json", ".png"}
            and not any(x in p.parts for x in [".next", "__pycache__", "node_modules"])
        )
    paths += [
        ROOT / p
        for p in [
            ".coveragerc",
            "docs/phase1b/required-tests.json",
            "docs/phase1c/required-tests.json",
            "docs/phase2a/required-tests.json",
            "docs/phase2a/research/source-lock.json",
            "package.json",
            "package-lock.json",
            "pyproject.toml",
            "uv.lock",
            "compose.yaml",
            "e2e.config.ts",
            "docs/contracts/openapi.json",
            "docs/contracts/event-envelope.schema.json",
            "docs/phase1a/required-tests.json",
            "services/api/Dockerfile",
            "requirements-bootstrap.txt",
            ".github/workflows/phase1a.yml",
        ]
    ]
    research_root = (ROOT / "docs/phase2a/research").resolve()
    lock = json.loads((research_root / "source-lock.json").read_text())
    for entry in lock["sources"]:
        candidate = (research_root / entry["local"]).resolve()
        if not candidate.is_relative_to(research_root) or not candidate.is_file():
            raise ValueError("Research evidence path escaped or missing")
        paths.append(candidate)
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}


def fingerprint():
    return hashlib.sha256(json.dumps(inventory(), sort_keys=True).encode()).hexdigest()


if __name__ == "__main__":
    print(fingerprint())
