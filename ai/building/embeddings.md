# Embeddings Deep-Dive

**Overview:** Embeddings map text to vectors such that **semantic similarity ≈ geometric proximity**. They're the substrate of RAG retrieval, semantic search, clustering, dedup, recommendations, and classification. This is the companion your `rag-guide.md` assumes — the properties and gotchas of the vectors themselves.

---

## What the Vector Captures (and doesn't)

An embedding model (typically a BERT-style bidirectional encoder, contrastively trained on pairs) compresses a text's *meaning as trained* into 256–3072 dims. Key properties:
- **Trained-notion-of-similarity:** models are tuned so queries sit near their *answers* (asymmetric retrieval), not just near paraphrases — why some models want `query:` / `passage:` prefixes; skipping them measurably hurts.
- **Bag-of-meaning tendencies:** negation ("covers X" vs "does not cover X"), numbers, dates, and exact identifiers embed weakly — semantically tiny, lexically decisive. **This is the argument for hybrid search:** BM25 catches what vectors blur (IDs, part numbers, negations); vectors catch what keywords miss (synonyms, paraphrase). Hybrid + reranker is the default-good stack (`../rag-guide.md`).
- **One vector per chunk = averaging:** a chunk about five topics embeds as a muddy mean. Hence chunking strategy *is* embedding strategy: semantically coherent chunks (respect headings/paragraphs), sized to one idea (~200–500 tokens typical), with overlap; **contextual enrichment** (prepend doc title/section or an LLM-written one-line context to each chunk before embedding) sharply improves retrieval of context-dependent chunks.

## Similarity Math (the 3 facts you need)
- **Cosine similarity** is the default; most modern models emit **normalized** vectors, making cosine ≡ dot product ≡ (monotonic with) Euclidean — the metric choice mostly stops mattering *if* you normalize. Just match the metric to what the model was trained with and stay consistent.
- **Scores are relative, not absolute:** 0.82 means "closer than 0.79," not "82% relevant" — score distributions vary by model and corpus. Thresholds must be calibrated per corpus on labeled examples (`../quality/evals.md`), and re-calibrated when the model changes.
- **High-dim intuition fails:** everything is "kind of far" from everything; ranking survives, raw distances mislead. Trust top-k order + a reranker, not distance magnitudes.

## Operational Realities

- **Embeddings are model-versioned:** vectors from different models (or versions) are **incompatible spaces** — never mix in one index. Model upgrade = re-embed the corpus = plan for it (store raw text + model version alongside vectors; re-embedding is a batch job — `../inference/cost_engineering.md` batch APIs).
- **Matryoshka (MRL) embeddings:** trained so prefixes of the vector are usable — store/search at 256–512 dims (cheap, fast), optionally rescore top candidates at full dim. Directly attacks vector-store cost at scale.
- **Dimension × count = your bill:** 10M chunks × 1536 dims × 4 bytes ≈ 60GB of raw vectors before index overhead — quantized vectors (int8/binary) + MRL shrink it dramatically with modest recall cost.
- **ANN indexes (HNSW):** approximate by design — recall/latency/memory tuned via `ef`/`M` parameters; measure recall@k against exact search on a sample, don't assume. pgvector gives you HNSW inside Postgres (your stack) — right up until index size/QPS says dedicated store (`../../system-design/data/search_and_analytics.md`).
- **Freshness & consistency:** the index is derived data — CDC/outbox-fed, eventually consistent, permission-filtered per tenant (the RAG-BOLA point, `../llm_agent_security.md` §4).

## Beyond Retrieval (cheap wins)
- **Near-dup detection / dedup** of documents, tickets, cached LLM answers (semantic cache: embed query → if a very-close past query exists, serve its answer)
- **Clustering + labeling** for corpus exploration (embed → HDBSCAN/k-means → LLM names each cluster)
- **Lightweight classification:** embed + logistic regression — trains in seconds, often beats prompting for stable label sets at ~zero inference cost
- **Routing:** embed the request, nearest-centroid picks the specialist agent/prompt — cheaper than an LLM router call

## Related
- `../rag-guide.md` (the pipeline these vectors feed), `../../system-design/data/search_and_analytics.md` (infra view), `../quality/evals.md` (retrieval metrics: recall@k, MRR)
