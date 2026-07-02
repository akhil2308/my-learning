# ID Generation at Scale

**Overview:** `BIGSERIAL` is perfect — until you shard, go multi-region, generate IDs client-side, or mind that your competitors can read your order volume from your URLs. Then "give me a unique ID" becomes a real design problem with a small set of standard answers.

---

## Why Auto-Increment Breaks

1. **Sharding:** every shard's sequence starts at 1 → collisions (workaround — offset/interleaved sequences — is brittle ops)
2. **Central bottleneck/SPOF** if you keep one sequence source for all shards
3. **Pre-insert IDs impossible:** client/app can't know the ID before the DB round trip (batch building, event IDs, offline-first)
4. **Information leakage:** sequential IDs reveal volume and invite enumeration (`/orders/10001`, `/orders/10002`... — pair with the BOLA discussion in `../security/web_api_attacks.md`)

## The Requirements Checklist
Unique (globally) · no coordination on the hot path · **roughly time-sortable** (the underrated one — see index locality below) · compact · unguessable if IDs are exposed.

---

## The Options

### UUIDv4 (random)
128 random bits. Zero coordination, unguessable, universal support.
**The hidden cost — index locality:** B-tree inserts land at *random* positions → page splits, cold-page churn, bloated indexes, poor range scans. Measurable write degradation on big tables. Also 16 bytes (vs 8) multiplied across every FK and index.

### UUIDv7 (timestamp-prefixed) — **the modern default**
```
48 bits unix-ms timestamp │ version bits │ 74 bits randomness
```
Time-ordered → inserts append to the "right edge" of the index (locality restored), keeps UUID compatibility (Postgres `uuid` column), still unguessable, generated anywhere with no coordination. Standardized RFC 9562; `uuid7` libs in every language, native in Postgres 18.
Trade: creation-time is readable from the ID (usually fine; occasionally a privacy consideration).

### Snowflake IDs (Twitter lineage)
```
64 bits:  timestamp-ms (41) │ machine/worker id (10) │ per-ms sequence (12)
```
- 64-bit integer (half the storage of UUID), k-sorted by time, ~4M IDs/sec/machine
- **The operational catch:** assigning unique worker IDs *is* a coordination problem (ZooKeeper/etcd lease, K8s ordinal, IP-derived) — see `consensus_and_coordination.md`
- **Clock skew:** timestamp regression risks duplicates → NTP discipline + refuse-to-generate (or hold) on backward clock. This is the classic Snowflake incident.
- Variants everywhere: Instagram (shard id in the middle, generated *inside* Postgres via PL/pgSQL), Discord, Sony's Sonyflake.

### Interesting alternates
- **ULID:** 48-bit time + 80-bit random, Crockford base32 (`01ARZ3NDEKTSV4RRFFQ69G5FAV`) — lexicographically sortable *as a string*; UUIDv7's spiritual twin, nicer to read.
- **NanoID / short codes:** URL-friendly short random strings (invite codes, short links) — size vs collision probability is a birthday-bound calculation; check it.
- **KSUID** (Segment): 32-bit seconds + 128-bit random.
- **DB ticket/block allocation:** central table hands out ranges of plain integers to app nodes (Flickr's scheme) — simple, but the allocator is back on the availability path.

---

## Practical Guidance

| Situation | Pick |
|---|---|
| New system, general purpose | **UUIDv7** (or ULID) |
| Storage/index bytes matter at huge scale, infra maturity exists | Snowflake-style 64-bit |
| Single Postgres, internal-only IDs, no exposure | `BIGSERIAL` honestly remains fine |
| Public-facing reference codes | Random short ID (NanoID) *mapped to* an internal ordered ID |
| Event/message IDs for dedupe | UUIDv7 — sortable helps debugging, uniqueness enables idempotency (`distributed_transactions.md`) |

- Dual-ID pattern: internal ordered PK (joins, locality) + external random ID (API surface) — decouples performance from exposure.
- Never parse business meaning out of IDs beyond rough time; encode meaning in columns.
- If staying with UUIDv4 on an existing system, know the index-locality tax is what you're paying.

## Related
- `../database_scaling.md` (sharding necessitates this), `consensus_and_coordination.md` (worker-ID assignment), `../security/web_api_attacks.md` (enumeration)
