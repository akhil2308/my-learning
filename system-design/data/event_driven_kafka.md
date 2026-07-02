# Event-Driven Architecture & Kafka Internals

**Overview:** Your `Messaging_Models_...md` compares brokers; this doc goes a level deeper — how Kafka actually works (partitions, consumer groups, delivery semantics) and the architectural patterns built on top (events-as-facts, event sourcing, CQRS). Kafka's mental model: **not a queue — a distributed, replicated, append-only log** that consumers read at their own pace.

---

## Kafka Mechanics

### Topics, Partitions, Offsets
- A **topic** splits into **partitions**; each partition is an ordered, immutable log; each record has an **offset**.
- **Ordering is guaranteed ONLY within a partition.** All of a key's ordering needs must share a partition → `partition = hash(key) % num_partitions` — so choose the key as "the unit whose events must stay ordered" (`user_id`, `order_id`).
- Partition count = the **parallelism ceiling** (max useful consumers per group = partitions). Increasing partitions later remaps keys (`hash % N` — compare `consistent_hashing.md`) → breaks key-ordering at the transition. Overprovision modestly upfront (e.g., 3–6× expected consumers).
- Retention by **time/size, not consumption** — consumers reading the same topic don't steal from each other; replay = rewind offsets. This is the property queues don't have.
- Replication: each partition has a leader + followers; producers/consumers talk to the leader; `acks=all` + `min.insync.replicas=2` = durable writes.

### Consumer Groups
- Within a group, each partition is owned by exactly one consumer → **competing-consumers** scaling with per-key ordering preserved.
- Different groups each get **all** messages independently (pub/sub) — offsets are per-group.
- **Rebalancing** (consumer joins/dies) briefly pauses the group; frequent rebalances (crashloops, slow processing exceeding `max.poll.interval.ms`) are a classic production pain.
- **Consumer lag** (latest offset − committed offset) is THE health metric: growing lag = falling behind = your backpressure signal (`../requests/backpressure_load_shedding.md`).

### Delivery Semantics (where the bugs live)
The crux is **when the consumer commits its offset** relative to doing the work:
- Commit **before** processing → crash loses the message: *at-most-once*
- Commit **after** processing → crash reprocesses: ***at-least-once* (the default reality)**
- "Exactly-once": producer idempotence + transactions make it real for **Kafka→Kafka** pipelines (Streams). The moment a side effect leaves Kafka (DB write, email), you're back to **at-least-once + idempotent consumer** — dedupe on event ID / upsert / inbox pattern. Design every consumer idempotent; treat EOS claims with suspicion.
- Poison messages: retry N times → **dead-letter topic** + alert, or one bad record halts the partition.

---

## Architectural Patterns

### Events as facts (EDA baseline)
Services publish immutable facts (`OrderPlaced`), not commands; consumers react independently. Decouples teams and runtimes; new consumers attach without touching producers. Costs: eventual consistency between services (`consistency_models.md`), flow visibility (tracing across async hops), and **schema governance** — events are your public API → Schema Registry (Avro/Protobuf) + backward-compatible evolution (add optional fields; never repurpose).
Publish via **outbox** (`distributed_transactions.md`) or events silently go missing.

**Event notification vs event-carried state:** thin event (`order_id` only — consumers call back for data, coupling returns) vs fat event (full snapshot — self-sufficient consumers, bigger payloads, versioning weight). Default fat-ish: include what consumers need to avoid the callback.

### Event Sourcing
State is not stored — it's **derived**: persist the full sequence of events (`AccountOpened`, `Deposited(500)`...) and fold them to get current state; snapshot periodically for speed.
- Free audit log, time travel, retroactive new projections
- Heavy costs: event schema evolution forever, unfamiliar querying, upfront design of event granularity. **Niche tool** — apply to the one aggregate that needs auditability (ledger, order lifecycle), not the whole system.

### CQRS
Separate the **write model** (normalized, invariant-enforcing) from **read models** (denormalized projections built by consuming events — into Postgres views, Elasticsearch, Redis). Each side scales and evolves independently; reads are eventually consistent with writes (UI must tolerate the gap). Pairs naturally with EDA/event sourcing; overkill when a read replica would do.

### Stream Processing (name-check)
Stateful transforms over streams — joins, windows, aggregations: Kafka Streams, Flink. The layer above consumers when logic exceeds "handle one message."

---

## Kafka vs Queues (when NOT to Kafka)
Simple task distribution (send email, resize image) with no replay/ordering/fan-out needs → **SQS/RabbitMQ is less machinery**: per-message ack, dead-lettering, delayed delivery built in, no partition math. Kafka earns its complexity at: multiple consumers of the same stream, replay, key ordering, high throughput, stream processing.

## Related
- `../Messaging_Models_and_Comparison_RabbitMQ_Kafka_ActiveMQ.md`, `distributed_transactions.md` (outbox), `consistency_models.md`, `id_generation.md` (event IDs)
