**English** | [Türkçe](tr/FINDINGS.md)

# Findings — what is Jev, and how much of what is said about it holds up?

Last reviewed: 2026-09-19 · Model version observed: `jev-1.13.0` · Every row links to its source. Trust order and method: [`METHODOLOGY.md`](METHODOLOGY.md). Full source list: [`SOURCES.md`](SOURCES.md).

Verdict labels: **VERIFIED** (primary source or a call anyone can repeat against the documented API) · **VENDOR CLAIM** (true that the vendor says it; not independently confirmed) · **CONTESTED** (independent evidence disagrees or qualifies it) · **NOT FOUND** (we could not locate a primary source). Two more markers appear where none of the four fits: **ANECDOTE** (a public report we could not link to or reproduce — never used as evidence) and **OUR CONCLUSION** (our own inference from the linked rows above it, not a fact from a source).

## 1. What it is

| Finding | Verdict | Source |
|---|---|---|
| Jev is a decision model, not a text generator. You send a `state` and typed questions; it returns probabilities. Three question types: **choice** (up to 255 options), **score** (ordered rungs), **noul** (yes/no). It writes no prose and gives no reasons. | VERIFIED | [TypeSafe docs](https://docs.typesafe.ai/llms.txt); our own calls to `POST https://api.typesafe.ai/v1/systemone` (the endpoint and request shape are documented, so anyone with an API key can repeat this call) |
| Many questions can be asked over the same state in a single request; latency stays roughly flat as questions are added. | VERIFIED | [TypeSafe docs](https://docs.typesafe.ai/llms.txt); our calls (3 questions ≈ 0.6–1.0 s end to end from Türkiye; repeatable against the documented endpoint) |
| Context is bounded: 64k tokens total, 32k for state plus the longest question. | VERIFIED | [Model jaggedness: jev-1.13](https://docs.typesafe.ai/model-jaggedness/jev-1.13) |
| Price: $0.042 per 1M input tokens, no output tokens billed. | VERIFIED | [Vercel AI Gateway model page](https://vercel.com/ai-gateway/models/jev) (the vendor's own pricing page returned 404 when we checked) |
| The same model is reachable through the vendor API and through Vercel AI Gateway, with different request shapes (yes/no is `noul` on one, `boolean` on the other; confidence is inside the answer on one, in provider metadata on the other). | VERIFIED | Our own calls; [vercel/ai gateway source](https://github.com/vercel/ai/blob/main/packages/gateway/src/gateway-evaluation-model.ts) |
| Company: TypeSafe AI; $40M seed led by DCVC; founders Diogo Almeida (ex-OpenAI), Erik Gafni, Sasha Sheng. | VERIFIED | Consistent across several independent news outlets and the law firm's own announcement — links under "funding" in [`SOURCES.md`](SOURCES.md) |

## 2. What "cannot hallucinate" actually means

| Finding | Verdict | Source |
|---|---|---|
| The guarantee is about **shape**: Jev can only answer inside the options you gave it, so there is no malformed output. It can still pick the wrong option, confidently. | VERIFIED | [TypeSafe docs](https://docs.typesafe.ai/llms.txt); independent video demos listed in [`SOURCES.md`](SOURCES.md) |
| The vendor publishes its own list of weaknesses: literal reading, math and numbers ("Jev is not a calculator"), date/time comparison, indirection, large state full of irrelevant detail, adversarial content, contradictory instructions and criteria, generation. | VERIFIED | [Model jaggedness: jev-1.13](https://docs.typesafe.ai/model-jaggedness/jev-1.13) |
| Jev is **not deterministic** from call to call: the probability for the same question moves slightly between calls, so a value near a threshold can flip the thresholded answer. (One developer reported 0.50, 0.48 and 0.45 for one question in the vendor's community Discord — no public URL, so we list it as an anecdote only.) | VERIFIED for the repository below; the Discord report is an ANECDOTE | [yodablocks/commitjev](https://github.com/yodablocks/commitjev) reports measuring this; pattern and mitigations in [`PATTERNS.md`](PATTERNS.md) |
| Text embedded in the state can shift the answer (fake authority, embedded instructions). | VERIFIED | [Model jaggedness: adversarial content](https://docs.typesafe.ai/model-jaggedness/jev-1.13) |

## 3. Speed, cost and accuracy claims

| Claim | Verdict | What the source actually says |
|---|---|---|
| "193.6× faster, 444.6× cheaper" | VENDOR CLAIM | The figures are in [TypeSafe's launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev) (Diogo Almeida, 2026-09-15). The same post says they come from workflow examples the vendor chose and are expected to be at the **upper end** of real-world gains; it lists its own caveats (demo selection, judge-model choice, training distribution). The general range the vendor gives is 20–200× faster, 40–400× cheaper. |
| Vendor "accuracy" figures | VENDOR CLAIM | Accuracy in the launch post means **agreement with judge models** (GPT-6 Astra and Fable 5.1 averaged), not agreement with ground truth. [OrcaRouter's write-up](https://www.orcarouter.ai/blog/jev-typesafe-system-one-what-we-know) separates vendor numbers from independent ones. |
| "67.8% accuracy, on par with Sonnet 5" | NOT FOUND | Repeated in several videos; OrcaRouter attributes a 67.8% figure to the vendor's internal benchmark, but we could not find that sentence on the vendor's page. An unrelated 67.8% appears in an [independent calibration study](https://github.com/Adilmp/does-jev-confidence-mean-anything) as the score of an "always answer no" baseline. Do not conflate them. |
| Independent speed/cost check | VERIFIED | [Every's test](https://every.to/also-true-for-humans/mini-vibe-check-typesafe-s-jev-judged-everything-i-ve-written-in-0-7-seconds): Jev caught 6 of 7 planted flaws, Fable 5.1 caught 7 of 7; Jev was about 25× faster per passage at roughly 1/580 of the cost. Good, not flawless. |
| "Cheaper" is not automatic | CONTESTED | [rtrvr.ai's browser-agent benchmark](https://rtrvr.ai/blog/jev-browser-agent-benchmark) (Bhavani Kalisetty, 2026-09-16): using Jev to score context made tasks 31–43% faster but **raised total cost** by 38% (LinkedIn task) and 51% (Amazon task); context scoring was 78.7% of the Jev spend. Many cheap calls add up. |
| Offloading decisions from a coding model | CONTESTED | [dnikolayev/typesafe-offload-bench](https://github.com/dnikolayev/typesafe-offload-bench): a cascade cut time by 32–58% and tokens by 52–62% on 100 synthetic cases; the authors state this is not an invoice saving and that four models lost agreement with reference labels in cascade mode. |

## 4. Calibration — does 0.9 mean 90%?

| Finding | Verdict | Source |
|---|---|---|
| The vendor describes a training method, RLCD ("Reinforcement Learning for Calibrated Decisions"), whose **goal** is that a stated 70% is right 70% of the time. The vendor publishes no calibration measurement (no ECE, Brier score or reliability curve). | VENDOR CLAIM (design goal, not a measured result) | [Launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev) |
| Independent measurement 1: 8,000 judgments against human labels. Probabilities were systematically shifted toward "yes" — at a stated ~75%, the true rate was ~10%. Raw ECE 0.156–0.209; a two-parameter recalibration removed ~96% of it. Ranking quality was good (AUC 0.90–0.91). The author's framing: the ordering is right, the units are wrong. | CONTESTED | [Adilmp/does-jev-confidence-mean-anything](https://github.com/Adilmp/does-jev-confidence-mean-anything) |
| Independent measurement 2: 662 prompt-injection messages — 96.5% accuracy, ROC-AUC 0.9927, ECE 0.0588; the model was **under**-confident (every band above 0.85 was 100% correct). | VERIFIED (independent, public corpora) | [Gaurav-Gosain/jev-sec-bench](https://github.com/Gaurav-Gosain/jev-sec-bench) |
| Independent measurement 3: tool-call injection detection, 1,942 requests for $0.061 — AUC 0.976 (InjecAgent), 1.000 (BIPIA email), 0.993 (hand-labelled calls). The authors warn that a threshold calibrated for Jev does not transfer to general models behind the same gateway. | VERIFIED | [agent-chaperone/agent-chaperone](https://github.com/agent-chaperone/agent-chaperone) |
| Takeaway: calibration **direction depends on the task**. Treat the probability as a well-ordered score and calibrate thresholds on your own labelled data. | OUR CONCLUSION | Drawn from [Adilmp's study](https://github.com/Adilmp/does-jev-confidence-mean-anything) (over-confident toward "yes"), [jev-sec-bench](https://github.com/Gaurav-Gosain/jev-sec-bench) (under-confident) and [agent-chaperone](https://github.com/agent-chaperone/agent-chaperone) (thresholds do not transfer) |
| "Confidence" in the API is how concentrated the distribution is, not the winner's probability. On a score question we saw confidence 0.00 next to a perfectly meaningful score of 1.9 (mass split between two adjacent rungs). A fixed confidence threshold is the wrong tool for score questions. | VERIFIED | [TypeSafe docs](https://docs.typesafe.ai/llms.txt); we saw this in our own call, and it is repeatable by calling the same question type against the documented API |

## 5. What nobody outside the vendor knows

Model size, architecture and training data are undisclosed: neither the [launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev) nor the [documentation](https://docs.typesafe.ai/llms.txt) states them. Statements such as "O(1)", "removes the KV-cache bottleneck" or specific parameter counts appear in commentary videos (listed under "video" in [`SOURCES.md`](SOURCES.md)) but in **no primary source we could find** — NOT FOUND.

## 6. The public reaction, both ways

- Enthusiasm: within days, hundreds of public repositories ([`REPOS.md`](REPOS.md)) and at least eight curated lists ([`SOURCES.md`](SOURCES.md)).
- Scepticism: "12 million views for a JSON classifier? Yeah, we're in a bubble" — [Niels Rogge on X](https://x.com/NielsRogge/status/2100114968460820986) (we could not open the post directly; the quote was confirmed through search results).
- Several groups rebuilt a "local Jev" by reading option probabilities from open models, two of them benchmarked against the real model — see the `text-generation-experiment` and `eval-benchmark` [categories](categories/).

## Bottom line

This paragraph is our synthesis of sections 1–4 above; every fact in it is sourced there. Jev is a fast, cheap, well-ordered **scorer** for questions you can phrase as typed choices over a bounded state. Verified ([§1](#1-what-it-is), [§2](#2-what-cannot-hallucinate-actually-means)): the interface, the price, the speed class, the schema guarantee, the vendor's own weakness list. Not verified ([§3](#3-speed-cost-and-accuracy-claims), [§4](#4-calibration--does-09-mean-90)): that its probabilities are calibrated on your task, that it is cheaper end-to-end in your pipeline, and any headline multiplier. Build the decision machine around it — thresholds, an "uncertain" band, averaging near the line, a fallback, a log — and measure on your own labelled data.
