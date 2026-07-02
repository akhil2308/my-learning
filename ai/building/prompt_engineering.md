# Prompt Engineering as Engineering

**Overview:** Prompts are code: they encode behavior, they break on "dependency" upgrades (model versions), they need version control, tests, and review. This doc is the engineering discipline, not a tips listicle.

---

## What Reliably Works (the durable core)

1. **Be explicit and specific.** Models don't infer unstated requirements. "Summarize" → "Summarize in 3 bullets for a technical audience; include concrete numbers; omit marketing language." Most "model is dumb" bugs are underspecified prompts.
2. **Structure the prompt.** Delimit sections (XML tags work well: `<instructions>`, `<context>`, `<examples>`, `<output_format>`); separate role/rules (system) from task (user) from data (clearly fenced). Structure also enables prompt caching layout (`../inference/cost_engineering.md`).
3. **Few-shot examples are specification by demonstration** — often stronger than descriptions, especially for format and edge-case behavior. Curate 2–5 diverse examples *including a hard/edge case*; keep format 100% consistent (the model imitates format as much as content); for classification, balance classes (models pick up label priors from examples).
4. **Give room to think.** For non-trivial reasoning, let the model produce analysis *before* the answer (or use a reasoning model — `../emerging/reasoning_test_time_compute.md`). Forcing answer-first removes the scratchpad (`../foundations/transformers_attention.md`).
5. **Positive instructions beat negative** ("respond in formal English" > "don't be casual"); put critical instructions early AND restate the task last on long prompts (`../foundations/context_windows.md` lost-in-the-middle).
6. **Define the failure behavior:** what to do when the answer isn't in the context ("say INSUFFICIENT_DATA") — unspecified failure modes become hallucinations (`../quality/hallucination_grounding.md`).

## Prompts Are Code: the Practices

- **Version control:** prompts in git (files/templates, not inline f-strings scattered through code); changes reviewed like code. Template variables explicit and validated.
- **Test:** every prompt with real traffic gets an eval set — golden examples + regression cases from production failures. A prompt change ships when evals pass, not when one manual try looks good (`../quality/evals.md`). This is the difference between prompt *engineering* and prompt *vibing*.
- **Pin and record:** model + version + sampling params logged with every request (`../foundations/sampling_decoding.md`); model upgrades are migrations — run the eval suite against the new model before switching.
- **One prompt, one job:** mega-prompts doing five things degrade unpredictably and can't be tested in isolation — decompose into a pipeline/graph of focused prompts (this is half of why agent architectures exist — `agent_architectures.md`).
- **A/B in production** for consequential prompts; offline evals are necessary but not sufficient.

## Failure Modes to Recognize
- **Instruction dilution:** 40 rules in a system prompt → later/middle ones silently ignored. Prioritize ruthlessly; move policy into validation code where possible (deterministic beats instructed).
- **Example overfitting:** model copies an example's *content* into answers. Make examples obviously schematic/distinct from real data.
- **Prompt drift:** teams patch prompts per incident until they're contradictory sediment. Refactor prompts like code; delete rules whose evals still pass without them.
- **Cross-model portability is limited:** a tuned prompt is tuned *to a model*. Keep the intent documented (comments!) so re-tuning is re-derivation, not archaeology.
- Treat *user-visible* prompt text as attack surface and assume it leaks (`../llm_agent_security.md`).

## Meta-Prompting
Use a strong model to draft/critique/compress prompts ("rewrite this prompt to be unambiguous; list underspecified cases"). Automated prompt optimization (DSPy/GEPA-style — evolve prompts against an eval metric) is maturing fast — it presupposes the thing that matters most anyway: **a good eval set.** The eval is the asset; the prompt is derived.

## Related
- `../quality/evals.md` (the other half of this discipline), `structured_outputs.md`, `../emerging/context_engineering.md` (this doc's agent-era successor)
