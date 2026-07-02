# Memory for Agents

**Overview:** The model has no memory — every request starts from zero, and "memory" is entirely an engineering construct: *what you choose to put back into context.* Memory design is therefore a storage + retrieval + curation problem (your home turf), with one LLM-specific twist: whatever you retrieve consumes context budget and attention (`../foundations/context_windows.md`).

---

## The Layers

```
Working memory     = the current context window (this turn's transcript + state)
Thread memory      = one conversation/task, persisted (checkpointer)
Long-term memory   = across threads/sessions (the actual design problem)
```

## Thread Memory: Transcript Management

The transcript grows every turn; unmanaged, it hits cost blowup (quadratic re-billing — `../inference/cost_engineering.md`), context limits, and context rot. The standard compaction pattern:

```
[ system prompt ]
[ structured running state: facts, decisions, IDs, open TODOs ]   ← lossless, curated
[ summary of older turns ]                                        ← lossy, regenerated
[ last N turns verbatim ]                                         ← recency fidelity
```
- **Summarization is lossy where it hurts most:** numbers, IDs, exact user constraints vanish first → keep those in the *structured state*, not the prose summary. The split (lossy narrative + lossless ledger) is the whole trick.
- Tool outputs: distill before they enter the transcript at all (`tool_use.md`) — cheaper than summarizing them later.
- **Checkpointer hygiene (the LangGraph lesson):** persist *curated* state, not every internal node message — internal scratch leaking into durable thread state is both a correctness bug (your context-leakage debugging) and a memory-poisoning surface (`../llm_agent_security.md` §5). Decide explicitly per state key: durable vs scratch.

## Long-Term Memory: the Three Kinds (useful taxonomy)

1. **Episodic** — what happened: past conversations/tasks and their outcomes. Store: summaries/transcripts, embedded for retrieval. Use: "as we discussed last week," learning from past task failures.
2. **Semantic** — facts about the world/user: preferences, profile, domain facts. Store: structured records (KV/rows: `user.prefers = concise`) — **structured beats vector-soup for facts**; retrieval is a lookup, precision is perfect, updates are targeted.
3. **Procedural** — how to do things: learned instructions, successful playbooks, per-user prompt addenda ("this user's 'deploy' means the staging pipeline"). Effectively self-updating prompt fragments — the highest-leverage and the most dangerous kind (a bad learned rule misbehaves forever).

## The Hard Parts (where memory systems actually fail)

- **The write policy:** what's worth remembering? Options: model-decided (a `save_memory` tool — flexible, noisy), extraction pass after each session (background job distills facts/preferences), explicit-only (user says "remember X" — highest precision). Start explicit + extraction; earn your way to model-decided.
- **The read policy:** retrieve by relevance (embed query → top-k memories, `embeddings.md`) + recency + a small always-on core (profile). Injecting too many memories re-creates context rot — memory retrieval needs the same k-discipline as RAG.
- **Update & contradiction:** "user moved to Bangalore" must *supersede* "lives in Delhi," not coexist — facts need identity + versioning (upsert semantics), which vector stores don't give you; another vote for structured semantic memory with timestamps.
- **Forgetting is a feature:** TTLs on episodic detail, decay/compaction of unused memories, and user-visible/erasable memory (trust + GDPR/DPDP — `../../security/infrastructure_security.md` §7).
- **Poisoning:** anything written to memory from untrusted content is a persistent injection — sanitize at write time (`../llm_agent_security.md`).
- **Scoping:** per-user always; per-team/tenant explicitly; cross-user leakage via shared memory is the memory version of BOLA.

## Evaluate It Like a Feature
Memory has failure modes evals must catch: recalls wrong fact > recalls nothing. Test: fact retention across sessions, supersession correctness, retrieval precision (irrelevant-memory injection rate), and behavior *without* memory as the baseline (`../quality/evals.md`) — plenty of memory systems lose to a good prompt + no memory.

## Related
- `../foundations/context_windows.md`, `agent_architectures.md` (state/checkpointing), `embeddings.md`, `../emerging/context_engineering.md`
