<!-- GENERATED — do not edit; run tools/build.py -->
English | [Türkçe](../tr/categories/text-generation-experiment.md)

# Text generation experiments

15 repositories in this category, sorted by class then score.

[All repositories](../REPOS.md)

| Repository | Class | Total | Calls Jev | What it does | Evidence |
|---|---|---|---|---|---|
| [rhighs/jev-code](https://github.com/rhighs/jev-code) | A | 10 | yes | The LLM suggests semantic sub-problems/code options, Jev approves/selects/reviews; the LLM can never approve a plan, choose a tool, or write a file | [evidence](https://github.com/rhighs/jev-code#readme) |
| [BunsDev/typesafe-ai-playground](https://github.com/BunsDev/typesafe-ai-playground) | A | 9 | yes | A community Jev playground with many real Jev demos: extraction, ask-gate triage, tool-router, reranker, PR-review, AST governance | [evidence](https://github.com/BunsDev/typesafe-ai-playground) |
| [MM-sheng/jevspeak](https://github.com/MM-sheng/jevspeak) | B | 10 | yes | A speech engine that generates semantic IR with ~13 parallel Jev decisions \(no generative LLM\) and converts it to sentences with a deterministic grammar compiler | [evidence](https://github.com/MM-sheng/jevspeak#readme) |
| [pcarrier/skibidu](https://github.com/pcarrier/skibidu) | B | 9 | yes | An experiment having Jev build an AST node by node, requesting approval for every subtree, in Scheme code generation; the author shared a finding of 'completely unsuitable' | [evidence](https://github.com/pcarrier/skibidu#readme) |
| [rivianpratama/JevPixelArt](https://github.com/rivianpratama/JevPixelArt) | B | 9 | yes | Jev determines every pixel channel with a Score question; sharpens the flat distribution and compensates for lack of shared context by injecting one-time composition answers into every request | [evidence](https://github.com/rivianpratama/JevPixelArt#readme) |
| [wei-b0/gram-render](https://github.com/wei-b0/gram-render) | B | 9 | yes | A generative interface for Telegram bots: Jev never writes text, it only selects among candidate structures derived from data \(which view, which order\). | [evidence](https://github.com/wei-b0/gram-render) |
| [dani1005/book-aurora](https://github.com/dani1005/book-aurora) | B | 8 | yes | A visualization that 'reads' a novel with Jev via 10 parallel emotion scores per passage and draws a color band; supports hedge-retry and dual OpenRouter/native providers | [evidence](https://github.com/dani1005/book-aurora) |
| [finetuningsingh/jev-chatbot](https://github.com/finetuningsingh/jev-chatbot) | B | 8 | yes | An experiment comparing 7 different methods \(word tree, scoring, letter-first, etc.\) for turning Jev, which only answers choice questions, into word-by-word text generation | [evidence](https://github.com/finetuningsingh/jev-chatbot#readme) |
| [chrismoseley/jev-extraction-marker-recovery](https://github.com/chrismoseley/jev-extraction-marker-recovery) | B | 7 | yes | A script recovering flattened footnote/superscript markers in OCR using a regex-finder + Jev \(Noul+Choice\) | [evidence](https://github.com/chrismoseley/jev-extraction-marker-recovery) |
| [replynodes/jev-web-analyzer](https://github.com/replynodes/jev-web-analyzer) | B | 7 | yes | A demo evaluating a SaaS website from a first-visitor's perspective via 10 questions with Jev; strict URL/DNS filtering against SSRF, page content processed under the 'untrusted data, not instructions' principle | [evidence](https://github.com/replynodes/jev-web-analyzer#readme) |
| [florian-hoenicke/jev-gpt](https://github.com/florian-hoenicke/jev-gpt) | C | 6 | yes | An experiment generating text via a chained choice-question pipeline \(word type -&gt; WordNet category -&gt; embedding group -&gt; word -&gt; ranking\) \(~400 calls/prompt\) | [evidence](https://github.com/florian-hoenicke/jev-gpt#readme) |
| [tylerjharden/harden-jev-decides](https://github.com/tylerjharden/harden-jev-decides) | C | 6 | yes | A fun dashboard where Jev decides, in a single request with weighted scores, which project idea becomes the live MVP for a stream | [evidence](https://github.com/tylerjharden/harden-jev-decides#readme) |
| [carlaiau/readwithjev](https://github.com/carlaiau/readwithjev) | C | 5 | yes | A research prototype showing sentence-level eight-emotion scoring and a character minimap while reading a novel with Jev | [evidence](https://github.com/carlaiau/readwithjev#readme) |
| [pekth/draftpulse](https://github.com/pekth/draftpulse) | C | 4 | yes | A live viral-score prediction while writing an X post; Jev answers a few narrow questions, weighted-combined in code; a fake heuristic kicks in if there's no key | [evidence](https://github.com/pekth/draftpulse) |
| [dabit3/jev-experiments](https://github.com/dabit3/jev-experiments) | C | 2 | yes | A collection of latency-focused TypeSafe/Jev demos made by Devin; the top-level README is thin, details are in subdirectory READMEs | [evidence](https://github.com/dabit3/jev-experiments) |
