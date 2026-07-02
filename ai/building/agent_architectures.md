# Agent Architectures

**Overview:** An agent = LLM + tools + a loop, where **the model's outputs decide the control flow**. The architecture question is how much control flow to delegate to the model vs encode in the graph. The honest heuristic: **use the least agency that solves the problem** — every step of model-decided control flow is a reliability tax.

---

## The Spectrum of Agency

```
Workflow (fixed pipeline)  →  Router  →  Tool-loop agent (ReAct)  →  Planner  →  Multi-agent
   deterministic, testable  ────────────────────────────────→   flexible, compounding error
```
- **Workflow / chain:** LLM steps in a fixed DAG (extract → transform → draft → check). Not an "agent," and often the right answer — predictable, cheap, evaluable per-step.
- **Router:** one LLM call classifies, deterministic code dispatches. Agency limited to one decision.
- **ReAct-style tool loop:** think → call tool → observe → repeat until done. The workhorse. Needs: iteration caps, tool-error feedback into context, termination criteria.
- **Plan-then-execute:** planner emits a step list; executor runs it (optionally replanning on failure). Better for long tasks (the plan anchors against drift); worse when early steps invalidate the plan.
- **Reflection/critic:** generate → critique (self or second model/tests) → revise. Cheap quality wins where a verifier exists (code + tests is the ideal case).

**Compounding reliability math:** a 10-step agent at 95% per-step success ≈ 60% task success. Levers: fewer steps (better tools > more steps), higher per-step reliability (validation, retries), and recoverability (checkpoints, replanning) — this arithmetic should drive architecture more than any pattern's elegance.

## Multi-Agent: Supervisor/Worker

One orchestrator decomposes and routes to specialist workers, each with its own prompt, tools, and (crucially) **its own context window**.

Why it earns its complexity (when it does):
1. **Context isolation** — workers don't drown in each other's transcripts; the supervisor sees distilled results, not raw noise (`../emerging/context_engineering.md`)
2. **Least-privilege tools per worker** (`../llm_agent_security.md`)
3. **Focused prompts** — a 10-rule specialist beats a 50-rule generalist (instruction dilution)
4. Per-node model routing — small models for narrow workers (`../inference/cost_engineering.md`)

The costs (learned the hard way — see the SupervisorNode debugging history):
- **Handoff lossiness:** the supervisor's task description to a worker, and the worker's summary back, are both compression steps — under-specified handoffs are the #1 multi-agent bug. **Pass structured state (schemas), not prose**, across edges.
- **Debugging spans agents:** you need per-node tracing with a shared task/trace ID (`../quality/llm_observability.md`) or failures are archaeology.
- Supervisor loops (re-delegating a failing subtask forever) → per-worker retry budgets + escalation-to-human paths.
- Peer-to-peer agent swarms (no supervisor) demo well and debug terribly — prefer hierarchy.

## State Management (the LangGraph lessons)

- **The graph state is an API:** define the schema deliberately (what's shared vs node-private); reducers for concurrent writes; don't let every node dump prose into a shared `messages` list.
- **Scope internal chatter:** worker-internal tool loops should NOT persist into the durable conversation state — your checkpointer context-leakage bug (internal node messages surviving across turns) is the canonical instance. Write to the checkpointer deliberately (curate what persists), treat everything else as scratch.
- **Checkpointing = agent durability:** persistent state per thread enables resume-after-crash, human-in-the-loop interrupts, and time-travel debugging — the agent equivalent of `../../system-design/data/distributed_transactions.md` thinking (idempotent nodes, replayable steps).
- Long-horizon memory beyond the thread: `agent_memory.md`.

## Design Checklist
- [ ] Could a workflow/router do this? (start there; add agency on demonstrated need)
- [ ] Per-step success measured; iteration/recursion caps set
- [ ] Tool results truncated/structured before entering state
- [ ] Handoffs are schemas; state scope (shared vs scratch) explicit
- [ ] Human-in-the-loop gates on consequential actions; checkpoints enable resume
- [ ] Eval at task level AND step level (`../quality/evals.md`)

## Related
- `tool_use.md`, `agent_memory.md`, `../emerging/context_engineering.md`, `../llm_agent_security.md`
