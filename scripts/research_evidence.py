"""Closed aggregate export; never release vectors, subject records, model URLs or arbitrary fields."""

import math
import re


def aggregate(report, source_digest):
    if (
        report["source_digest"] != source_digest
        or report["status"] != "synthetic_smoke_only"
        or report["real_models_benchmarked"] != 0
        or report["pipeline_images"] != 32
    ):
        raise ValueError("stale or non-synthetic smoke evidence")
    metrics = report["metrics"]
    if (
        metrics["data_class"] != "synthetic"
        or metrics["recognition_accuracy_claim"] is not False
        or not re.fullmatch("[a-f0-9]{64}", metrics["manifest_digest"])
    ):
        raise ValueError("invalid synthetic protocol")
    counts = metrics["denominators"]
    if counts != {"gallery_images": 16, "probes": 17, "mate_present": 16, "mate_absent": 1, "subjects": 16}:
        raise ValueError("incomplete smoke manifest")

    def rate(value):
        if value is None or (
            type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1
        ):
            raise ValueError("invalid aggregate")
        return value

    recall = {k: rate(metrics["recall"][k]) for k in ["1", "10", "50"]}
    burden = metrics["false_leads_per_query"]
    if type(burden) not in (int, float) or not math.isfinite(burden) or not 0 <= burden <= 50:
        raise ValueError("invalid review burden")
    return {
        "status": "synthetic_smoke_only",
        "real_models_benchmarked": 0,
        "pipeline_images": 32,
        "manifest_digest": metrics["manifest_digest"],
        "denominators": dict(counts),
        "recall": recall,
        "fpir": rate(metrics["fpir"]),
        "fnir": rate(metrics["fnir"]),
        "tpir": rate(metrics["tpir"]),
        "false_leads_per_query": burden,
        "recognition_accuracy_claim": False,
        "operational_threshold": "unset",
    }
