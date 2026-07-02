# Search & Analytics at Scale (OLTP vs OLAP, Inverted Indexes, Columnar Stores)

**Overview:** Postgres is a transaction machine. Two workloads eventually outgrow it: **full-text search** ("find products matching 'wireles headphone'" — typo intended) and **analytics** ("revenue by region by week for 2 years"). Both fail on row-store B-trees for structural reasons; both have purpose-built engines. The meta-skill: recognizing *which* workload you're looking at.

---

## OLTP vs OLAP

| | OLTP (Postgres) | OLAP (warehouse) |
|---|---|---|
| Query shape | fetch/update few rows by key | scan millions of rows, few columns, aggregate |
| Storage | **row**-oriented (whole row together) | **column**-oriented |
| Optimized for | latency, concurrency, ACID | scan throughput, compression |
| Data freshness | the source of truth | seconds→hours behind |

**Why columnar wins analytics:** `SELECT region, SUM(amount) ... GROUP BY region` on a row store reads *every column* of every row off disk. A column store reads just `region` + `amount` — often <5% of the bytes — and same-type columns compress brutally well (RLE, dictionary, delta: 10–30×) and vectorize on CPU. Same logic in reverse: point lookups/updates on columnar are terrible. Neither store is "better" — they're transposed for different access patterns.

**Engines:** Snowflake/BigQuery/Redshift (managed warehouses), **ClickHouse** (self-hosted real-time analytics; superb for event/log analytics), DuckDB (in-process — the "pandas replacement" for local OLAP), Parquet (the columnar *file* format for data lakes).

### Getting data there: CDC pipelines
Never run analytics on the OLTP primary (one fat scan evicts the buffer cache and tanks p99 for real users; a replica dedicated to internal queries is the honest interim hack).
The standard pipeline: **Debezium tails the Postgres WAL → Kafka → warehouse sink** — the same CDC machinery as the outbox pattern (`distributed_transactions.md`). Batch ELT (Fivetran/Airbyte + dbt) when hours of lag is fine.

---

## Full-Text Search: the Inverted Index

B-trees answer "row → value"; search needs **"term → rows"** — a transposed (inverted) index:

```
Documents:  d1: "cheap wireless mouse"   d2: "wireless headphones"
Inverted index:
  wireless   → [d1, d2]
  mouse      → [d1]
  headphone  → [d2]        (after analysis)
```

**Analysis pipeline** (the part that makes search feel smart — applied to docs at index time AND to queries): tokenize → lowercase → **stemming** ("headphones"→"headphone") → synonyms/stopwords. Typo tolerance = fuzzy matching (edit distance) or n-grams. **Relevance ranking** — BM25 scoring (term frequency × rarity, length-normalized) — is what separates search from `WHERE LIKE`.

**Engines:** Elasticsearch/**OpenSearch** (the default: inverted index sharded across nodes + aggregations + the ELK logging stack), **Meilisearch/Typesense** (lightweight, great DX for product search), Lucene under most of them.

**Postgres FTS first, though:** `tsvector` + GIN index handles stemming, ranking, and modest scale with zero new infrastructure — the right v1 for most apps. Graduate to a real engine when relevance tuning, typo tolerance, faceting, or index size demand it.

**The sync problem (always):** search index = derived data, updated from the source of truth via CDC/events → *eventually consistent* — a just-created product may be unsearchable for seconds. Design the UX for it; rebuildability from source is your recovery story.

### Vector search (the 2020s addition)
Semantic similarity via embeddings + ANN indexes (HNSW): **pgvector** (in Postgres — your stack), dedicated stores (Qdrant, Milvus), or hybrid keyword+vector in OpenSearch. Same derived-data/sync rules apply. Ranking quality in RAG = hybrid BM25 + vector + reranker (see `../../ai/rag-guide.md` — this doc is the infra-side view of the same pipeline).

---

## Choosing (cheat table)

| Need | Reach for |
|---|---|
| "Find rows matching text, ranked, typo-tolerant" | PG FTS → Meilisearch/OpenSearch as it grows |
| Dashboards/aggregations over history | Warehouse (Snowflake/BigQuery) or ClickHouse |
| Real-time event/log analytics, self-hosted | ClickHouse |
| Log search for debugging | Loki (cheap, label-based) or ELK (full text) |
| Semantic/RAG retrieval | pgvector → dedicated vector store at scale |
| All of the above tomorrow | Ship Postgres today; wire CDC early — it feeds every derived store |

## Related
- `event_driven_kafka.md` + `distributed_transactions.md` (CDC/outbox feed derived stores), `consistency_models.md` (derived data = eventual), `../../ai/rag-guide.md`
