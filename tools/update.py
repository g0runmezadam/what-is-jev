#!/usr/bin/env python3
"""Find new Jev repositories and refresh the metadata of the known ones.

    python tools/update.py [--topic jev] [--limit 1000] [--no-readme]

This script never calls a model and never scores anything. It only:

* asks ``gh api`` for ``topic:<topic>`` and reads ``data/manual.txt``,
* writes the repositories that ``data/repos.jsonl`` does not know yet to
  ``data/pending.txt`` and downloads their metadata plus the first 12K of
  their README into ``ham/`` (git-ignored, never published),
* refreshes ``meta`` on the known rows,
* marks a row that answers 404 as ``status: gone`` - the row is kept.

Scoring is a separate step: an agent scores ``data/pending.txt`` with
``data/rubric.md`` into ``data/incoming/*.jsonl`` and ``tools/build.py``
imports that.

The ``gh`` subprocess is injected (``runner``) so the tests stay offline.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build  # noqa: E402  (same directory)

README_LIMIT = 12000
PER_PAGE = 100

#: How many times a rate-limited search is tried again, and how long we wait
#: in between. The wait is injected in the tests so they stay instant.
SEARCH_RETRIES = 2
SEARCH_BACKOFF = (20, 60)

RATE_LIMIT = re.compile(r"rate limit|HTTP 403|HTTP 429|abuse detection|"
                        r"secondary rate", re.IGNORECASE)

#: A repository name and nothing else. No backslash, no "..", no path.
#: \Z, not $: "a/one\n" is not a repository name.
REPO_NAME = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9._-]+\Z")


def valid_repo_name(name):
    """True only for ``owner/name``: what GitHub allows and nothing more."""
    if not isinstance(name, str) or not REPO_NAME.match(name):
        return False
    if ".." in name or "\\" in name:
        return False
    return True


def ham_path(root, kind, filename):
    """A path under ``ham/<kind>/``. Raises when the result escapes ham/."""
    base = os.path.realpath(os.path.join(root, "ham"))
    target = os.path.realpath(os.path.join(base, kind, filename))
    if target != base and not target.startswith(base + os.sep):
        raise ValueError("ham/ dışına yazma denemesi: %r" % filename)
    return target


def gh_runner(args):
    """Default runner: really call ``gh``. Returns (code, stdout, stderr)."""
    proc = subprocess.run(["gh"] + list(args), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def _search_page(runner, topic, page, sleep):
    """One page of results as (items, ok). ``ok`` is False when gh failed."""
    attempt = 0
    while True:
        code, out, err = runner([
            "api", "-X", "GET", "search/repositories",
            "-f", "q=topic:%s" % topic,
            "-f", "per_page=%d" % PER_PAGE,
            "-f", "page=%d" % page,
        ])
        if code == 0:
            try:
                return (json.loads(out) or {}).get("items") or [], True
            except ValueError:
                # a truncated body is a failed search, not an empty one
                return [], False
        if attempt < SEARCH_RETRIES and RATE_LIMIT.search(err or out or ""):
            sleep(SEARCH_BACKOFF[min(attempt, len(SEARCH_BACKOFF) - 1)])
            attempt += 1
            continue
        return [], False


def search_topic(runner, topic="jev", limit=1000, sleep=None):
    """(pairs, ok). A failed search is never an empty one: ``ok`` says which.

    Telling the two apart is the whole point. An empty answer means "no new
    repository"; a rate-limited one means "we do not know", and treating it
    as the first would wipe data/pending.txt.
    """
    sleep = sleep or time.sleep
    found = []
    seen = set()
    page = 1
    while len(found) < limit:
        items, ok = _search_page(runner, topic, page, sleep)
        if not ok:
            return [], False
        if not items:
            break
        for item in items:
            name = item.get("full_name")
            if name and name.lower() not in seen:
                seen.add(name.lower())
                found.append((name, item))
        if len(items) < PER_PAGE:
            break
        page += 1
    return found[:limit], True


def fetch_repo(runner, repo):
    """(payload, gone). ``gone`` is True when GitHub answered 404."""
    code, out, err = runner(["api", "repos/" + repo])
    if code != 0:
        return None, "404" in (err or "") or "Not Found" in (err or "")
    try:
        return json.loads(out), False
    except ValueError:
        return None, False


def fetch_readme(runner, repo):
    code, out, _err = runner(["api", "repos/%s/readme" % repo,
                              "-H", "Accept: application/vnd.github.raw"])
    if code != 0:
        return None
    return out


def meta_from_payload(payload):
    license_field = payload.get("license")
    if isinstance(license_field, dict):
        license_field = license_field.get("spdx_id") or license_field.get("key")
    topics = payload.get("topics")
    return {
        "description": payload.get("description"),
        "stars": payload.get("stargazers_count"),
        "forks": payload.get("forks_count"),
        "language": payload.get("language"),
        "license": license_field,
        "created_at": payload.get("created_at"),
        "pushed_at": payload.get("pushed_at"),
        "archived": payload.get("archived"),
        "fork": payload.get("fork"),
        "topics": list(topics) if isinstance(topics, list) else [],
    }


def read_manual(path):
    return build.read_lines(path)


def run(root, runner=None, topic="jev", limit=1000, want_readme=True, sleep=None):
    """Do one update pass. Returns a report dict; writes no page."""
    runner = runner or gh_runner
    data_dir = os.path.join(root, "data")
    repos_path = os.path.join(data_dir, "repos.jsonl")
    records, _errors = build.read_jsonl(repos_path)
    known = {r.get("repo", "").lower(): r for r in records}

    report = {"new": [], "refreshed": [], "gone": [], "unreachable": [],
              "rejected": [], "search_failed": False}

    found, ok = search_topic(runner, topic=topic, limit=limit, sleep=sleep)
    if not ok:
        # We do not know what is out there. Writing pending.txt now would
        # throw away the list we already have, so nothing is written at all.
        report["search_failed"] = True
        return report

    candidates = []
    seen = set()
    for name, _payload in found:
        if name.lower() not in seen:
            seen.add(name.lower())
            candidates.append(name)
    for name in read_manual(os.path.join(data_dir, "manual.txt")):
        if name.lower() not in seen:
            seen.add(name.lower())
            candidates.append(name)

    safe = []
    for name in candidates:
        if valid_repo_name(name):
            safe.append(name)
        else:
            report["rejected"].append(name)

    new = sorted((n for n in safe if n.lower() not in known), key=str.lower)
    report["new"] = new

    # metadata for the newcomers goes to ham/ (git-ignored), never to data/
    for name in new:
        payload, gone = fetch_repo(runner, name)
        if payload is None:
            report["unreachable"].append(name)
            continue
        flat = name.replace("/", "@")
        build.write_text(
            ham_path(root, "meta", flat + ".json"),
            json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=1) + "\n")
        if want_readme:
            body = fetch_readme(runner, name)
            if body:
                build.write_text(ham_path(root, "readme", flat + ".md"),
                                 body[:README_LIMIT])

    build.write_text(os.path.join(data_dir, "pending.txt"),
                     "".join(name + "\n" for name in new))

    for rec in records:
        if not valid_repo_name(rec.get("repo")):
            report["rejected"].append(rec.get("repo"))
            continue
        payload, gone = fetch_repo(runner, rec["repo"])
        if gone:
            if rec.get("status") != "gone":
                rec["status"] = "gone"
            report["gone"].append(rec["repo"])
            continue
        if payload is None:
            report["unreachable"].append(rec["repo"])
            continue
        rec["meta"] = meta_from_payload(payload)
        rec["status"] = "active"
        report["refreshed"].append(rec["repo"])

    records.sort(key=lambda r: r.get("repo", "").lower())
    build.write_text(repos_path, build.dump_jsonl(records))
    return report


def main(argv=None, root=None, runner=None, sleep=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--topic", default="jev")
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--no-readme", action="store_true")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    if root is None:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report = run(root, runner=runner, topic=args.topic, limit=args.limit,
                 want_readme=not args.no_readme, sleep=sleep)
    if report["search_failed"]:
        print("HATA: arama başarısız (gh hata verdi ya da kota doldu). "
              "data/pending.txt'e dokunulmadı, hiçbir şey yazılmadı.")
        return 1
    print("yeni: %d, tazelenen: %d, kayıp: %d, ulaşılamayan: %d, reddedilen: %d"
          % (len(report["new"]), len(report["refreshed"]),
             len(report["gone"]), len(report["unreachable"]),
             len(report["rejected"])))
    for name in report["new"]:
        print("  yeni: " + name)
    for name in report["rejected"]:
        print("  reddedildi (repo adı değil): %r" % (name,))
    return 0


if __name__ == "__main__":
    sys.exit(main())
