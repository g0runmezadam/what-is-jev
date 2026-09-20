**English** | [Türkçe](tr/README.md)

# What is Jev?

A sourced, critical research file on **Jev** — TypeSafe AI's "System One" decision model — plus a rubric-scored map of what people are actually building with it.

Jev does not write text. You give it a state and typed questions (**choice**, **score**, **noul** = yes/no); it returns probabilities. That makes it cheap, fast and easy to wire into software — and also easy to over-sell. This repository tries to answer three questions with evidence instead of enthusiasm:

1. **What is Jev, really?** Which claims are verified, which are vendor marketing repeated by others, and which contradict each other → [`FINDINGS.md`](FINDINGS.md)
2. **What are people building with it?** Every public GitHub repository we could find (the current count is in the table below), each scored on the same fixed rubric → [`REPOS.md`](REPOS.md), best-in-class in [`TOP.md`](TOP.md), browsable by [category](categories/)
3. **Which design patterns keep recurring — and which are backed by measurements?** → [`PATTERNS.md`](PATTERNS.md)

> **Everything here comes from publicly available sources** — official documentation, public GitHub repositories, public videos, articles and posts — plus our own API calls, which we describe so you can repeat them. **Every claim and every entry links to its source.** Nothing is taken from private or paywalled material, and we do not republish third-party content: you get the link and our assessment, not a copy. The full source list, with URLs and a trust level for each, is in [`SOURCES.md`](SOURCES.md).

We are not affiliated with TypeSafe AI. This is independent research.

**This repository is updated continuously.** New Jev repositories appear every day; we pick them up, score them with the same rubric, re-check the top class, and add new sources and findings as they are verified. The "Data as of" date below tells you how fresh the numbers are, and [`CHANGELOG.md`](CHANGELOG.md) lists what changed in each update.

<!-- STATS:START -->
| Number | Value |
|---|---|
| Repositories | 933 |
| Calls Jev | yes 627 · no 273 · unclear 33 |
| Classes | A 269 · B 297 · C 367 |
| Audited | 347 |
| Sources | 90 |
| Data as of | 2026-09-20 |

**Top categories**

- [Other](categories/other.md) — 187
- [Classification and triage](categories/classification-triage.md) — 106
- [SDKs and clients](categories/sdk-client.md) — 83
- [Evaluation and benchmarks](categories/eval-benchmark.md) — 80
- [Agent gates](categories/agent-gate.md) — 58
- [Code review hooks](categories/code-review-hook.md) — 55
- [Games and demos](categories/game-demo.md) — 55
- [Lists and directories](categories/list-directory.md) — 52
<!-- STATS:END -->

## How to read this repository

| If you want… | Go to |
|---|---|
| The short, sourced answer to "what is Jev?" | [`FINDINGS.md`](FINDINGS.md) |
| Every source we used, with links and trust levels | [`SOURCES.md`](SOURCES.md) |
| How we scored repositories, and the limits of that method | [`METHODOLOGY.md`](METHODOLOGY.md), [`data/rubric.md`](data/rubric.md) |
| The strongest projects, by category | [`TOP.md`](TOP.md) |
| All repositories in one category (agent gates, routers, compaction, …) | [`categories/`](categories/) |
| Recurring design patterns with evidence | [`PATTERNS.md`](PATTERNS.md) |
| Machine-readable data | [`data/repos.jsonl`](data/repos.jsonl), [`data/sources.jsonl`](data/sources.jsonl), schema in [`data/SCHEMA.md`](data/SCHEMA.md) |
| To hand this repository to your own AI assistant | [`llms.txt`](llms.txt) and [`AGENTS.md`](AGENTS.md) |
| To add a repository or correct an entry | [`CONTRIBUTING.md`](CONTRIBUTING.md) |

## Source trust order

When sources disagree, we rank them like this — and say so next to each finding:

1. TypeSafe's official documentation, and our own real API calls
2. Independent tests that publish their numbers and method
3. Community repositories and public messages
4. Launch and explainer videos (most repeat the vendor's figures)
5. Secondary summaries (including AI-generated ones) — **never used as evidence**

## Honest limits

- Repository scores are **an LLM's judgment against a written rubric**, reviewed by a second pass for the top class. They are not benchmarks of the projects themselves.
- For most repositories we read the description, metadata and the **first 12,000 characters of the README** — not the code. A project can be better or worse than its README.
- "Calls Jev" means the README or code shows a real call to the Jev / System One API. `jev` is a free-form GitHub topic; many tagged repositories have nothing to do with TypeSafe's model, and we mark them as such rather than dropping them.
- **Star counts never affect a score.**
- Jev is not deterministic from call to call, and vendor accuracy figures measure agreement with judge models, not ground truth. Details and links in [`FINDINGS.md`](FINDINGS.md).
- The ecosystem moves daily. Each entry carries the date it was scored and the rubric version used.

## Staying current

New Jev repositories appear every day. `tools/update.py` discovers them (GitHub topic search plus manually submitted links) without calling any model; new entries are then scored with the same rubric and merged by `tools/build.py`, which regenerates every list page in both languages from `data/repos.jsonl`. Generated pages are never edited by hand. Entries for deleted repositories are kept and marked `gone`.

## Languages

English is the default. A full Turkish version lives under [`tr/`](tr/README.md). Both are generated from the same data, so they cannot drift apart.
