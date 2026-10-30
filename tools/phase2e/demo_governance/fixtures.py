"""Blinded fictional fixture decisions. No pixels, model scores or identities here."""

from .records import canonical, digest, require, sha, time_value


def seal_review(images, links, partitions, *, fixture, previous=None, score_seen=False):
    """Freeze complete 48/24 selection. Same-manifest renewal is not fresh review.

    Human content review and signature remain separate. This validates only
    completeness/immutability; engineering cannot supply an actual F judgment.
    """
    require(
        type(images) is list and len(images) == 48 and type(links) is list and len(links) == 24,
        "fixture_inventory",
    )
    require(
        all(
            type(x) is dict
            and set(x) == {"id", "sha256", "decision", "reviewed"}
            and sha(x["sha256"])
            and x["decision"] in {"approved", "hold", "rejected"}
            for x in images
        ),
        "image_decisions",
    )
    names = {x["id"] for x in images}
    require(
        len(names) == 48
        and all(
            type(x) is dict
            and set(x) == {"left", "right", "decision"}
            and x["left"] in names
            and x["right"] in names
            and x["left"] != x["right"]
            and x["decision"] in {"fictional_link", "hold", "rejected"}
            for x in links
        ),
        "link_decisions",
    )
    require(
        len({(x["left"], x["right"]) for x in links}) == 24
        and len([v for x in links for v in [x["left"], x["right"]]]) == len(names)
        and {v for x in links for v in [x["left"], x["right"]]} == names,
        "link_inventory",
    )
    require(
        type(partitions) is dict
        and set(partitions) == {"gallery", "query"}
        and set(partitions["gallery"]).isdisjoint(partitions["query"])
        and set(partitions["gallery"]) | set(partitions["query"]) == names,
        "fixture_partition",
    )
    for image in images:
        time_value(image["reviewed"])
    raw = canonical({"images": images, "links": links, "partitions": partitions})
    require(digest(raw) == fixture, "fixture_identity")
    require(not score_seen or (previous is not None and raw == previous), "score_informed_change")
    return raw
