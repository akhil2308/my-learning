# GAP-MAP — Coverage Audit vs Target Curriculum

**Audit date:** 2026-07-07 · **Docs inventoried:** 66 markdown files + `leveling-system.json` (6-level DSA ladder) + 26 solved problems.

## Headline findings

1. **Zero docs have a pass/fail practice rep. Zero docs have a mermaid diagram.** The repo is a good encyclopedia with no feedback loops — exactly the failure mode you named. The DSA track is the only exception: `leveling-system.json` + solutions *is* a rep system, just untimed.
2. **Coverage is strongly lopsided toward distributed systems / system design / AI (strong) and away from single-machine fundamentals.** Curriculum areas A (how computers run code), B (OS), D (DB internals), E (local concurrency), and K (interview execution) are near-total gaps. MVCC, isolation levels, EXPLAIN ANALYZE, epoll, the GIL, asyncio internals: **not mentioned once** in 66 docs.
3. Most existing docs are ~500–700 words, opinionated, interview-oriented, with `## Related` cross-links — good quality, wrong session shape. They need reps appended, not rewrites.

**Verdict totals against the target curriculum (46 nodes):** 14 COVERED (all rep-less) · 9 PARTIAL · 23 MISSING.
**Estimated Phase 2 work:** ~27 new docs + ~24 rep-appends ≈ **50 sessions** (exact list in CURRICULUM.md).

---

## Part 1 — Coverage scoring vs target curriculum

Status: ✅ COVERED (rep-append only) · 🟡 PARTIAL (extend or new focused doc) · ❌ MISSING (new doc)

### A. How computers actually run my code — ❌ entire area missing

| Node | Status | Evidence | Action |
|---|---|---|---|
| CPU/memory model: stack vs heap, caches, locality | ❌ MISSING | nothing | new doc |
| CPython internals: bytecode, GIL, refcount + GC | ❌ MISSING | "GIL" appears nowhere (grep hits were "fragile"/"agile") | new doc |
| Python performance model: multiprocessing / asyncio / C extensions | ❌ MISSING | asyncio only mentioned in passing in 2 docs | new doc |

### B. Operating systems — ❌ entire area missing

| Node | Status | Evidence | Action |
|---|---|---|---|
| Processes vs threads, context switching, scheduling | ❌ MISSING | nothing | new doc |
| Virtual memory, paging, OOM in containers | ❌ MISSING | nothing | new doc |
| File descriptors, sockets, epoll → what an event loop is | ❌ MISSING | "epoll" appears nowhere | new doc |
| Linux for backend: signals, cgroups, what K8s limits do | ❌ MISSING | `horizontal_scaling_autoscaling.md` covers HPA, not the cgroup/OOM-kill mechanics under it | new doc |

### C. Networking — mostly covered, one gap

| Node | Status | Evidence | Action |
|---|---|---|---|
| TCP/IP walkthrough: request leaves my service | 🟡 PARTIAL | `connection_management.md` (handshake cost, TCP gotchas), `What_is_a_Protocol.md` (intro) — no packet-level end-to-end walkthrough | new doc |
| HTTP/1.1 vs 2 vs 3, keep-alive, HOL blocking | ✅ COVERED | `system-design/requests/connection_management.md` — working depth | rep-append |
| TLS handshake, certificates, mTLS | ✅ COVERED | `system-design/security/infrastructure_security.md` §2 — working depth | rep-append |
| DNS, L4 vs L7 LB, proxies, connection pooling | 🟡 PARTIAL | `load balancer.md` (deep), `api_gateway.md`, pooling in `connection_management.md`; **DNS resolution path missing** | fold DNS into TCP walkthrough doc + rep-append `load balancer.md` |

### D. Database internals (Postgres-centered) — ❌ biggest technical gap

| Node | Status | Evidence | Action |
|---|---|---|---|
| Storage: pages, heap, B-tree; when indexes don't help | ❌ MISSING | B-tree only name-dropped in `id_generation.md` / `search_and_analytics.md` | new doc |
| LSM trees vs B-trees | 🟡 PARTIAL | one line in `search_and_analytics.md` context | new doc (pairs with storage) |
| MVCC, isolation levels, locking, deadlocks | ❌ MISSING | "MVCC" and "isolation level" appear **nowhere** | new doc(s) |
| Reading EXPLAIN ANALYZE like a senior | ❌ MISSING | nothing | new doc |
| Replication, failover, pgbouncer, partitioning | 🟡 PARTIAL | `database_scaling.md` covers the ladder at design level; pgbouncer name-dropped; no failover/pooler mechanics | new doc + rep-append `database_scaling.md` |
| Redis internals: single-threaded, persistence, eviction, wrong-tool cases | 🟡 PARTIAL | `caching.md` has eviction policies + Redis-vs-Memcached take; README has external links (not docs) | new doc |

### E. Concurrency & parallelism

| Node | Status | Evidence | Action |
|---|---|---|---|
| asyncio event loop internals, blocking-the-loop failures | ❌ MISSING | nothing (your daily stack!) | new doc |
| Threads, locks, races, queues as sane default | ❌ MISSING | nothing at single-process level | new doc |
| Distributed locks, leases, fencing tokens | ✅ COVERED | `system-design/data/consensus_and_coordination.md` — working depth | rep-append |

### F. Distributed systems — strongest area

| Node | Status | Evidence | Action |
|---|---|---|---|
| CAP/PACELC, consistency models | ✅ COVERED | `consistency_models.md` — working-deep, genuinely good | rep-append |
| Idempotency, retries, exactly-once myths, outbox | 🟡 PARTIAL | outbox in `distributed_transactions.md`, retry storms in `backpressure_load_shedding.md`, idempotency scattered across 5 docs — no single treatment | new doc consolidating + rep-append `distributed_transactions.md` |
| Kafka vs RabbitMQ vs Redis streams | ✅ COVERED | `Messaging_Models_and_Comparison_RabbitMQ_Kafka_ActiveMQ.md` + `event_driven_kafka.md` (Redis streams thin — cover in Redis internals doc) | rep-append |
| Consensus at working level (Raft) | ✅ COVERED | `consensus_and_coordination.md` | rep-append (same rep as fencing row) |
| Caching strategies, invalidation, stampede | ✅ COVERED | `caching.md` — stampede/penetration/hot-key all there | rep-append |

### G. System design (interview canon)

| Node | Status | Evidence | Action |
|---|---|---|---|
| Back-of-envelope estimation | ✅ COVERED | `capacity_estimation.md` + `queueing_theory.md` — strong | rep-append |
| 8–10 canonical designs (URL shortener, rate limiter, feed, chat, notifications…) | 🟡 PARTIAL | all *components* exist; `System Design Challenge Simulator.md` is a practice harness; **zero worked end-to-end designs** | new docs (~2 designs/session) |
| AI/LLM system design as interview stories | 🟡 PARTIAL | `agent_architectures.md`, `rag-guide.md` are knowledge docs, not interview-shaped designs | new doc(s) |

### H. DSA (pattern gaps only)

Covered patterns (all rep-append: add timed pass/fail sets): sliding window, two pointers, prefix sum, binary search, backtracking, heaps, DP, permutations/combinations.

| Missing pattern | Status | Action |
|---|---|---|
| Graphs: BFS/DFS, topological sort, union-find | ❌ MISSING | new doc(s) |
| Trees/BST: traversals, recursion patterns, LCA | ❌ MISSING | new doc |
| Intervals + greedy | ❌ MISSING | new doc |
| Stacks / monotonic stack | ❌ MISSING | new doc |
| Linked lists (in-place reversal, fast/slow beyond cycle) | 🟡 PARTIAL | fast/slow mentioned in `two_pointers.md` | fold into rep-append or thin doc |

### I. Security — fully covered, all rep-less

| Node | Status | Evidence | Action |
|---|---|---|---|
| AuthN/AuthZ: sessions vs JWT, OAuth2/OIDC, token mistakes | ✅ COVERED | `system-design/security/authn_authz.md` — deep | rep-append |
| OWASP top 10, backend exploits + fixes | ✅ COVERED | `system-design/security/web_api_attacks.md` — deep | rep-append |
| Crypto literacy, TLS trust chains, secrets | ✅ COVERED | `system-design/security/infrastructure_security.md` — deep | rep-append |

*(Note: README links these under `security/` but they live in `system-design/security/` — cosmetic, fix in passing.)*

### J. AI/LLM engineering — strongest area, as expected. Gap-check result: no new docs needed

| Node | Status | Evidence | Action |
|---|---|---|---|
| Inference/serving economics: batching, KV cache, quantization | ✅ COVERED | `inference_internals.md`, `serving_throughput.md`, `cost_engineering.md`, `AWQ & GPTQ.md` | rep-append (bundle) |
| Evals + observability for agents | ✅ COVERED | `quality/evals.md`, `quality/llm_observability.md` | rep-append |
| Fine-tune vs RAG vs prompting decision framework | ✅ COVERED | `lora_peft.md` §"When (and When Not)", `rag-guide.md`, `prompt_engineering.md` | rep-append |

### K. Interview execution — ❌ entire area missing

| Node | Status | Evidence | Action |
|---|---|---|---|
| STAR story bank (IRIS, RAPID, supervisor orchestration, fastapi template) | ❌ MISSING | nothing | new doc (template + 8 slots) |
| Senior behavioral themes | ❌ MISSING | nothing | new doc |

---

## Part 2 — Full doc inventory

Depth: **intro** (explainer, no opinions) · **working** (opinionated, interview-usable) · **deep** (comprehensive). Rep = has a pass/fail practice rep. **No doc has one; column kept for the record.**

### `ai/` (26 docs — all working depth unless noted, all rep-less)

| Doc | Topic | Depth |
|---|---|---|
| `foundations/tokenization.md` | BPE, token quirks | working |
| `foundations/transformers_attention.md` | Attention data-flow view | working |
| `foundations/context_windows.md` | Long context, degradation | working |
| `foundations/sampling_decoding.md` | Temperature, logprobs | working |
| `building/prompt_engineering.md` | Prompts-as-code practices | working |
| `building/embeddings.md` | Similarity math, ops realities | working |
| `building/structured_outputs.md` | Constrained decoding tiers | working |
| `building/tool_use.md` | Function-calling loop, executor | working |
| `building/agent_architectures.md` | Agency spectrum, supervisor/worker | working |
| `building/agent_memory.md` | Memory layers, taxonomy | working |
| `inference/inference_internals.md` | Prefill/decode, KV cache | working |
| `inference/serving_throughput.md` | vLLM, continuous batching, spec-dec | working |
| `inference/cost_engineering.md` | Cost levers, prompt caching | working |
| `quality/evals.md` | Eval sets, LLM-judge tiers | working |
| `quality/hallucination_grounding.md` | Confabulation mechanics, mitigation | working |
| `quality/llm_observability.md` | Task-level traces, metrics | working |
| `training/training_pipeline.md` | Pretrain→SFT→RLHF/DPO/RLVR | working |
| `training/lora_peft.md` | LoRA/QLoRA, when to fine-tune | working |
| `training/model_architectures.md` | MoE, SSMs, model cards | working |
| `emerging/mcp.md` | MCP model + security | working |
| `emerging/context_engineering.md` | Context budget techniques | working |
| `emerging/reasoning_test_time_compute.md` | Reasoning models, TTC | working |
| `emerging/emerging_landscape.md` | Mid-2026 snapshot | working |
| `rag-guide.md` | End-to-end advanced RAG | **deep** |
| `llm_agent_security.md` | Prompt injection, lethal trifecta | **deep** |
| `llm-fine-tuning.md` | Fine-tuning pipeline walkthrough | intro (superseded by `training/`) |
| `AWQ & GPTQ.md` | Quantization methods | intro |

### `code/` (9 docs, all rep-less in the pass/fail sense; problems mapped via `leveling-system.json`)

| Doc | Topic | Depth |
|---|---|---|
| `technique/sliding_window.md` | Fixed + variable windows | working |
| `technique/two_pointers.md` | Converging, fast/slow | working |
| `technique/prefix_sum.md` | Range queries + hashmap | working |
| `technique/binary_search.md` | One template, search-on-answer | working |
| `technique/backtracking.md` | Choose/explore/un-choose | working |
| `technique/heaps.md` | Top-K, k-way merge, two heaps | working |
| `technique/dynamic_programming.md` | Memo vs tabulation, 5 patterns | working |
| `Permutation.md` | Permutation walkthrough | intro |
| `combinations.md` | Subsets/combinations | intro |

### `system-design/` (30 docs)

| Doc | Topic | Depth |
|---|---|---|
| `requests/queueing_theory.md` | Little's Law, hockey stick | working |
| `requests/rate_limiting.md` | Algorithms + distributed | working |
| `requests/api_gateway.md` | Gateway vs proxy vs LB, BFF | working |
| `requests/connection_management.md` | HTTP/1.1→3, pooling, TCP gotchas | working |
| `requests/async_request_patterns.md` | Polling/webhooks/SSE/WS | working |
| `requests/backpressure_load_shedding.md` | Bounded queues, retry storms | working |
| `compute/stateless_design.md` | State externalization | working |
| `compute/horizontal_scaling_autoscaling.md` | HPA, cold starts | working |
| `compute/serverless_vs_containers.md` | Trade-off matrix | working |
| `data/consistency_models.md` | CAP/PACELC, quorums, CRDTs | working |
| `data/consistent_hashing.md` | Rings, virtual nodes | working |
| `data/consensus_and_coordination.md` | Raft, locks, fencing tokens | working |
| `data/distributed_transactions.md` | 2PC vs sagas, outbox | working |
| `data/event_driven_kafka.md` | Partitions, delivery semantics, CQRS | working |
| `data/cdn_and_edge.md` | Cache-control, edge | working |
| `data/id_generation.md` | UUIDv7, Snowflake | working |
| `data/search_and_analytics.md` | Inverted indexes, OLTP/OLAP | working |
| `security/authn_authz.md` | Sessions/JWT/OAuth2/OIDC, RBAC→ReBAC | **deep** |
| `security/web_api_attacks.md` | OWASP attack→defense | **deep** |
| `security/infrastructure_security.md` | Crypto map, TLS, secrets, K8s | **deep** |
| `resilience/capacity_estimation.md` | Latency ladder, BoE method | working |
| `resilience/multi_region_dr.md` | RTO/RPO, active-active | working |
| `caching.md` | Write strategies, stampede | working |
| `database_scaling.md` | Replicas→partition→shard ladder | working |
| `load balancer.md` | LB deep dive | **deep** |
| `Messaging_Models_and_Comparison_RabbitMQ_Kafka_ActiveMQ.md` | Broker comparison | working |
| `productionizing.md` | 13-dimension prod checklist | **deep** |
| `What_is_a_Protocol.md` | Protocol basics | intro |
| `System Design Challenge Simulator.md` | LLM interview-sim prompt | (practice tool) |
| `my problem.md` | Original gap analysis | (meta) |

### Other
| Item | Topic | Note |
|---|---|---|
| `README.md` | Curriculum map + AWS deployment summary | index |
| `leveling-system.json` | 6-level gamified LeetCode ladder | **this is the RPG convention to extend** |
| `leveling-system-solutions/` (26 .py) | Solved problems | reps for DSA levels 1–2 |
| `python/ruff-guide` | Ruff notes | out of curriculum scope |

---

## Part 3 — Rep-append list (good docs, no rep — append `## Practice Rep`, don't rewrite)

Interview-critical first:

1. `system-design/data/consistency_models.md`
2. `system-design/data/consensus_and_coordination.md` (covers fencing/locks node too)
3. `system-design/data/distributed_transactions.md`
4. `system-design/caching.md`
5. `system-design/data/event_driven_kafka.md` (+ cite `Messaging_Models…` — one rep covers both)
6. `system-design/resilience/capacity_estimation.md`
7. `system-design/requests/connection_management.md` (HTTP versions node)
8. `system-design/security/authn_authz.md`
9. `system-design/security/web_api_attacks.md`
10. `system-design/security/infrastructure_security.md` (TLS/mTLS + crypto + secrets)
11. `system-design/load balancer.md`
12. `system-design/database_scaling.md`
13. `ai/inference/inference_internals.md` (one rep bundling serving_throughput + cost_engineering)
14. `ai/quality/evals.md` (one rep bundling llm_observability)
15. `ai/training/lora_peft.md` (fine-tune vs RAG vs prompt decision rep)
16. `ai/building/agent_architectures.md`
17. `ai/rag-guide.md`
18. `ai/llm_agent_security.md`
19–25. `code/technique/*.md` ×7 — timed problem-set reps (pass = solve N in T min), wired to `leveling-system.json`

Lower priority (post-Aug): `requests/rate_limiting.md`, `requests/backpressure_load_shedding.md`, `requests/queueing_theory.md`, `compute/stateless_design.md`, `resilience/multi_region_dr.md`.

---

## Part 4 — What Phase 1 will contain (preview, not the manifest)

- **New docs (~27):** A ×3 · B ×4 · C ×1 (TCP+DNS walkthrough) · D ×6 (postgres-internals-1-storage, -2-mvcc, -3-explain, -4-replication; lsm-vs-btree folded into storage or separate; redis-internals) · E ×2 · F ×1 (idempotency-retries-outbox) · G ×5 (4× canonical-designs @ 2/session + 1 AI-systems interview stories) · H ×4 (graphs ×2, trees, intervals+monotonic-stack) · K ×2
- **Rep-appends (~24):** list above
- **Fast lane:** D (all), E-asyncio, A-cpython/GIL, C-tcp-walkthrough, G (all), H (all), K (all), I rep-appends — these are the highest-frequency senior backend/AI interview topics.

**Awaiting your review before generating `CURRICULUM.md`.**
