# LLM Cost Engineering

**Overview:** LLM cost is a design property, not a billing surprise. The levers, roughly in order of typical impact: send fewer tokens → cache what you send → route to cheaper models → batch what isn't urgent. This doc is the checklist version of the cost work you already do on agent platforms.

---

## Know Your Cost Anatomy First

```
request_cost = input_tokens × input_price + output_tokens × output_price (3–5× input)
agent_task_cost = Σ over steps — transcripts GROW: step N re-sends steps 1..N−1
conversation cost grows ~quadratically with turns (stateless APIs re-bill history)
```
Instrument per-request tokens/cost with attribution (user, feature, agent, node) *before* optimizing — `../quality/llm_observability.md`. The top-3 cost drivers are usually a surprise.

## Lever 1: Send Fewer Tokens
- **Trim the transcript:** compaction/summarization of old turns; cap tool outputs (the #1 agent bloat source — a full JSON API dump enters context and gets re-sent every subsequent step; truncate/extract at the tool boundary).
- **Prompt diet:** few-shot examples earn their tokens or get cut; verbose schemas/system prompts audited quarterly (they're re-sent on *every* call).
- **Retrieval discipline:** top-k tight; rerank-then-send-less beats send-everything (`../rag-guide.md`).
- **Cap output:** `max_tokens` sized to the task; "be concise" instructions; structured outputs with short keys where volume is high.

## Lever 1.5: Semantic Caching (skip the model entirely)
Different beast from prompt caching below: cache the **full response**, keyed by embedding similarity of the request — "what's your refund policy" and "how do refunds work" hit the same entry. Lives in your gateway, no provider involvement (LiteLLM / Portkey / Kong AI Gateway all ship it as a config flag).
- Repetitive, question-shaped workloads (support bots, FAQ-style internal tools) see **20–40% hit rates** → those requests cost ~zero and return in milliseconds.
- **The similarity threshold is a correctness dial, not a perf knob:** too loose → a confidently wrong cached answer to a subtly different question (worse than paying full price); too tight → no hits. Start strict, tune against your eval set (`../quality/evals.md`), and scope cache keys per-tenant so one user's answer never leaks to another.
- Wrong tool for agent loops — every step's context is unique. That's the next lever's job.

## Lever 2: Prompt Caching (the biggest single win for agents)
Providers persist the KV cache of a request's **prefix**; a subsequent request sharing that exact prefix pays ~10% of input price on the cached part (and gets faster TTFT). Mechanics: `inference_internals.md`.
- **Layout for it:** stable content first (system prompt, tool schemas, reference docs, few-shot), volatile content last. One dynamic value (a timestamp!) early in the prompt destroys all downstream cache hits.
- Agent loops are the perfect customer: step N's prompt = step N−1's prompt + a bit → near-total prefix reuse.
- Mind TTLs (minutes-scale typically) — burst workflows benefit; sporadic ones don't. Measure the cache-hit rate; treat a drop as a regression.

## Lever 3: Model Routing & Cascades
Most workloads are a mix of easy and hard requests; price spread between small and frontier models is 10–100×.
- **Static routing:** classify tasks at design time — extraction/classification/formatting → small model; multi-step reasoning → big model. Per-node choice in a graph (your supervisor's workers don't all need the frontier model — the router/supervisor itself often can be small too).
- **Cascade:** try cheap model → validate (schema check, judge, logprob confidence — `../foundations/sampling_decoding.md`) → escalate failures only. Works when validation is reliable; beware silent-plausible failures.
- **Distill the stable path:** high-volume, well-understood task → fine-tune a small model on the big model's outputs (`../training/training_pipeline.md`); classic 10×+ unit-cost reduction once volume justifies it.
- Track **cost-per-successful-task**, not cost-per-request — a cheap model with 2× retries and lower success can lose.

## Lever 4: Batch & Off-Peak
Provider **batch APIs** (~50% discount, hours-scale SLA) for anything asynchronous: evals, backfills, embedding jobs, nightly enrichment. Design pipelines to separate interactive from batchable early — retrofitting is harder.

## Lever 5 (self-hosting): Utilization
Own GPUs → cost = utilization game: continuous batching, prefix caching, quantized weights (`serving_throughput.md`, `../AWQ & GPTQ.md`), right-sized model per task. Under ~sustained-high utilization, APIs usually win — same math as `../../system-design/compute/serverless_vs_containers.md`.

## Guardrails (denial-of-wallet is real)
Per-user/per-key token budgets · agent recursion & tool-call caps · max_tokens everywhere · alerting on cost anomalies (a runaway loop shows up in $/hour before anything else) · rate limits (`../../system-design/requests/rate_limiting.md`). Security angle: `../llm_agent_security.md` §6.

## Related
- `inference_internals.md` (why output > input), `serving_throughput.md`, `../foundations/context_windows.md` (compaction), `../quality/llm_observability.md`
