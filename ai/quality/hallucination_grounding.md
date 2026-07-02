# Hallucination & Grounding

**Overview:** Models confabulate: fluent, confident, wrong. This isn't a bug being patched out — it's intrinsic to how generation works — so the engineering posture is **contain and verify**, not "prompt it away." This doc: why it happens, where it bites, and the mitigation stack in order of effectiveness.

---

## Why Models Confabulate (mechanics, not moralizing)

1. **Generation is next-token prediction, not lookup:** the model produces the most *plausible* continuation; plausible and true correlate imperfectly, especially in the long tail. A citation-shaped slot gets filled with a citation-shaped string.
2. **Training rewards answering:** pretraining has no "I don't know" signal for most gaps; RLHF raters historically preferred confident answers — models are calibrated toward *attempting*. Refusal is the behavior you must explicitly engineer space for.
3. **No internal fact/guess distinction the model reliably reports:** verbalized confidence ("I'm 90% sure") is weakly calibrated, and RLHF makes logprobs overconfident (`../foundations/sampling_decoding.md`) — useful signals, never guarantees.
4. **Fluency masks failure:** the same polish applies to right and wrong answers — humans (and LLM judges) over-trust fluent text.

## The Risk Map (where to spend defense budget)
High risk: specific facts in the long tail (minor people, niche APIs, exact numbers/dates), **citations & references** (the classic fabrication), post-cutoff anything, cross-lingual facts, arithmetic. Lower risk: general concepts, summarization *of provided text* (though intrusion of outside "knowledge" still occurs), transformation tasks. Design rule: **the more retrieval-like the task, the less you should rely on weights** — move facts into context.

## The Mitigation Stack (strongest first)

### 1. Grounding: retrieve, don't recall
Put the facts in context (RAG, tool calls, fresh API data) and instruct answers **from the provided context only** — converts open-book recall into reading comprehension, the regime models are good at. Residual failure mode shifts to *faithfulness* (ignoring/misreading context — measurable, `evals.md`) and retrieval misses. Explicit **abstention path** required: "if the context doesn't contain the answer, say INSUFFICIENT_DATA" — an unspecified failure mode becomes a confabulation (`../building/prompt_engineering.md`).

### 2. Verification by construction
Where outputs are checkable, check them in code: generated SQL → execute against schema; code → run tests; extracted quotes → **string-match against the source** (quote-then-answer patterns make faithfulness mechanically verifiable); numbers → recompute via calculator tool; URLs/citations → resolve them. Every claim converted into a verifiable artifact leaves the trust-the-model regime. This is the cheapest big win and pairs with reflection loops (`../building/agent_architectures.md`).

### 3. Citations as UX + audit
Grounded answers cite chunk/source IDs → users can verify, evals can check citation-support ("does the cited passage actually entail the claim"), and injected/poisoned content becomes visible (`../llm_agent_security.md`).

### 4. Confidence routing
Logprob-based confidence on classification/extraction, self-consistency (sample n, agreement rate) on reasoning, judge-verifier passes on high-stakes generation → **route low-confidence to a bigger model or a human**, don't ship it. Calibrate thresholds on labeled data (`evals.md`).

### 5. Prompt-level hygiene (helps, doesn't solve)
Permission to abstain; "distinguish facts from the provided context vs your general knowledge"; ask for sources-first-then-answer; lower temperature for factual tasks. Real but marginal next to 1–2.

## Measuring It
Faithfulness (claims supported by context — NLI/judge-based, per-claim), abstention correctness (does it refuse when it should — include unanswerable cases in the eval set!), citation precision, and the **hallucination-rate trend across model/prompt versions**. A system that never abstains has an unmeasured hallucination rate, not a zero one.

## Product Posture
Match stakes to trust: medical/legal/financial surfaces get grounding + citations + human review; a brainstorming tool doesn't. Communicate uncertainty in the UI. And log user corrections — they're free eval cases (`llm_observability.md`).

## Related
- `../rag-guide.md` (grounding infrastructure), `evals.md`, `../foundations/sampling_decoding.md` (logprobs), `../building/structured_outputs.md` (abstention fields)
