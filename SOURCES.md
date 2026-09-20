<!-- GENERATED — do not edit; run tools/build.py -->
English | [Türkçe](tr/SOURCES.md)

# Sources

Everything this repository claims rests on one of these. Every row carries a link; a row without one does not get written.

## Official documentation

| Source | Author | Date | Trust | Status | Note |
|---|---|---|---|---|---|
| [Introducing System One Models and Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) | Diogo Almeida / TypeSafe | 2026-09-15 | 5 | read | TypeSafe's own launch post for System One models and Jev: speed/cost claims, workflow evals, and its own nuance boxes admitting vendor bias. |
| [TypeSafe documentation bundle \(llms.txt\)](https://docs.typesafe.ai/llms.txt) | TypeSafe | 2026-09-19 | 5 | read | The vendor's own documentation bundle: API, question types, what confidence means, known weaknesses, cookbook. Read on 2026-09-19. |
| [Model jaggedness — jev-1.13](https://docs.typesafe.ai/model-jaggedness/jev-1.13) | TypeSafe |  | 5 | read | TypeSafe's own page listing Jev's known weaknesses: literal reading, math, dates, indirection, adversarial content, context limits — "Jev is not a calculator." |
| [Jev — Vercel AI Gateway model page](https://vercel.com/ai-gateway/models/jev) | Vercel | 2026-09-19 | 5 | read | Vercel's own Jev model page: pricing $0.042/1M input tokens, output capped at 0 tokens, 32k context window, in the AI Gateway catalog. |
| [gateway-evaluation-model.ts \(vercel/ai SDK source\)](https://github.com/vercel/ai/blob/main/packages/gateway/src/gateway-evaluation-model.ts) | Vercel |  | 5 | read | Source file in the vercel/ai SDK implementing the Gateway's evaluation-model client: request shape, headers, and endpoint used to call Jev. |

## Our own measurements

| Source | Author | Date | Trust | Status | Note |
|---|---|---|---|---|---|
| [Our own System-1 API calls](https://api.typesafe.ai/v1/systemone) | this repository | 2026-09-10 | 5 | read | Our own calls against the System-1 endpoint: latency, response shape, how the probability moves. Numbers we measured, not numbers we were told. |

## Independent tests

| Source | Author | Date | Trust | Status | Note |
|---|---|---|---|---|---|
| [does-jev-confidence-mean-anything](https://github.com/Adilmp/does-jev-confidence-mean-anything) | Adilmp |  | 4 | read | Independent calibration test on 8,000 judgments: Jev's stated confidence is miscalibrated \(ECE 0.16-0.21\) though ranking \(AUC ~0.90\) is good. |
| [agent-chaperone](https://github.com/agent-chaperone/agent-chaperone) | agent-chaperone | 2026-09-19 | 4 | read | Independent test of Jev as an agent guardrail: high AUC \(0.976-1.000\) detecting prompt injection and unsafe tool calls across 1,942 requests. |
| [typesafe-offload-bench](https://github.com/dnikolayev/typesafe-offload-bench) | dnikolayev | 2026-09-17 | 4 | read | Independent cascade benchmark: routing tasks through Jev before larger coding models cut time 32-58% and tokens 52-62%, with caveats noted by the authors. |
| [Mini vibe check: TypeSafe's Jev judged everything I've written in 0.7 seconds](https://every.to/also-true-for-humans/mini-vibe-check-typesafe-s-jev-judged-everything-i-ve-written-in-0-7-seconds) | Every | 2026-09-16 | 4 | read | Every's independent test: Jev caught 6 of 7 planted errors across 12 passages in 0.7s median, versus Claude Fable catching all 7 slower. |
| [jev-sec-bench](https://github.com/Gaurav-Gosain/jev-sec-bench) | Gaurav Gosain | 2026-09-16 | 4 | read | Independent security benchmark: Jev scores 96.5% accuracy on prompt-injection detection \(ROC-AUC 0.99\) and appears under-confident rather than over-confident. |
| [jev-bias-bench](https://fox-islam.github.io/jev-bias-bench/) | Fox Islam | 2026-09-20 | 4 | read | Independent fairness benchmark measuring how Jev's answers shift when only a person's described identity changes, reporting signed favorability deltas with false-discovery-rate correction. |
| [jev-frontier benchmark \(repository\)](https://github.com/manjunathshiva/jev-frontier-bench) | manjunathshiva | 2026-09-19 | 4 | read | Independent 200-decision benchmark of Jev 1.13 against five reasoning-enabled LLMs on four public datasets; code, item manifest and raw responses are published. |
| [Jev browser-agent benchmark](https://www.rtrvr.ai/blog/jev-browser-agent-benchmark) | Bhavani Kalisetty / rtrvr.ai | 2026-09-16 | 4 | read | rtrvr.ai's own browser-agent benchmark: Jev sped up tasks 31-43% but raised total cost 38-51% because context-scoring calls were expensive. |

## Articles

| Source | Author | Date | Trust | Status | Note |
|---|---|---|---|---|---|
| [TypeSafe AI Emerges From Stealth With $40M in Funding With New Model for Composable AI](https://www.hpcwire.com/aiwire/2026/09/16/typesafe-ai-emerges-from-stealth-with-40m-in-funding-with-new-model-for-composable-ai/) | AIwire | 2026-09-16 | 3 | read | Funding: news coverage of the $40M seed round led by DCVC and the founding team. Used only for company facts, not for model claims. |
| [TypeSafe AI Raises $40M in Seed Funding](https://www.finsmes.com/2026/09/typesafe-ai-raises-40m-in-seed-funding.html) | FinSMEs | 2026-09-16 | 3 | read | Funding: second independent outlet reporting the same $40M seed round; listed to show the figure is consistent across outlets. |
| [Jev : Reviews, Price, Info &amp; 30 Alternatives AI Tools \| 2026 - AIxploria](https://www.aixploria.com/en/jev-typesafe-ai/) | AIxploria |  | 2 | read | AIxploria directory page summarizing Jev's primitives and pricing from TypeSafe's site; lists cons: waitlist-gated, text-only, vendor-only benchmarks so far. |
| [A deep dive into Jev, TypeSafe's System One model](https://flaviocopes.com/jev/) | Flavio Copes | 2026-09-20 | 2 | read | Developer-educator's early-access write-up explaining Jev's primitives and pricing, repeating TypeSafe's speed and cost figures while also listing concrete limitations such as math, dates and indirection. |
| [I Tested TypeSafe's Jev Against Claude, GPT-6, Kimi, MiniMax and DeepSeek](https://medium.com/@manjunath.shiva/i-tested-typesafes-jev-a-470-cheaper-decision-model-against-claude-gpt-6-kimi-minimax-and-d36ed152e861) | manjunath.shiva | 2026-09-20 | 2 | unavailable | Companion write-up to the benchmark repository. The page refused automated access when checked, so the repository README served as the primary record. |
| [TypeSafe Jev Review: The AI Model That Doesn't Generate Text](https://kingy.ai/blog/typesafe-jev-review-the-ai-model-that-doesnt-generate-text/) | Kingy AI | 2026-09-20 | 2 | read | Independent review written without live API access that separates vendor claims from evidence, noting Jev trailed a comparator on invoice processing and that confidence calibration remains unpublished. |
| [Learn Jev](https://learnjev.com) |  | 2026-09-20 | 2 | read | Independent, explicitly unaffiliated tutorial site that corrects overstated launch-coverage claims about Jev, including disputing 'never hallucinates' and the headline speed multiplier. |
| [What is Jev AI](https://medium.com/data-science-in-your-pocket/what-is-jev-ai-b8294d980001) |  |  | 2 | unavailable | Medium article on Jev listed in the source set; the page could not be fetched during review, so its content is unverified. |
| [Jev: TypeSafe's Decision Model, Speed and Cost Explained](https://www.orcarouter.ai/blog/jev-typesafe-system-one-what-we-know) | Magnus Corvin / OrcaRouter | 2026-09-16 | 2 | read | OrcaRouter blog separates TypeSafe's vendor claims from Every's independent numbers on Jev speed, cost, and accuracy; flags unproven calibration claims. |

## Videos

| Source | Author | Date | Trust | Status | Note |
|---|---|---|---|---|---|
| [Avenox — Jev video](https://www.youtube.com/watch?v=0f4TJMg7jLA) | Avenox |  | 4 | read | A Turkish-language explainer/use-cases video on Jev, scored as trust 4 \(an explainer/promotional video\): covers Jev's place in the stack, economics, use cases, and how it can be fooled. |
| [Jev \(Fully Tested\) + Browser Use: FASTEST AI Agent I'VE TRIED YET!](https://www.youtube.com/watch?v=SNJ3yuJ_QwY) |  | 2026-09-20 | 3 | read | Detailed independent test suite: negation handling, a prompt-injection probe, exact-value extraction, and an agent-audit check, each with reported numbers; explicitly says results don't establish production reliability. |
| [System One Jev \(Fully Explained\): Does this really beat Transformer models? \(Astra &amp; Fable?\)](https://www.youtube.com/watch?v=NIlQsncfVYs) |  | 2026-09-20 | 3 | read | Careful independent review citing TypeSafe's own workflow-benchmark percentages \(e.g. 67.8% vs 67.9%/74.1%\) and Every's test in detail; explains the probability-vs-confidence distinction with a concrete adapter example and flags the zero-hallucination framing precisely. |
| [🟢 Learn to Build a Airtable Clone with AI! \| Beginner Series Ep #16 \(B2B, Billing, AI Agents, MCP\)](https://www.youtube.com/watch?v=rz5y7nfmvis) |  |  | 2 | irrelevant | Unrelated Airtable-clone tutorial video; keyword search found zero mentions of Jev, TypeSafe, or System One. |
| [ChatGPT Co-Founder Launches 200x Faster AI: Matches Top Models](https://www.youtube.com/watch?v=EOzu25Mb0H8) |  |  | 2 | read | Independent news-summary channel repeating TypeSafe's own numbers \(193.6x faster, 444.6x cheaper on 4 internal workflows\); notes "cannot hallucinate" means schema-valid only. |
| [ChatGPT Co-Inventor Launches Jev, A Frontier Model That Never Generates Text](https://www.youtube.com/watch?v=Qz9gVzqcRhU) |  |  | 2 | read | Short independent news summary describing Jev as a model that never generates text, only typed decisions; repeats TypeSafe's own speed/price numbers. |
| [ChatGPT Images 2.5 Is INSANE: OpenAI Just Changed AI Image Generation](https://www.youtube.com/watch?v=xNSX8ZHpTpM) |  |  | 2 | irrelevant | Unrelated video about OpenAI image generation; Jev, TypeSafe, and System One are never mentioned. |
| [Coding a Cure for Cancer using AI with Dr Leon Chlon \(ex-Facebook, Harvard, Cambridge &amp; MIT\) EP.9](https://www.youtube.com/watch?v=emJq8JNRzd4) | Dr Leon Chlon |  | 2 | irrelevant | Unrelated interview about AI in cancer research; only false-positive match is "Geoffrey Hinton", not Jev or TypeSafe. |
| [Gemini 3.8 Flash Analysis](https://www.youtube.com/watch?v=jV4po1B7Bwo) |  |  | 2 | irrelevant | Unrelated video analyzing Google's Gemini 3.8 Flash model card; Jev, TypeSafe, and System One never appear. |
| [Gemini 3.8 Live and Jev Are Shaking Things Up](https://www.youtube.com/watch?v=4SqD_o-EAi8) | Daily AI Show \(Brian, Andy, Gareth\) |  | 2 | read | AI podcast reads TypeSafe's own announcement and demos \(Doom, wiki-race\); hosts stay cautious, having not used Jev themselves yet. |
| [Gestión del liderazgo con tecnología \| #ForoUNIR](https://www.youtube.com/watch?v=FHOd9yILXXQ) |  |  | 2 | irrelevant | Unrelated Spanish-language leadership/technology conference talk; no mention of Jev, TypeSafe, or System One. |
| [How I'd Learn AI Engineering From Zero in 2026 \(1 hour masterclass\)](https://www.youtube.com/watch?v=uSkm-2eb4Xk) |  |  | 2 | irrelevant | Unrelated AI-engineering learning roadmap video; keyword search found zero mentions of Jev, TypeSafe, or System One. |
| [I tried TypeSafe's System One Model: Jev](https://www.youtube.com/watch?v=CcmqPS6q9Gw) | Joe Maddalone |  | 2 | read | Independent developer's own test: fed video transcripts to Jev with 3 question types; one question returned zero confidence, a clear failure case. |
| [Jev AI Is INSANE… 193× Faster Than LLMs?!](https://www.youtube.com/watch?v=JZknBu3u8C0) |  |  | 2 | read | Fairly critical independent read of TypeSafe's own demo/graphs; flags that the "0% structured-output error" figure was never actually measured. |
| [Jev AI: Build &amp; Automate ANYTHING!](https://www.youtube.com/watch?v=INB6OeGaqps) | Julian Goldie |  | 2 | read | Promotional channel relaying other developers' Jev demos \(classification, lead scoring, browser automation\) and a claimed Claude Code context-compaction result, unverified. |
| [Jev AI Just Changed AI Agents Forever](https://www.youtube.com/watch?v=UbMdpR8Jlhc) |  |  | 2 | read | Marketing-heavy channel relaying unverified third-party demo numbers \(email/lead classification, browser automation\); notes Jev only sees question text, not field names. |
| [Jev AI: How it works for SEO?](https://www.youtube.com/watch?v=OX7WZN5snIs) |  |  | 2 | read | Independent SEO practitioner's proof-of-concept with Jev for internal linking and intent classification; repeatedly warns results are not proven accurate. |
| [Jev AI: The New System One Model Explained \| 193x Faster?](https://www.youtube.com/watch?v=47-u2is2fYA) |  | 2026-09-20 | 2 | read | Promotional explainer that states TypeSafe's RLCD calibration goal as an achieved fact \("probability actually matches its real-world accuracy"\) and repeats the 0% type-error and speed/cost multipliers uncritically. |
| [JEV Breakdown: The First AI Model Built For Code](https://www.youtube.com/watch?v=2Bs0Ink_-Uo) |  | 2026-09-20 | 2 | read | Well-organized explainer covering the Doom and wiki-race demos, but also states the RLCD calibration promise as an achieved fact rather than a vendor design goal. |
| [Jev: The New AI Model That's Breaking The Internet \(Full Tutorial\)](https://www.youtube.com/watch?v=Nq_lu5QT-fI) |  | 2026-09-20 | 2 | read | Independent hands-on tutorial building three small projects \(voice-controlled browser, memory recall system, YouTube-title scorer\); shows explicit probability thresholds \(e.g. below 0.5 = ignore\) used as fallback logic. |
| [Jev Çıktı — Nasıl Kullanılır? Düşünmeyen, Kod Yazmayan Yeni Bir Model](https://www.youtube.com/watch?v=zsrf22Ch6uM) | Digital Academy Turkey | 2026-09-20 | 2 | read | Turkish-language review citing an invoice-processing failure \(274 misread as 247\) and TypeSafe's own ~67%/61% workflow accuracy figures; discloses the channel is building a competing decision model, a conflict of interest worth flagging. |
| [I built a Jev Computer Use Agent, Its INSANE](https://www.youtube.com/watch?v=vSzde5be5XE) |  |  | 2 | unavailable | Transcript is a single-sentence announcement with no technical detail; too short to assess as a real source on Jev's behavior. |
| [Jev Demo with Cursor](https://www.youtube.com/watch?v=goVDTUd7-J0) |  | 2026-09-20 | 2 | read | Short independent demo: a Cursor plugin that reads plain-text rule files and rescores git-diff changes against them on every save, sub-second per run. |
| [Jev-Durchbruch: Die Architektur, die kein LLM mehr ist](https://www.youtube.com/watch?v=YsWvFYqouFY) |  |  | 2 | read | German-language AI news roundup where Jev is a brief segment; low technical detail, repeats unsourced "up to 200x" speed claims. |
| [Jev explained in 7min..](https://www.youtube.com/watch?v=vj7hysh0mOI) |  |  | 2 | read | Independent analyst argues Jev's edge is latency, not raw capability, and cites an unlinked open-source model claimed to do something similar. |
| [Jev for AI Agents: I Tested it with rtrvr.ai for browser automation](https://www.youtube.com/watch?v=JsNQwFB9N1Q) | rtrvr.ai \(Retriever\) team |  | 2 | read | rtrvr.ai team's own A/B test in a video: Jev sped up browser-agent tasks but raised total cost, an unusually honest negative finding. |
| [Jev is HERE. How to use it](https://www.youtube.com/watch?v=4mTLpuQpB80) | Ryan Vogel; Greg |  | 2 | read | Independent early-user interview: live email classification demo \(1,700 emails\); explicitly says Jev underperformed on a Bitcoin trading-signal test. |
| [Jev From TypeSafe is a New Class of AI Model that is FAST and CHEAP - But There is a Caveat!](https://www.youtube.com/watch?v=qdji39XXgEY) | Tech Nibble |  | 2 | read | Independent CLI demo shows concrete Jev failures: wrong on a primality test and a logic puzzle despite high stated confidence. |
| [Jev: The Schema-Safe AI That Could Change Automation Forever!](https://www.youtube.com/watch?v=RPpQacmBe4A) | Repo Chad | 2026-09-20 | 2 | read | Critical independent read of the launch material: flags that TypeSafe ran competing LLMs at minimal reasoning settings in its own demo comparisons, and separates the "0% type error" interface guarantee from model accuracy. |
| [Jev - The Ultimate Classification Model?](https://www.youtube.com/watch?v=X117w2Rark8) |  |  | 2 | read | Independent demo via OpenRouter covering classification, sentiment, injection, and tool-selection tasks; explicitly notes no architecture paper or diagram exists. |
| [Jev Ultrafast GitHub: How TypeSafe AI Makes Browser Agents Faster](https://www.youtube.com/watch?v=NFKHLhAvj1g) |  | 2026-09-20 | 2 | read | Technical walkthrough of the third-party Jev Ultrafast browser-agent project \(DOM-snapshot design, click-occlusion checks, stale-page handling\); also states that a 90% Jev confidence "mathematically guarantees" 9/10 correctness, which contradicts the independent calibration studies in FINDINGS.md. |
| [Jev by TypeSafe AI: Jev vs LLMs - Parallel Sampling, Lower Latency, and Typed Outputs](https://www.youtube.com/watch?v=JQFNpX1w6vY) |  |  | 2 | read | Corporate-toned explainer repeating TypeSafe's own RLCD framing and numbers; states plainly that "0% hallucination" means schema validity only. |
| [Livestream Coding with the new TypeSafe AI JEV Model \| Parallel Constrained Decoding](https://www.youtube.com/watch?v=5Lx4DLLYafM) |  | 2026-09-20 | 2 | read | Independent livestream exploring Jev's SDK and docs live; honest that the underlying "parallel constrained decoding" mechanism is guesswork \("nobody really knows"\), no firm new claims. |
| [Master 95% of JEV AI in 7 Minutes](https://www.youtube.com/watch?v=RzCHlj95Ons) | Kev |  | 2 | read | Promotional no-code channel demos lead-scoring and a computer-use tool; entirely positive tone, no weaknesses discussed. |
| [MCP for Performance Testing - Day 1: Introduction &amp; Fundamentals](https://www.youtube.com/watch?v=O8pFJFc21Eo) |  |  | 2 | irrelevant | Unrelated MCP performance-testing tutorial; keyword search found zero mentions of Jev, TypeSafe, or System One. |
| [Six things I tried with Jev \| TypeSafe AI](https://www.youtube.com/shorts/UaCjNDBRSdQ) |  | 2026-09-20 | 2 | read | Short independent report: replaced Gemini Flash with Jev for ranking, reranking and LLM-as-judge steps in a personal workflow; no numbers given, links to a longer external write-up. |
| [System One模型Jev​ \| Diogo Almeida \| TypeSafe AI \| RLCD \| RLHF \| 结构化输出 \| 不会聊天的模型 \| 丹尼尔卡尼曼 \| 杰文斯悖论](https://www.youtube.com/watch?v=xJ1GrKDpgm4) | 大飞/最佳拍档 |  | 2 | read | Critical Chinese-language news video citing named skeptics \(Niels Rogge, Harsha Gundala\) and TypeSafe's $40M funding round; most source-transparent video reviewed. |
| [System 1 Models Jev Explained: 200ms AI Decisions, Zero Token Streaming](https://www.youtube.com/watch?v=6RdpGVfqd4A) |  |  | 2 | read | Balanced independent explainer highlighting that TypeSafe's own release notes admit benchmark limitations, unusual for a launch post. |
| [What Is Jev, the New Model From TypeSafe AI? \| Tech Brew Ride Home Podcast](https://www.youtube.com/watch?v=Ipom6c1fcP0) | Tech Brew Ride Home Podcast |  | 2 | read | Tech news podcast reads a Register article on Jev verbatim, including a direct Diogo Almeida quote and the $40M funding figure. |
| [This AI Is 200x Faster Than an LLM - Jev by TypeSafe](https://www.youtube.com/shorts/D8qXexGbMMA) |  | 2026-09-20 | 2 | read | Very short promotional clip repeating TypeSafe's own speed multiplier as fact with no independent check. |
| [TypeSafe AI has introduced Jev, its first System One model designed for...](https://www.youtube.com/shorts/Uj8oEGeJ2gA) |  | 2026-09-20 | 2 | read | Very short generic announcement clip, no technical detail beyond the launch headline. |
| [TypeSafe Jev Hands-On Review - Is this a turning point for AI?](https://www.youtube.com/watch?v=hTCdkFWdtoo) | Sean Brownell | 2026-09-20 | 2 | read | Early-access hands-on demo: resume screening and a QA scorecard playground; reports own small-scale latency/cost numbers but calls Jev "deterministic," which the vendor's own docs do not claim. |
| [What Is Jev? TypeSafe's New System One AI Model Explained](https://www.youtube.com/watch?v=x_Bo9G-QQds) |  | 2026-09-20 | 2 | read | Pure explainer, no hands-on testing; accurately restates the choice/score/noul primitives and the routing use case without overclaiming. |
| [Why is everyone freaking out about Jev from TypeSafe? It's not an LLM! + Pacing the frontier labs](https://www.youtube.com/watch?v=QEJYjvWhZn8) | Daily AI Show \(with a TypeSafe DevRel guest\) | 2026-09-20 | 2 | read | Long AI-news podcast with a TypeSafe DevRel employee as guest; the employee states Jev is "probabilistic even at temperature zero... not deterministic," a vendor-side admission worth weighing against marketing claims of determinism elsewhere. |
| [wtf is jev?](https://www.youtube.com/watch?v=QbYBRjOaGOo) | CJ \(Syntax.fm\) |  | 2 | read | Syntax.fm host and Sentry engineer's own concrete demos: an LLM-free voice assistant and a Slack-bot model router built on Jev. |

## Community lists

| Source | Author | Date | Trust | Status | Note |
|---|---|---|---|---|---|
| [awesome-jev](https://github.com/AnotiaWang/awesome-jev) | AnotiaWang |  | 3 | read | Community-curated list of projects tagged as using Jev; a discovery list, not evidence for any claim about the model. |
| [awesome-jev-by-typesafe](https://github.com/Anil-matcha/awesome-jev-by-typesafe) | Anil-matcha |  | 3 | read | Community-curated list of projects tagged as using Jev; a discovery list, not evidence for any claim about the model. |
| [awesome-jev directory](https://awesomejev.vercel.app/) | valentynkit | 2026-09-19 | 3 | read | Community-curated directory of projects built on Jev. Useful as a discovery list, not as evidence for any claim about the model. |
| [awesome-jev](https://github.com/fatwang2/awesome-jev) | fatwang2 |  | 3 | read | Community-curated list of projects tagged as using Jev; a discovery list, not evidence for any claim about the model. |
| [awesome-jev-projects](https://github.com/logicrw/awesome-jev-projects) | logicrw |  | 3 | read | Community-curated list of projects tagged as using Jev; a discovery list, not evidence for any claim about the model. |
| [awesome-jev-typesafe](https://github.com/valentynkit/awesome-jev-typesafe) | valentynkit |  | 3 | read | Community-curated list of projects tagged as using Jev/TypeSafe; a discovery list, not evidence for any claim about the model. |
| [Awesome-jev-use](https://github.com/AiPersonacademy/Awesome-jev-use) | AiPersonacademy |  | 3 | read | Community-curated list of projects tagged as using Jev; a discovery list, not evidence for any claim about the model. |
| [awesome-jev](https://github.com/yibie/awesome-jev) | yibie |  | 3 | read | Community-curated list of projects tagged as using Jev; a discovery list, not evidence for any claim about the model. |
| [awesome-typesafe](https://github.com/AbdelStark/awesome-typesafe) | AbdelStark |  | 3 | read | Community-curated list of projects tagged as using Jev/TypeSafe; a discovery list, not evidence for any claim about the model. |
| [GitHub topic: jev](https://github.com/topics/jev) | GitHub | 2026-09-19 | 3 | read | GitHub's "jev" topic page, used as a repository-discovery source; the tag is free-form so some listed repos are unrelated to TypeSafe's Jev. |
| [Jev AI Community: Powered by the Jev Model](https://www.jevai.org/) | Jev AI Community | 2026-09-20 | 3 | read | Community hub distinct from TypeSafe: hosts a browser playground, user-submitted playbooks and API recipes, plus links to open-source projects like fast-jev-compaction and jevlike. |
| [The Ultimate Jev Resource List 2026](https://www.scriptbyai.com/jev-resource-list/) | ScriptByAI | 2026-09-20 | 3 | read | Independent aggregator page cataloging Jev SDKs, agent tools, cloud-gateway integrations and community projects; not affiliated with TypeSafe. |

## Tools

| Source | Author | Date | Trust | Status | Note |
|---|---|---|---|---|---|
| [Jev vs Open Model Arena](https://canyoubeatjev.fyi/) |  | 2026-09-20 | 3 | read | Browser tool letting users compare TypeSafe's Jev against open models via OpenRouter on preset scenarios; requires pasting Jev and OpenRouter API keys, which are sent through its server. |
| [classifier.dev](https://classifier.dev) | Michael Chomsky | 2026-09-20 | 3 | read | Commercial zero-shot text classification API with no key required for basic use; backend runs on Jev with a fallback to other language models when Jev is unavailable or confidence is low. |
| [jev-builder](https://collapseindex.github.io/jev-builder/) | Collapse Index Labs | 2026-09-20 | 3 | read | Open-source browser playground for drafting and running Jev questions, maintained by Collapse Index Labs; drafts and templates are stored only in browser localStorage. |
| [Jev x LIBERO Decision Lab](https://dimweaker.github.io/jev-libero/) | Dimweaker | 2026-09-20 | 3 | read | Open-source robotics demo showing a simulated robot's intent-strategy-motor decisions made via TypeSafe Jev combined with the LIBERO lifelong-learning benchmark suite. |
| [Nasrallah-AL/jev-cli](https://github.com/Nasrallah-AL/jev-cli) | Nasr Shaer \(Nasrallah-AL\) |  | 3 | read | GitHub source for jev-cli \(jevctl\): MIT-licensed, includes a Claude Code plugin with one compaction hook, no MCP server, no telemetry documented. |
| [Jev CLI \(jevctl\) product page](https://jevcli.vectorz.app/) | Nasr Shaer \(Nasrallah-AL\) |  | 3 | read | Third-party CLI product page for jevctl, explicitly "not affiliated with TypeSafe"; wraps the Jev API with commands like classify, route, verify. |
| [jevctl — npm](https://www.npmjs.com/package/jevctl) | Nasr Shaer \(Nasrallah-AL\) |  | 3 | read | npm package page for jevctl, the third-party Jev CLI; installed with npm i -g jevctl, requires Node.js 20.12+. |
| [Jev Logs](https://jevlogs.com) | Jalil \(reachjalil\) | 2026-09-20 | 3 | read | Independent open-source log-triage tool by a solo developer that uses Jev to score diagnostic value and route logs; explicitly states its cost estimates are not a benchmark. |
| [JevRouter](https://www.jevrouter.co/) | BillionsBobber | 2026-09-20 | 3 | read | Third-party agent tool-routing product that calls the Jev API to pick models and tools; publishes a self-run routing benchmark against DeepSeek V4.1 Flash labeled as directional estimates. |

## Community messages

| Source | Author | Date | Trust | Status | Note |
|---|---|---|---|---|---|
| ["12 million views for a JSON classifier?" \(X post\)](https://x.com/NielsRogge/status/2100114968460820986) | Niels Rogge | 2026-09-15 | 3 | read | HuggingFace researcher Niels Rogge's public reply to Jev's launch, questioning the hype around a structured-output classifier receiving mass attention. |
