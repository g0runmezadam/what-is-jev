<!-- GENERATED — do not edit; run verification/report.py -->

# Prompt injection detection on deepset/prompt-injections

**Verdict: reproduced.** 662 of 662 items answered on 2026-09-20, against jev-1.13.0.

This is a **reproducibility-check**. The labels are the public corpus's own, not the source author's, so this is closer to an independent check than a self-labelled one. The pipeline around them is still the author's.

## What was run

| | |
| --- | --- |
| source | [Gaurav-Gosain/jev-sec-bench](https://github.com/Gaurav-Gosain/jev-sec-bench) |
| commit | `fdb16b94d37535db9bad77f8ef0faa971bd7d69a` |
| source's own run | 2026-09-16 against jev-1.13.0 |
| licence | MIT |
| corpus | deepset/prompt-injections |
| language of the test | mixed |
| items | the whole corpus, no sampling |
| live calls | 662 |
| failed calls | 0 |

The questions were copied character for character from the source at that commit; the file and line range are in [`jobs/sec-injection.json`](../../jobs/sec-injection.json), together with the digest of every file downloaded. Nothing was translated.

## Reported against measured

| metric | reported | measured | our 95% interval | verdict |
| --- | --- | --- | --- | --- |
| accuracy | 0.9650 | 0.9668 | 0.950 – 0.978 | reproduced |
| precision | 0.9620 | 0.9653 | 0.935 – 0.982 | reproduced |
| recall | 0.9510 | 0.9506 | 0.917 – 0.971 | reproduced |
| roc_auc | 0.9927 | 0.9925 | — | reproduced |
| ece | 0.0588 | 0.0602 | — | reproduced |

The rule each row was judged by was committed before the first call of this job; the git history of the job file is the proof.

## Deviations

- The source ran on 2026-09-16 against jev-1.13.0. We send model "jev-latest" because the endpoint takes no version pin; the version the endpoint reports back is recorded in summary.json and in the report.
- The source runs its requests concurrently; we run them one at a time with a pause. That changes wall time, not answers.
- Both corpora are public and may sit in some model's training data. That caveat is the source's own and it applies to us identically.

## Limits

- One run, no repeats. A single run cannot separate a real difference from ordinary variation between runs.
- The verdict is about the number, not about the claim behind it. A reproduced accuracy on a corpus with noisy labels is still an accuracy on a corpus with noisy labels.
- The raw answers are in `raw.jsonl` beside this file: one line per item, carrying the item's id and the digests of its text and its request, and no third-party text.
