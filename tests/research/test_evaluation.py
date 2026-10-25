import hashlib
from dataclasses import replace

import pytest
from foc_api.research.evaluation import Record, capture_gap, evaluate, retrieve
from foc_api.research.pipeline import QualificationError


def image_hash(value):
    return hashlib.sha256(value.encode()).hexdigest()


def vector(index):
    return tuple(1.0 if i == index else 0.0 for i in range(128))


def rows():
    return [
        Record(
            image_hash("ga"),
            "a",
            "fa",
            "ca",
            "found",
            "gallery",
            "test",
            vector(0),
            capture_lower="2010-01-01",
            capture_upper="2010-01-01",
        ),
        Record(image_hash("gb"), "b", "fb", "cb", "found", "gallery", "test", vector(1)),
        Record(
            image_hash("pa"),
            "a",
            "fa",
            "qa",
            "missing",
            "probe",
            "test",
            vector(0),
            capture_lower="2020-01-01",
            capture_upper="2020-01-01",
        ),
        Record(image_hash("pc"), "c", "fc", "qc", "missing", "probe", "test", vector(2)),
    ]


def test_metrics_use_separate_present_absent_denominators():
    report = evaluate(rows(), threshold=0.5)
    assert report["denominators"] == {
        "gallery_images": 2,
        "probes": 2,
        "mate_present": 1,
        "mate_absent": 1,
        "subjects": 1,
    }
    assert report["recall"] == {"1": 1.0, "10": 1.0, "50": 1.0}
    assert report["fpir"] == 0 and report["fnir"] == 0 and report["tpir"] == 1
    assert report["false_leads_per_query"] == 0
    assert report["subject_bootstrap_95_recall_at_1"] == [1.0, 1.0]
    assert report["true_lead_capture_gap_counts"] == {"over5y": 1}
    assert report["recognition_accuracy_claim"] is False
    assert evaluate(rows(), threshold=0.5) == report


def test_open_set_false_match_is_not_hidden_by_recall():
    data = rows()
    data[-1] = replace(data[-1], vector=vector(0))
    result = evaluate(data, threshold=0.5)
    assert result["recall"]["1"] == 1 and result["fpir"] == 1 and result["false_leads_per_query"] == 0.5


def test_threshold_miss_is_distinct_from_retrieval_hit():
    data = rows()
    data[2] = replace(data[2], vector=vector(2))
    result = evaluate(data, threshold=0.5)
    assert result["recall"]["10"] == 1 and result["fnir"] == 1 and result["tpir"] == 0


def test_unknown_and_uncertain_capture_intervals_stay_explicit():
    data = rows()
    assert capture_gap(data[0], data[1]) == {"kind": "unknown", "lower_days": None, "upper_days": None}
    uncertain = replace(data[2], capture_lower="2010-01-01", capture_upper="2020-01-01")
    assert capture_gap(data[0], uncertain)["lower_days"] == 0
    assert evaluate([data[0], data[1], uncertain, data[3]], threshold=0.5)[
        "true_lead_capture_gap_counts"
    ] == {"uncertain_cross_bin": 1}


@pytest.mark.parametrize(
    "mutation",
    [
        "duplicate",
        "subject-split",
        "family-split",
        "case-label",
        "real",
        "space",
        "inverted-date",
        "partial-date",
        "negative-age",
        "partial-age",
        "unknown-partition",
    ],
)
def test_manifest_adversarial_inputs_fail_closed(mutation):
    data = rows()
    if mutation == "duplicate":
        data.append(data[0])
    elif mutation == "subject-split":
        data[2] = replace(data[2], partition="development")
    elif mutation == "family-split":
        data[-1] = replace(data[-1], family="fa", partition="development")
    elif mutation == "case-label":
        data[-1] = replace(data[-1], case="ca")
    elif mutation == "real":
        data[0] = replace(data[0], synthetic=False)
    elif mutation == "space":
        data[0] = replace(data[0], space_id="same_dimension_other_weights")
    elif mutation == "inverted-date":
        data[0] = replace(data[0], capture_lower="2021-01-01")
    elif mutation == "partial-date":
        data[0] = replace(data[0], capture_upper=None)
    elif mutation == "negative-age":
        data[0] = replace(data[0], age_min_months=-1, age_max_months=2)
    elif mutation == "partial-age":
        data[0] = replace(data[0], age_max_months=2)
    else:
        data[0] = replace(data[0], partition="production")
    with pytest.raises(QualificationError):
        evaluate(data, threshold=0.5)


@pytest.mark.parametrize("threshold", [float("nan"), float("inf"), 2, None, True])
def test_unfrozen_invalid_thresholds_rejected(threshold):
    with pytest.raises(QualificationError):
        evaluate(rows(), threshold=threshold)


def test_absent_denominator_is_null_when_no_open_set_probes():
    assert evaluate(rows()[:3], threshold=0.5)["fpir"] is None


def test_empty_and_incomplete_evaluations_rejected():
    for data in [[], rows()[:2], [rows()[2]]]:
        with pytest.raises(QualificationError):
            evaluate(data, threshold=0.5)


def test_ties_photo_caps_and_registry_filter_are_deterministic():
    data = rows()
    g = [replace(data[0], image_hash=image_hash("x" + str(i))) for i in range(7)]
    g += [
        replace(data[1], vector=vector(0)),
        replace(data[0], image_hash=image_hash("same"), case="ignored", registry="missing"),
    ]
    found = retrieve(data[2], g)
    assert [r["case"] for r in found] == ["ca", "cb"] and found[0]["omitted_photos"] == 4
    assert retrieve(data[2], list(reversed(g))) == found


@pytest.mark.parametrize("budget", [0, 51, True])
def test_retrieval_budget_cannot_be_bypassed(budget):
    data = rows()
    with pytest.raises(QualificationError):
        retrieve(data[2], data[:2], k=budget)
