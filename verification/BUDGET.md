# Call budget

One line per job. The ceiling for this round is **3,000 live calls**, counted
here rather than estimated. `calls` is the `calls` field of that job's
`summary.json`, which is one per raw line: every request that left this machine,
including the ones that failed and the ones a resumed run had already paid for.

| date | job | calls | running total | note |
| --- | --- | --- | --- | --- |
| 2026-09-20 | sec-injection | 662 | 662 | the whole corpus, 3 of them a smoke test before the full run |
| 2026-09-20 | sec-code-pairs | 400 | 1062 | 200 matched pairs, both halves |

Remaining: **1,938**.
