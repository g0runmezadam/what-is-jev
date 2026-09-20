**English** | [Türkçe](tr/CONTRIBUTING.md)

# Contributing

This repository depends on corrections more than on new material — every claim in it is only as good as the source behind it. If something is wrong, say so with a link.

## Adding a repository

Criteria: **public**, **working** (not an empty skeleton), and either actually calling the Jev/System-1 API, or genuinely researching/measuring Jev (a benchmark, a calibration study, a critique — it does not have to call the API itself). A repository that merely carries the `jev` GitHub topic without being about TypeSafe's model does not qualify; see `calls_jev` in [`data/SCHEMA.md`](data/SCHEMA.md).

Two ways to add one:

1. **Issue or pull request** with the repository URL and one sentence on what it does. It gets scored against the current [`data/rubric.md`](data/rubric.md) and merged by `tools/build.py`.
2. **`data/manual.txt`** — add one `owner/name` per line (see the format already in the file). `tools/update.py` picks these up the same way it picks up the topic search, downloads metadata and README, and queues it in `data/pending.txt` for scoring.

Do not open a PR that edits `REPOS.md`, a `categories/*.md` page, `TOP.md`, or `SOURCES.md` directly — they are generated (first line: `<!-- GENERATED — do not edit; run tools/build.py -->`) and any hand edit will be overwritten by the next build.

## Disputing a score

Open an issue naming the repository and the row's `total`/`class`, with a link to the evidence that changes the picture — e.g. a README section the scorer missed, a benchmark the "evidence" score should reflect, or a reason `relevance`/`novelty` was over- or under-stated against [`data/rubric.md`](data/rubric.md). A score changes only with a stated reason tied to the rubric, not because the number "feels wrong" — say which axis, and why.

## Adding a source

Add a line to `data/sources.jsonl` with a required `url` (must be `http://` or `https://`) plus `type`, `title`, `author`, `date`, `trust` (1–5) and a short note. See the field list and trust-level guide in [`data/SCHEMA.md`](data/SCHEMA.md#sourcesjsonl). A source with no working link will not be accepted — this repository does not cite anything a reader cannot go open.

## Disputing a finding

Open an issue quoting the line in [`FINDINGS.md`](FINDINGS.md) and linking the primary source that contradicts or qualifies it. "I don't think this is right" without a source will not change a verdict label; a competing primary source will.

## Editing generated pages

Never by hand. `REPOS.md`, `TOP.md`, `SOURCES.md`, every file under `categories/`, and their `tr/` counterparts are produced by `tools/build.py` from `data/repos.jsonl` and `data/sources.jsonl`. If a generated page looks wrong, the fix is either a data correction (see above) or a bug in `tools/build.py` itself — file the latter as a normal code issue.

## Running the tests

Before submitting a change to `tools/`, `data/`, or the schema:

```
python tools/build.py --check          # generated pages must already match the data
python -X utf8 -m unittest discover -s tests
```

Both must pass. `--check` writes nothing and exits non-zero if any generated page is stale relative to `data/`; the test suite covers schema validation, the legacy import rules, determinism (same input → byte-identical output), and that the English and Turkish page sets match exactly.
