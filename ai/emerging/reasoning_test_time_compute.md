# Reasoning Models & Test-Time Compute

**Overview:** The scaling story added a second axis. Axis 1 (classic): more training compute → better model. Axis 2 (the o1/R1 era): **more inference compute per query** → better answers from the *same* model. "Reasoning models" are models trained to exploit axis 2 — they generate long internal chains of thought before answering, and accuracy scales with how many thinking tokens you let them spend.

---

## How They Work

- **Mechanically:** the model emits an extended (often hidden/summarized) thinking phase — exploring approaches, checking itself, backtracking — then a final answer. The thinking tokens are the model's only scratchpad (`../foundations/transformers_attention.md`): more tokens = more serial computation steps.
- **How they're trained:** RLVR — RL against **verifiable rewards** (math answers checked, code run against tests): the model learns that thinking longer raises verified correctness, and *discovers* behaviors like self-correction and backtracking rather than being hand-taught them (`../training/training_pipeline.md` §3.5). DeepSeek-R1's open replication made the recipe common knowledge.
- **Consequence of the training signal:** gains are largest where verification exists — math, code, logic, structured analysis — and transfer unevenly to fuzzy tasks (writing quality, chat) where a standard model at equal cost may match or win.

## The New Cost/Latency Model

Thinking tokens are output tokens: billed, and generated serially before the user sees anything.
```
reasoning request ≈ (hidden thinking: 100s–10,000s tokens) + visible answer
→ 5–100× the latency and cost of a standard call for hard problems
```
- **Effort/budget knobs** (low/medium/high, or explicit token budgets) make thinking a *dial*: per-request quality-vs-cost tuning — a new routing dimension (`../inference/cost_engineering.md`): easy request → standard model; hard verified-domain request → reasoning model, effort scaled to stakes.
- UX: hide the wait behind streamed thinking summaries/progress; reasoning models are for *tasks*, not chat ping-pong.
- Prompting changes: they need **goals and constraints, not step-by-step instructions** — "think step by step" scaffolding and heavy few-shot CoT are redundant or harmful; state the problem, the success criteria, and get out of the way.

## Test-Time Compute Beyond One Long Chain
The general principle — spend inference compute to buy accuracy — has several forms:
- **Sequential:** longer CoT (the reasoning-model default)
- **Parallel:** best-of-N / self-consistency — sample N solutions, majority-vote or verifier-select (`../foundations/sampling_decoding.md`)
- **Verifier-guided:** generate → check (tests, judge, reward model) → revise/re-sample — strongest where checking ≪ solving
- **Agentic:** spend the compute on *tool loops* — search, run code, iterate (`../building/agent_architectures.md`); for many real tasks, an agent loop with a standard model beats pure thinking (fresh information beats rumination)
These compose: reasoning model + tools + verification is the current ceiling for hard tasks (and the recipe behind frontier coding/research agents).

## Engineering Implications
1. **Routing is now 3-D:** model size × thinking effort × agentic tools — pick per task class, validated on your evals (`../quality/evals.md`).
2. **Verification is the bottleneck skill:** the whole paradigm leans on checkable outcomes — designing your tasks to be verifiable (tests, schemas, ground truth) pays twice: better training-free accuracy today (verifier-guided sampling) and RLVR-readiness if you ever post-train (`../quality/hallucination_grounding.md` §verification).
3. **Distillation flows downhill:** reasoning traces from big models fine-tune small ones into competent reasoners — expect capable cheap reasoning tiers, keep re-checking your routing table.
4. Don't pay the reasoning tax on extraction/formatting/simple QA — measure; the failure mode of the era is defaulting everything to the most expensive thinking setting.

## Related
- `../training/training_pipeline.md` (RLVR), `../inference/cost_engineering.md`, `../building/agent_architectures.md`, `context_engineering.md`
