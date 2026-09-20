"""Run one job: ``python -X utf8 verification/run.py --job sec-injection``.

The order of operations is the point of this script. A job file, with its
acceptance rule in it, is committed first. Only then is anything sent. The git
history is what proves the rule was not written to fit the result.

Flags worth knowing:

``--dry-run``      build the items, send nothing, print what a run would cost.
``--max-calls N``  lower the job's own ceiling for this run; never raise it.
``--limit N``      cut the item list to the first N of the seeded order.
``--pause S``      seconds between calls (default 0.15).

A run can be stopped at any point and started again: answered items are skipped.
"""

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import client
import corpora
import runner
import sampling
import sources


def cache_dir(root):
    """Where third-party bytes live: outside the published tree, ignored by git."""
    return os.path.join(root, "ham", "verification-cache")


def load_job(job_id):
    path = os.path.join(HERE, "jobs", job_id + ".json")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def verify_pinned_files(job, cache):
    """Re-download every pinned file and check its digest before trusting it."""
    for ref in job.get("files", []):
        _, got = corpora.pinned_file(cache, job["source"]["repo"],
                                     job["source"]["commit"], ref["path"],
                                     ref.get("sha256"))
        print("  pinned %s %s" % (ref["path"], got[:12]))


def build(job, root):
    cache = cache_dir(root)
    verify_pinned_files(job, cache)
    adapter = sources.ADAPTERS[job["adapter"]]
    items = adapter.items(job, cache)
    wanted = int(job.get("sample", {}).get("n", len(items)))
    if wanted < len(items):
        items = sampling.sample(items, wanted, job["seed"],
                                job.get("sample", {}).get("stratum"))
    else:
        items = sorted(items, key=lambda it: it["id"])
    return adapter, items


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", required=True)
    parser.add_argument("--root", default=os.path.dirname(HERE))
    parser.add_argument("--max-calls", type=int, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--pause", type=float, default=0.15)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    job = load_job(args.job)
    adapter, items = build(job, args.root)
    if args.limit:
        items = items[:args.limit]
    if args.max_calls is not None:
        job["max_calls"] = min(job.get("max_calls", args.max_calls),
                               args.max_calls)

    print("job %s: %d items, ceiling %d" % (job["id"], len(items),
                                            job["max_calls"]))
    if args.dry_run:
        print("dry run: nothing was sent")
        print(json.dumps({"items": len(items),
                          "first_ids": [i["id"] for i in items[:5]]}, indent=2))
        return 0

    def caller(state, questions):
        out = client.call(state, questions)
        if args.pause:
            time.sleep(args.pause)
        return out

    def progress(done, total):
        if done % 25 == 0 or done == total:
            print("  %d/%d" % (done, total), flush=True)

    summary = runner.run_job(job, items, job["questions"], os.path.join(
        args.root, "verification"), caller=caller, scorer=adapter.score,
        progress=progress)

    print(json.dumps({k: summary[k] for k in
                      ("calls", "answered", "failed", "model_versions",
                       "verdict", "stopped")}, indent=2))
    for criterion in summary["criteria"]:
        print("  %-10s reported %-8s observed %-8s %s" % (
            criterion["metric"], criterion["reported"],
            _short(criterion.get("observed")), criterion["verdict"]))
    return 0


def _short(value):
    return "n/a" if value is None else "%.4f" % value


if __name__ == "__main__":
    raise SystemExit(main())
