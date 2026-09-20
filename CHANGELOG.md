**English** | [Türkçe](tr/CHANGELOG.md)

# Changelog

What changed in each update of the data and the findings. Newest first. The numbers on the front page are generated from the data; this page says where they came from.

## 2026-09-20

- **129 repositories added** (909 counted in total): 90 from the daily `github.com/topics/jev` search, 39 shared publicly in the community channel. Two shared links had already been deleted and were skipped. Twelve of the shared repositories turned out to have no connection to Jev (general agent frameworks, a list with a six-figure star count, a graph database, a trading bot); they are kept and marked `calls_jev: no` with a score of zero — star counts never enter a score.
- **Metadata refreshed** for every known repository; repositories that have disappeared are marked `gone`, not removed.
- **28 sources added** (88 in total): 16 newly published videos and 12 websites built on or about Jev, each scored for its link to Jev, independence and verifiability before being listed.
- **Findings**, each checked against its primary page before it went in ([`FINDINGS.md`](FINDINGS.md)):
  - the vendor's own launch post says the comparison models in its wiki-race demo ran without reasoning — added as VERIFIED;
  - a new section on **bias and fairness**, built on the first independent benchmark of that kind (method only; we quote no numbers we did not re-extract);
  - a common misreading of calibration ("90% confident means right nine times out of ten") — added as CONTESTED;
  - one claim was **rejected**: a statement about non-determinism had been attributed to a vendor employee, but the transcript shows the show's hosts said it after the guest had left.
- **Patterns**: a caution about third-party sites that relay your API key through their own server ([`PATTERNS.md`](PATTERNS.md)).
- **Pipeline**: third-party text (repository descriptions, topics) is now cleaned before it becomes data, after a description containing a Markdown link stopped the build; audit results can now be imported as dated batches.
- **Audit**: all 54 class A rows that were awaiting audit (42 first scored today, 12 scored on 2026-09-19 and moved into class A by the rubric rule) were re-read by a single reviewer, README open, against the unchanged rubric. Scores changed in 31 of them; 11 fell out of class A (43 stayed, 7 became B, 4 became C). The most common inflation this time was **novelty** — ports and reproductions that repeat the baseline pattern — followed by maturity. Eight repositories were scored *up* on evidence because their own published measurements had been under-counted. Audited rows now total 337, and none are waiting.

## 2026-09-19

- First data set: 785 repositories (387 shared in the community channel, 398 more from the topic search), scored on the fixed rubric; five duplicate pairs marked.
- All 288 rows first scored as class A re-read by one reviewer; 261 changed, class A went from 288 to 217 ([`METHODOLOGY.md`](METHODOLOGY.md), section 4).
- 60 sources; findings, methodology and twelve recurring patterns written in English and Turkish.
