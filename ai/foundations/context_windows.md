# Context Windows & Long Context

**Overview:** The context window is the model's entire working memory — everything it can "see" for this forward pass: system prompt, history, retrieved docs, tool results, and its own output so far. "1M-token context" marketing hides the operative truth: **advertised context ≠ effective context.**

---

## What the Number Means (and costs)

- The window is the max total tokens (input + output) per request. Exceed it → hard error or silent truncation (know which your stack does — silent truncation causes the weirdest bugs).
- **Cost scales with what you send:** stateless APIs re-send (and re-bill) the whole conversation every turn — a chat's cumulative cost grows ~quadratically with turns unless you cache/compact (`../inference/cost_engineering.md`).
- **Latency:** prefill time grows with input length (attention's O(n²), `foundations` doc) — a 200k-token prompt has noticeable time-to-first-token even before generating anything.

## Effective Context: the Degradations

### Lost in the Middle
Retrieval accuracy over long contexts is **U-shaped**: models attend well to the beginning and end, worse to the middle. Placement is leverage: instructions and the most critical material at the start; the question/task restated at the end; the middle is where evidence goes to be ignored.

### Context Rot
Performance degrades as contexts grow *even when the extra tokens are relevant* — more candidates for attention = more dilution, more distraction by near-matches. Needle-in-a-haystack benchmarks (one fact, clean haystack) wildly overstate real capability; multi-fact reasoning over long context degrades much earlier than the advertised limit.

### Distraction & sycophancy to context
Irrelevant-but-plausible content gets *used*: stale tool outputs, earlier mistakes in the transcript, contradictory retrieved chunks. The model weights presence heavily — garbage in context is worse than no context. This is also why poisoned retrieval works (`../llm_agent_security.md`).

**Working assumption:** treat effective high-quality reasoning capacity as a fraction of advertised context, degrading gradually — and *measure it for your task* (`../quality/evals.md`) rather than trusting the spec sheet.

## Engineering the Window (context management)

1. **Curate, don't stuff.** RAG's top-k relevant chunks usually beat dumping whole documents — retrieval is context *quality* engineering, not just a size workaround (`../rag-guide.md`).
2. **Compaction for long agent sessions:** summarize older turns, keep recent turns verbatim + a running structured state (facts, decisions, open TODOs). Summarization is lossy — keep IDs/numbers/decisions explicit in the structured part (`../building/agent_memory.md`).
3. **Prompt-cache-friendly layout:** stable prefix (system prompt, tool schemas, reference docs) first, volatile content last — cache hits on the prefix slash cost and TTFT (`../inference/cost_engineering.md`).
4. **Tool results are context too:** a verbose API response (full JSON dump) pollutes; truncate/summarize tool outputs before they enter the transcript — one of the highest-ROI habits in agent building.
5. **Sub-agents as context isolation:** give a subtask its own fresh window; return only the distilled result to the parent — context architecture, not just org structure (`../emerging/context_engineering.md`).
6. **Positional strategy:** system rules up top; few-shot examples early; evidence in the middle (accepting its weakness); the actual question + output format last.

## How Long Context Got Long (name-checks)
RoPE scaling/extension (train short, extrapolate long), attention variants (sliding-window, sparse patterns), and better long-context training data. Implication: extension techniques are part of why quality at extreme lengths varies so much between models claiming the same window.

## Related
- `transformers_attention.md` (the quadratic why), `../emerging/context_engineering.md` (the discipline built on this), `../building/agent_memory.md`, `../inference/cost_engineering.md`
