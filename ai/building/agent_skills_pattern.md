# Agent Skills: Progressive-Disclosure Instructions

**Overview:** The pattern for giving an agent a lot of procedural knowledge without paying for it on every call: package instructions as **folders the agent loads on demand** (a `SKILL.md` entry point + supporting resources) instead of stuffing everything into the system prompt. Up front the agent sees only names + one-line descriptions; it reads the full procedure when a task actually matches. **Skills are `context_engineering.md` applied to instructions** — the same budget mindset, pointed at "how to do things" instead of "what is true."

---

## The Mechanics

- A skill = a directory: `SKILL.md` (frontmatter: name + one-line description; body: the procedure) + optional resources — reference docs, templates, executable scripts.
- **Progressive disclosure, three levels:**
  ```
  L1  name + description     always in context      ~tens of tokens each
  L2  SKILL.md body          loaded on trigger      ~hundreds–low thousands
  L3  linked resources       read only if the       unbounded — never in
      / scripts              procedure needs them   context unless fetched
  ```
  You pay for depth only when it's used. 50 skills at L1 cost less than one verbose system-prompt section — the same selection economics as tool count in `tool_use.md` (few visible things, each cheap; detail behind a fetch).
- **Deterministic steps become scripts, not prose:** a skill that says "run `validate.py`" beats one that describes the validation in English the model re-interprets each time — the *model decides, code computes* boundary from `tool_use.md`, applied to instructions.

## When Skills Beat the Alternatives

- **vs prompt stuffing:** everything-in-system-prompt is re-sent and re-billed every call (`../inference/cost_engineering.md`), dilutes attention (context rot), and buries the rule that matters for *this* task under 30 that don't. Skills load the relevant 1–2 procedures at full fidelity instead of 30 at degraded attention.
- **vs fine-tuning:** procedures change weekly; weights don't want to. A skill is a markdown edit — versionable, diffable, reviewable, instantly live, and it works across model swaps. Fine-tune for *style/format at volume* (`../training/lora_peft.md`); write a skill for *how we do deployments here*.
- **vs tools:** a tool is a capability (fetch, mutate, compute); a skill is *knowledge about procedure* — which tools, in what order, with what checks. Skills routinely orchestrate tools; they don't replace them.
- The honest limit: the model must *choose* to load the right skill from its description — same coin-flip-routing failure as ambiguous tool descriptions (`tool_use.md`). Descriptions carry the behavior here too.

## Related
- `../emerging/context_engineering.md` (the discipline this instantiates — just-in-time loading, §technique 1), `tool_use.md` (selection tax, descriptions-as-behavior), `../inference/cost_engineering.md` (why L1-only visibility wins), `agent_memory.md` (skills are curated *shared* memory; memory is learned *per-agent* state)
