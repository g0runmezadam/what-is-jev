<!-- GENERATED — do not edit; run verification/report.py -->

# Vulnerable code detection on 200 matched pairs

**Verdict: reproduced.** 400 of 400 items answered on 2026-09-20, against jev-1.13.0.

This is a **reproducibility-check**. The 400 snippets and their pairing are read from the per-sample output the source committed, because its pair selection runs inside its own runtime and re-implementing that shuffle would be guessing. The labels underneath are the public corpus's, but they reach us through the source's file, so this is a reproducibility check and is not called anything stronger.

## What was run

| | |
| --- | --- |
| source | [Gaurav-Gosain/jev-sec-bench](https://github.com/Gaurav-Gosain/jev-sec-bench) |
| commit | `fdb16b94d37535db9bad77f8ef0faa971bd7d69a` |
| source's own run | 2026-09-16 against jev-1.13.0 |
| licence | MIT |
| corpus | CyberNative/Code_Vulnerability_Security_DPO |
| language of the test | en |
| items | every snippet in the pinned output, no sampling |
| live calls | 400 |
| failed calls | 0 |

The questions were copied character for character from the source at that commit; the file and line range are in [`jobs/sec-code-pairs.json`](../../jobs/sec-code-pairs.json), together with the digest of every file downloaded. Nothing was translated.

## Reported against measured

| metric | reported | measured | our 95% interval | verdict |
| --- | --- | --- | --- | --- |
| pair_accuracy | 0.8900 | 0.8800 | 0.828 – 0.918 | reproduced |
| accuracy | 0.7150 | 0.7125 | 0.666 – 0.755 | reproduced |
| roc_auc | 0.7940 | 0.7922 | — | reproduced |
| ece | 0.1868 | 0.1867 | — | reproduced |

The rule each row was judged by was committed before the first call of this job; the git history of the job file is the proof.

## Deviations

- The pairs are the source's selection, not one we drew ourselves; a different draw would give a different 200 pairs from the same corpus.
- A tie between the two halves counts as not ranked, which is the source's own rule.
- We send model "jev-latest"; the version the endpoint reports is recorded in summary.json.

## Limits

- One run, no repeats. A single run cannot separate a real difference from ordinary variation between runs.
- The verdict is about the number, not about the claim behind it. A reproduced accuracy on a corpus with noisy labels is still an accuracy on a corpus with noisy labels.
- The raw answers are in `raw.jsonl` beside this file: one line per item, carrying the item's id and the digests of its text and its request, and no third-party text.
