# Consistent Hashing

**Overview:** How do N nodes share ownership of millions of keys so that adding/removing a node moves the **fewest** keys? Naive `hash(key) % N` remaps almost *everything* when N changes; consistent hashing remaps only ~1/N. It's the backbone of Cassandra/DynamoDB partitioning, Redis-style cache sharding, and CDN routing.

---

## The Problem with Modulo

```
hash(key) % 4  →  add a 5th node  →  hash(key) % 5
```
~80% of keys now map to a different node. For a cache fleet, that's a near-total miss storm hammering the database; for a data store, a massive rebalancing.

## The Ring

1. Imagine the hash space (0 → 2³²−1) bent into a **circle**.
2. Hash each **node** onto the ring (`hash(node_id)`).
3. Hash each **key** onto the ring; a key belongs to the **first node clockwise** from it.

```
        node A
      /        \
  key3          key1
     |            |     key1,key2 → B (next clockwise)
  node C        node B  key3      → A
      \        /
        key2
```

**Adding node D** between A and B: only the keys in the arc (A → D] move — from B to D. Everything else untouched. **Removing a node:** its keys slide to the next clockwise neighbor. Either way, ~K/N keys move instead of ~K.

## Virtual Nodes (the fix that makes it practical)

With one point per node, arcs are wildly uneven (random placement) and a removed node dumps its entire load onto one neighbor. Solution: each physical node gets **100–1000 virtual nodes** (hash `nodeA#0`, `nodeA#1`, ...) scattered around the ring.
- Load evens out statistically
- A dead node's keys **spread across many** successors, not one
- **Heterogeneous capacity:** big machine → more vnodes (proportional share)

```python
import hashlib, bisect

class ConsistentHashRing:
    def __init__(self, nodes, vnodes=150):
        self.ring = sorted(
            (self._hash(f"{n}#{i}"), n)
            for n in nodes for i in range(vnodes)
        )
        self.keys = [h for h, _ in self.ring]

    def _hash(self, s):
        return int(hashlib.md5(s.encode()).hexdigest(), 16)

    def get_node(self, key):
        idx = bisect.bisect(self.keys, self._hash(key)) % len(self.ring)
        return self.ring[idx][1]
```

## Replication on the Ring
Store each key on its owner **plus the next R−1 distinct physical nodes** clockwise (the "preference list"). This is exactly Dynamo/Cassandra's replication — the ring gives you both placement and replica sets in one structure.

## Alternatives Worth Knowing
- **Rendezvous (HRW) hashing:** for each key, score every node by `hash(key, node)`, pick the max. Same minimal-movement property, no ring/vnode bookkeeping — great for small N (picking 1 of ~20 caches).
- **Jump consistent hash (Google):** tiny, fast, perfectly balanced — but nodes are numbered 0..N−1 and only added/removed *at the end* → shines when a directory assigns shard *numbers*.
- **Range-based partitioning with a coordinator** (HBase, TiKV, Vitess): explicit key-range → shard mapping, enabling range scans and *deliberate* (not hash-random) splitting of hot shards. See `../database_scaling.md`.

## Where You'll Meet It
- **Distributed caches:** client-side sharding across memcached/Redis nodes (Redis Cluster itself uses a fixed 16384-slot variant — same idea, precomputed)
- **Dynamo-style stores:** Cassandra, DynamoDB, Riak — ring + vnodes + preference-list replication
- **LBs/CDNs:** Envoy's ring-hash / Maglev LB policies for cache-affinity routing
- **Hot key caveat:** consistent hashing balances *keys*, not *load* — one celebrity key still overwhelms its owner. Fixes: key salting (`key#1..#k`) or a front cache (see `../caching.md` hot-key section).

## Related
- `../database_scaling.md` (sharding strategies), `../caching.md`, `event_driven_kafka.md` (Kafka chose fixed partitions instead — compare!)
