# The Emerging Landscape (mid-2026 snapshot)

**Overview:** A map of the concepts rising right now — enough on each to recognize it, place it, and know when to dig deeper. Deliberately a snapshot: revisit and prune this doc every ~6 months (dated claims rot fast in this field).

---

## Agentic Everything (the center of gravity)

- **Agents as the deployment unit:** the industry's frame shifted from "chat with a model" to "delegate a task to an agent" — long-running, tool-using, checkpointed tasks (`../building/agent_architectures.md` is the durable core; this is its moment).
- **Multi-agent orchestration going mainstream:** the single do-everything agent is giving way to orchestrator + specialist teams (the microservices-ification of agents) — with all the distributed-systems consequences your `system-design/` folder predicts: handoff contracts, tracing, failure isolation.
- **Agentic coding as the proving ground:** CLI/IDE agents (Claude Code-class tools) doing multi-file, test-driven, hours-long tasks — the pattern (verify-loop + tools + checkpoints) is the template other domains copy. The skill shift: from writing code to *specifying, reviewing, and evaluating* agent work.
- **Computer-use agents:** models operating GUIs via screenshots + clicks — the universal-but-slow fallback where no API exists; API/MCP always beats pixels when available. Reliability still the gating factor.
- **Agent interop protocols:** **MCP** for agent↔tool (won — `mcp.md`); **A2A**-class protocols for agent↔agent discovery/delegation across vendors — earlier on the adoption curve; watch, don't bet the architecture yet.
- **Agent commerce/payments:** agents transacting (paid APIs, purchases) with spend controls and delegated authority — protocols emerging; the "autonomy stops at the till" problem. Early but inevitable; treat as: budgets + allowlists + confirmation gates (`../llm_agent_security.md` thinking applied to money).

## Model-Side Currents

- **Test-time compute / reasoning models:** the second scaling axis — own doc (`reasoning_test_time_compute.md`).
- **SLM renaissance:** distilled 1–8B models handling the volume tier; "frontier designs, small models execute" (`../training/model_architectures.md`).
- **Open-weight pressure:** strong open models (DeepSeek/Qwen/Llama lineages, heavy Chinese-lab momentum) keep compressing the frontier-to-free gap — recheck build-vs-API and routing tables quarterly (`../inference/cost_engineering.md`).
- **Native multimodality & any-to-any:** text/image/audio/video in and out of one model; voice-native agents. Architecture: `../training/model_architectures.md`.
- **Long-context economics:** hybrid SSM/attention models making 1M-token-class context cheap-ish — pressure on (not replacement of) RAG: retrieval remains about *quality and freshness*, not just fitting (`../foundations/context_windows.md`).

## Practice-Side Currents

- **Context engineering as the named discipline:** own doc (`context_engineering.md`).
- **Automated prompt/agent optimization:** LLM-guided evolution of prompts and agent scaffolds against eval metrics (DSPy/GEPA lineage) — "the eval is the asset" made literal: given a good metric, the artifact optimizes itself (`../building/prompt_engineering.md`).
- **Agent memory as a product surface:** persistent, user-visible, cross-session memory shipping in major assistants — the three-kind taxonomy and poisoning risks now mainstream concerns (`../building/agent_memory.md`).
- **Evals & governance industrialization:** enterprises evaluating on reliability-under-constraints rather than benchmark scores; regulation (EU AI Act era) pushing audit trails, logging, and risk classification — observability (`../quality/llm_observability.md`) doubles as compliance infrastructure.
- **The experience-learning thesis:** agents improving from their own interaction outcomes (RL on real tasks, not static data) — the research direction behind self-improving agents; production reality today = the eval flywheel, done manually.

## How to Use This Doc
Skim quarterly. For each item ask: (1) does it change my routing/cost table? (2) does it change my architecture defaults? (3) is it still just a demo? Promote items that graduate into their own doc; delete items that fizzle. Last reviewed: **2026-07**.

## Related
- Every doc in `emerging/`; `../inference/cost_engineering.md` and `../building/agent_architectures.md` absorb most of the practical fallout
