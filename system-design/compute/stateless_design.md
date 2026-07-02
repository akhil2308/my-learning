# Stateless Design & Session Externalization

**Overview:** A service is **stateless** when any replica can serve any request — nothing about a client's session lives in one process's memory or disk. Statelessness is *the* enabling property behind horizontal scaling, rolling deploys, autoscaling, and self-healing. It doesn't eliminate state; it **relocates** it to systems built for it.

---

## Why It Matters (what breaks without it)

If node 3 holds user X's session in memory:
- LB must route X to node 3 forever (**sticky sessions**)
- Node 3 dies / deploys → X is logged out mid-checkout
- Autoscaler can't remove node 3 safely; new nodes don't help X
- Load skews: long-lived sticky users pile onto old nodes

Statelessness converts "which node?" from a correctness question into a pure load-balancing question.

## Sticky Sessions (and why they're a trap)

LB pins a client to one backend (cookie-based or IP-hash affinity). Legitimate as a **transitional crutch** for legacy in-memory-session apps, and inherent to WebSockets (a connection *is* sticky). But as an architecture: uneven load, deploy pain, failure = data loss. Externalize instead.

---

## Where Each Kind of State Goes

| In-process state (bad) | External home (good) |
|---|---|
| Session dict in memory | **Redis** (session store, TTL) or signed cookie/JWT (client-side claims) |
| Uploaded files on local disk | **Object storage (S3)** — local disk is a scratchpad, wiped on reschedule |
| In-memory cache as source of truth | Redis/Memcached (in-process caching is fine ONLY as a best-effort layer over shared truth) |
| Locks via `threading.Lock` across "the" process | **Distributed locks** (Redis/Postgres advisory) — see `../data/consensus_and_coordination.md` |
| Rate-limit counters per process | Redis counters (`../requests/rate_limiting.md`) |
| Scheduled job "runs on the one instance" | Distributed-locked job or K8s CronJob |
| WebSocket connections | Inherently stateful → pub/sub backplane (`../requests/async_request_patterns.md`) |
| Business data | The database, obviously — the point is nothing *else* becomes an accidental database |

**The test:** `kubectl delete pod` any single pod at random, any time. If any user notices beyond a possibly-retried request, you have hidden state.

---

## Session Externalization: the two strategies

### 1. Server-side sessions in Redis
Cookie holds only a random session ID; all data in Redis with TTL.
- Instant revocation, small cookie, data never leaves your infra.
- Cost: Redis lookup per request (sub-ms; cache-friendly), Redis becomes critical-path (HA it).

### 2. Client-side state (JWT / signed cookies)
Claims live in the token; server verifies signature — zero lookup.
- Perfectly stateless servers; the trade is revocation difficulty and token size.
- Full comparison: `../security/authn_authz.md` §2–3.

Hybrid (common): JWT for identity claims + Redis for heavier session data and revocation lists.

---

## Subtle Statefulness (the ones that sneak in)

- **Local caches that matter:** cold pod = slow pod → readiness/warm-up handling (`horizontal_scaling_autoscaling.md`), and never *correctness*-dependent local caches.
- **In-flight requests ARE state:** graceful shutdown (drain on SIGTERM) is what makes "kill any pod" true.
- **Module-level singletons** accumulating data (metrics dicts, dedupe sets) — memory leaks *and* correctness bugs across replicas.
- **"Leader-ish" behavior** (one instance does the nightly job) — make it explicit with leases/locks, not "we only run one replica."
- **Temp files:** fine within a request; anything needed *across* requests goes to S3.

## When State Is the Point
Databases, brokers, and stateful stream processors are legitimately stateful — they get the heavyweight machinery (replication, consensus, StatefulSets, persistent volumes). The design principle is really: **push state down into the few systems engineered for it, keep the wide compute layer stateless.**

## Related
- `horizontal_scaling_autoscaling.md`, `../security/authn_authz.md`, `../data/consensus_and_coordination.md`
