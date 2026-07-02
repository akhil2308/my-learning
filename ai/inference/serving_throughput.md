# LLM Serving & Throughput: vLLM, Batching, Speculative Decoding

**Overview:** How inference servers turn the raw mechanics (`inference_internals.md`) into high-throughput services. Relevant whether you self-host (vLLM/TGI/SGLang) or just want to understand why your API provider behaves the way it does.

---

## Continuous Batching (the big idea)

Decode is memory-bandwidth-bound: one weight-load can serve **many** sequences' next-token computations almost for free → batching multiplies throughput.

- **Static batching (naive):** group N requests, run until *all* finish. Short requests wait for the longest; new arrivals wait for the batch. Terrible utilization.
- **Continuous (in-flight) batching:** the scheduler operates **per iteration** — every decode step, finished sequences exit and queued requests join immediately. GPU stays full; no convoy effect. This single idea is most of vLLM's famous throughput gain.
- The trade: bigger batches → higher throughput but higher per-token latency (contention). **Throughput vs latency is a scheduler policy** — batch-size caps, priority queues; the same knobs as any queueing system (`../../system-design/requests/queueing_theory.md`).

## PagedAttention & Prefix Sharing (vLLM)

KV caches allocated as fixed-size **pages** (vs contiguous max-length reservations):
- ~zero fragmentation → more concurrent sequences per GPU (throughput is a KV-memory game)
- **Copy-on-write prefix sharing:** requests sharing a prefix (same system prompt; best-of-N sampling from one prompt) share those KV pages physically
- **SGLang's RadixAttention** generalizes this: an LRU radix tree over *all* recent requests' KV — automatic cross-request prefix caching; huge for agent workloads that re-send growing transcripts

## Speculative Decoding

Decode wastes compute (bandwidth-bound) → spend it on speculation: a small **draft model** proposes k tokens cheaply; the big model **verifies all k in one parallel pass** (parallel verification ≈ prefill-shaped work). Accepted → k tokens for ~1 big-model step; rejected → keep the longest valid prefix + the big model's own token.
- **Losslessness:** rejection sampling makes output distribution identical to the big model alone — it's pure speedup (2–3× typical), not quality trade
- Variants: self-speculation via extra decode heads (Medusa/EAGLE), n-gram lookup drafts
- Works best when text is predictable (code, boilerplate); adversarially low gain on high-entropy output

## Serving Metrics (the RED of LLMs)
```
TTFT      time to first token        (prefill + queueing)  → p50/p99
TPOT/ITL  time per output token      (decode health)
Throughput  tokens/sec (system)      — the capacity number
Goodput    requests meeting BOTH TTFT & TPOT SLOs — the honest metric
+ KV cache utilization, queue depth, preemption/eviction rate
```
Chasing raw tokens/sec alone produces giant batches that violate latency SLOs — set SLOs, maximize goodput.

## Ops Notes for Self-Hosting
- **Preemption:** KV memory exhausted mid-flight → some sequence gets evicted/recomputed; visible as mid-stream stalls. Watch the preemption counter; it means you're over-admitting (admission control — `../../system-design/requests/backpressure_load_shedding.md`).
- **Prefill/decode interference:** a giant incoming prompt's prefill stalls everyone's decode → chunked prefill (interleave) or disaggregated prefill/decode fleets (the frontier pattern).
- Multi-GPU: tensor parallelism (split layers across GPUs — needs fast interconnect) for models too big for one card; pipeline/expert parallelism at larger scale.
- Autoscaling LLM pods: scale on queue depth / KV utilization, not CPU (`../../system-design/compute/horizontal_scaling_autoscaling.md`); cold starts are brutal (tens of GB of weights to load) → keep warm pools.
- Stack choices: **vLLM** (default, ecosystem), **SGLang** (radix cache, structured output speed), **TGI**, **TensorRT-LLM** (NVIDIA-tuned peak perf, more build pain), **llama.cpp/Ollama** (local/CPU/Mac — your M5 runs this class).

## Related
- `inference_internals.md`, `cost_engineering.md`, `../../system-design/requests/queueing_theory.md` (same discipline, GPU edition)
