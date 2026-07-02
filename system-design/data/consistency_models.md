# Consistency Models, CAP & PACELC

**Overview:** Once data lives in more than one place (replicas, caches, regions), "what value does a read return?" stops having an obvious answer. Consistency models are the contracts that answer it. This doc turns CAP from a slogan into a working tool — the gap named in `my problem.md`.

---

## CAP, Stated Precisely

During a **network partition** (nodes can't talk), a distributed system must choose per-operation:
- **CP:** refuse some requests to stay consistent (e.g., a minority-side node won't serve writes)
- **AP:** keep serving everywhere, accept divergence, reconcile later

Clarifications that fix common misuse:
1. **P is not optional.** Partitions happen; CAP asks what you do *when* they do. "CA system" ≈ single-node system.
2. **It's per-operation, not per-database.** The same system can do CP writes and AP reads.
3. **C in CAP = linearizability** (strongest), not "some consistency."

## PACELC (the more useful framing)

> If **P**artition: choose **A** or **C**. **E**lse (normal operation): choose **L**atency or **C**onsistency.

The **ELC** half matters daily: even with zero partitions, strong consistency costs latency (coordination round trips — brutal cross-region). Examples: DynamoDB = PA/EL (available + fast, eventual by default); Spanner = PC/EC (consistent always, pays latency); Cassandra = tunable per query.

---

## The Consistency Spectrum (strong → weak)

1. **Linearizable (strong):** every read sees the latest completed write; the system behaves like one copy. Cost: consensus/quorum on the path.
2. **Sequential:** all clients see the same order of operations; that order may lag real time.
3. **Causal:** operations that *depend* on each other appear in order everywhere (reply never appears before its post); concurrent-independent ops may differ in order. The sweet spot for many social/collab systems.
4. **Session guarantees (client-centric)** — the practical middle tier:
   - **Read-your-own-writes:** you see your own update (the replica-lag bug users actually notice)
   - **Monotonic reads:** never see data go *backwards* in time between your reads
   - **Monotonic writes / writes-follow-reads**
5. **Eventual:** stop writing → replicas converge, eventually. No promise about *when* or what reads see meanwhile. What async replication and most caches give you by default.

**Design question per data type:** what does the user story break under? Account balance → strong. Like-count → eventual is invisible. Profile edit → read-your-own-writes minimum (route the author's reads to primary briefly — `../database_scaling.md`).

---

## Quorums: Tuning the Dial

With **N** replicas, write to **W**, read from **R**:
```
R + W > N  →  read and write sets overlap → reads see latest write ("strong-ish")
R + W ≤ N  →  faster, eventual
```
- N=3: `W=2, R=2` balanced; `W=3, R=1` fast reads/fragile writes; `W=1, R=1` yolo.
- Cassandra/Dynamo expose this **per query** (`QUORUM`, `ONE`, `LOCAL_QUORUM`).
- Caveat: quorum overlap alone isn't full linearizability under failures/concurrent writes — treat it as "very strong reads," and use consensus (`consensus_and_coordination.md`) where correctness is absolute.

## Conflicts (the AP tax)

Accepting writes on both sides of a partition ⇒ conflicting versions to reconcile:
- **Last-Writer-Wins:** simple; silently drops one write; clocks lie (see clock note).
- **Version vectors:** detect true conflicts vs stale reads; surface siblings to the app (classic Dynamo).
- **CRDTs:** data types that merge mathematically, guaranteed convergence — counters, sets, and the tech behind collaborative editors (your README's OT/CRDT note). Constraint: your operation must fit a CRDT shape (increments/adds — yes; "balance ≥ 0" invariant — no).
- **Application merge:** show both, ask the user, or domain rules ("union the shopping carts" — the famous Dynamo example).

**Clock note:** physical clocks skew, so "last" writer is genuinely ambiguous → logical clocks (Lamport), hybrid logical clocks (HLC), or Spanner's TrueTime (atomic clocks bounding uncertainty) exist precisely for this.

---

## Where Each Model Lives (practical map)
- **Postgres primary:** linearizable on the primary; **async replicas: eventual** — your default stack is already a mixed-consistency system
- Redis cache in front of DB: eventual by construction (staleness window = TTL/invalidation lag)
- Kafka: strong ordering *within a partition* only
- DynamoDB: eventual default, strongly-consistent-read flag; Spanner/CockroachDB: linearizable, pay in latency
- **Interview move:** never say "we'll use eventual consistency" without immediately saying *which anomaly you're accepting and why users won't notice.*

## Related
- `../database_scaling.md` (replication lag), `consensus_and_coordination.md`, `distributed_transactions.md`, `../resilience/multi_region_dr.md`
