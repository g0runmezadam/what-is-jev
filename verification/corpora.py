"""Loading the public corpora a job runs on, without cloning anybody's repository.

Two rules hold everywhere in this module.

**Nothing is executed.** A source repository is read, never run. Its question
wording and, where a job needs it, its committed per-sample output are pulled as
files from ``raw.githubusercontent.com`` pinned to a commit, so the bytes a
reader downloads tomorrow are the bytes this run used.

**Nothing third-party is stored inside the repository.** Everything lands in a
cache folder that is ignored by git. What the repository keeps is an item id and
a digest.
"""

import hashlib
import json
import os
import urllib.parse
import urllib.request

ROWS_API = "https://datasets-server.huggingface.co/rows"
RAW_HOST = "https://raw.githubusercontent.com"
PAGE = 100
AGENT = {"User-Agent": "what-is-jev-verification"}


def get(url, timeout=120):
    request = urllib.request.Request(url, headers=AGENT)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def sha256(blob):
    return hashlib.sha256(blob).hexdigest()


def raw_url(repo, commit, path):
    """A URL pinned to a commit. A branch name would not be a pin."""
    return "/".join([RAW_HOST, repo, commit, path])


def pinned_file(cache_dir, repo, commit, path, expected=None):
    """Download one file from a pinned commit into the cache and check it.

    An expected digest is compared when the job carries one; the digest of what
    actually arrived is always returned, so the first run can write it down.
    """
    os.makedirs(cache_dir, exist_ok=True)
    name = "%s@%s@%s" % (repo.replace("/", "@"), commit[:12],
                         path.replace("/", "~"))
    target = os.path.join(cache_dir, name)
    if os.path.exists(target):
        with open(target, "rb") as handle:
            blob = handle.read()
    else:
        blob = get(raw_url(repo, commit, path))
        with open(target, "wb") as handle:
            handle.write(blob)
    got = sha256(blob)
    if expected and got != expected:
        raise ValueError("%s: digest does not match the pinned one" % path)
    return blob, got


def _cached_json(cache_dir, name, produce):
    os.makedirs(cache_dir, exist_ok=True)
    target = os.path.join(cache_dir, name)
    if os.path.exists(target):
        with open(target, encoding="utf-8") as handle:
            try:
                return json.load(handle)
            except ValueError:
                pass
    rows = produce()
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(rows, handle, ensure_ascii=False)
    return rows


def dataset_rows(cache_dir, dataset, splits, config="default"):
    """Every row of the named splits, paged the way the source pages them."""
    safe = dataset.replace("/", "@")

    def produce():
        out = []
        for split, total in splits:
            for offset in range(0, total, PAGE):
                query = urllib.parse.urlencode({
                    "dataset": dataset, "config": config, "split": split,
                    "offset": offset, "length": min(PAGE, total - offset)})
                page = json.loads(get(ROWS_API + "?" + query).decode("utf-8"))
                for entry in page.get("rows", []):
                    row = dict(entry.get("row") or {})
                    row["_split"] = split
                    row["_index"] = entry.get("row_idx")
                    out.append(row)
        return out

    return _cached_json(cache_dir, safe + ".json", produce)
