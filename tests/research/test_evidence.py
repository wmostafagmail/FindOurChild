import copy
import hashlib
import json
import re
from pathlib import Path

import pytest

from scripts.research_benchmark import run
from scripts.research_evidence import aggregate

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def smoke():
    return run()


def test_no_recognition_artifact_is_cleared_and_all_source_evidence_is_pinned():
    catalog = json.loads((ROOT / "config/research-candidates.json").read_text())
    assert len(catalog["candidates"]) == 5 and catalog["synthetic_only"] is True
    for candidate in catalog["candidates"]:
        assert candidate["weight_sha256"] is None
        assert not any(
            candidate[k]
            for k in ["weight_download_allowed", "evaluation_use_allowed", "operational_use_allowed"]
        )
        assert re.fullmatch("[a-f0-9]{40}", candidate["code_commit"])
    lock = json.loads((ROOT / "docs/phase2a/research/source-lock.json").read_text())
    for source in lock["sources"]:
        assert source["status"] == "retrieved_text_only"
        assert re.fullmatch("[a-f0-9]{40}", source["commit"])
        path = ROOT / "docs/phase2a/research" / source["local"]
        assert path.suffix in {".md", ".py", ""}
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"]


def test_export_retains_only_aggregate_evidence(smoke):
    raw = copy.deepcopy(smoke)
    raw["arbitrary"] = "SYNTHETIC_SECRET_CANARY"
    raw["metrics"]["vectors"] = ["SYNTHETIC_SECRET_CANARY"]
    clean = aggregate(raw, raw["source_digest"])
    assert "SYNTHETIC_SECRET_CANARY" not in json.dumps(clean)
    assert clean["pipeline_images"] == 32 and clean["real_models_benchmarked"] == 0
    assert clean["operational_threshold"] == "unset" and clean["recognition_accuracy_claim"] is False


@pytest.mark.parametrize(
    "mutation",
    ["source", "real", "status", "count", "data", "accuracy", "hash", "nan", "injection", "burden"],
)
def test_unsafe_or_incomplete_benchmark_evidence_blocks_ci(smoke, mutation):
    raw = copy.deepcopy(smoke)
    if mutation == "source":
        raw["source_digest"] = "stale"
    elif mutation == "real":
        raw["real_models_benchmarked"] = 1
    elif mutation == "status":
        raw["status"] = "qualified"
    elif mutation == "count":
        raw["metrics"]["denominators"]["probes"] = 0
    elif mutation == "data":
        raw["metrics"]["data_class"] = "real"
    elif mutation == "accuracy":
        raw["metrics"]["recognition_accuracy_claim"] = True
    elif mutation == "hash":
        raw["metrics"]["manifest_digest"] = "injected"
    elif mutation == "nan":
        raw["metrics"]["fpir"] = float("nan")
    elif mutation == "injection":
        raw["metrics"]["recall"]["1"] = "SYNTHETIC_SECRET_CANARY"
    else:
        raw["metrics"]["false_leads_per_query"] = float("inf")
    with pytest.raises(ValueError):
        aggregate(raw, smoke["source_digest"])
