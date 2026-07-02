# Database Scaling: Replication, Sharding & the Path Between

**Overview:** Databases are usually the first real bottleneck as a system grows, and the hardest component to scale because they hold **state**. This doc covers the escalation ladder — from a single Postgres instance to a sharded fleet — and the trade-offs at each rung.

---

## The Scaling Ladder (do these in order)

```
1. Optimize          → indexes, query tuning, connection pooling (PgBouncer)
2. Vertical scale    → bigger box (works far longer than people admit)
3. Add caching       → Redis in front (see caching.md)
4. Read replicas     → scale reads
5. Partitioning      → split tables within one instance
6. Sharding          → split data across instances (last resort)
```

**Key point for interviews:** jumping to sharding without exhausting 1–5 is a red flag. A single well-tuned Postgres on modern hardware handles tens of thousands of QPS.

---

## Step 4: Replication (scaling reads)

One **primary** takes all writes; changes stream to **replicas** (Postgres: WAL streaming) which serve reads.

```
            writes
Client ──────────────→ Primary
   │                      │ WAL stream
   │ reads          ┌─────┴─────┐
   └───────────→ Replica 1   Replica 2
```

### Sync vs Async Replication
- **Async (default):** primary confirms write immediately; replicas catch up. Fast, but a primary crash can lose the last few transactions, and replicas serve slightly stale data (**replication lag**).
- **Sync:** primary waits for replica acknowledgment. No loss, but every write pays the latency, and a slow replica stalls writes. Middle ground: quorum/semi-sync (wait for 1 of N).

### The Replication Lag Trap: Read-Your-Own-Writes
User updates their profile (→ primary), page reloads and reads a lagging replica → their change "disappeared."
**Fixes:**
- Route reads to the primary for X seconds after a user's write (sticky reads)
- Route reads *for data the user just modified* to the primary
- Session-level LSN tracking: only read from replicas that have caught up to your write

### Failover
Replica promotion on primary failure — handled by Patroni (Postgres), RDS Multi-AZ, or Sentinel (Redis). Watch out for **split brain** (two nodes think they're primary); fencing/quorum prevents it.

---

## Step 5: Partitioning (within one instance)

Split a huge table into smaller physical pieces the planner can skip.
- **Range:** by date — perfect for time-series; drop old partitions instead of DELETE
- **List:** by region/tenant
- **Hash:** even spread when no natural ranges exist

Postgres has this native (`PARTITION BY RANGE (created_at)`). Solves "one giant table" problems (bloated indexes, slow vacuums) without distributed-systems pain.

---

## Step 6: Sharding (across instances)

Each **shard** is an independent database holding a slice of the data. Now writes scale too — at the cost of significant complexity.

### Choosing the Shard Key (the decision that makes or breaks it)
The shard key determines which shard owns each row. Good keys:
- **High cardinality** and even distribution (avoid hot shards)
- Match the **dominant query pattern** — queries should hit ONE shard

Examples: `user_id` for user-centric apps (all of a user's data co-located); Instagram sharded by user with region awareness. **Bad key:** `created_at` for write-heavy data — all writes hammer the newest shard.

### Routing Strategies
- **Hash-based:** `shard = hash(key) % N` — even spread, but resharding when N changes moves almost everything → use **consistent hashing** (only ~1/N of keys move)
- **Range-based:** key ranges per shard — enables range scans, risks hot spots
- **Directory-based:** lookup service maps key → shard — flexible, extra hop, the directory becomes critical infrastructure

### What Sharding Breaks
1. **Cross-shard joins** — gone. Denormalize, or join in the application layer.
2. **Cross-shard transactions** — need 2PC or sagas; both are painful. Design so transactions stay within a shard.
3. **Unique auto-increment IDs** — need Snowflake-style IDs (timestamp + machine + sequence) or UUIDv7.
4. **Rebalancing** — hot or oversized shards need splitting/migration while live. This is operationally the hardest part.
5. **Analytics** — cross-shard aggregation → ship data to a warehouse (CDC → OLAP) instead.

---

## Alternatives Before/Instead of Manual Sharding
- **Managed distributed SQL:** CockroachDB, YugabyteDB, Spanner, Vitess (MySQL), Citus (Postgres extension) — sharding handled for you
- **Polyglot persistence:** move the specific painful workload out (hot counters → Redis, event firehose → Cassandra/Kafka, search → Elasticsearch) and keep Postgres for relational core
- **CQRS:** separate write model from read models fed by events; each side scales independently

---

## Interview Cheat Codes
- "Reads are the bottleneck" → cache + replicas. "Writes are the bottleneck" → shard (after vertical + partition).
- Always mention **replication lag** and read-your-own-writes when you say "read replica."
- Always mention **shard key choice + resharding pain** when you say "sharding."
- CAP framing: within a replicated Postgres setup, sync vs async replication is exactly the consistency-vs-availability/latency trade.
