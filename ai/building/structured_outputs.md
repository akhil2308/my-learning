# Structured Outputs & Constrained Decoding

**Overview:** Production systems need machine-parseable model output — JSON matching a schema, valid SQL, exact enum values. Three tiers of enforcement exist; know which guarantees each actually provides, because "the model usually returns JSON" is not an engineering guarantee.

---

## Tier 1: Ask Nicely (prompting)
Schema in the prompt + few-shot examples + "return only JSON, no prose."
Works ~90–99% depending on complexity — which means **guaranteed eventual failure** at volume: markdown fences around the JSON, trailing commentary, invented fields, wrong types on edge cases. Fine for prototypes; never load-bearing alone.

## Tier 2: JSON Mode (provider flag)
Provider constrains decoding to emit **syntactically valid JSON** — parseable, always. But *any* valid JSON: schema conformance (fields, types, enums) is NOT guaranteed. Eliminates parse errors; leaves semantic errors.

## Tier 3: Schema-Constrained / Grammar-Constrained Decoding
The real thing: at **every decode step**, tokens that cannot lead to a valid continuation of the schema/grammar are **masked out** (logits set to −∞) before sampling. The model literally cannot produce an invalid field name or type.
- How: JSON Schema (or any CFG — SQL dialects, regex) compiled to a state machine that walks alongside generation, computing the allowed-token set per step. Libraries: **Outlines**, **XGrammar**, llguidance; vLLM/SGLang integrate them server-side; provider "structured outputs with strict schemas" = the managed version. Overhead is now near-zero (compiled masks).
- Function-calling argument generation (`tool_use.md`) is this machinery applied to tool schemas.

### The honest caveats
- **Syntactically perfect ≠ semantically correct:** constrained decoding guarantees shape, not truth — `{"sentiment": "positive"}` can still be the wrong classification, and a forced schema can *mask* model confusion (it must emit *something* valid). Keep an escape hatch: a `"confidence"` or `"unable_to_determine"` field beats forcing a guess.
- **Over-constraining can hurt reasoning:** forcing immediate rigid JSON removes the thinking scratchpad (`../foundations/transformers_attention.md`). Pattern: let the model reason free-form first, then emit the structured block (a `"reasoning"` field first in the schema, or two-step: think → extract). Reasoning models handle this natively (`../emerging/reasoning_test_time_compute.md`).
- Deeply nested/recursive schemas degrade quality — flatten where possible; several simple extractions can beat one mega-schema.

---

## The Production Pattern (belt and suspenders)

```python
class Verdict(BaseModel):
    reasoning: str                       # scratchpad first
    category: Literal["bug","feature","question"]
    priority: int = Field(ge=1, le=5)
    confidence: float = Field(ge=0, le=1)

async def classify(text: str, retries: int = 2) -> Verdict:
    for attempt in range(retries + 1):
        raw = await llm(prompt(text), response_schema=Verdict)   # tier 3 if available
        try:
            v = Verdict.model_validate_json(raw)                 # validate ANYWAY
            if v.confidence < 0.5:
                return await escalate(text)                      # bigger model / human
            return v
        except ValidationError as e:
            prompt_extra = f"Previous output invalid: {e}. Fix and re-emit."  # error → feedback
    raise StructuredOutputError(text)
```
Rules: **always validate even with constrained decoding** (defense in depth; provider modes have edge cases) · feed validation errors back on retry (models self-correct well — same principle as tool errors, `tool_use.md`) · bump temperature slightly on retry to escape a bad mode (`../foundations/sampling_decoding.md`) · budget retries and have a terminal behavior · track schema-failure rate as a first-class metric — a rise means prompt/model drift (`../quality/llm_observability.md`).

## Beyond JSON
Grammar constraints generalize: SQL (constrain to your dialect + read-only verbs — pairs with the least-privilege DB role, `../llm_agent_security.md`), classification (mask to exactly the label tokens — also makes logprob confidence clean), code with syntax guarantees, domain DSLs.

## Related
- `tool_use.md`, `../foundations/sampling_decoding.md` (logit masking = sampling machinery), `prompt_engineering.md`
