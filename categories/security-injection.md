<!-- GENERATED — do not edit; run tools/build.py -->
English | [Türkçe](../tr/categories/security-injection.md)

# Security and prompt injection

9 repositories in this category, sorted by class then score.

[All repositories](../REPOS.md)

| Repository | Class | Total | Calls Jev | What it does | Evidence | Audited |
|---|---|---|---|---|---|---|
| [agent-chaperone/agent-chaperone](https://github.com/agent-chaperone/agent-chaperone) | A | 14 | yes | An MCP proxy + hook firewall; scans before tool calls and before the result is read, uses one-time full-argument approval tokens, detects tool-list drift; measured with AUC 0.976-1.0 on public datasets like InjecAgent/BIPIA | [evidence](https://github.com/agent-chaperone/agent-chaperone#readme) | yes |
| [leepokai/jev-guard](https://github.com/leepokai/jev-guard) | A | 11 | yes | A security hook running across 8 different coding-agent/hosts; makes a deny/ask/allow decision with four typed questions \(risk/approval/user_requested/from_untrusted\), scans instruction files \(skill/CLAUDE.md\) for leakage/hidden execution | [evidence](https://github.com/leepokai/jev-guard) | yes |
| [rodriveiga01/second-thought](https://github.com/rodriveiga01/second-thought) | B | 10 | yes | A terminal belt: evaluates every shell command before it runs with a calibrated multiple-choice judgment \(is it dangerous? what type? how confident?\) and gives allow/warn/block | [evidence](https://github.com/rodriveiga01/second-thought#readme) | yes |
| [cobusgreyling/Jev](https://github.com/cobusgreyling/Jev) | B | 8 | yes | An unofficial Jev showcase lab + TS harness CLI; has commands like 'jev route --goal' and 'jev guard --text "Ignore previous instructions"' | [evidence](https://github.com/cobusgreyling/Jev#readme) | no |
| [newuser7171/antivirus](https://github.com/newuser7171/antivirus) | B | 7 | yes | A desktop antivirus doing file/URL/live-process EDR scanning; extracts structural features and has Jev \(choice/score/noul\) decide severity/action, with adjustable sensitivity tiers | [evidence](https://github.com/newuser7171/antivirus#readme) | no |
| [newuser7171/jev-ndr](https://github.com/newuser7171/jev-ndr) | B | 7 | yes | An NDR platform that batch-classifies live socket/DNS traffic with Jev/classifier.dev \(1000 domains/~650ms\) to detect C2/DGA/exfiltration | [evidence](https://github.com/newuser7171/jev-ndr#readme) | no |
| [adrianpeticila/gorgona](https://github.com/adrianpeticila/gorgona) | C | 6 | no | A zero-dependency, deterministic \(regex/graph-based\) agent guardrail engine; deliberately avoids using an LLM judge | [evidence](https://github.com/adrianpeticila/gorgona#readme) | no |
| [EpicEric/safe-sh](https://github.com/EpicEric/safe-sh) | C | 6 | yes | A wrapper replacing 'sh'/'bash' that statically analyzes curl\|bash scripts with Jev before execution and blocks based on a warn/error threshold | [evidence](https://github.com/EpicEric/safe-sh#readme) | yes |
| [newuser7171/jev-vpn](https://github.com/newuser7171/jev-vpn) | C | 5 | yes | A local VPN/proxy ad blocker combining static ad/tracker lists with Jev-based zero-day ad classification | [evidence](https://github.com/newuser7171/jev-vpn#readme) | no |
