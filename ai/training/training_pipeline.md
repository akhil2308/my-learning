# The Training Pipeline: Pretraining → SFT → RLHF/DPO

**Overview:** How a pile of internet text becomes a chat assistant — the consumer's view. You'll rarely run these stages, but knowing them explains model behaviors (sycophancy, refusals, overconfidence), what fine-tuning can and can't change, and what model cards mean. Complements `../llm-fine-tuning.md` (the hands-on slice).

---

## Stage 1: Pretraining (capability)

Next-token prediction over trillions of tokens (web, code, books). Months on thousands of GPUs; the ~all-of-the-cost stage. Output: a **base model** — a raw text-completion engine with broad knowledge and in-context learning ability, but no dialogue behavior (ask it a question; it may continue with *more questions*, because that's plausible text).
- Scaling laws (Chinchilla): capability ∝ compute = params × tokens, with an optimal ratio — why model generations improve predictably and why data quality/curation became the battleground.
- **Knowledge cutoff** is set here; facts live in these weights (`hallucination_grounding.md` on why that's fragile).
- Mid-training additions: long-context extension, code/math-heavy phases, synthetic data.

## Stage 2: Supervised Fine-Tuning (format & instruction-following)

Train on curated (instruction → ideal response) pairs — tens of thousands to millions, human-written and increasingly synthetic (strong-model-generated, filtered). Teaches: chat format, following instructions, style, tool-call syntax (`../building/tool_use.md` behavior is installed here).
**Key mental model:** SFT primarily *elicits and shapes* what pretraining built; it adds format and behavior far more effectively than new knowledge — which is why fine-tuning for facts loses to RAG (`../llm-fine-tuning.md`).

## Stage 3: Preference Optimization (quality & alignment)

Problem: "good response" is easier to *judge* than to *write* → learn from comparisons.
- **RLHF (classic):** humans rank response pairs → train a **reward model** to predict preferences → RL (PPO) optimizes the LLM against it, with a KL leash to the SFT model (don't drift into reward-hacking gibberish).
- **DPO and successors:** skip the explicit reward model + RL loop; a clever loss trains directly on preference pairs. Far simpler/cheaper, quality-competitive — why it displaced PPO for most open-model post-training.
- **Behavioral side effects you observe daily:** *sycophancy* (agreeing feels preferred), hedging boilerplate, refusal patterns, confident tone (preferred by raters) → the overconfidence that makes logprobs miscalibrated (`../foundations/sampling_decoding.md`). When a model's "personality" annoys you, you're feeling the preference data.

## Stage 3.5: RLVR — the reasoning-era addition

**RL from Verifiable Rewards:** on tasks with checkable answers (math, code+tests, logic), reward correctness directly — no human preference proxy, no reward-model gaming. Scaled up with long chain-of-thought generation, this is what produces **reasoning models** (o1/R1-style): the model learns to *spend tokens thinking* because thinking demonstrably raises the verified reward (`../emerging/reasoning_test_time_compute.md`). Verifiability is the constraint — it's why reasoning gains land first in math/code and generalize outward unevenly.

## Distillation (how small models got good)
Train a small model on a large model's outputs (responses, reasoning traces, preference judgments) — transferring capability downmarket. Most strong small models are heavily distilled; it's also *your* tool: distill your prompted-frontier-model workload into a small model once volume justifies (`../inference/cost_engineering.md`).

## Reading a Model Card (the consumer checklist)
Base vs instruct/chat variant · knowledge cutoff · context length (and *tested* length) · post-training style (affects tone/refusals) · reasoning vs standard · tool-calling/JSON training · license (open-weight ≠ open-anything) · benchmark table (rank models, not your task — `evals.md`).

## Related
- `../llm-fine-tuning.md`, `lora_peft.md` (the efficient how), `../emerging/reasoning_test_time_compute.md`, `model_architectures.md`
