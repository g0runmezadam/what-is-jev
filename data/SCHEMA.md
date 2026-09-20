# data/ — the single source of truth

Everything under the repository root and under `tr/` that is marked
`GENERATED` is produced from the two files in this directory by
`python tools/build.py`. Edit the data, never the generated page.

| File | What it is | Who writes it |
|---|---|---|
| `repos.jsonl` | one scored repository per line | `tools/build.py --import-legacy`, then agents through `data/incoming/*.jsonl` |
| `sources.jsonl` | one source per line | by hand |
| `schema/repo.schema.json` | machine-readable shape of a `repos.jsonl` line | by hand |
| `schema/source.schema.json` | machine-readable shape of a `sources.jsonl` line | by hand |
| `rubric.md` / `../tr/data/rubric.md` | the scoring rubric, `version: 1` | by hand |
| `manual.txt` | repositories to pick up that the topic search misses | by hand |
| `pending.txt` | what `tools/update.py` found and nobody has scored yet | `tools/update.py` |
| `incoming/*.jsonl` | freshly scored rows waiting to be merged | agents |
| `incoming/applied/` | batches already merged (git-ignored) | `tools/build.py` |
| `audits/*.jsonl` | audit results waiting to be merged | the auditor |
| `audits/applied/` | audit files already merged (git-ignored) | `tools/build.py` |
| `applied-batches.jsonl` | one line per file already merged: `name`, `sha256`, `applied_at`, and `kind` for an audit | `tools/build.py` |

## data/incoming — new scores arrive here

An incoming line is a **complete** `repos.jsonl` row in English field names,
and it is held to exactly the rules a stored row is held to — the same
validation function checks both. A line with a missing field, an unknown
field or a bad value fails the build, and nothing from any batch is applied —
a half-merged batch would leave the data in a state no file on disk
describes. "A bad value" includes a date that is not a real calendar day, a
`rubric_version` that is not a known version of the rubric, a `meta` object
that is not the ten GitHub fields, a score outside 0–3, a `total` that is not
the sum, a link that is not http(s), and any text carrying markup or private
data.

* A repository the data does not know is added, with `first_seen` taken from
  the row's `scored_at`.
* A repository it does know keeps `first_seen`, `audit_note_en`,
  `audit_note_tr`, `duplicate_of` and `audited_at`; the scores, texts, category and
  `calls_jev` are overwritten, `scored_at` moves forward, and `audited`
  becomes false — the new numbers have not been through a second pass.
* A row **older** than the score already stored (an earlier `scored_at`) is
  not applied. The run names it and carries on: an old score never overwrites
  a newer one.
* After a successful merge `data/repos.jsonl` and `data/applied-batches.jsonl`
  are replaced in one step, and only then does the batch move to
  `data/incoming/applied/`. `--check` merges in memory to tell you the pages
  are stale, but writes nothing and moves nothing.

## data/audits — the second pass comes back

A new score arrives `audited: false`, and an unaudited row never reaches
`TOP.md` however high it scored. `data/audits/*.jsonl` is how one auditor's
reading gets back into the data, and it is held to the same discipline an
incoming batch is held to: one validation, one bad line stops every file,
an atomic write, a ledger entry, and `--check` that writes and moves nothing.

An audit line is not a repository row. It carries only what the auditor
decided:

```json
{"repo": "owner/name",
 "scores": {"depth": 0, "relevance": 0, "novelty": 0, "maturity": 0, "evidence": 0},
 "audit_note_en": "…", "audit_note_tr": "…",
 "duplicate_of": null,
 "audited_at": "2026-09-20"}
```

* The repository **must** already be in the data. An audit of a row nobody
  scored is an error, not a new row: the auditor confirms a score, they do
  not write one.
* `scores` overwrites the row's scores, and `total` and `class` are
  **recomputed** from them by the rubric. The auditor does not write a class,
  so an audit cannot contradict the scale it measured against.
* `audited` becomes true, and `audited_at` records the day of the reading.
* Both notes are required and neither may be empty — the public pages show
  the note in their own language, so a missing one would leave a reader with
  no reason. They go through the same text rules every stored text goes
  through: no markup, no `javascript:`/`data:`, no private detail.
* `duplicate_of` is either null or a repository that is **also** in the data,
  and never the row itself.
* An audit whose `audited_at` is **older** than the row's `scored_at` is not
  applied, and the run names it: an auditor cannot have read a score that was
  written after them.
* When a batch and an audit arrive in the same run, the batch is applied
  first and the audit second — the auditor read the newest score, so the
  audit lands on top of it. A broken line anywhere stops both.
* A later score clears `audited` again but keeps `audited_at`, the way it
  keeps the note: it is the record of a reading that did happen.

### applied-batches.jsonl — what has already been applied

Filing a batch away can fail (the file is locked, the disk is full) while the
data it produced is already stored. Without a record of that, the batch would
be applied again on the next run, and an old batch re-applied after a newer
one would quietly bring the old scores back. So every applied batch is
recorded, in a tracked file rather than in the git-ignored archive:

```json
{"applied_at": "2026-09-25", "name": "batch-1.jsonl", "sha256": "…"}
{"applied_at": "2026-09-26", "kind": "audit", "name": "2026-09-26.jsonl", "sha256": "…"}
```

* A file whose `name`, `sha256` **and** kind are already recorded is never
  applied a second time; only its move into `incoming/applied/` or
  `audits/applied/` is retried.
* `kind` is `audit` for an audit file. A line without a `kind` is an incoming
  batch — that is what every line written before audits existed is.
* The same file name with different content is a different batch.
* `applied_at` is the newest `scored_at` in the batch — the newest
  `audited_at` in an audit file — not the time of the run: the same file
  applied on two machines writes the same line.
* If a run is interrupted between the two replacements, the next one stops
  with an error naming the leftover `.tmp` file and what to do with it — it
  does not guess which of the two files is the truth.

## The rule that outranks the others

**Every row carries a source link.** `url` and `evidence_url` are both
required and must start with `http://` or `https://`. A row that cannot point
at something a reader can open is not written. `tools/build.py` fails the
build rather than publish a linkless row.

Local README copies live in `ham/` (git-ignored, third-party content). They
are never copied into a generated page. When a score rests on a local README
copy the evidence link becomes `<repository url>#readme`, which points at the
same text on GitHub.

## repos.jsonl

| Field | Type | Notes |
|---|---|---|
| `repo` | `owner/name` | unique, case-insensitively |
| `url` | https | **required** |
| `source_set` | `discord` \| `topic` \| `manual` | where the repository came from |
| `first_seen`, `scored_at` | `YYYY-MM-DD` | dates, not timestamps, so a rebuild is deterministic |
| `rubric_version` | integer | which version of `rubric.md` produced the scores |
| `meta` | object | `description, stars, forks, language, license, created_at, pushed_at, archived, fork, topics` — GitHub metadata, refreshed by `tools/update.py` |
| `category` | slug | one of the sixteen below |
| `calls_jev` | `yes` \| `no` \| `unclear` | is there evidence of a real Jev/System-1 call |
| `question_types` | list | `choice`, `score`, `noul` |
| `scores` | object | `depth, relevance, novelty, maturity, evidence`, each 0–3 |
| `total` | 0–15 | must equal the sum of `scores` |
| `class` | `A` \| `B` \| `C` | A: `total ≥ 11` or (`relevance = 3` and `novelty ≥ 2`); B: 7–10; C: ≤ 6 |
| `summary_en` / `summary_tr` | string | what it does, ≤ 25 words |
| `takeaway_en` / `takeaway_tr` | string | the one idea worth carrying over |
| `risk_en` / `risk_tr` | string | key handling, closed binaries, telemetry, embedded instructions |
| `evidence_url` | https | **required**; falls back to `url` |
| `audited` | bool | a second pass over the rubric confirmed the scores |
| `audited_at` | `YYYY-MM-DD` | **optional**; the day an auditor read the row. A row nobody has audited does not carry the field at all |
| `audit_note_en` / `audit_note_tr` | string | why the auditor changed or kept them, in both languages; each page shows the note in its own language |
| `duplicate_of` | `owner/name` or null | duplicates are listed but never counted |
| `status` | `active` \| `gone` | a 404 marks the row, it is never deleted |

### Third-party text is cleaned before it is stored

`meta.description`, each `meta.topics` entry, `meta.license` and
`meta.language` are written by somebody else. `tools/update.py` never stores
them as they arrive: every one goes through `build.clean_third_party` first,
and so does the `ham/meta/*.json` copy the scoring agent reads. A markdown
link or image keeps its label and loses its target, HTML tags and the
`javascript:`/`data:` schemes are dropped, line breaks and control characters
collapse to one space, text longer than 400 characters is cut and ends in ` …`,
and a private detail (e-mail address, private IP, local path) becomes
`[redacted]` — the run names the repository it came from and carries on
rather than stopping the daily refresh over somebody else's e-mail address.
What the cleaner returns always passes `validate`; the build refuses markup
in these fields, so the refresh must be unable to produce any.

Before `tools/update.py` replaces `data/repos.jsonl` it runs the same
`validate` the build runs. If anything fails the file is left untouched and
the run exits 1 naming the row and the field: a half-refreshed data file is
worse than none. The replacement itself is a temporary file and an
`os.replace`, so no reader ever sees it half written.

Category slugs: `agent-gate`, `code-review-hook`, `model-router`,
`compaction-memory`, `classification-triage`, `search-rerank`,
`security-injection`, `browser-computer-use`, `game-demo`, `sdk-client`,
`cli`, `mcp-skill-plugin`, `eval-benchmark`, `list-directory`,
`text-generation-experiment`, `other`.

On a class conflict the auditor wins: `audited: true` rows keep the class the
auditor set, and the build says nothing. An unaudited row whose class does not
follow the rubric produces a warning.

## sources.jsonl

`id`, `type`, `title`, `url` (**required**, http(s)), `author`, `date`,
`lang`, `trust` (1–5), `note_en`, `note_tr`, `status`.

`type` is one of `official-docs`, `own-measurement`, `independent-test`,
`article`, `video`, `community-list`, `tool`, `community-message`.
`status` is `read`, `irrelevant` or `unavailable`.

Trust order: official documentation and our own measurements (5), independent
tests with numbers (4), community lists and tools (3), articles and videos
(2), second-hand syntheses (1). A second-hand synthesis of other sources is
not itself a source.

## The commands

```
python tools/build.py                 # regenerate every page from data/
python tools/build.py --import-legacy # rebuild repos.jsonl from the original working files (not published)
python tools/build.py --check         # write nothing; exit 1 if a page is stale
python tools/build.py --strict        # warnings and missing translations fail
python tools/update.py                # find new repositories, refresh metadata
```

`--check` is what a pre-commit hook or CI should run: the generated pages must
match the data exactly.

## The legacy import, once

`--import-legacy` is **not** part of the normal flow. `repos.jsonl` is the one
source of truth, new scores arrive through `data/incoming/`, and the original
working files leave the repository after the last import — they are not
published. A build without the flag never looks at that directory and says
nothing about it; a build with the flag and no directory fails rather than
write an empty data file.

`--import-legacy` reads the 2026-09-19 working files (not published) and
writes `repos.jsonl`. It only ever reads that directory. Rules it applies:

* `sonuc-*.jsonl` in filename order; when a repository appears twice, the
  later file wins.
* A line that is not valid JSON is skipped and reported, never guessed at.
* Turkish field and value names are mapped to the English schema
  (`kategori` → `category`, `evet/hayir/belirsiz` → `yes/no/unclear`,
  `P1…P5` → `depth, relevance, novelty, maturity, evidence`).
* `kanit_url` pointing at a local README copy becomes `<url>#readme`; anything
  else that is not a link falls back to `url`.
* `A-denetim.jsonl`, when it exists, overrides scores, sets `audited` and
  `duplicate_of`. When it does not exist the build warns and carries on. Its
  `gerekce` is an internal note written for us and is **not** imported.
* `denetim-notlari.jsonl`, when it exists, fills `audit_note_en` and
  `audit_note_tr` — the public note. When it does not exist both fields stay
  empty and the build warns.
* A `denetim-notlari.jsonl` row flagged `hardware_penalty` gets its
  `relevance` back from the audit's `eski` block: the auditor cut it because
  the project needs hardware they did not have, which says nothing about the
  project at public scale. The other four axes stay at the audited value,
  `total` and `class` are recomputed from the rubric, and the note is
  untouched.
* `ceviri-*.jsonl`, when it exists, fills the `_en` fields. Translator *input*
  files (`ceviri-girdi-*.jsonl`) are deliberately ignored. Rows still missing
  a translation are counted, and `--strict` turns that count into a failure.
* `first_seen` and `scored_at` are set to the date the working files were
  produced (2026-09-19), so importing twice gives byte-identical output.
