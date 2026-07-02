# Sampling & Decoding

**Overview:** The model outputs a probability distribution over its vocabulary; **decoding** is how one token gets picked from it. These are the knobs you actually control per-request, and they explain non-determinism, "creativity," and several classes of production bugs.

---

## The Knobs

### Temperature
Rescales logits before softmax: `p_i ∝ exp(logit_i / T)`.
- **T → 0:** distribution sharpens toward the argmax (greedy) — focused, repetitive-prone
- **T = 1:** the model's raw learned distribution
- **T > 1:** flattens — diverse, increasingly incoherent
- Practical bands: extraction/classification/code **0–0.3** · general assistant **0.5–0.8** · brainstorming/creative **0.9–1.2**

### Top-p (nucleus) & Top-k
Truncate the tail *before* sampling: top-k keeps the k most likely tokens; **top-p keeps the smallest set whose cumulative probability ≥ p** (adaptive — narrow when the model is confident, wide when uncertain; why it aged better than top-k). Common: `top_p 0.9–1.0`. Tune temperature *or* top-p, not both aggressively.

### Penalties
Frequency/presence/repetition penalties discourage reuse — a blunt fix for loops; prefer fixing the prompt or lowering context rot (`context_windows.md`) first.

## Why temp=0 Still Isn't Deterministic
Greedy decoding should be reproducible, but: floating-point non-associativity under different batch compositions/kernels, MoE routing sensitivity, and provider-side infra changes all perturb logits enough to flip near-ties. **Design rule: never build logic that requires bitwise-identical LLM outputs** — validate semantically (schema, tests) instead. Seeds (where offered) are best-effort.

## Beyond One-Token-at-a-Time
- **Greedy** = argmax each step; locally optimal, globally mediocre.
- **Beam search** keeps B candidate sequences — standard in translation, mostly *unused* for chat LLMs (drifts toward bland, repetitive text; open-ended generation wants sampling).
- **Best-of-N / self-consistency:** sample N full answers, pick by majority vote or a verifier/reward model — the crude ancestor of test-time compute scaling (`../emerging/reasoning_test_time_compute.md`).
- **Speculative decoding** — a *serving* optimization, not a quality knob (`../inference/serving_throughput.md`).
- **Constrained decoding** — mask invalid tokens each step to force JSON/grammar (`../building/structured_outputs.md`).

## Logprobs: the Underused Output
Most APIs can return per-token log-probabilities. Uses:
- **Confidence signals** for classification (logprob of the label token) → route low-confidence cases to review/bigger model
- Cheap **hallucination smell test:** low-probability spans in factual claims correlate with confabulation (imperfect but free) — `../quality/hallucination_grounding.md`
- Debugging: see exactly where a generation went off the rails
- Calibration caveat: RLHF'd models are systematically overconfident; treat logprobs as relative, not absolute probabilities

## Production Guidance
| Task | Setting |
|---|---|
| Extraction, classification, tool-arg generation | temp 0–0.2 (+ schema enforcement) |
| Agent reasoning/planning steps | temp 0–0.5 — agents compound randomness across steps; keep it low |
| User-facing prose | temp ~0.7 |
| Creative / idea generation | temp 1.0+, or best-of-N |

- **Log the sampling params with every request** — "same prompt, different behavior" bugs are frequently a silently-changed temperature; params belong in your prompt-versioning story (`../building/prompt_engineering.md`).
- Retries on malformed output: consider bumping temperature slightly on retry (escape the same bad mode) — then validate.

## Related
- `transformers_attention.md` (where logits come from), `../building/structured_outputs.md`, `../emerging/reasoning_test_time_compute.md`
