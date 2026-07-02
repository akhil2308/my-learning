# Context Engineering

**Overview:** The discipline that superseded "prompt engineering" as the operative skill for agents: **curating everything that enters the model's context window across a whole task** — instructions, tools, retrieved knowledge, memory, tool results, sub-agent reports. The premise (from `../foundations/context_windows.md`): context is a finite, degrading resource — attention budget — and agent quality is mostly determined by what you spend it on. Prompt engineering optimizes one message; context engineering optimizes the *information architecture of a running system*.

---

## The Budget Mindset

Every token in context: costs money (re-sent each step — `../inference/cost_engineering.md`), dilutes attention (context rot), and is a candidate for the model to latch onto (including wrongly — stale results, poisoned content). So each category earns its place:

```
context = system rules + tool schemas + memory + retrieved knowledge
        + transcript + tool results + current task
each line item: is it needed NOW, at this fidelity, at this position?
```

## The Core Techniques (a unification of things you know)

1. **Curate inputs:** retrieval over stuffing (top-k + rerank, `../rag-guide.md`); just-in-time loading (fetch when the task needs it — often via a tool — instead of preloading everything "in case"); minimal tool sets per node (`../building/tool_use.md` selection tax).
2. **Distill at every boundary:** tool outputs summarized/truncated before entering the transcript; sub-agent reports as structured schemas, not prose dumps; documents → relevant extracts. Boundaries are where bloat enters; filter there once instead of paying every step after.
3. **Compact over time:** the compaction pattern — structured lossless state + lossy summary + verbatim recent turns (`../building/agent_memory.md`). Long-horizon agents live or die on this.
4. **Isolate with sub-agents:** a subtask gets a **fresh window**, does its messy exploration there, returns only the distilled result — context isolation is the *strongest* argument for multi-agent architectures, stronger than the org-chart metaphor (`../building/agent_architectures.md`).
5. **Position deliberately:** stable content first (cache-friendly), rules early, evidence middle, task restated last (`../foundations/context_windows.md` U-curve + prompt caching layout).
6. **Externalize state:** the file system / DB / scratchpad as extended memory — the agent writes intermediate results OUT of context and retrieves on demand (notes-to-self, plans as files). Context holds pointers and the working set, not the archive.
7. **Trust-tier what enters:** provenance tags on retrieved/web/tool content; untrusted tiers can't trigger consequential actions unGated (`../llm_agent_security.md`) — security is a context-engineering concern too.

## Failure Modes (name them in reviews)
- **Context pollution:** one giant raw tool dump early poisons every later step (the single most common agent bug)
- **Context clash:** stale earlier state contradicting fresh data — the model may pick either; supersede explicitly (update the structured state, don't just append)
- **Instruction burial:** critical rule at token 40k of a 100k transcript — rules live in the (restated) system zone, not the flow
- **Compaction amnesia:** the summary dropped the one ID that mattered — IDs/numbers/decisions go in the lossless ledger
- **Poisoned persistence:** bad content written into memory/state replays forever (`../building/agent_memory.md`)

## Making It Engineering (not folklore)
- **Look at your contexts.** Regularly read full rendered prompts at each agent step (tracing must capture them — `../quality/llm_observability.md`); most fixes are obvious once seen.
- **Metrics:** tokens-per-step trend across a task (bloat curve), share of context by category (tools vs transcript vs retrieval), cache-hit rate, and eval scores vs context size (find *your* rot threshold — `../quality/evals.md`).
- **Review context architecture like schema design:** what enters state, at what fidelity, who compacts, what persists — decided deliberately per agent, written down. This doc + your SupervisorNode architecture .md habit = the practice.

## Related
- `../foundations/context_windows.md` (the physics), `../building/agent_memory.md` + `../building/agent_architectures.md` (the mechanisms), `../inference/cost_engineering.md` (the bill)
