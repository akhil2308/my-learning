# CURRICULUM — The Ascension Tree

Built from [GAP-MAP.md](GAP-MAP.md). Only `MISSING`/`PARTIAL` nodes and rep-appends — nothing already covered gets rewritten. Extends the repo's leveling convention (`leveling-system.json` levels 1–6 = DSA) with **Levels 7–16: backend/AI fundamentals**. Each level is a zone; each session is exactly 90 min (30 read / 60 rep); every session ends in one binary pass/fail rep.

## TL;DR

- **51 doc-sessions total**: 28 new docs + 23 rep-appends. Plus 7 DSA **timed warmup reps** (25 min each, interleaved — not calendar sessions).
- **Fast lane `[INTERVIEW-CRITICAL]`: 39 sessions**, ordered below as the literal execution sequence. Post-Aug ladder: 12 sessions.
- **Pacing math (today = 7-Jul, first application = 1-Aug = 25 days):** 39 sessions ÷ 25 days = 1.56/day. Realistic split: **sessions 1–27 are the must-finish-before-applying core** (~1.1/day); sessions 28–39 are consolidation reps in your strong areas (security/AI) — run them during the application/interview window at low cost. If a day slips, cut from 28–39, never from 1–27.
- DSA warmups: one timed technique rep per weekday morning (25 min), cycling the 7 existing technique docs. They ride alongside, not instead of, the day's session.

---

## Skill tree (zones)

| Level | Zone | Curriculum area | Sessions |
|---|---|---|---|
| 7 | The Interpreter | A — how computers run my code | 3 |
| 8 | The Kernel | B — operating systems | 4 |
| 9 | The Wire | C — networking | 3 |
| 10 | The Vault | D — database internals | 7 |
| 11 | The Race | E — concurrency | 3 |
| 12 | The Swarm | F — distributed systems | 5 |
| 13 | The Arena | G — system design canon | 7 |
| 14 | The Gate | I — security | 3 |
| 15 | The Oracle | J — AI/LLM (reps only) | 6 |
| 16 | The Final Boss | K — interview execution | 2 |
| — | Daily grind | H — DSA patterns | 4 new + 7 warmup reps |

---

## FAST LANE — execute in this order (all `[INTERVIEW-CRITICAL]`)

Type: **NEW** = new doc per the template · **REP** = append `## Practice Rep` to existing doc.

### Week 1 (7–13 Jul) — The Interpreter, The Kernel, The Race, The Wire

| # | Session id | Type | Output | Covers → rep |
|---|---|---|---|---|
| 1 | `cpython-internals` | NEW | `fundamentals/machine/cpython_internals.md` | Bytecode, GIL, refcounting + gc → rep: predict-then-verify with `dis`, `sys.getrefcount`, a GIL-bound benchmark |
| 2 | `python-performance-model` | NEW | `fundamentals/machine/python_performance_model.md` | asyncio vs threads vs multiprocessing vs C-ext decision tree → rep: make one workload 10× faster by picking right |
| 3 | `star-story-bank` | NEW | `interview/star_story_bank.md` | Template + 8 empty slots (IRIS, RAPID, supervisor orch, fastapi template…) → rep: fill 2 slots today; 1/week after (early on purpose — stories need marinating) |
| 4 | `processes-threads-scheduling` | NEW | `fundamentals/os/processes_threads_scheduling.md` | fork/exec, context switch cost, CFS → rep: measure switch cost + thread-vs-process memory with real numbers |
| 5 | `fds-sockets-epoll` | NEW | `fundamentals/os/fds_sockets_epoll.md` | FDs, socket lifecycle, select→epoll → rep: write a 30-line epoll echo server, explain each syscall in strace |
| 6 | `asyncio-event-loop` | NEW | `fundamentals/concurrency/asyncio_event_loop.md` | Loop internals on top of epoll (builds on #5), blocking-the-loop failures → rep: detect + fix a blocked loop with `loop.slow_callback_duration` |
| 7 | `threads-locks-queues` | NEW | `fundamentals/concurrency/threads_locks_queues.md` | Races, locks, why queues are the sane default → rep: write a race, prove it, fix it two ways |
| 8 | `tcp-request-walkthrough` | NEW | `fundamentals/networking/tcp_request_walkthrough.md` | DNS → handshake → TLS → bytes → close, packet level → rep: narrate a real request from `tcpdump` output |
| 9 | `connection-management` | REP | `system-design/requests/connection_management.md` | HTTP/1.1 vs 2 vs 3, pooling → rep: demonstrate HOL blocking + pool exhaustion with httpx |

### Week 2 (14–20 Jul) — The Vault

| # | Session id | Type | Output | Covers → rep |
|---|---|---|---|---|
| 10 | `postgres-internals-1-storage` | NEW | `db/postgres_internals_1_storage.md` | Pages, heap, B-tree, when indexes don't help → rep: 3 queries where the planner ignores your index; explain why |
| 11 | `postgres-internals-2-mvcc` | NEW | `db/postgres_internals_2_mvcc.md` | MVCC, isolation levels, locks, deadlocks → rep: produce a deadlock + a serialization failure on demand in two psql sessions |
| 12 | `postgres-internals-3-explain` | NEW | `db/postgres_internals_3_explain.md` | Reading EXPLAIN ANALYZE like a senior → rep: fix a seeded slow query to <50ms and defend the plan |
| 13 | `postgres-internals-4-replication` | NEW | `db/postgres_internals_4_replication.md` | WAL, replication, failover, pgbouncer modes, partitioning → rep: whiteboard the failover story + pgbouncer mode quiz, pass/fail rubric |
| 14 | `lsm-vs-btree` | NEW | `db/lsm_vs_btree.md` | Write/read amplification, where each shows up (RocksDB, Cassandra, Kafka) → rep: given 5 workloads, pick the engine and defend it |
| 15 | `redis-internals` | NEW | `db/redis_internals.md` | Single-threaded model, persistence (RDB/AOF), eviction, wrong-tool cases → rep: break Redis 3 ways (big key, KEYS, eviction storm) and explain each |
| 16 | `idempotency-retries` | NEW | `system-design/data/idempotency_retries.md` | Idempotency keys, retry budgets, exactly-once myths, outbox recap → rep: design the payment-retry contract, checked against 6 failure injections |

### Week 3 (21–27 Jul) — The Swarm, The Arena

| # | Session id | Type | Output | Covers → rep |
|---|---|---|---|---|
| 17 | `consistency-models` | REP | `system-design/data/consistency_models.md` | → rep: classify 8 real features by required consistency model, justify each |
| 18 | `consensus-coordination` | REP | `system-design/data/consensus_and_coordination.md` | Raft + fencing tokens → rep: tell the "distributed lock without fencing" failure story end-to-end, unaided |
| 19 | `distributed-transactions` | REP | `system-design/data/distributed_transactions.md` | → rep: convert a 3-service flow to saga + outbox on the whiteboard, including compensation paths |
| 20 | `caching` | REP | `system-design/caching.md` | → rep: stampede simulation — reproduce, then fix with lock/TTL-jitter/refresh-ahead |
| 21 | `kafka-messaging` | REP | `system-design/data/event_driven_kafka.md` (cites Messaging_Models doc) | → rep: delivery-semantics drill — design consumer for at-least-once with idempotent processing, quiz rubric |
| 22 | `capacity-estimation` | REP | `system-design/resilience/capacity_estimation.md` | → rep: 3 timed back-of-envelope estimates, each <5 min, within 10× |
| 23 | `canonical-1-shortener-ratelimiter` | NEW | `system-design/designs/canonical_1_shortener_ratelimiter.md` | Two worked designs → rep: re-derive one in 25 min against the Challenge Simulator |
| 24 | `canonical-2-feed-notifications` | NEW | `system-design/designs/canonical_2_feed_notifications.md` | Fan-out on write/read, notification dedup → rep: same simulator format |
| 25 | `canonical-3-chat-presence` | NEW | `system-design/designs/canonical_3_chat_presence.md` | WS at scale, ordering, presence → rep: same simulator format |
| 26 | `canonical-4-scheduler-storage` | NEW | `system-design/designs/canonical_4_scheduler_storage.md` | Distributed job scheduler + object storage (Dropbox-style) → rep: same simulator format |
| 27 | `ai-system-design-stories` | NEW | `system-design/designs/ai_system_design_stories.md` | Agent platform, RAG at scale, eval pipeline — your home turf as interview designs → rep: deliver each as a 10-min narrated design, recorded |

### Week 4 (28 Jul – 1 Aug + interview window) — The Gate, The Oracle, The Final Boss

Consolidation reps in your strong areas — cheap sessions, safe to overlap with applications.

| # | Session id | Type | Output | Covers → rep |
|---|---|---|---|---|
| 28 | `authn-authz` | REP | `system-design/security/authn_authz.md` | → rep: whiteboard OAuth2+PKCE flow blind + token-mistake spot-the-bug set |
| 29 | `web-api-attacks` | REP | `system-design/security/web_api_attacks.md` | → rep: fix 5 seeded vulns in a FastAPI snippet file, all must pass |
| 30 | `inference-economics` | REP | `ai/inference/inference_internals.md` (bundles serving_throughput + cost_engineering) | → rep: cost/latency model for a given agent workload; numbers defensible |
| 31 | `evals-observability` | REP | `ai/quality/evals.md` (bundles llm_observability) | → rep: design the eval set + trace schema for one of your real agents |
| 32 | `agent-architectures` | REP | `ai/building/agent_architectures.md` | → rep: narrate your supervisor-orchestration design vs alternatives, 10 min recorded |
| 33 | `rag-at-scale` | REP | `ai/rag-guide.md` | → rep: defend HyDE/multi-query/compression choices against 6 adversarial questions |
| 34 | `llm-agent-security` | REP | `ai/llm_agent_security.md` | → rep: lethal-trifecta audit of one of your real agents, written verdict |
| 35 | `behavioral-themes` | REP → NEW | `interview/behavioral_themes.md` | Ownership, conflict, scaling decisions, mentoring → rep: map each theme to a filled STAR slot from #3 |

### DSA track — interleaved, not calendar sessions

New pattern docs (slot into weeks 2–3 as weekend doubles):

| # | Session id | Type | Output |
|---|---|---|---|
| 36 | `graphs-1-bfs-dfs` | NEW | `code/technique/graphs_bfs_dfs.md` |
| 37 | `graphs-2-toposort-unionfind` | NEW | `code/technique/graphs_toposort_unionfind.md` |
| 38 | `trees-bst` | NEW | `code/technique/trees_bst.md` |
| 39 | `intervals-monotonic-stack` | NEW | `code/technique/intervals_monotonic_stack.md` |

Warmup reps (25 min, one per weekday, cycling — appended to the 7 existing technique docs): `sliding_window`, `two_pointers`, `prefix_sum`, `binary_search`, `backtracking`, `heaps`, `dynamic_programming`. Format: 1 timed problem from `leveling-system.json`, pass = accepted solution within the time box (Easy 15 min / Medium 25 min). Linked-list patterns fold into the `two_pointers` rep.

---

## POST-AUG LADDER — 12 sessions, run during/after the interview pipeline

| # | Session id | Type | Output | Note |
|---|---|---|---|---|
| P1 | `virtual-memory-oom` | NEW | `fundamentals/os/virtual_memory_oom.md` | **First pick if ahead of schedule** — "why did my pod OOMKill" is fast-lane-adjacent |
| P2 | `linux-cgroups-k8s-limits` | NEW | `fundamentals/os/linux_cgroups_k8s_limits.md` | Signals, cgroups, what K8s limits do to your process; pairs with P1 |
| P3 | `cpu-memory-model` | NEW | `fundamentals/machine/cpu_memory_model.md` | Stack/heap, caches, locality |
| P4 | `infrastructure-security` | REP | `system-design/security/infrastructure_security.md` | TLS/mTLS + secrets rep |
| P5 | `load-balancer` | REP | `system-design/load balancer.md` | L4/L7 drill |
| P6 | `database-scaling` | REP | `system-design/database_scaling.md` | Ladder re-derivation rep |
| P7 | `lora-peft` | REP | `ai/training/lora_peft.md` | Fine-tune vs RAG vs prompt decision rep |
| P8 | `rate-limiting` | REP | `system-design/requests/rate_limiting.md` | |
| P9 | `backpressure-load-shedding` | REP | `system-design/requests/backpressure_load_shedding.md` | |
| P10 | `queueing-theory` | REP | `system-design/requests/queueing_theory.md` | |
| P11 | `stateless-design` | REP | `system-design/compute/stateless_design.md` | |
| P12 | `multi-region-dr` | REP | `system-design/resilience/multi_region_dr.md` | |

---

## Generation plan (Phase 2)

Batches of ~5, one commit per batch, fast-lane order: sessions 1–8 → 10–16 → 23–27 + 36–39 → rep-appends (9, 17–22, 28–35, warmups) → post-Aug ladder. Every new doc follows the template (TL;DR / Mental Model mermaid / What Actually Happens / Opinionated Take / Interview Ammo / Practice Rep / Self-Check). Also in passing: fix README `security/` → `system-design/security/` links and register Levels 7–16 in the README map.

**Awaiting your go before Phase 2 generation.**
