"""Reproducible synthetic metric harness, not evidence of real-child recognition accuracy."""

import math
import random
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from .pipeline import SYNTHETIC_SPACE, QualificationError, digest, validate_vector


@dataclass(frozen=True)
class Record:
    image_hash: str
    subject: str
    family: str
    case: str
    registry: str
    role: str
    partition: str
    vector: tuple
    space_id: str = SYNTHETIC_SPACE.id
    synthetic: bool = True
    capture_lower: str | None = None
    capture_upper: str | None = None
    age_min_months: int | None = None
    age_max_months: int | None = None

    def validate(self):
        for value in (self.image_hash, self.subject, self.family, self.case):
            if (
                not isinstance(value, str)
                or not value
                or len(value) > 80
                or not all(c.isalnum() or c in "-_" for c in value)
            ):
                raise QualificationError("invalid opaque identifier")
        if self.synthetic is not True or self.space_id != SYNTHETIC_SPACE.id:
            raise QualificationError("incompatible or unauthorized data")
        if (
            self.role not in {"gallery", "probe"}
            or self.registry not in {"missing", "found"}
            or self.partition not in {"development", "calibration", "test"}
        ):
            raise QualificationError("invalid partition")
        if not re.fullmatch(r"[a-f0-9]{64}", self.image_hash):
            raise QualificationError("invalid content hash")
        validate_vector(self.vector)
        if (self.capture_lower is None) != (self.capture_upper is None):
            raise QualificationError("incomplete capture interval")
        if self.capture_lower is not None and date.fromisoformat(self.capture_lower) > date.fromisoformat(
            self.capture_upper
        ):
            raise QualificationError("inverted capture interval")
        if (self.age_min_months is None) != (self.age_max_months is None):
            raise QualificationError("incomplete age interval")
        if self.age_min_months is not None and (
            type(self.age_min_months) is not int
            or type(self.age_max_months) is not int
            or not 0 <= self.age_min_months <= self.age_max_months <= 1500
        ):
            raise QualificationError("invalid age interval")


def capture_gap(a, b):
    if a.capture_lower is None or b.capture_lower is None:
        return {"kind": "unknown", "lower_days": None, "upper_days": None}
    al, au, bl, bu = [
        date.fromisoformat(x) for x in (a.capture_lower, a.capture_upper, b.capture_lower, b.capture_upper)
    ]
    low = max(0, (al - bu).days, (bl - au).days)
    high = max(abs((al - bu).days), abs((au - bl).days))
    return {"kind": "interval", "lower_days": low, "upper_days": high}


def retrieve(probe, gallery, k=50, photo_cap=3):
    if type(k) is not int or not 1 <= k <= 50 or type(photo_cap) is not int or not 1 <= photo_cap <= 10:
        raise QualificationError("invalid retrieval budget")
    probe.validate()
    if len(gallery) > 10000:
        raise QualificationError("gallery limit")
    selected = defaultdict(list)
    for row in gallery:
        row.validate()
        if row.role != "gallery" or row.partition != probe.partition or row.registry == probe.registry:
            continue
        selected[row.case].append(row)
    cases = []
    for case, rows in selected.items():
        # Content order makes photo sampling stable, before similarity is observed.
        chosen = sorted({r.image_hash: r for r in rows}.values(), key=lambda r: r.image_hash)[:photo_cap]
        pairs = [(sum(a * b for a, b in zip(probe.vector, r.vector, strict=True)), r) for r in chosen]
        score, best = min(pairs, key=lambda p: (-p[0], p[1].image_hash))
        cases.append(
            {
                "case": case,
                "score": max(-1.0, min(1.0, score)),
                "subject": best.subject,
                "gap": capture_gap(probe, best),
                "omitted_photos": len(rows) - len(chosen),
            }
        )
    return sorted(cases, key=lambda r: (-r["score"], r["case"]))[:k]


def evaluate(records, *, threshold, seed=20261025, bootstrap_samples=2000):
    if type(threshold) not in (float, int) or not math.isfinite(threshold) or not -1 <= threshold <= 1:
        raise QualificationError("explicit frozen threshold required")
    if type(bootstrap_samples) is not int or not 100 <= bootstrap_samples <= 10000 or type(seed) is not int:
        raise QualificationError("invalid bootstrap protocol")
    if not records or len(records) > 10000:
        raise QualificationError("invalid manifest size")
    partitions, seen, case_subjects = {}, set(), {}
    for r in records:
        r.validate()
        if r.image_hash in seen:
            raise QualificationError("duplicate/capture leakage")
        seen.add(r.image_hash)
        for key in ("subject:" + r.subject, "family:" + r.family):
            if key in partitions and partitions[key] != r.partition:
                raise QualificationError("identity/family split leakage")
            partitions[key] = r.partition
        if r.case in case_subjects and case_subjects[r.case] != r.subject:
            raise QualificationError("inconsistent case ground truth")
        case_subjects[r.case] = r.subject
    gallery = [r for r in records if r.role == "gallery" and r.partition == "test"]
    probes = [r for r in records if r.role == "probe" and r.partition == "test"]
    if not gallery or not probes:
        raise QualificationError("empty test gallery/probe")
    present, absent, hits, subjects, gaps = (
        [],
        [],
        {k: [] for k in (1, 10, 50)},
        defaultdict(list),
        defaultdict(int),
    )
    strata = {"capture_gap": defaultdict(list), "capture_age": defaultdict(list)}
    subject_hits = {k: defaultdict(list) for k in hits}
    wrong = 0
    for p in probes:
        ranked = retrieve(p, gallery)
        mate = any(r.subject == p.subject and r.registry != p.registry for r in gallery)
        accepted = [r for r in ranked if r["score"] >= threshold]
        wrong += sum(r["subject"] != p.subject for r in accepted)
        if not mate:
            absent.append(bool(accepted))
            continue
        present.append(any(r["subject"] == p.subject for r in accepted))
        for k, values in hits.items():
            values.append(any(r["subject"] == p.subject for r in ranked[:k]))
            subject_hits[k][p.subject].append(values[-1])
        subjects[p.subject].append(hits[1][-1])
        true_gallery = [r for r in gallery if r.subject == p.subject and r.registry != p.registry]
        pair_gaps = [capture_gap(p, r) for r in true_gallery]
        bucket = "unknown"
        if all(g["kind"] != "unknown" for g in pair_gaps):
            low = min(g["lower_days"] for g in pair_gaps)
            high = max(g["upper_days"] for g in pair_gaps)
            bucket = (
                "0-1y"
                if high <= 366
                else "1-3y"
                if 366 < low and high <= 1096
                else "3-5y"
                if 1096 < low and high <= 1827
                else "over5y"
                if low > 1827
                else "uncertain_cross_bin"
            )
        gaps[bucket] += 1
        outcome = {"recall": {str(k): hits[k][-1] for k in hits}, "tpir": present[-1]}
        strata["capture_gap"][bucket].append(outcome)
        age_bucket = "unknown"
        if p.age_min_months is not None:
            age_bucket = "uncertain_cross_bin"
            for label, low, high in [
                ("0-2y", 0, 35),
                ("3-5y", 36, 71),
                ("6-9y", 72, 119),
                ("10-13y", 120, 167),
                ("14-17y", 168, 215),
                ("over17y", 216, 1500),
            ]:
                if low <= p.age_min_months <= p.age_max_months <= high:
                    age_bucket = label
                    break
        strata["capture_age"][age_bucket].append(outcome)

    def mean(values):
        return sum(values) / len(values) if values else None

    macro = [mean(values) for _, values in sorted(subjects.items())]
    intervals = None
    if macro:
        rng = random.Random(seed)
        draws = sorted(mean([rng.choice(macro) for _ in macro]) for _ in range(bootstrap_samples))
        intervals = [
            draws[int(0.025 * bootstrap_samples)],
            draws[min(bootstrap_samples - 1, int(0.975 * bootstrap_samples))],
        ]
    stratified = {}
    for name, buckets in strata.items():
        stratified[name] = {
            bucket: {
                "mate_present": len(items),
                "recall": {str(k): mean([v["recall"][str(k)] for v in items]) for k in hits},
                "tpir": mean([v["tpir"] for v in items]),
            }
            for bucket, items in sorted(buckets.items())
        }
    return {
        "schema_version": "evaluation-1",
        "data_class": "synthetic",
        "recognition_accuracy_claim": False,
        "protocol": {
            "space_id": SYNTHETIC_SPACE.id,
            "threshold": threshold,
            "threshold_source": "synthetic_fixture_protocol_v1",
            "seed": seed,
            "bootstrap_samples": bootstrap_samples,
            "photo_cap": 3,
            "top_k": 50,
            "training_overlap": "not_applicable_weight_free_fixture",
            "ann_status": "not_run",
        },
        "manifest_digest": digest([r.__dict__ for r in records]),
        "denominators": {
            "gallery_images": len(gallery),
            "probes": len(probes),
            "mate_present": len(present),
            "mate_absent": len(absent),
            "subjects": len(subjects),
        },
        "recall": {str(k): mean(v) for k, v in hits.items()},
        "macro_recall_at_1": mean(macro),
        "macro_recall": {str(k): mean([mean(v) for v in subject_hits[k].values()]) for k in hits},
        "strata": stratified,
        "subject_bootstrap_95_recall_at_1": intervals,
        "fpir": mean(absent),
        "tpir": mean(present),
        "fnir": 1 - mean(present) if present else None,
        "false_leads_per_query": wrong / len(probes),
        "true_lead_capture_gap_counts": dict(sorted(gaps.items())),
        "limitations": [
            "geometric/vector fixtures only",
            "no child accuracy or fairness evidence",
            "no operational threshold",
            "rare-event confidence and sample-power approval pending",
        ],
    }
