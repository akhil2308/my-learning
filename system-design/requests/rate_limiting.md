# Rate Limiting & Throttling (Deep Dive)

**Overview:** Rate limiting bounds how fast clients can consume your system. It's simultaneously a fairness tool, a protection layer (brute force, scraping), and a stability mechanism (preventing overload). The hard part isn't the algorithm — it's doing it **consistently across many nodes**.

---

## The Algorithms

### 1. Fixed Window
Counter per window (`user:123:minute:1720000`). Simple, O(1).
**Flaw — boundary burst:** 100 req at 11:59:59 + 100 at 12:00:01 = 200 in 2 seconds, all "within limits."

### 2. Sliding Window Log
Store timestamp of every request (Redis sorted set), count entries in the last N seconds.
Exact, but O(limit) memory per key — expensive at high limits.

```python
# Redis sliding window (atomic via pipeline/Lua)
now = time.time()
pipe.zremrangebyscore(key, 0, now - window)   # drop old entries
pipe.zadd(key, {str(uuid4()): now})
pipe.zcard(key)                               # count = current rate
pipe.expire(key, window)
```

### 3. Sliding Window Counter (the pragmatic default)
Weighted blend of previous + current fixed windows: `count = curr + prev × overlap_fraction`. Near-exact, O(1) memory. What Cloudflare uses.

### 4. Token Bucket
Bucket holds up to `burst` tokens, refilled at `rate`/sec; each request spends one. **Allows controlled bursts** while enforcing a long-term average — usually the right semantic for APIs (clients are bursty by nature). Nginx `limit_req` (with `burst=`), AWS API Gateway use this.

### 5. Leaky Bucket
Requests enter a queue drained at a constant rate. Smooths output perfectly — good when the *downstream* needs steady flow (e.g., calling a fragile third-party API). Adds queueing latency.

**Choosing:** API limits → token bucket. Accurate billing/quota → sliding window counter. Smoothing calls *you make* to others → leaky bucket.

---

## Distributed Rate Limiting (the real problem)

With N app nodes, local counters allow N× the limit. Options:

1. **Centralized store (Redis + Lua):** one atomic script checks-and-increments. Accurate; adds a Redis round-trip per request and makes Redis hot-path critical. Standard answer.
2. **Local cache + async sync:** each node keeps local counters, syncs to Redis periodically. Fast, slightly over-admits during sync gaps — usually acceptable.
3. **Gateway-level:** enforce at the single entry point (Envoy ratelimit service, Kong, API Gateway) — the cleanest place; app nodes never see excess traffic.
4. **Client-partitioned:** consistent-hash users to nodes so each user's counter lives on one node (see consistent_hashing.md).

**Precision vs cost trade:** exact global limiting is expensive; "roughly 1000/min, occasionally 1050" is fine for protection purposes. Only billing needs exactness.

---

## Design Decisions

- **Dimensions:** per-IP (crude — NATs/offices share IPs), per-user, per-API-key, per-endpoint, per-tenant. Real systems layer several: `login: 5/min/IP` AND `global: 1000/s`.
- **Response contract:** `429` + `Retry-After` header + `X-RateLimit-Limit/Remaining/Reset` headers so well-behaved clients self-regulate.
- **Fail-open vs fail-closed:** if Redis is down, do you admit everything (availability) or reject everything (protection)? Default fail-open for general APIs, fail-closed for auth endpoints.
- **Tiering:** limits as a product feature (free: 100/day, pro: 10k/day) — keep config per key, not hardcoded.
- Rate limiting caps *rate*; **concurrency limiting** caps simultaneous in-flight work (semaphores) — you often need both (see backpressure doc).

---

## Related
- Backpressure & load shedding (`backpressure_load_shedding.md`) — what to do when limits aren't enough
- Security uses (`../security/web_api_attacks.md` §5)
- LeetCode: Logger Rate Limiter (359), Design Hit Counter (362)
