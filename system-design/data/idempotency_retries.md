# Idempotency & Retries — exactly-once delivery is a myth; exactly-once *effect* is a design you build

**Level 12 · The Swarm · Session 16 · [INTERVIEW-CRITICAL]**
*Consolidates threads from `distributed_transactions.md` (outbox), `../requests/backpressure_load_shedding.md` (retry storms), `event_driven_kafka.md` (delivery semantics) into the one pattern interviews actually probe.*

## TL;DR

- The root problem is one ambiguity: **a timeout tells you nothing.** The request may have failed before processing, during, or after-but-the-ack-was-lost. Any retry therefore risks a duplicate — retries and duplicates are the same decision.
- Delivery guarantees end at **at-least-once** (with retries) or **at-most-once** (without). "Exactly-once delivery" across a network is impossible; **exactly-once effect** = at-least-once delivery + idempotent processing. That sentence is the interview answer.
- The workhorse: **idempotency keys** — client generates a unique key per logical operation; server atomically records key→result and replays the stored result on duplicates. Atomicity of *check-and-record* is the part everyone gets wrong.
- Retries need a budget or they're a weapon: **exponential backoff + jitter + retry cap + only on safe errors** — and never stack retries at every layer (client × gateway × service × queue = amplification).
- The **transactional outbox** is the same idea for events: write the business row and the event in *one* DB transaction; a relay publishes with at-least-once semantics; consumers dedupe. DB transaction + idempotent consumer = end-to-end exactly-once effect.

## Mental Model

```mermaid
sequenceDiagram
    participant C as client (retries)
    participant S as payment service
    participant DB as Postgres
    C->>S: POST /charge {key: "ord-7-charge", ₹500}
    S->>DB: BEGIN: INSERT idempotency_keys(key,'in_progress')
    Note over S,DB: unique constraint = the atomic gate
    S->>S: charge via PSP…
    S->>DB: UPDATE key → 'done' + response; COMMIT
    S--xC: 💥 response lost (timeout)
    C->>S: retry POST /charge {key: "ord-7-charge"}
    S->>DB: INSERT … conflict!
    DB-->>S: key exists, status=done, stored response
    S-->>C: 200 (replayed result — charged once)
```

## What Actually Happens

**A payment retry, every branch of it:**

1. Client calls `POST /charge`. Network hiccup → timeout after 3 s. **Three possible worlds:** request never arrived; service is mid-charge; charge completed, ack lost. The client cannot distinguish them — this is the fundamental limit (two-generals, if an interviewer wants the name).
2. **Naive retry** double-charges in world 3. **No retry** drops revenue in world 1. So: retry *with* an idempotency key. The client generates it **per logical operation, not per HTTP attempt** — `order-7-charge`, minted when the user clicked Pay, stable across retries, stored client-side before the first attempt.
3. Server-side, the key table does the work, and the atomicity matters: `INSERT INTO idempotency_keys (key, status) VALUES (:k, 'in_progress')` **relies on the unique constraint** as the gate. Check-then-insert as two steps is a [TOCTOU race](../../fundamentals/concurrency/threads_locks_queues.md) — two concurrent retries both pass the check. The constraint violation *is* the feature.
4. On conflict, read the row: `done` → **replay the stored response** (same status code, same body — the client can't tell, which is the point). `in_progress` → the first attempt is still running: return `409/425 retry-later` (or block briefly). Never run the business logic twice. Keys get a TTL (e.g., 24–72 h) and the response payload is stored alongside.
5. **The retry policy on the client** decides whether this machinery gets a workout or a beating: retry only idempotent-safe failures (connect errors, 503, 429-with-Retry-After; **never** 4xx logic errors), exponential backoff (`base × 2^n`) **with full jitter** (herd-breaking — thundering retry waves are self-DDoS, per `../requests/backpressure_load_shedding.md`), a total budget (e.g., 3 attempts or 10 s, whichever first), and **one owner of retries per call chain** — if the gateway retries and the client retries and the mesh retries, a single 30 s outage becomes a 27× traffic spike at recovery.
6. **The async twin — outbox:** service A must "update order AND emit OrderPlaced." Two systems, no shared transaction ([2PC declined, per `distributed_transactions.md`](distributed_transactions.md)). Write both rows in one Postgres transaction (order update + `outbox` insert); a relay (poller or logical-replication CDC — [session 13's machinery](../../db/postgres_internals_4_replication.md)) publishes to Kafka and marks sent. Crash anywhere = unsent row still there = republish = **at-least-once**. 
7. **The consumer closes the loop:** processes `OrderPlaced` idempotently — either a dedupe table keyed by event ID (same unique-constraint trick, ideally in the same transaction as the side effect), or a **naturally idempotent** operation (`SET status='shipped'`, `INSERT ... ON CONFLICT DO NOTHING`). Kafka's "exactly-once" (transactions/EOS) covers Kafka-to-Kafka topologies; the moment a side effect leaves Kafka (DB write, email, HTTP call), you're back to consumer idempotency. Say that distinction precisely and interviewers relax.
8. **What can still go wrong:** non-deterministic handlers replaying different responses (store the response, don't recompute); idempotency key scoped too wide (per-user instead of per-operation → drops legitimate second orders) or too narrow (per-attempt → useless); side effects *outside* the transaction boundary (send email, then crash before recording the key → email twice — move it behind the outbox too); TTL shorter than the client's maximum retry horizon.

## The Opinionated Take

- **Make idempotency the default for every mutating endpoint, not a payments special.** An `Idempotency-Key` header + one table + a decorator/middleware in your fastapi template is a day of work and permanently changes what retries cost you. (Stripe's API is the reference design; copy it shamelessly.)
- **Prefer naturally idempotent designs over dedupe bookkeeping** where the domain allows: absolute state writes (`SET x = 5`, not `INCR`), `ON CONFLICT DO NOTHING`, state machines that ignore stale transitions. The dedupe table is for when money or side effects make "just overwrite" wrong.
- **Retries are a systemwide contract, not a client setting.** Decide the single retry owner per hop, propagate deadlines/budgets (`X-Request-Deadline`), and return `Retry-After` on 429/503 so clients back off *your* way. When you'd be wrong: truly fire-and-forget telemetry — drop it, don't retry it.
- **Outbox over "publish then commit" (or commit then publish) every time** consistency matters — both orderings have a crash window that lies. The polling relay is boring and fine below ~1k events/s; CDC when it isn't.

## Interview Ammo

1. **"Why is exactly-once delivery impossible, and what do we do instead?"** — Ack loss makes received-vs-not undecidable (two generals); so: at-least-once delivery + idempotent processing = exactly-once *effect*. Deliver the distinction crisply; it's a screening question for senior.
2. **"Design idempotency for a payment API."** — Client-minted key per logical op → unique-constraint-gated insert → in_progress/done state machine → replay stored response → TTL. Name the two classic bugs: check-then-insert race, and side effects outside the transaction.
3. **"What's wrong with retries on every layer?"** — Multiplicative amplification (3×3×3), synchronized waves without jitter, retrying non-idempotent ops, no budget → recovery-time self-DDoS. Prescribe: one owner, backoff+full jitter, budget, safe-errors-only, Retry-After.
4. **"How do you atomically update the DB and publish an event?"** — You don't; you make it *look* atomic: outbox in the same transaction + relay + consumer dedupe. Contrast with 2PC (blocking, coordinator SPOF) in one sentence.
5. **"Kafka says exactly-once — so is this solved?"** — Within Kafka's read-process-write loop (transactions + idempotent producer), yes; for any external side effect, no — consumer idempotency remains your job. Knowing where the guarantee's boundary sits is the senior tell.

## Practice Rep (60 min, pass/fail)

Build `idempotency_lab.py`: FastAPI + Postgres. `POST /charge` with an `Idempotency-Key` header; "charging" = insert into `charges` + 200 ms sleep. Then a chaos client that fires **6 failure injections**:

1. Duplicate sequential request (same key, after success) → must replay identical response, `charges` count 1.
2. **Concurrent** duplicates (two tasks, same key, simultaneously) → one processes, one gets in-progress/replayed; count 1. (This is the unique-constraint test — a check-then-insert implementation fails here.)
3. Timeout mid-processing (client gives up at 100 ms, server finishes) then retry → count 1, response replayed.
4. Server crash simulation: raise an exception after charging but before marking done; retry → your design must either roll back the charge with the key row (same transaction) or recover — count must end 1. Document which you chose.
5. Same user, *different* logical operation (new key) → count 2 (scope check).
6. Retry with the key after TTL expiry (set TTL to 2 s for the test) → document the behavior you chose and why it's defensible.

**Pass:** injections 1–5 produce exactly the counts above with evidence logged; injection 4's transaction-boundary decision written in 2 sentences; injection 6's trade-off articulated (replay-window vs storage vs double-charge risk).
**Fail:** the concurrent case (2) double-charges — that's the whole exercise — or any "it works" claim without the row counts printed.

## Self-Check (5 questions, answers at bottom)

1. A timeout occurred. Enumerate the three states the operation could be in, and what property makes retrying safe anyway.
2. Why must the idempotency check be a unique constraint rather than a SELECT-then-INSERT?
3. What makes full jitter more important than the backoff itself in a mass-recovery scenario?
4. Walk the crash windows of "commit DB then publish" and "publish then commit DB," and say what the outbox changes.
5. Your consumer's side effect is sending an email. Where does exactly-once effect actually come from — and what's the honest residual risk?

---

<details><summary>Answers</summary>

1. Never-arrived / in-flight (processing) / completed-with-lost-ack. Retrying is safe iff processing is idempotent — the duplicate either replays a stored result or hits a no-op, so all three worlds converge to one effect.
2. Two concurrent requests can both run the SELECT (no row yet), both proceed, both INSERT/process — the classic TOCTOU race. The unique constraint makes the database serialize the decision atomically; the loser gets a conflict it can handle.
3. Backoff without jitter keeps the herd synchronized — every client returns at the same instants, producing waves that re-trip the recovering service. Full jitter spreads attempts uniformly, converting spikes into a flat, absorbable load.
4. Commit-then-publish: crash after commit, before publish → event lost forever. Publish-then-commit: crash after publish, before commit → consumers act on a transaction that never happened. Outbox: event and state share one atomic commit; the relay retries publishing (duplicates allowed, losses impossible) — shifting the burden to consumer dedupe, which is solvable.
5. From a dedupe check (event ID recorded transactionally) *before* handing to the mail provider, plus the provider's own idempotency key if it has one. Residual: crash between provider accept and your record commit → possible duplicate email — you choose at-least-once for email because the alternative (at-most-once) silently drops it; duplicates are annoying, losses are support tickets.

</details>
