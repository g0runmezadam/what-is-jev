"""Deterministic sampling.

A re-run has to be able to say *which* items it measured, and a reader has to be
able to get the same list. Python's own `hash` is salted per process and
`random.shuffle` depends on the interpreter's generator, so neither is written
down here. The order comes from a digest of the seed and the item id, which is
the same on any machine, any Python, any day.
"""

import hashlib


def _rank(seed, item_id):
    blob = ("%d:%s" % (seed, item_id)).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def deterministic_order(items, seed):
    """Every item id, ordered by its digest. The order the sample is cut from."""
    return [item["id"] for item in
            sorted(items, key=lambda it: (_rank(seed, it["id"]), it["id"]))]


def sample(items, n, seed, stratum=None):
    """*n* items, chosen the same way every time.

    Without *stratum* the first *n* of the digest order are taken. With it, the
    strata are filled round robin from their own digest orders, so a small class
    is still represented when a large one could have swallowed the sample.
    """
    ordered = sorted(items, key=lambda it: (_rank(seed, it["id"]), it["id"]))
    if n >= len(ordered):
        return ordered
    if not stratum:
        return ordered[:n]

    groups = {}
    for item in ordered:
        groups.setdefault(item.get(stratum), []).append(item)

    out = []
    names = sorted(groups, key=lambda k: (k is None, str(k)))
    while len(out) < n:
        took = False
        for name in names:
            if not groups[name]:
                continue
            out.append(groups[name].pop(0))
            took = True
            if len(out) == n:
                break
        if not took:
            break
    return sorted(out, key=lambda it: (_rank(seed, it["id"]), it["id"]))
