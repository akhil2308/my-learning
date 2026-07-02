# Model Architecture Landscape: MoE, Multimodal, SSMs & Reading Model Cards

**Overview:** Enough architecture literacy to read a model card or paper intelligently and predict cost/latency/behavior from the spec — not to design networks. The decoder-only transformer (`../foundations/transformers_attention.md`) is the baseline; this doc covers the variations that matter.

---

## Dense vs Mixture-of-Experts (MoE)

- **Dense:** every parameter participates in every token. Capability and cost scale together.
- **MoE:** each transformer block's MLP is replaced by N expert MLPs + a **router** that sends each token to the top-k (usually 1–2) experts. Headline consequence: **total params ≠ active params** — e.g., "≈400B total / ≈17–37B active" class models compute like a mid-size model while storing frontier-scale knowledge.
- **The trade you feel operationally:** compute per token ∝ *active* params (fast, cheap decode) but **memory ∝ total params** (all experts must be resident) → MoE is great for providers with big GPU fleets, awkward for self-hosting (VRAM bill of the total size, speed of the active size).
- Quirks: routing adds training instability (load-balancing losses), slightly higher output variance (routing sensitivity — one reason temp-0 non-determinism, `../foundations/sampling_decoding.md`), and expert-parallel serving complexity. Most frontier models are now MoE — when a card says "A × B activated," read it as speed≈B, memory≈A.

## Multimodal Models

- **Dominant pattern (late fusion):** a vision encoder (ViT) turns images into token-like embeddings → projected into the LLM's embedding space → the transformer attends over text and image tokens uniformly. Images are "just more tokens" — which is why image inputs consume large token counts (cost!) and why fine detail (small text, dense charts) degrades with downscaling: resolution/tiling policy is a real quality knob.
- **Early-fusion / natively multimodal:** trained on interleaved modalities from scratch; increasingly the frontier norm; enables native image *generation* and tighter cross-modal reasoning.
- Audio/video follow the same recipe (encoders → token streams); video = many frames = token explosion, hence aggressive sampling.
- Practical: OCR-ish extraction from clean docs is strong; precise spatial reasoning, counting, and reading tiny text remain weak spots — evaluate on *your* documents (`../quality/evals.md`).

## State-Space Models & Hybrids (the attention challengers)

- **Motivation:** attention is O(n²) with a linearly growing KV cache (`../inference/inference_internals.md`). **SSMs (Mamba family)** process sequences recurrently with **constant memory per token** and O(n) compute — no KV cache blowup; enormous appeal for long context and cheap inference.
- **The catch:** a fixed-size state must *compress* history — precise long-range recall ("quote line 3 of the doc") suffers vs attention's exact lookup.
- **Where it landed:** **hybrids** — mostly-SSM/linear-attention layers with periodic full-attention layers (Jamba-style and successors) capture most of the efficiency while retaining recall. Expect the "cheap long-context" model tier to be hybrid; pure transformers hold the quality frontier.
- Related efficiency lineage inside transformers themselves: GQA/MQA, sliding-window attention, attention sinks — same war, incremental weapons.

## Small Language Models (SLMs)
1–8B models (Phi/Gemma/Qwen-small class) punched far above their size via data curation + distillation from frontier models (`training_pipeline.md`). Role: the cheap tier in routing/cascades (`../inference/cost_engineering.md`), on-device/edge inference (your M-series runs these locally), fine-tune targets (`lora_peft.md`), and specialist agent workers (`../building/agent_architectures.md`). The pattern: **frontier model designs the workflow; SLMs run the volume.**

## Reading a Model Card: the Spec-to-Consequence Table
| Spec line | What it tells you |
|---|---|
| Dense 8B / 70B | memory ≈ 2×params (fp16) or ~0.5–0.6× (4-bit); speed ∝ params |
| MoE "A total, B active" | speed/cost ≈ B, VRAM ≈ A |
| GQA, kv_heads=8 | smaller KV cache → more concurrency (`../inference/`) |
| Context 128k/1M | advertised; effective is less — test (`../foundations/context_windows.md`) |
| "Reasoning" / thinking budget | test-time compute model (`../emerging/reasoning_test_time_compute.md`) |
| Vision-language | image tokens = cost; check resolution handling |
| License (Apache/community/custom) | open-weight ≠ unrestricted — read it |

## Related
- `../foundations/transformers_attention.md`, `../inference/inference_internals.md`, `training_pipeline.md`, `../emerging/emerging_landscape.md`
