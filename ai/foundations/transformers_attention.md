# Transformers & Attention: The Data-Flow View

**Overview:** What actually happens to your prompt inside the model — traced as data through the system, no math derivations. Knowing this flow explains context limits, cost structure, latency behavior, and half of prompt engineering.

---

## The Pipeline

```
text → tokenizer → token IDs → embeddings → N transformer blocks → logits → sampled token → (append, repeat)
```

1. **Tokenize:** text becomes ~4-chars-per-token integer IDs (see `tokenization.md`).
2. **Embed:** each token ID looks up a vector (~thousands of dims). Position info is mixed in (RoPE in modern models) so order matters.
3. **Transformer blocks (×30–100+):** each block = **attention** (tokens exchange information) + **MLP** (each token processed independently — where most parameters/"knowledge" live). Residual connections mean each block *refines* a running representation rather than replacing it.
4. **Logits → sampling:** the final vector for the *last position* becomes a probability distribution over the whole vocabulary; one token is sampled (`sampling_decoding.md`); append it; run again.

**LLMs generate one token at a time, each requiring a full forward pass.** Everything about inference cost follows from this (`../inference/inference_internals.md`).

## Attention in One Paragraph

For each token, attention asks: *which earlier tokens are relevant to me right now?* Every token emits a **query** ("what I'm looking for"), a **key** ("what I contain"), and a **value** ("what I'll contribute"). Each position scores its query against all keys, softmaxes the scores into weights, and takes the weighted sum of values. Result: the word "it" can pull information from "the cat" ten tokens back — attention is a learned, content-based routing table, recomputed at every layer. **Multi-head** = many of these routing tables in parallel, each specializing (syntax, coreference, position...). **Causal masking** = tokens only attend backwards (that's what makes it a *generator*).

## The Consequences You Feel Daily

- **Quadratic attention:** every token attends to every prior token → compute/memory grow ~O(n²) with context length. Why long context costs disproportionately and why "just stuff everything in context" degrades (`context_windows.md`).
- **KV cache:** keys/values of past tokens are cached so each new token doesn't recompute history — the central object of serving economics (`../inference/inference_internals.md`).
- **In-context learning is attention at work:** few-shot examples work because attention routes information from your examples to the generation — no weights change. "Learning" in the prompt is retrieval + routing, which is why format consistency in examples matters so much.
- **No scratch memory:** the model's only working memory is the token stream itself. Chain-of-thought works because intermediate tokens *are* the scratchpad — forcing an answer-first format literally removes the space to compute (`../emerging/reasoning_test_time_compute.md`).
- **Parameters = frozen knowledge; context = working set.** Weights don't change at inference. Fresh facts must arrive via context (RAG, tools) — the entire justification for `../rag-guide.md`.

## Vocabulary for Model Cards
- **Decoder-only:** all modern chat LLMs (GPT/Claude/Llama lineage) — the generate-left-to-right architecture above. Encoder models (BERT) read bidirectionally → embeddings/classification, not generation.
- **Parameters (7B/70B):** total learned weights; rough capability/cost proxy. **MoE:** only a fraction of parameters active per token (`../training/model_architectures.md`).
- **Hidden dim / layers / heads:** width, depth, and routing capacity — internals you rarely need beyond reading papers.

## Related
- `tokenization.md`, `sampling_decoding.md`, `context_windows.md`, `../inference/inference_internals.md`
