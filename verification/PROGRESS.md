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
- Job 1, prompt injection, run: reproduced on all five published numbers.
- Job 2, matched code pairs, run: reproduced on all four. See `RESULTS.md`.

## Next concrete step

Define job 3 from the inventory. 1,938 calls are left of the 3,000.

The cheapest next one is the agent skill router (72 cases, about 287 calls): its
catalogue and its 72 cases are in the source repository as data, so it needs no
dataset reconstruction — the same shape as the two jobs already here. The
frontier benchmark below is the more valuable one and the more expensive one.

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
