"""Permanent source-lineage lookup excludes pairings, scores, model and authorization IDs."""

from .plans import catalog
from .records import decode, digest, require, schema


def validate_plan(raw):
    plan = decode(raw, ceiling=131072, depth=6, arrays=48)
    schema(plan, "fixture-plan.schema.json")
    require(type(plan["schema_version"]) is int and type(plan["metadata_version"]) is int, "fixture_version")
    _, data = catalog()
    expected = {p["path"]: (g, p) for g in data["groups"] for p in g["photos"]}
    images = {}
    for row in plan["images"]:
        ref = row["image_ref"]
        require(ref in expected and ref not in images, "fixture_membership")
        group, source = expected[ref]
        require(row["expected_git_pointer_blob"] == source["git_pointer_blob"]
                and row["expected_lfs_sha256"] == source["publisher_sha256"]
                and type(row["expected_bytes"]) is int and row["expected_bytes"] == source["bytes"],
                "fixture_source")
        require(row["fictional_group"] == group["fictional_group"], "fixture_group")
        for field in ["capture_date", "capture_age_months"]:
            bounds = row[field]
            if bounds["status"] != "unknown":
                low, high = bounds["lower"], bounds["upper"]
                require(type(low) is type(high) and low <= high, "fixture_interval")
                if field == "capture_age_months":
                    require(type(low) is int and type(high) is int, "fixture_age")
                if bounds["status"] == "exact":
                    require(low == high, "fixture_exact")
            else:
                require(bounds["basis"] == "not_known", "fixture_unknown")
        images[ref] = row
    seen, groups = set(), set()
    for link in plan["pairings"]:
        a, b = link["left_image_ref"], link["right_image_ref"]
        require(a != b and a in images and b in images and a not in seen and b not in seen, "fixture_pair")
        require(link["fictional_group"] not in groups and images[a]["fictional_group"]
                == images[b]["fictional_group"] == link["fictional_group"], "fixture_pair_group")
        require(images[a]["partition"] == images[b]["partition"]
                and images[a]["enrollment"] == images[b]["enrollment"], "fixture_split")
        seen.update([a, b])
        groups.add(link["fictional_group"])
    require(seen == set(expected), "fixture_coverage")
    return plan


def lineage_key(plan):
    # Fixed approved upstream lineage, not caller-selected labels, bytes, model/space or epoch.
    _, data = catalog()
    return digest({"project": "find-our-child", "repository": data["repository"], "commit": data["commit"],
                   "images": sorted(p["path"] for g in data["groups"] for p in g["photos"])})


def freeze(tx, plan, derivatives):
    require(set(derivatives) == {p["image_ref"] for p in plan["images"]}, "fixture_derivatives")
    for value in derivatives.values():
        require(type(value) is str and len(value) == 64 and all(c in "0123456789abcdef" for c in value),
                "fixture_derivative_hash")
    key = lineage_key(plan)
    seal = {"plan_sha256": digest(plan), "derivatives": derivatives}
    prior = tx.get("exposure", key)
    require(prior is None or prior == seal, "fixture_permanent_freeze")
    if prior is None:
        tx.put("exposure", key, seal)
        tx.audit("first_image_boundary", key)
    return key


def outcomes(plan, rows):
    require(type(rows) is list and len(rows) == 48, "outcome_denominator")
    allowed = {"no_face", "multiple_faces", "failed", "withdrawn", "success"}
    require({r.get("ref") for r in rows} == {r["image_ref"] for r in plan["images"]}
            and all(set(r) == {"ref", "outcome"} and r["outcome"] in allowed for r in rows),
            "outcome_membership")
    return rows
