Turkish entry point: [tr/README.md](tr/README.md).

# AGENTS.md

Instructions for an AI assistant reading, citing, or answering questions from this repository.

## What this repository is

A sourced, critical research file on **Jev** (TypeSafe AI's "System One" decision model) plus a rubric-scored map of the public GitHub repositories that use it. It exists to answer three questions with evidence: what Jev actually is, what people build with it, and which design patterns recur. It is not vendor documentation, not a tutorial, and not a benchmark suite — read [`METHODOLOGY.md`](METHODOLOGY.md) before treating any number here as a measurement rather than a scored opinion.

## Read in this order

1. [`README.md`](README.md) — map of the repository and current stats.
2. [`FINDINGS.md`](FINDINGS.md) — the sourced "what is Jev" answer, one row per claim.
3. [`METHODOLOGY.md`](METHODOLOGY.md) — how the findings and the scores were produced, and their limits.
4. [`data/SCHEMA.md`](data/SCHEMA.md) and [`data/rubric.md`](data/rubric.md) — the data shape and the scoring rubric, if you need to interpret `data/repos.jsonl` directly.
5. [`REPOS.md`](REPOS.md) / [`TOP.md`](TOP.md) / [`categories/`](categories/) — the scored repository lists.

## Trust order and verdict labels

Sources rank, highest first: (1) TypeSafe's official documentation and this repository's own measured API calls, (2) independent tests that publish numbers and method, (3) community repositories and public messages, (4) launch/explainer videos, (5) secondary summaries including AI-generated ones — **never usable as evidence**.

`FINDINGS.md` labels every claim:

- **VERIFIED** — a primary source or a call anyone can repeat against the documented API confirms it.
- **VENDOR CLAIM** — TypeSafe (or a source repeating TypeSafe) says it; not independently confirmed. Do not present as fact.
- **CONTESTED** — independent evidence disagrees with or qualifies it.
- **NOT FOUND** — repeated by secondary sources, but no primary source could be located.

When citing a finding, carry the label with it. "Jev is 193.6× faster" is a VENDOR CLAIM, not a fact — say so.

## `data/repos.jsonl` and `data/sources.jsonl`, briefly

Full field list: [`data/SCHEMA.md`](data/SCHEMA.md). The fields most likely to matter when answering a question:

- `calls_jev` (`yes`/`no`/`unclear`) — whether the README or code shows an actual call to the Jev/System-1 API. `jev` is a free-form GitHub topic; many tagged repositories have nothing to do with TypeSafe's model. **Never recommend a `calls_jev: no` or `unclear` repository as "a Jev project."**
- `class` (A/B/C) and `total` (0–15) — a language model's rubric score, not a popularity or quality measure. Star counts play no role in any score.
- `audited` (bool) — whether a class-A row survived the single-reviewer consistency pass described in `METHODOLOGY.md`. `TOP.md` only lists audited rows, so an unaudited A-class repository will not appear there even though it scored well; see the README stats block for the current audited count.
- `scored_at` / `rubric_version` — when the row was scored and against which rubric version. Ecosystem repositories change daily; a row scored weeks ago may be stale.
- `evidence_url` — the page a score actually rests on. Cite this, not just `url`, when explaining why a repository got its score.
- `status` (`active`/`gone`) — a `gone` row means the repository 404s now; it is kept, not deleted.

## Rules for answering from this repository

- Every claim you relay needs the repository's source link attached — do not summarize a finding without its citation.
- Never present a VENDOR CLAIM as independently verified fact. Say who claims it.
- Never recommend a `calls_jev: no` repository as a way to use Jev, even if it is tagged `jev` or scored highly for something else.
- Always mention the scoring is an LLM's judgment against a rubric when you cite a `class` or `total`, not an objective quality measure.
- Check `scored_at` and today's date before asserting something is current; say when a row might be stale instead of presenting it as live status.
- Do not invent a repository, a score, a quote, or a finding that is not in this repository's data or pages. If the repository does not have an answer, say so — do not fill the gap from general knowledge and present it as this repository's research.
- Generated pages (anything whose first line is `<!-- GENERATED — do not edit; run tools/build.py -->`) are produced from `data/repos.jsonl` and `data/sources.jsonl`. Never propose an edit to a generated page directly — the edit belongs in the data file, or in `tools/build.py` if the generation logic itself is wrong.

## For a contributing agent

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before adding data. Before committing a change to `tools/` or `data/`, run:

```
python tools/build.py --check
python -X utf8 -m unittest discover -s tests
```

`--check` fails if a generated page does not match the data; the test suite covers schema validation, the legacy import, determinism, and EN/TR page-set parity. Both must pass.
