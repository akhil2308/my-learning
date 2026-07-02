# Backpressure, Load Shedding & Admission Control

**Overview:** Rate limiting protects against individual abusive clients. This doc is about **aggregate overload** — when total legitimate demand exceeds capacity. The core principle: **a system that rejects some work keeps serving; a system that accepts everything collapses and serves no one.** Overload handling is a designed behavior, not an accident.

---

## Why Systems Collapse Under Load (congestion collapse)

1. Load exceeds capacity → queues grow → latency rises
2. Clients time out and **retry** → effective load *increases* further
3. Server does work for requests whose clients already gave up (wasted work)
4. Queues consume memory, GC pressure rises, throughput *drops* below normal capacity
5. Goodput → 0 even though the server is "busy" at 100% CPU

The fix at every layer: bound the queues, reject early, make retries polite.

---

## Backpressure

**Definition:** downstream signals upstream to slow down, propagating resistance toward the source instead of buffering infinitely.

- **Bounded queues everywhere:** an unbounded queue converts overload into an OOM crash later. When the bound is hit → block the producer (backpressure) or reject (shedding). Both beat unbounded.
- **Natural backpressure exists in:** TCP (flow control windows), HTTP/2 (stream flow control), Kafka consumers (pull model — consumers take only what they can handle; consumer lag *is* the visible backpressure), async frameworks (asyncio semaphores bounding concurrent tasks).
- **Where it breaks:** fire-and-forget push (unbounded task spawning, `asyncio.create_task` per request with no semaphore), unbounded thread pool queues, producers ignoring queue depth.

```python
# Bounding concurrency to a fragile downstream
sem = asyncio.Semaphore(50)          # max 50 in-flight calls
async def call_downstream(payload):
    async with sem:                   # producers wait — backpressure
        return await client.post(url, json=payload, timeout=2.0)
```

---

## Load Shedding

When you can't slow the source (public internet), **drop work deliberately and cheaply**:

- **Reject early:** shed at the gateway/entry, before deserialization, DB pools, or business logic spend resources. A rejection costing 0.1ms protects work costing 100ms.
- **Prioritized shedding:** not all requests are equal — shed health-check-crawlers and analytics before checkout and payments. Requires request classification (endpoint, customer tier, or an explicit `criticality` header).
- **Signals to shed on:** queue depth / queue *wait time* (best — directly measures overload), in-flight request count, p99 latency, memory. CPU alone is a lagging, noisy signal.
- **Response:** `429`/`503` + `Retry-After`. Cheap static responses; never render an expensive error page under overload.
- **Deadline propagation:** pass the request's remaining time budget downstream (`x-request-deadline`); any hop that can't finish in budget aborts immediately — stops the "work for dead clients" waste.

---

## Admission Control & Adaptive Concurrency

Static limits (max 200 in-flight) need manual tuning and go stale. **Adaptive concurrency** measures its way to the limit:

- **Gradient/TCP-Vegas style (Netflix concurrency-limits):** track latency; when latency rises relative to the no-load baseline, shrink the concurrency limit; when healthy, probe upward. AIMD — same algorithm as TCP congestion control.
- **CoDel for queues:** drop requests that have *waited* longer than a target (e.g., 5ms) — controls queueing delay directly rather than queue length.
- The theory of *why* limits must exist at all: `queueing_theory.md` — latency explodes near 100% utilization.

---

## The Retry Storm (client side of the contract)

Overload handling fails if clients retry aggressively:
- **Exponential backoff + full jitter** — mandatory
- **Retry budgets:** retries ≤ ~10% of requests; beyond that, stop retrying (you're the DDoS now)
- **Circuit breakers** stop hammering a dependency that's clearly down
- **Honor `Retry-After`.** Never retry non-idempotent ops without idempotency keys.

---

## Checklist
- [ ] Every queue and pool in the system is **bounded** — inventory them
- [ ] Entry point sheds on queue-wait-time with cheap 429/503 responses
- [ ] Requests classified so shedding is priority-aware
- [ ] Deadlines propagate; expired work is abandoned
- [ ] Clients: backoff + jitter + retry budget + circuit breaker
- [ ] Load test past the breaking point and verify goodput *plateaus* instead of collapsing

## Related
- `queueing_theory.md` (the math), `rate_limiting.md` (per-client), `../../system-design/productionizing.md` §4
