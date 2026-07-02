# LoRA & PEFT: Parameter-Efficient Fine-Tuning

**Overview:** Full fine-tuning updates every weight — for a 70B model that means hundreds of GB of optimizer state and a GPU cluster. PEFT (Parameter-Efficient Fine-Tuning) freezes the base model and trains a tiny add-on. **LoRA** won this category so decisively that "fine-tuning" colloquially means LoRA now. Companion to `../llm-fine-tuning.md` — this is the mechanism and the decisions.

---

## LoRA in One Diagram

A weight matrix update ΔW is constrained to be **low-rank**: instead of learning ΔW (d×d, millions of params), learn two skinny matrices:

```
W_effective = W_frozen + (α/r) · B·A        A: r×d,  B: d×r,   r ≪ d  (r = 4–64)

forward pass: h = W_frozen·x + B·(A·x)      — a cheap parallel branch
```
- Trainable params drop ~100–1000× (a 70B LoRA = tens of MB, not GB)
- **Why it works:** task adaptation empirically lives in a low-dimensional subspace — you're steering a capable model, not teaching it from scratch (same lesson as SFT generally, `training_pipeline.md`)
- **Zero inference overhead** if you merge: `W' = W + BA` folds the adapter into the base weights

## QLoRA: the Consumer-Hardware Unlock
Base model quantized to **4-bit** (NF4) and frozen; LoRA adapters train in bf16 on top; gradients flow through the quantized weights. Result: fine-tune a 70B on a single 48GB GPU, a 7–13B on a gaming card / your M-series Mac (MPS support exists; MLX is the smoother Apple path). Quality ≈ 16-bit LoRA for most tasks. This + `../AWQ & GPTQ.md` (inference-side quantization) are the two halves of "big models on small hardware."

## The Knobs (what actually matters)

- **Rank r:** 8–16 default; 32–64 for harder/style-heavy tasks. Diminishing returns beyond — more data beats more rank.
- **α (scaling):** convention α = 2r; effectively a learning-rate multiplier on the adapter.
- **Target modules:** minimum = attention projections (q,v); common best practice = **all linear layers** (q,k,v,o + MLP) — bigger quality gain than raising r.
- **Learning rate:** ~1e-4 (10× higher than full FT norms); LoRA is forgiving here.
- Data >> hyperparameters: 500–5,000 **high-quality, consistent** examples beat 50k scraped ones. Format consistency in training data is behavior consistency at inference.

## Multi-Adapter Serving (the ops win)
Adapters are swappable attachments to one shared base:
- **Per-tenant/per-task adapters:** one base model in GPU memory + N tiny adapters, hot-swapped or batched together (vLLM supports multi-LoRA serving) — massively cheaper than N fine-tuned model copies
- A/B testing fine-tunes = swapping MB-sized files
- Merge-to-base when you want zero-overhead single-task deployment

## When (and When Not) to Fine-Tune — the honest decision
Reach for LoRA when: a **stable, high-volume, well-defined** task needs consistent style/format/domain behavior; prompting + few-shot has plateaued *on your evals*; unit cost matters (distill the prompted frontier model into a small tuned one — `../inference/cost_engineering.md`); or strict latency/self-host constraints exist.
Don't fine-tune for: **knowledge injection** (RAG wins: updatable, citable, no retraining — `hallucination` & `rag-guide`), fast-changing behavior (prompt changes deploy in minutes; retrains take days), or before you have an eval set (you can't measure the win) and a few hundred good examples.
Failure modes: overfitting to training phrasing, **catastrophic forgetting** of general ability (mitigate: mix general data in, keep r modest, eval broadly), and silently training on garbage labels.

Other PEFT flavors (name-check): prefix/prompt-tuning (learned soft tokens — mostly superseded), IA³, DoRA (LoRA refinement, modest gains). LoRA/QLoRA is the default; the rest are paper-reading vocabulary.

## Related
- `../llm-fine-tuning.md` (pipeline), `training_pipeline.md` (where SFT sits), `../AWQ & GPTQ.md`, `../quality/evals.md` (measure before/after — non-negotiable)
