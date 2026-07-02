# Tool Use / Function Calling: How It Actually Works

**Overview:** "Function calling" demystified: the model never executes anything. It emits a **structured request** ("call `get_weather` with `{city: "Mumbai"}`"); *your code* executes it and feeds the result back as a new message. Tool use = a conversation protocol + a runtime loop you own.

---

## The Loop (what really happens)

```
1. Request:  messages + tool schemas (name, description, JSON Schema params)
2. Model:    returns either text OR tool_call(s) {name, arguments-as-JSON}
             (a decision made by generating special tokens — trained behavior)
3. You:      validate args → execute → append a tool-result message
4. Repeat:   model sees result, continues — more calls or a final answer
```
Under the hood, tool schemas are rendered *into the prompt* (they consume tokens — 20 verbose tools can be thousands of tokens per call, every call — `../inference/cost_engineering.md`), and the model was fine-tuned to emit call syntax when appropriate. There is no magic layer: it's constrained generation (`structured_outputs.md`) + your executor.

## Schema Design = Prompt Engineering

The model chooses and fills tools based ONLY on names, descriptions, and parameter schemas. Most tool-use failures are schema failures:
- **Descriptions carry the behavior:** when to use it, when NOT to ("Use for real-time prices; NOT for historical data — use `get_history`"), units, formats, one example value. Ambiguous overlapping tools → coin-flip routing.
- **Few, powerful, orthogonal tools** beat many granular ones: selection accuracy degrades with tool count and similarity. If two tools are always called together, merge them. (Dozens of tools → retrieve-then-expose a relevant subset per request.)
- **Enums and tight types over free strings** — every constraint you encode is a hallucinated-argument class eliminated.
- **Design return values for the model, not for machines:** a tool returning a 40KB JSON dump poisons context (`../foundations/context_windows.md`); return the distilled, labeled result ("Price: ₹425.30 as of 14:02 IST") + an ID to fetch detail. Tool output design is the highest-ROI, least-practiced skill here.
- **Errors are prompts too:** return actionable errors the model can react to ("date must be YYYY-MM-DD; you sent 12/05/2026") — the model self-corrects shockingly well given a good error, and loops hopelessly on `500 Internal Error`.

## The Executor You Must Build (the engineering half)

- **Validate arguments like user input:** schema-parse (Pydantic), bound values, authorize *per argument* (the model is attacker-influenceable — `../llm_agent_security.md` §3). Never `eval` anything.
- **Reliability wrapping:** timeouts, retries with backoff on transient tool failures (retry the *tool*, not the LLM), circuit breakers on flaky downstreams — your standard resilience stack (`../../system-design/productionizing.md` §4) applies verbatim; the LLM loop just sits on top.
- **Parallel calls:** models can emit multiple independent calls in one turn — execute concurrently (asyncio.gather), return all results together; big latency win for fan-out lookups. Sequential-dependent calls stay sequential (the model handles this if descriptions make dependencies clear).
- **Idempotency for mutating tools:** the loop retries; providers redeliver; the model repeats itself. Same discipline as `../../system-design/data/distributed_transactions.md` — idempotency keys on anything that writes. Plus confirmation gates on consequential actions (`agent_architectures.md`).
- **Loop guards:** max tool-calls per task; detect repeated identical calls (classic stuck pattern) → inject a nudge or abort.
- Log every call: name, args, result size, latency, error — per-tool success rate is your best agent-health metric (`../quality/llm_observability.md`).

## Choosing What Becomes a Tool
Deterministic logic stays in code (don't ask the model to add numbers — give it a calculator, or better, don't involve it). Tools are for **capabilities the model lacks**: fresh data, private data, side effects, precise computation. The boundary discipline: *model decides and composes; code computes and enforces.*

**MCP** standardizes exactly this tool interface across providers — `../emerging/mcp.md`.

## Related
- `structured_outputs.md` (how emission is constrained), `agent_architectures.md` (the loop's owner), `../llm_agent_security.md`, `../emerging/mcp.md`
