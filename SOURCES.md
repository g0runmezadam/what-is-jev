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
| [Jev browser-agent benchmark](https://www.rtrvr.ai/blog/jev-browser-agent-benchmark) | Bhavani Kalisetty / rtrvr.ai | 2026-09-16 | 4 | read | rtrvr.ai's own browser-agent benchmark: Jev sped up tasks 31-43% but raised total cost 38-51% because context-scoring calls were expensive. |

## Articles

| Source | Author | Date | Trust | Status | Note |
|---|---|---|---|---|---|
| [TypeSafe AI Emerges From Stealth With $40M in Funding With New Model for Composable AI](https://www.hpcwire.com/aiwire/2026/09/16/typesafe-ai-emerges-from-stealth-with-40m-in-funding-with-new-model-for-composable-ai/) | AIwire | 2026-09-16 | 3 | read | Funding: news coverage of the $40M seed round led by DCVC and the founding team. Used only for company facts, not for model claims. |
| [TypeSafe AI Raises $40M in Seed Funding](https://www.finsmes.com/2026/09/typesafe-ai-raises-40m-in-seed-funding.html) | FinSMEs | 2026-09-16 | 3 | read | Funding: second independent outlet reporting the same $40M seed round; listed to show the figure is consistent across outlets. |
| [Jev : Reviews, Price, Info &amp; 30 Alternatives AI Tools \| 2026 - AIxploria](https://www.aixploria.com/en/jev-typesafe-ai/) | AIxploria |  | 2 | read | AIxploria directory page summarizing Jev's primitives and pricing from TypeSafe's site; lists cons: waitlist-gated, text-only, vendor-only benchmarks so far. |
| [What is Jev AI](https://medium.com/data-science-in-your-pocket/what-is-jev-ai-b8294d980001) |  |  | 2 | unavailable | Medium article on Jev listed in the source set; the page could not be fetched during review, so its content is unverified. |
| [Jev: TypeSafe's Decision Model, Speed and Cost Explained](https://www.orcarouter.ai/blog/jev-typesafe-system-one-what-we-know) | Magnus Corvin / OrcaRouter | 2026-09-16 | 2 | read | OrcaRouter blog separates TypeSafe's vendor claims from Every's independent numbers on Jev speed, cost, and accuracy; flags unproven calibration claims. |

## Videos

| Source | Author | Date | Trust | Status | Note |
|---|---|---|---|---|---|
| [Avenox — Jev video](https://www.youtube.com/watch?v=0f4TJMg7jLA) | Avenox |  | 4 | read | A Turkish-language explainer/use-cases video on Jev, scored as trust 4 \(an explainer/promotional video\): covers Jev's place in the stack, economics, use cases, and how it can be fooled. |
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
| [I built a Jev Computer Use Agent, Its INSANE](https://www.youtube.com/watch?v=vSzde5be5XE) |  |  | 2 | unavailable | Transcript is a single-sentence announcement with no technical detail; too short to assess as a real source on Jev's behavior. |
| [Jev-Durchbruch: Die Architektur, die kein LLM mehr ist](https://www.youtube.com/watch?v=YsWvFYqouFY) |  |  | 2 | read | German-language AI news roundup where Jev is a brief segment; low technical detail, repeats unsourced "up to 200x" speed claims. |
| [Jev explained in 7min..](https://www.youtube.com/watch?v=vj7hysh0mOI) |  |  | 2 | read | Independent analyst argues Jev's edge is latency, not raw capability, and cites an unlinked open-source model claimed to do something similar. |
| [Jev for AI Agents: I Tested it with rtrvr.ai for browser automation](https://www.youtube.com/watch?v=JsNQwFB9N1Q) | rtrvr.ai \(Retriever\) team |  | 2 | read | rtrvr.ai team's own A/B test in a video: Jev sped up browser-agent tasks but raised total cost, an unusually honest negative finding. |
| [Jev is HERE. How to use it](https://www.youtube.com/watch?v=4mTLpuQpB80) | Ryan Vogel; Greg |  | 2 | read | Independent early-user interview: live email classification demo \(1,700 emails\); explicitly says Jev underperformed on a Bitcoin trading-signal test. |
| [Jev From TypeSafe is a New Class of AI Model that is FAST and CHEAP - But There is a Caveat!](https://www.youtube.com/watch?v=qdji39XXgEY) | Tech Nibble |  | 2 | read | Independent CLI demo shows concrete Jev failures: wrong on a primality test and a logic puzzle despite high stated confidence. |
| [Jev - The Ultimate Classification Model?](https://www.youtube.com/watch?v=X117w2Rark8) |  |  | 2 | read | Independent demo via OpenRouter covering classification, sentiment, injection, and tool-selection tasks; explicitly notes no architecture paper or diagram exists. |
| [Jev by TypeSafe AI: Jev vs LLMs - Parallel Sampling, Lower Latency, and Typed Outputs](https://www.youtube.com/watch?v=JQFNpX1w6vY) |  |  | 2 | read | Corporate-toned explainer repeating TypeSafe's own RLCD framing and numbers; states plainly that "0% hallucination" means schema validity only. |
| [Master 95% of JEV AI in 7 Minutes](https://www.youtube.com/watch?v=RzCHlj95Ons) | Kev |  | 2 | read | Promotional no-code channel demos lead-scoring and a computer-use tool; entirely positive tone, no weaknesses discussed. |
| [MCP for Performance Testing - Day 1: Introduction &amp; Fundamentals](https://www.youtube.com/watch?v=O8pFJFc21Eo) |  |  | 2 | irrelevant | Unrelated MCP performance-testing tutorial; keyword search found zero mentions of Jev, TypeSafe, or System One. |
| [System One模型Jev​ \| Diogo Almeida \| TypeSafe AI \| RLCD \| RLHF \| 结构化输出 \| 不会聊天的模型 \| 丹尼尔卡尼曼 \| 杰文斯悖论](https://www.youtube.com/watch?v=xJ1GrKDpgm4) | 大飞/最佳拍档 |  | 2 | read | Critical Chinese-language news video citing named skeptics \(Niels Rogge, Harsha Gundala\) and TypeSafe's $40M funding round; most source-transparent video reviewed. |
| [System 1 Models Jev Explained: 200ms AI Decisions, Zero Token Streaming](https://www.youtube.com/watch?v=6RdpGVfqd4A) |  |  | 2 | read | Balanced independent explainer highlighting that TypeSafe's own release notes admit benchmark limitations, unusual for a launch post. |
| [What Is Jev, the New Model From TypeSafe AI? \| Tech Brew Ride Home Podcast](https://www.youtube.com/watch?v=Ipom6c1fcP0) | Tech Brew Ride Home Podcast |  | 2 | read | Tech news podcast reads a Register article on Jev verbatim, including a direct Diogo Almeida quote and the $40M funding figure. |
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

## Tools

| Source | Author | Date | Trust | Status | Note |
|---|---|---|---|---|---|
| [Nasrallah-AL/jev-cli](https://github.com/Nasrallah-AL/jev-cli) | Nasr Shaer \(Nasrallah-AL\) |  | 3 | read | GitHub source for jev-cli \(jevctl\): MIT-licensed, includes a Claude Code plugin with one compaction hook, no MCP server, no telemetry documented. |
| [Jev CLI \(jevctl\) product page](https://jevcli.vectorz.app/) | Nasr Shaer \(Nasrallah-AL\) |  | 3 | read | Third-party CLI product page for jevctl, explicitly "not affiliated with TypeSafe"; wraps the Jev API with commands like classify, route, verify. |
| [jevctl — npm](https://www.npmjs.com/package/jevctl) | Nasr Shaer \(Nasrallah-AL\) |  | 3 | read | npm package page for jevctl, the third-party Jev CLI; installed with npm i -g jevctl, requires Node.js 20.12+. |

## Community messages

| Source | Author | Date | Trust | Status | Note |
|---|---|---|---|---|---|
| ["12 million views for a JSON classifier?" \(X post\)](https://x.com/NielsRogge/status/2100114968460820986) | Niels Rogge | 2026-09-15 | 3 | read | HuggingFace researcher Niels Rogge's public reply to Jev's launch, questioning the hype around a structured-output classifier receiving mass attention. |
