"""The job runner: one item, one request, one line on disk.

Three things the runner is built around.

**A line is written before the next call is made.** A run of several hundred
items on somebody else's budget must survive being killed. The raw file is
append-only and is re-read at the start of the next run, so an interrupted job
resumes instead of paying twice.

**The raw file carries no third-party text.** An item is identified by its id and
the digest of its text, and the request by the digest of its body. That is enough
to prove which item produced which answer, and it copies nobody's corpus into a
public repository.

**The ceiling is hard.** ``max_calls`` is counted in the runner, not in a comment.
A job that would exceed it stops, records what it has, and says so.
"""

import datetime
import hashlib
import json
import os

import stats

RAW = "raw.jsonl"
SUMMARY = "summary.json"


def digest(value):
    blob = value if isinstance(value, bytes) else str(value).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def body_digest(state, questions):
    """A digest of the request, so a reader can tell two runs apart."""
    return digest(json.dumps({"state": state, "questions": questions},
                             ensure_ascii=False, sort_keys=True))


def read_raw(path):
    """Every complete record in the raw file. A torn line is dropped."""
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if isinstance(record, dict) and record.get("item"):
                out.append(record)
    return out


def repair_raw(path):
    """Rewrite the raw file with only its complete records.

    A killed run leaves half a line behind. Appending after it would glue the
    next record onto the wreck and lose both, so the file is squared up before
    anything is added to it.
    """
    records = read_raw(path)
    if not os.path.exists(path):
        return records
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) == len(records) and text.endswith("\n"):
        return records
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False,
                                    sort_keys=True) + "\n")
    return records


def answered_ids(records):
    """The items that already have an answer. A failed item is tried again."""
    return {r["item"] for r in records if r.get("ok")}


def overall(verdicts):
    """The weakest verdict of the parts. No criterion is allowed to be carried."""
    if not verdicts:
        return stats.NOT_RUN
    return max(verdicts, key=lambda v: stats.RANK.get(v, 3))


def run_job(job, items, questions, root, caller, scorer=None, progress=None,
            today=None):
    """Run *items* through *caller*, appending to the job's raw file.

    *caller* has the signature of :func:`client.call`; the tests pass a fake one
    and no live run happens inside the test suite.
    """
    folder = os.path.join(root, "results", job["id"])
    os.makedirs(folder, exist_ok=True)
    raw_path = os.path.join(folder, RAW)

    records = repair_raw(raw_path)
    done = answered_ids(records)
    ceiling = int(job.get("max_calls", 0))
    spent = 0
    stopped = None

    for item in items:
        if item["id"] in done:
            continue
        if spent >= ceiling:
            stopped = "call ceiling reached"
            break
        response = caller(item["state"], questions)
        spent += 1
        record = {
            "item": item["id"],
            "item_sha256": item.get("text_sha256"),
            "label": item.get("label"),
            "group": item.get("group"),
            "request_sha256": body_digest(item["state"], questions),
            "ok": bool(response.get("ok")),
            "status": response.get("status"),
            "reason": response.get("reason"),
            "detail": response.get("detail") or "",
            "model": response.get("model"),
            "latency_ms": response.get("latency_ms"),
            "answers": response.get("answers") or {},
        }
        with open(raw_path, "a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, ensure_ascii=False,
                                    sort_keys=True) + "\n")
        records.append(record)
        if progress:
            progress(len(records), len(items))

    good = [r for r in records if r.get("ok")]
    measured = (scorer or (lambda records, items: {}))(good, items)
    criteria = []
    for criterion in job.get("criteria", []):
        judged = dict(criterion)
        judged.update(stats.judge(criterion, measured))
        criteria.append(judged)

    summary = {
        "id": job["id"],
        "title": job.get("title", job["id"]),
        "source": job["source"],
        "lang": job.get("lang"),
        "seed": job.get("seed"),
        "run_at": (today or datetime.date.today().isoformat()),
        "items_offered": len(items),
        # Every raw line is one request that left this machine, across every
        # run of this job. The budget is counted from here, so a resumed job
        # must not forget what the run before it spent.
        "calls": len(records),
        "calls_this_run": spent,
        "answered": len(good),
        "failed": len(records) - len(good),
        "max_calls": ceiling,
        "stopped": stopped,
        "model_versions": sorted({r["model"] for r in good if r.get("model")}),
        "measured": measured,
        "criteria": criteria,
        "verdict": overall([c["verdict"] for c in criteria]),
    }
    with open(os.path.join(folder, SUMMARY), "w", encoding="utf-8",
              newline="\n") as handle:
        handle.write(json.dumps(summary, ensure_ascii=False, indent=2,
                                sort_keys=True) + "\n")
    return summary
