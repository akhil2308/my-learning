# Caching Strategies

**Overview:** Caching stores frequently accessed data in a faster layer (usually memory) to reduce latency and load on the source of truth. It is the highest-leverage performance tool in backend systems — and the source of the two hardest problems in CS: cache invalidation and naming things.

---

## Where Caches Live (the layers)

```
Client (browser cache)
  → CDN (static assets, edge caching)
    → API Gateway / Reverse Proxy (response caching)
      → Application (in-process cache, e.g. LRU dict)
        → Distributed Cache (Redis / Memcached)
          → Database (buffer pool, query cache)
```

Each layer trades freshness for latency. Most backend design questions are about the **distributed cache** layer.

---

## Write Strategies (how cache and DB stay in sync)

### 1. Cache-Aside (Lazy Loading) — *the default*
App reads cache first; on miss, reads DB and populates cache. Writes go to DB, then **invalidate** (delete) the cache key.

```python
def get_user(user_id):
    user = redis.get(f"user:{user_id}")
    if user is None:                      # miss
        user = db.query(User, user_id)
        redis.setex(f"user:{user_id}", 3600, serialize(user))  # always set TTL
    return user

def update_user(user_id, data):
    db.update(User, user_id, data)
    redis.delete(f"user:{user_id}")       # invalidate, don't update
```

- **Pros:** Only caches what's actually read; cache failure ≠ system failure.
- **Cons:** First read after write is a miss (latency spike); brief window for stale reads.
- **Why delete instead of update on write:** Setting the new value in cache during a write races with concurrent writes — two updates can land in cache in the wrong order. Deletion is idempotent and order-safe.

### 2. Write-Through
Writes go to cache, cache synchronously writes to DB. Cache is always fresh; writes are slower. Good for read-heavy data that must never be stale.

### 3. Write-Behind (Write-Back)
Writes go to cache, flushed to DB asynchronously in batches. Fastest writes, but **data loss risk** if cache dies before flush. Used for metrics, counters, like-counts.

### 4. Read-Through
Like cache-aside, but the cache itself (not the app) loads from DB on miss. Cleaner app code; needs cache-side support.

---

## Eviction Policies

- **LRU (Least Recently Used):** default choice, good general behavior
- **LFU (Least Frequently Used):** better when a stable hot set exists (Redis: `allkeys-lfu`)
- **TTL-based:** every key expires; the safety net against permanent staleness — **always set a TTL** even with explicit invalidation
- Redis config: `maxmemory` + `maxmemory-policy` (e.g., `allkeys-lru`)

---

## The Classic Failure Modes (interview favorites)

### 1. Cache Stampede / Thundering Herd
A hot key expires → thousands of requests miss simultaneously → all hit the DB at once.
**Fixes:**
- **Lock/single-flight:** first miss acquires a lock (`SET key_lock NX EX 5`), rebuilds; others wait or serve stale
- **Probabilistic early refresh:** refresh before expiry with probability increasing near TTL
- **Jittered TTLs:** `TTL = base + random(0, spread)` so keys don't expire together

### 2. Cache Penetration
Requests for keys that **don't exist** (e.g., malicious IDs) always miss and hammer the DB.
**Fixes:** cache negative results (`"NULL"` with short TTL), or a Bloom filter in front.

### 3. Hot Key
One key (celebrity profile) overwhelms a single cache node.
**Fixes:** replicate the key across nodes with suffixes (`user:123:#1..#N`), or add a tiny in-process cache in front of Redis.

### 4. Stale Data / Invalidation Bugs
The eternal problem. Mitigations: short TTLs as backstop, event-driven invalidation (CDC via Debezium → invalidate on DB change), versioned keys (`user:123:v42`).

---

## Redis vs Memcached (quick take)

| | Redis | Memcached |
|---|---|---|
| Data structures | rich (lists, sets, sorted sets, streams) | strings only |
| Persistence | optional (RDB/AOF) | none |
| Clustering | Redis Cluster / Sentinel | client-side sharding |
| Threading | single-threaded core (fast enough) | multi-threaded |

Default to **Redis** — the data structures alone (rate limiting with sorted sets, distributed locks, pub/sub) justify it.

---

## Rules of Thumb
1. Cache-aside + TTL + jitter covers 90% of cases.
2. Invalidate by **deleting**, never by updating.
3. Every key gets a TTL. No exceptions.
4. Measure hit rate — below ~80% for a read-heavy service, revisit key design or TTLs.
5. The cache must be a **performance layer, not a correctness layer** — the system should survive (degraded) with the cache down.
