"""Weight-free synthetic pipeline/evaluation smoke benchmark; exports aggregates only."""

import hashlib
import json
import platform
import time
from pathlib import Path

from foc_api.research.evaluation import Record, evaluate
from foc_api.research.pipeline import SyntheticAdapter, fixture

from scripts.fingerprint import fingerprint

ROOT = Path(__file__).resolve().parents[1]


def run():
    adapter = SyntheticAdapter()
    rows = []
    timings = []
    for i in range(16):
        for role, registry, suffix in [("gallery", "found", "g"), ("probe", "missing", "p")]:
            data = fixture(i if role == "gallery" else i + 16)
            start = time.perf_counter_ns()
            stage = adapter.embed(data, subject_approved=True)
            timings.append((time.perf_counter_ns() - start) / 1e6)
            image_hash = hashlib.sha256(data).hexdigest()
            rows.append(
                Record(
                    image_hash,
                    "subject" + str(i),
                    "family" + str(i),
                    suffix + str(i),
                    registry,
                    role,
                    "test",
                    stage.value["vector"],
                    capture_lower="2010-01-01" if role == "gallery" else "2020-01-01",
                    capture_upper="2010-01-01" if role == "gallery" else "2020-01-01",
                    age_min_months=12 if role == "gallery" else 132,
                    age_max_months=24 if role == "gallery" else 144,
                )
            )
    rows.append(
        Record(
            hashlib.sha256(b"analytic-unit-vector-127").hexdigest(),
            "absent",
            "absent-family",
            "absent-case",
            "missing",
            "probe",
            "test",
            tuple(1.0 if i == 127 else 0.0 for i in range(128)),
        )
    )
    metrics = evaluate(rows, threshold=0.99)
    assert metrics == evaluate(rows, threshold=0.99)
    return {
        "status": "synthetic_smoke_only",
        "source_digest": fingerprint(),
        "runtime": {
            "python": platform.python_version(),
            "os": platform.system(),
            "architecture": platform.machine(),
        },
        "dependency_locks": {
            p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
            for p in ["uv.lock", "package-lock.json", "compose.yaml"]
        },
        "pipeline_images": 32,
        "metrics": metrics,
        "timing": {
            "scope": "local synthetic adapter only; no neural model, GPU, queue or operational sizing claim",
            "unit": "ms",
            "samples": len(timings),
            "p50": sorted(timings)[len(timings) // 2],
            "p95": sorted(timings)[int(len(timings) * 0.95)],
        },
        "real_models_benchmarked": 0,
        "model_qualification": "blocked_pending_exact_artifact_and_training_rights_and_separate_data_protocol",
    }


def main():
    path = ROOT / "artifacts/raw/research-benchmark.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(run(), indent=2, allow_nan=False) + "\n")
    path.chmod(0o600)
    print("Synthetic pipeline/evaluation smoke completed; zero recognition models benchmarked")


if __name__ == "__main__":
    main()
