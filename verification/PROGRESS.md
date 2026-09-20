# Progress

## Done

- The pipeline: `client.py` (key handling, retries, masking), `sampling.py`
  (digest-ordered deterministic samples), `stats.py` (Wilson, ROC-AUC, ECE and
  the three acceptance rules), `runner.py` (resume, hard ceiling, raw lines
  without third-party text), `corpora.py` (pinned downloads, dataset paging),
  `sources.py` (per-source adapters), `run.py` (the command line),
  `report.py` and `export_site.py` (generated pages and the site export).
- Unit tests in `tests/test_verification.py`. They do not touch the network and
  pass on a machine with no key.
- Job 1, prompt injection, defined and run. See `RESULTS.md`.
- Job 2, matched code pairs, defined.

## Next concrete step

Run job 2: `python -X utf8 verification/run.py --job sec-code-pairs`
(400 calls). Then `python -X utf8 verification/report.py`, add the row to
`BUDGET.md`, commit, push.

## Job 3, and why it is not defined yet

The frontier benchmark's Jev arm is 200 items across four public datasets. Its
committed `results/items_manifest.json` carries, per item, only the `id`, the
task, the option set, the gold label and the **sha256 of the state and of the
instructions** — not the text. So the items have to be rebuilt from the four
datasets with the source's own sampling (its `sample()` function, seed 20260919,
parquet files from the dataset host) and then checked against those digests.

That digest check is worth the work: it turns "we think we used the same items"
into something a reader can verify. But it is a day's work on its own, not a
variation on the two jobs already here, so it was left rather than half-done.

Jobs 4 to 8 from the inventory are unstarted.

## Rules for whoever picks this up

- The order is not negotiable: the job file with its acceptance rule is
  committed **before** the first live call of that job.
- The call ceiling for this round is 3,000. `BUDGET.md` is the count, and it is
  updated from `summary.json` after every run, not estimated.
- A source repository is never cloned and its code is never run. Files are
  downloaded from URLs pinned to a commit, and their digests are in the job file.
- No third-party corpus text enters this repository, whatever the licence says.
- A job whose question wording or data file cannot be found in the source is not
  run: it is recorded as blocked, with the reason.
