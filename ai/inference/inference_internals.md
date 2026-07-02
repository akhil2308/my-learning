# LLM Inference Internals: Prefill, Decode & the KV Cache

**Overview:** The foundation for all serving/cost/latency reasoning. One request has two phases with opposite hardware profiles, and one data structure — the KV cache — dominates the economics. Backend intuition maps directly: this is a throughput/latency/memory capacity-planning problem wearing a GPU.

---

## Two Phases, Opposite Bottlenecks

### Prefill (process the prompt)
All input tokens run through the model **in parallel** (one big matrix multiply per layer). **Compute-bound** — GPUs love it. Determines **TTFT** (time to first token). Scales with input length (attention makes it superlinear).

### Decode (generate the output)
One token per forward pass, sequentially — each pass must load **all model weights** from GPU memory to produce a single token. **Memory-bandwidth-bound**: the GPU's compute units idle waiting on weight streaming. Determines **TPOT** (time per output token, ≈ constant per token).

```
latency ≈ TTFT(input_len) + output_tokens × TPOT
```
**Consequences:** output tokens cost far more than input tokens (hence API pricing asymmetry, ~3–5×); "be concise" is a latency *and* cost optimization; batching fixes decode efficiency (amortize the weight-load across many sequences — the whole premise of `serving_throughput.md`).

## The KV Cache

Without caching, generating token N recomputes attention keys/values for all N−1 prior tokens — O(n²) per token, O(n³) per sequence. The fix: **store every token's K and V vectors after first computation**; each new token computes only its own K/V and attends against the cache.

The cache is huge and grows linearly with sequence length:
```
KV bytes ≈ 2 (K&V) × layers × kv_heads × head_dim × bytes_per_val × seq_len
e.g. a 70B-class model at fp16 ≈ ~0.3–0.5 MB per token
→ a 32k-token conversation ≈ 10–16 GB of GPU memory — for ONE sequence
```
**GPU memory = weights + Σ(KV caches of all in-flight sequences)** → concurrent capacity is a KV-memory budget. Little's Law applies unchanged: in-flight sequences = request rate × duration (`../../system-design/requests/queueing_theory.md`).

### Attacking KV size (why these exist)
- **GQA/MQA** (grouped/multi-query attention): many query heads share few KV heads → 4–8× smaller cache; standard in modern models
- **KV quantization** (8-/4-bit cache), sliding-window attention (cap cached span)
- **PagedAttention** (vLLM): allocate cache in fixed-size pages, not contiguous max-length slabs → kills fragmentation, enables cache *sharing* for common prefixes — the OS-virtual-memory idea applied to KV (`serving_throughput.md`)
- **Prefix/prompt caching:** persist the KV of a stable prefix (system prompt + tools) across requests → pay its prefill once (`cost_engineering.md`)

## Quantization (weights side)
Fewer bits per weight → less memory *and* faster decode (bandwidth-bound ⇒ fewer bytes = more tokens/s). fp16 → int8 ≈ lossless; 4-bit (AWQ/GPTQ — see `../AWQ & GPTQ.md`) small quality cost, big wins. Why 4-bit 70B on modest hardware is viable at all.

## Latency Anatomy (debugging map)
| Symptom | Suspect |
|---|---|
| High TTFT, fine streaming | long input / cold prompt cache / queueing before prefill |
| Fine TTFT, slow streaming | TPOT: batch contention, memory bandwidth, long-context attention cost |
| Both degrade under load | KV memory exhaustion → queueing/preemption (`serving_throughput.md`) |

**Always stream** for interactive UX — perceived latency is TTFT, not total (`../../system-design/requests/async_request_patterns.md` SSE section).

## Related
- `serving_throughput.md`, `cost_engineering.md`, `../foundations/transformers_attention.md`, `../AWQ & GPTQ.md`
