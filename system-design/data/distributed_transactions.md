# Distributed Transactions: 2PC, Sagas & the Outbox Pattern

**Overview:** Inside one Postgres, ACID makes multi-step changes atomic for free. Split the data across services/shards/brokers and that guarantee evaporates: "reserve inventory AND charge payment AND create order" can now half-happen. This doc covers the three responses — and the design move that avoids the problem entirely.

**Option zero (use it more):** draw service boundaries so operations that must be atomic live in ONE database. Many "we need distributed transactions" problems are boundary mistakes.

---

## Two-Phase Commit (2PC)

A coordinator makes N databases commit atomically:
```
Phase 1 (prepare): coordinator → all: "can you commit?"  each locks + votes
Phase 2 (commit):  all yes → "commit!"   any no → "abort!"
```
**Why the industry moved away from it for microservices:**
- **Blocking:** between prepare and commit, participants hold locks; if the coordinator dies there, they hold them until it returns (in-doubt transactions)
- Availability = product of all participants' availability; latency = slowest participant × 2 round trips
- Requires XA support everywhere (brokers, HTTP services: no)

Legitimate homes today: *inside* distributed databases (Spanner/CockroachDB run 2PC over consensus-replicated shards, fixing the coordinator-failure problem), and legacy XA enterprise stacks. Between microservices: use sagas.

---

## Sagas: sequence of local transactions + compensations

Break the business transaction into per-service **local** ACID transactions; if step k fails, run **compensating transactions** to undo steps 1..k−1.

```
create order → reserve inventory → charge payment ✗
                     ↓ compensate
cancel order ← release inventory ←
```

### Choreography (event-driven)
Each service reacts to the previous service's event (`OrderCreated` → inventory acts → `InventoryReserved` → payment acts...).
- No central coordinator; loosely coupled
- The flow exists *nowhere explicitly* — beyond ~3–4 steps it becomes untraceable, and cyclic event dependencies creep in

### Orchestration (a saga coordinator)
An orchestrator (dedicated service or workflow engine — **Temporal**, AWS Step Functions) commands each step and tracks state explicitly.
- Flow visible in one place; timeouts/retries/compensation logic centralized; state queryable ("where is order 123 stuck?")
- The orchestrator must be reliable (workflow engines persist state — that's their whole job)
- **Default to orchestration for anything ≥3 steps or involving money.**

### Saga truths people learn the hard way
1. **No isolation** (the I in ACID is gone): intermediate states are *visible* — another request can see the order while payment is pending. Design states explicitly (`PENDING_PAYMENT`) rather than pretending atomicity.
2. **Compensations are business logic, not rollbacks:** you can't un-send an email or un-capture instantly — compensation may be "refund," "apologize," "flag for ops." Some steps are non-compensatable → order them last ("pivot" step).
3. **Every step and compensation must be idempotent + retried** — sagas run on at-least-once infrastructure.

---

## The Dual-Write Problem & the Outbox Pattern

The bug underlying most event-driven data loss:
```python
await db.commit(order)          # succeeds
await kafka.send(order_event)   # crash here → DB updated, event lost forever
```
No ordering of the two lines fixes it — two systems, no shared transaction.

**Transactional Outbox:** write the event *into the same DB transaction* as the state change; a separate relay publishes it.
```sql
BEGIN;
  INSERT INTO orders (...);
  INSERT INTO outbox (event_type, payload, created_at) VALUES ('OrderCreated', {...});
COMMIT;   -- atomic: both or neither
```
Relay options: a poller (`SELECT ... FOR UPDATE SKIP LOCKED`, publish, mark done) — simple and fine; or **CDC** (Debezium tails the WAL and publishes) — lower latency, no polling load, more moving parts.
Delivery becomes **at-least-once** → consumers dedupe on event ID (idempotency, again). Outbox is the mandatory companion to any saga/event architecture — it's how each local step reliably announces itself.

(*Inbox pattern* is the mirror image on the consumer side: record processed event IDs transactionally with their effects.)

---

## Decision Guide
| Situation | Answer |
|---|---|
| Steps can live in one DB | **Move them there** (option zero) |
| Multi-service workflow, ≤ a few steps, low stakes | Choreographed saga + outbox |
| Multi-service workflow, money/complex/long-running | **Orchestrated saga** (Temporal/Step Functions) + outbox |
| Multi-shard write inside one distributed DB | The DB's own 2PC (Spanner/Cockroach) — transparent to you |
| "DB update + publish event" anywhere | **Outbox**, always |

## Related
- `event_driven_kafka.md`, `consensus_and_coordination.md`, `consistency_models.md` (visible intermediate states = a consistency model choice), `../../system-design/productionizing.md` §8

## Practice Rep (60 min, pass/fail) — Session 19 [INTERVIEW-CRITICAL]

**Convert a 3-service flow to saga + outbox, on a whiteboard, with compensation.** The flow: place order → charge payment → reserve inventory → confirm.

1. (25 min) Draw the orchestrated saga: state machine states, per-step outbox events (`../data/idempotency_retries.md` mechanics), and — the graded part — **compensation paths for a failure at every step** (payment fails; inventory fails *after* charge; confirmation service down). Mark which compensations are retryable vs terminal.
2. (15 min) Annotate the anomaly window: name the intermediate state a user can observe (charged-but-not-reserved), how long it lasts, and the product mitigation (pending status, not silent).
3. (15 min) Write the "why not 2PC" paragraph: blocking on coordinator failure, locks held across services, availability coupling — and the one case you'd still accept it (single distributed DB doing it transparently).

**Pass:** every failure point has a drawn compensation or explicit "park for human" path; the charged-but-not-reserved window is named with mitigation; 2PC paragraph gives the blocking argument precisely.
**Fail:** a saga where compensation is hand-waved ("we refund somehow"), or no observable-intermediate-state acknowledged — that's the whole trade being ignored.
