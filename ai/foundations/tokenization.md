# Tokenization

**Overview:** Models never see characters or words — they see **tokens**, subword chunks from a fixed vocabulary (~50k–250k entries) learned by frequency. Tokenization explains a whole family of LLM quirks and directly drives your API bill.

---

## BPE in Two Steps

Byte-Pair Encoding builds the vocabulary before training: start from bytes, repeatedly merge the most frequent adjacent pair into a new token ("t"+"h"→"th", "th"+"e"→"the"...) until vocab size is hit. Result: common words = 1 token, rare words split into pieces (`"tokenization"` → `token|ization`), anything representable (byte fallback = no unknown-token failures).

```
"The quick brown fox"      → 4 tokens      (common English ≈ 0.75 words/token)
"antidisestablishmentarianism" → ~6 tokens
'{"user_id": 42}'          → ~8 tokens     (JSON syntax is token-dense)
Hindi/Japanese text        → often 2–4× more tokens than equivalent English
```

## The Quirks It Explains

- **Character-level tasks fail:** "how many r's in strawberry" is hard because the model sees `str|awberry`, not letters. Same for reversing strings, precise character counts, some wordplay. Don't build features on character manipulation; use code tools.
- **Numbers are weird:** digits chunk inconsistently (`1234` might be `12|34`) → arithmetic quirks; another vote for calculator/code tools.
- **Whitespace matters:** `"hello"` and `" hello"` are *different tokens*; trailing spaces in prompts can degrade completions; indentation in code eats tokens.
- **Non-English tax:** fewer vocab merges for underrepresented languages → more tokens → higher cost + effectively smaller context for the same text. Matters for Indian-language products.
- **Tokenizers differ per model family:** token counts (and thus costs/context fits) aren't portable — count with the target model's tokenizer (tiktoken for OpenAI; Anthropic/HF have their own).

## Engineering Consequences

1. **Cost:** billing is per token, in and out. Rules of thumb: English ≈ 0.75 words/token ≈ 4 chars/token; code and JSON are denser than prose; verbose keys in structured outputs are pure cost (`{"u":42}` vs `{"user_identifier":42}` — weigh against readability).
2. **Context budgeting:** limits are in tokens, not characters — chunk sizes in RAG, truncation logic, and memory summarization must count tokens (`../building/agent_memory.md`).
3. **Latency:** output tokens are generated one-by-one → response latency scales with *output* token count far more than input (`../inference/inference_internals.md`). Asking for terse output is a latency optimization.
4. **Logit bias / banned tokens** operate on token IDs — one reason exact-string constraints are awkward (`../building/structured_outputs.md` does it properly).
5. **Special tokens** (`<|im_start|>`, role markers) structure chat — user text containing lookalike sequences is an injection vector; providers escape them, but be aware when building raw-completion pipelines (`../llm_agent_security.md`).

## Practical Habits
- Keep a token counter in dev tooling; log token counts per request (cost observability — `../quality/llm_observability.md`)
- When a prompt behaves oddly, look at its tokenization — invisible whitespace/unicode issues are real
- Estimate before building: (docs × tokens/doc) vs context window is a 30-second feasibility check

## Related
- `transformers_attention.md`, `context_windows.md`, `../inference/cost_engineering.md`
