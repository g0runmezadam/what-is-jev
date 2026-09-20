# Progress

## Done

- The pipeline: `client.py` (key handling, retries, masking), `sampling.py`
  (digest-ordered deterministic samples), `stats.py` (Wilson, ROC-AUC, ECE and
  the three acceptance rules), `runner.py` (resume, hard ceiling, raw lines
  without third-party text), `corpora.py` (pinned downloads, dataset paging),
  `sources.py` (per-source adapters), `run.py` (the command line).
- Unit tests in `tests/test_verification.py`. They do not touch the network.
- Job 1 defined and committed: `jobs/sec-injection.json`.

## Next concrete step

Run job 1 (`python -X utf8 verification/run.py --job sec-injection`), write its
`REPORT.md`, add the row to `BUDGET.md`, then define job 2 (the matched code
pairs from the same source) and job 3 (the frontier benchmark's Jev arm).

## Notes for whoever picks this up

- The order is not negotiable: the job file with its acceptance rule is
  committed **before** the first live call of that job.
- The call ceiling for this round is 3,000. `BUDGET.md` is the count.
- A source repository is never cloned and its code is never run.
