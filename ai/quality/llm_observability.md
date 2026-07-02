# Observability for LLM Applications

**Overview:** Classic observability (`../../system-design/productionizing.md` §2) tells you a request was slow or 500'd. LLM apps add a failure class it can't see: **the request succeeded and the output was wrong** — subtly, non-deterministically, sometimes only in aggregate. LLM observability = standard telemetry + capturing the *content* + measuring *quality* continuously.

---

## Traces: the Unit is the Task, Not the Request

An agent task = LLM calls + tool calls + retrievals + retries across nodes (and possibly services). You need the full tree under one trace:

```
task (trace_id, user, agent, version)
├─ node: supervisor  → llm_call (model, prompt_v, tokens in/out, TTFT, cost)
├─ node: researcher  → retrieval (query, top-k ids, scores) → llm_call
├─ node: executor    → tool_call (name, args, latency, error) × 3
└─ final answer (+ eventual user feedback)
```
- **OpenTelemetry GenAI semantic conventions** exist for exactly this (span attrs for model, token counts, tool names) — use them so LLM spans live in the *same* traces as your FastAPI/DB spans (you already run OTel; this is additive, not a parallel stack). LangGraph/LangChain callbacks → OTel exporters, or platforms (LangSmith, Langfuse, Braintrust, Arize Phoenix) that speak it.
- **Capture prompts and completions** (the payloads), with PII scrubbing rules and retention limits — without content, "why did it answer that?" is unanswerable. Sample if volume demands, but never sample errors/low-confidence out.
- Propagate `trace_id` into every downstream tool call — the agent version of correlation IDs.

## Metrics: Three Layers

**1. System (RED, per model/endpoint):** request rate, error rate (API errors, timeouts, rate-limit hits), TTFT & TPOT percentiles (`../inference/serving_throughput.md`), provider availability (multi-provider fallback decisions come from this).

**2. LLM-specific health:**
- Token usage in/out + **cost, attributed** (per user, feature, agent, node) — cost anomaly alerts catch runaway loops before the invoice does (`../inference/cost_engineering.md`)
- **Schema/parse failure rate** (structured outputs), **tool-call error rate per tool**, retry rates, agent iterations-per-task, cache hit rate (prompt cache + semantic cache)
- Guardrail/refusal trigger rates

**3. Quality (the new layer):**
- **Online evals:** run cheap graders on a sample of live traffic — faithfulness-to-context, judge scores on a rubric, abstention rate (`evals.md` mechanics, applied continuously)
- **User feedback signals:** explicit (thumbs) and implicit (regenerate clicks, immediate rephrasings, task abandonment, human-agent escalations) — implicit signals are higher-volume and less biased
- **Drift watch:** score trends per model version and over time — provider-side model updates shift behavior under a pinned prompt; a slow eval-score slide is your early warning

## The Feedback Flywheel (what it's all for)
```
production traces → sample/flag failures (low judge score, thumbs-down, schema fail)
   → human review queue → labeled cases → APPEND TO EVAL SET → fix → regression-protected
```
This loop is the actual product of observability — telemetry that never becomes eval cases is a dashboard, not a system. Make "promote trace to eval case" a one-click internal tool.

## Debugging Playbook
| Symptom | First look |
|---|---|
| "Agent did something weird" | Full trace: which node, which prompt version, what was in context (usually: polluted context/tool dump) |
| Quality dropped, nothing deployed | Provider model change → diff eval scores by model snapshot; check prompt-cache hit collapse |
| Cost spike | Attribution metric → runaway loop (iterations/task), transcript growth, cache-hit drop |
| Latency spike | TTFT vs TPOT split → prefill/queueing vs decode contention (`../inference/inference_internals.md`) |
| Sporadic schema failures | Cluster the failing inputs — they share a trait (length, language, an edge case) → new eval slice |

## Alerting
Symptom-based, per `productionizing.md` §11: cost/min anomaly, schema-failure rate > x%, judge-score drop > y over 1h, tool error rate per tool, provider error/latency SLO burn. Every alert links to the traces behind it.

## Related
- `evals.md` (the flywheel's other end), `../inference/cost_engineering.md`, `../../system-design/productionizing.md` §2/§11
