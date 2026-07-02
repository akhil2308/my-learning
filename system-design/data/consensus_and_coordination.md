# Distributed Consensus & Coordination

**Overview:** Some questions must have exactly ONE answer across all nodes even as machines crash and networks flake: *who is the primary? does this lock belong to anyone? what is config version 42?* Consensus is the machinery for agreeing on such answers. You will (rightly) never implement Raft — but you operate systems built on it daily, and its failure modes leak into yours.

---

## Why It's Hard: Split Brain

Node A can't reach node B. Is B dead, or is the *network* down? **You cannot distinguish these.** If A assumes B is dead and promotes itself while B still serves clients → **two primaries**, both accepting writes → divergence and data loss. Every consensus mechanism is ultimately an answer to split brain.

**The universal answer: majority quorum.** With N nodes, any decision requires ⌈N/2⌉+1 votes. Two disjoint majorities can't exist, so at most one side of any partition can decide. Hence:
- Clusters are **odd-sized** (3 or 5): 4 nodes tolerate 1 failure — same as 3, more cost
- Tolerating f failures needs **2f+1** nodes
- The minority side **loses availability on purpose** — that's CP behavior (see `consistency_models.md`)

---

## Raft in Five Sentences

(The consensus algorithm inside etcd, Consul, CockroachDB, TiKV, Kafka's KRaft — designed to be understandable, unlike Paxos.)

1. Nodes are **follower**, **candidate**, or **leader**; time divides into numbered **terms**.
2. Followers who stop hearing the leader's heartbeat start an election: increment term, vote for self, request votes; majority → **leader**. (Randomized election timeouts prevent perpetual split votes.)
3. All writes go through the leader, which appends to its **log** and replicates entries to followers.
4. An entry acknowledged by a **majority** is **committed** — durable even if the leader dies next instant.
5. Elections only elect candidates with up-to-date logs, so committed entries survive leadership changes.

**Operational leakage you'll actually feel:** leader elections cause brief write-unavailability blips (seconds); network flappiness causes election storms; a slow disk on the leader slows *every* write (log fsync is on the path); quorum loss (2 of 3 nodes down) = full write outage by design.

## The Coordination Services

You don't run Raft; you run a **coordination service** that runs it and exposes primitives:
- **etcd** (Kubernetes' brain), **ZooKeeper** (Kafka pre-KRaft, HBase), **Consul**
- Primitives: consistent small KV store, **compare-and-swap**, **leases/TTLs**, **watches** (notify on change)
- From those, everything else is built: leader election, service discovery, distributed locks, config with versioning
- They store **coordination metadata** (KBs, low write rate) — never application data

---

## Distributed Locks (the pragmatic tiers)

### Tier 1: Single-Redis lock — fine for efficiency, not correctness
```
SET lock:job42 <random_token> NX PX 30000     # acquire with TTL
# release: Lua script — delete ONLY if value == my token
```
- Token check prevents deleting someone else's lock after your TTL expired mid-work.
- **The unfixable flaw:** GC pause / network stall > TTL → lock expires → two holders. Acceptable when the lock merely avoids duplicate *work* (two nodes running the same cron = wasted compute, not corruption).
- **Redlock** (multi-Redis quorum variant) is famously disputed (Kleppmann's critique) — if you're considering it, you actually need Tier 2.

### Tier 2: Fencing tokens — locks for correctness
Lock service issues a **monotonically increasing token** with each grant; the protected resource **rejects any request bearing an older token than it has seen**. Now a zombie holder (paused, expired, resumed) gets rejected downstream. Requires the resource to participate — this is the part naive locking misses.

### Tier 0 (underrated): Postgres advisory locks / `SELECT ... FOR UPDATE`
If all contenders share a Postgres anyway, its locks are transactional, deadlock-detected, and free. Often the right answer for "only one worker processes this row."

## Leader Election (as a pattern)
"Exactly one instance does X (scheduler, singleton consumer)" = a held lease in etcd/Consul/K8s Lease objects, renewed on heartbeat; lose the lease → **stop acting immediately** (the hard part is the zombie leader who doesn't notice — fencing again). K8s controllers do exactly this via the leader-election client.

## Related
- `consistency_models.md` (quorums), `../database_scaling.md` (failover/split-brain), `distributed_transactions.md`, `event_driven_kafka.md` (KRaft)
