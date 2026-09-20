"""Export the re-run results for the public site: ``verification/tests.json``.

The site shows two kinds of record. A ``source-reported`` one relays what a
repository published, with its link, unchanged — that is everything we have not
re-run, including the tests that are not textual. A ``re-run`` one is ours: the
status, the reported number beside our own, the sample, the date, the model
version the endpoint reported, and a link to the raw answers.

Only the second kind is produced here. The first kind is assembled by the site
from this repository's own data, and mixing the two in one generator would make
it too easy to publish a relayed number wearing our badge.

``python -X utf8 verification/export_site.py``
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import report

RAW_BASE = "https://github.com/tunahansahin897/what-is-jev/blob/main/verification/results"


def record(job, summary):
    metrics = []
    for criterion in summary["criteria"]:
        metrics.append({
            "metric": criterion["metric"],
            "kind": criterion["kind"],
            "reported": criterion["reported"],
            "reported_at": criterion.get("reported_at"),
            "measured": criterion.get("observed"),
            "ci95": criterion.get("ci95"),
            "status": criterion["verdict"],
        })
    return {
        "type": "re-run",
        "id": summary["id"],
        "title": summary.get("title", summary["id"]),
        "lang": job.get("lang"),
        "lang_note": job.get("lang_note"),
        "kind": job.get("kind"),
        "kind_note": job.get("kind_note"),
        "status": summary["verdict"],
        "source": {
            "repo": summary["source"]["repo"],
            "url": summary["source"]["url"],
            "commit": summary["source"]["commit"],
            "license": summary["source"].get("license"),
            "reported_run": summary["source"].get("reported_run"),
        },
        "dataset": job.get("dataset", {}).get("name"),
        "sample": {
            "n": summary["answered"],
            "offered": summary["items_offered"],
            "rule": job.get("sample", {}).get("rule"),
            "seed": summary.get("seed"),
        },
        "run_at": summary["run_at"],
        "model_versions": summary["model_versions"],
        "calls": summary["calls"],
        "failed_calls": summary["failed"],
        "metrics": metrics,
        "deviations": job.get("deviations_known_before_the_run", []),
        "raw_url": "%s/%s/raw.jsonl" % (RAW_BASE, summary["id"]),
        "report_url": "%s/%s/REPORT.md" % (RAW_BASE, summary["id"]),
    }


def build(root=None):
    root = root or HERE
    rows = report.load(root)
    return {
        "schema": "what-is-jev/verification/tests.json",
        "version": 1,
        "note": "Test content is never translated. `lang` is the language the "
                "test was written and run in.",
        "records": [record(job, summary) for job, summary in rows],
    }


def main(root=None):
    root = root or HERE
    payload = build(root)
    path = os.path.join(root, "tests.json")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2,
                                sort_keys=True) + "\n")
    return len(payload["records"])


if __name__ == "__main__":
    print("%d record(s)" % main())
