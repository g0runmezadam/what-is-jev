**English** | [Türkçe](tr/METHODOLOGY.md)

# Methodology

What we actually did, in the order we did it. No step here is aspirational — if a step has not run yet, this page says so.

## 1. Scope: public sources only

Everything in this repository comes from material anyone can open: official documentation, public GitHub repositories, public videos, articles and posts, plus our own API calls (which we describe so you can repeat them). We do not copy third-party content into this repository — a finding or a repository entry links to its source and carries our assessment, never a reproduction of the source text. Nothing here rests on private or paywalled material. We do not publish numbers the reader cannot check. Anything we measured ourselves is either repeatable against the documented public API or left out.

## 2. Repository discovery

Two independent sets of GitHub repositories, gathered on 2026-09-19:

- **Set A — community channel.** 387 repository links shared publicly in a community channel (the raw message log is kept as a local working file, not published; a link and the sharer's comment is what we kept).
- **Set B — topic search.** `github.com/topics/jev` returned 433 repositories; 35 of those were already in set A, leaving 398 new ones.
- Combined: 785 repositories.

For each one we pulled metadata from the GitHub API (stars, forks, language, license, dates, archived/fork status, topics) and the first 12,000 characters of its README. 11 repositories in set A returned 404 (deleted or made private) — they are kept in the data with `status: gone`, not deleted, because a repository that existed and got taken down is itself a data point.

`jev` is a free-form GitHub topic. Many repositories that carry it have nothing to do with TypeSafe's model; we score those `calls_jev: no`, category `other`, and keep them rather than silently dropping them.

## 3. Scoring

Every repository is scored against the same fixed rubric ([`data/rubric.md`](data/rubric.md), `version: 1`): five axes (depth, relevance, novelty, maturity, evidence), each 0–3, for a total of 0–15, mapped to class A/B/C. The scores are a language model agent's judgment against that written rubric, not a benchmark of the code — for most repositories nobody read past the README and the metadata.

The 785 repositories were split into chunks and scored by separate agent sessions running the same rubric. Star counts play no role in any score — the rubric says so explicitly, and it is checked during the audit pass below. A repository's README is treated as data, not as instructions to the scoring agent; if a README addresses the reader as an agent, that gets recorded as a risk (embedded instruction), never acted on.

## 4. Consistency: the class-A audit

Scoring the same rubric across independent sessions did not produce consistent results: the share of class A repositories ranged from 25% to 60% session to session. Class A is also the list the ecosystem actually gets pointed to (`TOP.md`), so an inflated A class is the worst place for that inconsistency to live.

The fix we designed is a single-reviewer audit: one agent session re-reads every class-A row against the unchanged rubric, focused on the most-abused rule — the shortcut that admits a row to class A on `relevance = 3` and `novelty ≥ 2` even when its total is below 11 — and on typical inflation patterns (relevance scored 3 for a game or generic SDK, novelty scored high for the baseline pattern, evidence scored high with no numbers in the README). A reviewed row gets `audited: true` and an audit note in both languages explaining what changed or why the score was kept; a class conflict on an audited row is resolved in the auditor's favor.

**What the audit found (2026-09-19).** All 288 rows first scored as class A were re-read, README open, by one reviewer. At least one score changed in 261 of them. The most common inflation by far was **maturity** (lowered in 176 rows: most of these repositories were days old, and "tests, releases and active maintenance" cannot describe a one-day-old repository), then **novelty** (103: ports of one another repeating the baseline pattern), **evidence** (79: a quoted price or latency is not a measurement), **relevance** (64) and **depth** (41: reproductions that never call Jev). The share of rows that fell out of class A ranged from 9% to 47% depending on which scoring session had produced them. Five duplicate pairs (renamed repositories, identical READMEs) were marked and are excluded from counts.

Two things to know when reading the result. First, class A is still large, because the rubric admits a row through either of two doors — a total of 11 or more, or `relevance = 3` with `novelty ≥ 2` — and in a corpus dominated by agent gates, routers and compaction tools the second door is honestly wide. We did not change the rubric after the fact; instead [`TOP.md`](TOP.md) keeps a separate **measured core** (audited, class A, total of 13 or more) above the rest. Second, in four rows the reviewer had lowered relevance because the project runs only on hardware the reviewer did not have; that is not a property of the project, so those four relevance scores were restored and the rows re-classified by the rubric. Only audited rows appear in `TOP.md`. Rows first scored B or C were not audited. Every later update repeats this audit for the rows newly scored as class A, by a single reviewer reading the README, before they can enter `TOP.md`; each pass and its outcome is recorded in [`CHANGELOG.md`](CHANGELOG.md).

## 5. Videos

We started from one public list of 33 video sources. Automated transcripts were read for the ones that had them; the transcripts themselves are not republished here, only what we extracted from them plus a link back to the source. Of the 33: 7 turned out to be unrelated to Jev, 2 had empty transcripts, and 2 could not be fetched at all. A secondary AI-generated summary of these videos existed (from a notebook tool) and repeated vendor language uncritically ("deterministic", "90% confident means 90% right", "no verification layer needed") — we do not count that summary as evidence for anything; where a video made a claim, we went back to the transcript.

## 6. Web verification

Claims surfaced by videos or secondary write-ups were checked against their primary pages before being marked verified. The verdict labels used throughout this repository — **VERIFIED**, **VENDOR CLAIM**, **CONTESTED**, **NOT FOUND** — describe how far that check got, not how confident the claim sounds.

## 7. Honest limits

This list is deliberately longer than the one in the README, because it is the page meant for someone deciding how much to trust a specific row or claim:

- Every repository score is a language model's judgment against a written rubric — not a measurement of the project, and not something we independently re-derived except for the class-A audit above.
- For most repositories we read the description, the metadata, and the first 12,000 characters of the README. We did not read the code. A project can be meaningfully better or worse than what its README shows.
- The whole exercise is a single-day cross-section (2026-09-19). GitHub repositories, vendor documentation and pricing all change after that date; each row in `data/repos.jsonl` carries the date it was scored and the rubric version it used, precisely so a reader can tell how stale it might be.
- English and Turkish summaries and takeaways are produced together and reviewed for meaning, not translated word for word — if the two ever disagree, treat it as a bug and open an issue (see [`CONTRIBUTING.md`](CONTRIBUTING.md)).
- Star counts, follower counts and view counts never enter a score anywhere in this repository.

## 8. Staying current

`tools/update.py` finds new repositories (topic search plus `data/manual.txt`) and refreshes metadata on known ones. It calls no model and scores nothing — new repositories land in `data/pending.txt`, get scored by an agent against the current `data/rubric.md`, and are merged by `tools/build.py`, which regenerates every generated page in both languages from `data/repos.jsonl`. A repository that starts 404ing is marked `status: gone`, never deleted, so the history stays visible.

The rubric itself is versioned (`rubric_version` in every row). If the rubric changes, existing rows keep the version they were scored under until they are re-scored — a row is never silently reinterpreted under a newer rubric.

## 9. Asking for a correction

If a finding, a score, or a summary looks wrong: open an issue or a pull request with a link to the primary source that contradicts it. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the exact process — corrections are the one kind of contribution this repository depends on most, since every claim here is only as good as the source behind it.
