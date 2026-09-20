Turkish: [tr/verification/README.md](../tr/verification/README.md).

# Re-running other people's numbers

This folder re-runs the **textual** tests that community repositories publish
about Jev, using our own API key, in the test's **original language** and with
its **original inputs**, and then says plainly whether the published number came
back.

It exists because the rest of this repository refuses to publish a number a
reader cannot check. Relaying "96.5% accuracy" because a README says so is
exactly the thing this repository was built not to do.

## What is and is not claimed

- **Reproducibility check.** A source labelled its own data by hand, and we send
  the same items to the same endpoint with the same questions. A match means the
  pipeline reproduces; it says nothing about whether the labels were right.
- **Independent check.** The labels come from a public corpus the source did not
  make. A match is worth more, because two things had to agree.

Every job file says which of the two it is, in its `kind` field, and the report
repeats it. The distinction is never blurred in a headline.

- Tests that are not textual — games, robotics, browser control — are **not**
  re-run. They are relayed with their source, marked as the source's own number.
- Nothing is translated. A translated prompt is a different prompt, and a
  translated answer is a different measurement. Turkish pages describe a test in
  Turkish and show the test itself in the language it was written in.

## How a job works

1. A job file in [`jobs/`](jobs/) pins the source repository to a **commit**, not
   a branch; names the corpus and how it is reached; copies the source's own
   question wording character for character, with the file and line range it
   came from; and writes down **what would count as reproducing the number**.
2. That file is committed. The git history is the proof that the acceptance rule
   was fixed before anything was sent.
3. `run.py` builds the items, sends one request per item carrying the whole
   question battery (which is how the sources send it too), and appends one line
   per answer to `results/<job>/raw.jsonl`.
4. `summary.json` holds the counts, the metrics with their intervals, the model
   version the endpoint reported, the call count and the verdict.
   `REPORT.md` says the same thing in prose, including what went wrong.

The verdicts are `reproduced`, `partially reproduced`, `not reproduced`, and
`not run`. An unrun criterion is never a pass, and the verdict of a job is the
weakest verdict of its parts.

## The rules this folder keeps

- **The key never appears.** It is read from the environment, put into one
  header, and masked out of everything else. No log, no raw record, no report
  has ever held it.
- **No third-party text is stored.** A raw line carries the item's id, the digest
  of its text and the digest of the request. Not the corpus. Not even when the
  licence would allow it: a research file is not a mirror.
- **No source repository is cloned and no source code is run.** Question wording
  and committed outputs are downloaded as files from URLs pinned to a commit.
- **The call budget is counted, not estimated.** See [`BUDGET.md`](BUDGET.md).

## Running one

```
python -X utf8 verification/run.py --job sec-injection --dry-run
python -X utf8 verification/run.py --job sec-injection
```

The key is read from `TYPESAFE_API_KEY`. A run can be interrupted and started
again; items that already have an answer are skipped, so nothing is paid for
twice.

The unit tests never reach the network: every call in them goes through a fake
transport, and they pass on a machine with no key at all.

```
python -X utf8 -m unittest discover -s tests -t tests
```
