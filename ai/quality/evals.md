# Evals: Evaluation-Driven LLM Development

**Overview:** The single biggest maturity gap between teams that ship reliable LLM features and teams that don't. Without evals, every prompt tweak, model upgrade, and RAG change is vibes; with them, LLM development becomes normal engineering: change → run suite → compare → ship. **The eval set is the asset; prompts and models are swappable around it.**

---

## Why "Looks Good" Fails
LLM outputs are high-variance and failure is long-tailed: a prompt that aces your 5 manual tries fails on the 200 real inputs you didn't try. Fixing one case silently breaks another (prompt whack-a-mole). Model version upgrades shift behavior underneath you. The only defense is a fixed, representative test set run on every change — same logic as a test suite, adapted for non-deterministic, graded-quality outputs.

## Building the Eval Set

- **Source from reality:** seed with 20–50 real (or realistic) inputs; grow continuously from production — **every reported failure becomes an eval case** (the flywheel: prod feedback → eval case → fix → regression protection). A living 100–300-case suite beats a static 10k benchmark.
- **Cover the distribution:** typical cases, edge cases, adversarial inputs, out-of-scope inputs (where correct behavior is refusal/`INSUFFICIENT_DATA`), and per-segment slices (long docs, non-English, each tool path).
- **Define "good" explicitly per case:** exact expected output (classification/extraction), reference answer + rubric (generation), or property assertions ("mentions the refund policy," "contains no dollar amounts," "valid JSON matching schema"). Writing the criteria is where most of the thinking happens — it's the spec.

## Grading: the Three Tiers

1. **Code-based (prefer whenever possible):** exact/fuzzy match, schema validation, regex/property checks, "does the SQL run and return the reference result," "does the code pass tests." Deterministic, free, trustworthy. Design tasks to be code-gradable when you can — it's worth changing the output format for.
2. **LLM-as-judge:** a (strong) model grades outputs against a rubric. Essential for open-ended quality — and full of traps:
   - **Pairwise > absolute:** "which of A/B better satisfies the rubric" is far more reliable than "score 1–10" (scores are uncalibrated and drift)
   - Known biases: position bias (randomize order), length bias (judges favor longer), self-preference (a model favors its own outputs — judge with a different model), verbosity-as-quality confusion
   - **Calibrate the judge against human labels** on a sample (measure agreement) before trusting it; a judge is itself an LLM feature needing its own eval
   - Rubrics must be concrete: "helpful" → "answers the specific question asked, cites the provided context, ≤150 words"
3. **Human review:** the ground truth for calibration and the arbiter for high-stakes launches; too expensive for every run — spend it on judge calibration and disagreement sampling.

## Evaluating Systems, Not Just Prompts

- **RAG:** evaluate retrieval separately (recall@k, MRR against labeled relevant chunks) from generation (faithfulness-to-context, answer quality) — "retrieval fetched the right chunk but the model ignored it" and "retrieval missed" need different fixes (`../rag-guide.md`, `embeddings` calibration).
- **Agents:** task-level success (did the whole thing work, judged on final state — e.g., the DB row actually changed) AND step-level metrics (tool selection accuracy, argument validity, steps-to-completion, cost/task). Trajectory evals catch "right answer, horrifying path." Compounding math in `agent_architectures.md` says per-step rates are what you tune.
- **Regression discipline:** pin the suite; run on every prompt change, model upgrade, retrieval change; block ship on regressions like any CI gate. Track scores over time — slow drift is real (`llm_observability.md`).
- Non-determinism: run flaky cases n times, grade pass@k or mean; at temp 0 variance shrinks but doesn't vanish (`../foundations/sampling_decoding.md`).

## Tooling & Process
promptfoo / Braintrust / LangSmith datasets / OpenAI Evals / inspect-ai — or honestly, pytest + a YAML of cases + a judge helper gets a team surprisingly far (very buildable in your stack). What matters: cases in version control, results diffable between runs, one command.

Public benchmarks (MMLU etc.) rank *models*; they say nothing about *your task* — build yours.

## Related
- `prompt_engineering.md` (evals are its other half), `llm_observability.md` (production feedback loop), `hallucination_grounding.md` (faithfulness metrics)

## Practice Rep (60 min, pass/fail) — Session 31 [INTERVIEW-CRITICAL]
*Bundles this doc + `llm_observability.md`.*

**Design the eval set + trace schema for one of your real agents** (IRIS/RAPID/supervisor). Produce a `evals/` spec doc:

1. **Golden set (20 min):** 15+ cases spanning happy path, known failure modes, and 3 real production incidents turned into regression cases (the flywheel from `llm_observability.md`). Each case: input, expected behavior, grader tier (exact / LLM-judge rubric / human).
2. **Grader design (20 min):** for the LLM-judge cases, write the actual rubric prompt and name the judge's own failure modes you'll guard against (position bias, verbosity bias, self-preference) + how you'll calibrate it (human-labeled disagreement set).
3. **Trace schema (20 min):** define what every task logs (steps, retrieval sets + scores, tokens, tool calls, latency per step) such that a prod failure is replayable as a golden case. Name the offline-gate vs online-monitor split and the deploy gate threshold.

**Pass:** ≥15 cases with ≥3 from real incidents; judge rubric written (not described) with named biases + calibration plan; trace schema makes a failure replayable (a reviewer could reconstruct the incident from the fields).
**Fail:** golden set is all happy-path, or "LLM judges it" with no rubric and no calibration story.
