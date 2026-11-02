"""Resolve a closed catalog before any IO. This module never downloads asset bodies."""

import json

from .records import ROOT, digest, require

PROPOSAL = ROOT / "docs/planning/demo/DEMO_ASSET_PROPOSAL.json"


def catalog():
    proposal = json.loads(PROPOSAL.read_bytes())
    return proposal["weights"], proposal["dataset"]


def inventory(rows):
    weights, data = catalog()
    expected = {v["path"]: v for v in weights["files"]}
    expected.update({p["path"]: p for g in data["groups"] for p in g["photos"]})
    require(type(rows) is list and len(rows) == 51, "inventory_size")
    actual = {}
    for row in rows:
        require(type(row) is dict and set(row) == {"ref", "source_commit", "source_blob", "bytes"},
                "inventory_closed")
        ref = row["ref"]
        require(ref in expected and ref not in actual, "inventory_membership")
        source = expected[ref]
        image = ref.startswith("images/")
        require(row["source_commit"] == (data if image else weights)["commit"]
                and row["source_blob"] == source.get("git_pointer_blob", source.get("sha"))
                and type(row["bytes"]) is int and row["bytes"] == source.get("bytes", source.get("size")),
                "inventory_identity")
        actual[ref] = row
    return actual


def source_identity():
    weights, data = catalog()
    return digest({"weights": weights, "dataset": data})
