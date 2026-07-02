# Multi-Region Architecture & Disaster Recovery

**Overview:** Multi-AZ handles a datacenter failure; multi-region handles a *regional* one (rare but real: whole-region cloud outages happen ~yearly somewhere) — and separately, serves global users at local latency. The two motivations (DR vs latency) lead to different architectures. The hard part is never compute — **it's the data.**

---

## First: RTO & RPO (decide these before any architecture)

- **RPO (Recovery Point Objective):** how much data you may lose. RPO 1h → hourly backups suffice; RPO ~0 → synchronous replication.
- **RTO (Recovery Time Objective):** how long recovery may take. RTO 24h → restore from backup; RTO minutes → warm standby; RTO ~0 → active-active.
- Cost grows *exponentially* as both → 0. These are **business** numbers — get them stated, per system tier (payments ≠ recommendation engine), then buy exactly that much architecture.

## The DR Tiers

```
1. Backup & Restore        RTO: hours–days   RPO: hours    $
2. Pilot Light             RTO: ~1h          RPO: minutes  $$      (data replicated cross-region; compute templates ready, off)
3. Warm Standby            RTO: minutes      RPO: seconds+ $$$     (scaled-down full copy always running)
4. Active-Active           RTO: ~0           RPO: ~0*      $$$$    (all regions serve traffic)
```
Tier 1 is mandatory regardless of tier (it's also your ransomware/corruption/fat-finger recovery — replication faithfully replicates your `DELETE FROM users`). **Cross-region, cross-account backups, restore-tested** — `../../system-design/productionizing.md` §7.

---

## Active-Passive (warm standby) — the common sane choice

Primary region serves everything; standby receives **async** replicated data.
- **Async is forced by physics:** sync replication across 60–200ms RTT would add that to *every write*. Consequence: **failover loses the replication-lag window** (seconds of writes) — that's your real RPO.
- **Failover is the hard part, not the standby:**
  - DNS/traffic shift (Route 53 health checks, or anycast/Global Accelerator to dodge DNS TTL caching)
  - Promote the replica; reconfigure apps; **fence the old primary** so it stops accepting writes when it comes back (split brain across regions — see `consensus_and_coordination.md`)
  - Decide: automatic failover (risk: flapping/false positives causing split brain) vs human-approved (slower RTO, most orgs' honest choice)
- **A failover you haven't rehearsed doesn't exist.** Game-day it quarterly; failback (returning after recovery) needs its own tested plan — it's a reverse migration, not a switch.

## Active-Active — powerful, and mostly about the write model

All regions serve users (latency win: users hit the nearest region). Reads are easy — replicate data everywhere, read locally. **Writes are the fork in the road:**

1. **Single-writer (recommended default):** every region reads locally; all writes route to one home region. Simple consistency; write latency for far users; failover = promote another region.
2. **Partitioned writers (geo-homing):** each record has a home region (user's residence — also a data-sovereignty/DPDP fit); writes go home, reads local. Cross-partition operations become distributed transactions (`distributed_transactions.md`).
3. **Multi-writer:** any region accepts any write → **conflicts are now a feature of your life** (concurrent updates to the same row in two regions). Requires CRDTs/LWW/merge logic (`consistency_models.md`) or a database that does consensus per-write (Spanner, CockroachDB — paying cross-region latency on writes: PACELC in the flesh). Choose only with a real requirement.

Managed shortcuts: DynamoDB Global Tables / Cosmos DB (multi-writer, LWW-ish conflict handling — read the fine print), Aurora Global Database (single-writer, ~1s lag, fast promotion), CockroachDB/Spanner (consistent, latency-priced).

## The Auxiliary State Everyone Forgets
The database gets all the attention; failover then dies on: **Redis** (sessions/queues — replicate or accept loss?), **Kafka** (MirrorMaker/cluster linking — offsets don't translate 1:1), object storage (S3 CRR is easy — turn it on), secrets/config, DNS TTLs, and **quota/capacity in the standby region** (the standby that can't scale up during a real event is decoration). Inventory *every* stateful dependency; each needs its own RPO/RTO answer.

## Sequencing Advice
Multi-AZ (free-ish, always) → Tier 1 backups cross-region (cheap, mandatory) → warm standby when the business RTO demands it → active-active *reads* for latency → active-active *writes* only under duress. Each step multiplies operational surface; most companies claiming active-active run a well-rehearsed warm standby — that's not an insult, it's the correct trade.

## Related
- `consistency_models.md` (the write-model trade IS PACELC), `consensus_and_coordination.md` (fencing, split brain), `../data/cdn_and_edge.md` (latency for static/read paths without multi-region), `capacity_estimation.md`
