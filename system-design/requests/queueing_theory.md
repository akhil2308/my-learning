# Queueing Theory for Engineers (The Why Behind Scaling Intuition)

**Overview:** Two small formulas explain most production latency mysteries: why p99 explodes at 80% utilization, why "just add a queue" doesn't create capacity, and why removing 10% of load can cut latency 10×. No proofs — just the operational consequences.

---

## Little's Law

```
L = λ × W
concurrency = throughput × latency
```
Holds for ANY stable system (whole service, one pool, one queue). Uses:
- **Pool sizing:** service does 500 req/s at 200ms average → 500 × 0.2 = **100 requests in flight** on average → you need ≥100 units of concurrency (workers × connections) just to stand still.
- **Sanity checks:** "we'll handle 10k req/s with 50 workers" → implies 5ms per request end-to-end. Is that plausible? Little's Law is a lie detector for capacity claims.
- **Reverse reading:** if in-flight count is growing while throughput is flat, latency is growing — you're saturating.

---

## Utilization → Latency: The Hockey Stick

For a queue with random arrivals (M/M/1 approximation):

```
wait time ∝ ρ / (1 − ρ)        where ρ = utilization

ρ = 50% → wait =  1× service time
ρ = 80% → wait =  4×
ρ = 90% → wait =  9×
ρ = 95% → wait = 19×
ρ = 99% → wait = 99×
```

**Consequences you've felt:**
1. **Latency is nonlinear in load.** The last 20% of utilization causes almost all the queueing delay. This is why "CPU is only at 85%, we're fine" precedes outages.
2. **Headroom is a feature, not waste.** Running at ~60–75% utilization is the standard target *because* of this curve — the spare capacity buys flat latency and absorbs bursts.
3. **Small load reductions near saturation give huge latency wins** — shedding 10% of traffic at ρ=95% can cut wait times ~4×. This is the mathematical justification for load shedding.
4. **Variance makes it worse:** bursty arrivals and variable job sizes (the real world) queue *more* than the smooth-traffic formula predicts (Kingman's formula: wait scales with variability²). One slow endpoint sharing a worker pool with fast ones poisons the pool → isolate heavy work (bulkheads, separate queues).

---

## Queues Don't Add Capacity — They Buy Time

A queue in front of a service smooths **bursts**; it cannot fix **sustained** λ > μ (arrival rate > service rate). If demand exceeds capacity for long:
- queue length grows without bound → memory, then latency for *everyone* (items wait behind the backlog)
- eventually you serve requests whose clients gave up long ago

Hence: **bound every queue** and decide the overflow behavior (block = backpressure, drop = shedding). An unbounded queue is a deferred outage. See `backpressure_load_shedding.md`.

**Queue depth vs queue delay:** depth 1000 means nothing without the drain rate — 1000 items at 10k/s is 100ms; at 10/s it's 100 seconds. Alert on **estimated wait time** (depth ÷ drain rate) or item age, not raw depth.

---

## Tail Latency & Fan-Out Amplification

Percentiles compound brutally under fan-out. If one backend call is slower than its p99 1% of the time, a request touching **N** backends is slow with probability `1 − 0.99^N`:

```
N = 1   →  1% of requests hit a p99
N = 10  → ~10%
N = 100 → ~63%      ← "the tail at scale"
```
**Your p99 becomes someone's p50 after fan-out.** Mitigations:
- Reduce fan-out; parallelize what remains (total = max, not sum)
- **Request hedging:** after p95 delay, send a duplicate to another replica, take the first answer (needs idempotent reads; caps: hedge ≤5% of requests)
- Per-branch timeouts + partial results / graceful degradation
- Attack the *causes* of tails: GC pauses, cold caches, connection setup, noisy neighbors, that one unindexed query

---

## One-Screen Cheat Sheet
- `concurrency = throughput × latency` — size pools with it, audit claims with it
- Target ~60–75% utilization; latency ∝ ρ/(1−ρ) — the curve is the argument
- Bound every queue; alert on queue *delay*, not depth
- Sustained overload needs shedding or capacity, never "a bigger queue"
- Fan-out multiplies tail exposure: fix tails or hedge

## Related
- `backpressure_load_shedding.md`, `../resilience/capacity_estimation.md`, `../compute/horizontal_scaling_autoscaling.md`
