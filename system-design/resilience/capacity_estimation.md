# Capacity Estimation & Back-of-Envelope Math

**Overview:** The #1 system-design-interview skill and a genuinely useful engineering habit: sizing a system in 2 minutes with round numbers. The goal is never precision — it's catching order-of-magnitude errors ("that's 50TB/day, one Postgres won't do") and justifying architecture with arithmetic instead of vibes.

---

## Numbers Worth Memorizing (2020s edition)

### Latency ladder
```
L1 cache                          ~1 ns
Main memory reference           ~100 ns
Read 1MB from RAM               ~10 µs
NVMe SSD random read          ~20–100 µs
Read 1MB from SSD              ~200 µs–1 ms
Same-AZ network round trip     ~0.5 ms
Cross-AZ round trip             ~1–2 ms
Cross-region (same continent) ~20–80 ms
Cross-continent (IN↔US-East) ~180–250 ms
HDD seek                        ~10 ms
```
The ratios are the lesson: RAM is ~1000× SSD, SSD is ~100× cross-region. **A cache hit replaces a cross-region call at a millionth of the latency** — every caching/CDN/locality argument is this ladder.

### Throughput anchors (order of magnitude, tune-dependent)
```
Postgres (tuned, simple queries)      ~5k–20k QPS per beefy node
Redis                                  ~100k+ ops/s per node
Kafka                                  ~100s of MB/s per broker
Single app pod (FastAPI, light I/O)    ~1k–5k RPS
NVMe disk                              ~1–3 GB/s sequential, ~100k+ IOPS
```

### Conversion shortcuts
```
1 day ≈ 100,000 s  (86,400 — round to 10⁵ for mental math)
1M requests/day ≈ 12 RPS average
peak ≈ 2–5× average   (consumer traffic; pick 3× if unsure and say so)
2³⁰ ≈ 10⁹ (GB), 2⁴⁰ ≈ 10¹² (TB)
```

---

## The Method (5 steps, ~2 minutes)

1. **Users → actions:** DAU × actions/user/day
2. **QPS:** ÷ 10⁵ seconds, × peak factor; split read vs write (state the read:write ratio — 100:1 for feeds, 3:1 for chat)
3. **Storage:** items/day × bytes/item × retention (media dominates everything — separate metadata from blobs)
4. **Bandwidth:** QPS × payload size
5. **Sanity-check against the anchors** → conclusions ("40k read QPS ≫ one Postgres → cache + replicas")

State assumptions out loud; round aggressively (1 significant figure); keep units visible — unit errors are the classic failure.

## Worked Example: Twitter-Like Service

**Assume:** 200M DAU, 2 posts/user/day, read:write 100:1, post ≈ 300 bytes metadata, 10% carry a 200KB image, 5-year retention.

```
Writes:  200M × 2 = 400M posts/day ≈ 4k WPS avg → ~12k WPS peak
Reads:   100× writes ≈ 400k RPS avg → ~1.2M RPS peak

Storage (metadata): 400M × 300B ≈ 120 GB/day ≈ 44 TB/yr → ~220 TB / 5yr
Storage (images):   40M × 200KB ≈ 8 TB/day  → ~15 PB / 5yr   ← blobs dominate 60:1

Bandwidth (read, metadata only): 400k RPS × ~1KB ≈ 400 MB/s; images push it to multi-GB/s → CDN mandatory
```
**Conclusions the math forces:** reads → aggressive cache (1.2M RPS is a Redis-fleet/CDN problem, not a DB problem); 220TB metadata → sharded storage (`../database_scaling.md`); images → S3+CDN from day one (`../data/cdn_and_edge.md`); 12k WPS peak → fine for a partitioned write path (Kafka ingest, sharded DB).

## Sizing Compute & Connections (Little's Law, applied)

```
concurrency = throughput × latency          (see ../requests/queueing_theory.md)
```
Target 5k RPS at 100ms avg → 500 in-flight. At ~100 in-flight per async pod → **~5 pods at 100% — run 8–10** (60–70% utilization headroom; the hockey-stick argument).
DB connections: 10 pods × pool 20 = 200 > Postgres default max 100 → PgBouncer or smaller pools — *this multiplication is the #1 real-world capacity bug* (`../requests/connection_management.md`).

## Memory / Cache Sizing
"Cache the hot 20%": 500M items × 1KB = 500GB total → hot set ~100GB → a few Redis nodes or one big one. Always compare working-set size to RAM before assuming "we'll cache it."

---

## Cheat Card
- 1M/day ≈ 12 RPS · day ≈ 10⁵ s · peak = 3× avg
- RAM ≫ SSD ≫ network ≫ cross-region (10³ jumps)
- Blobs dominate storage; CDN for bytes, cache for reads, shard for writes
- concurrency = RPS × latency; run at ~⅔ utilization
- pods × pool_size vs DB max_connections — always check
- Say assumptions → compute → compare to anchors → conclude architecture

## Related
- `../requests/queueing_theory.md` (why the headroom), `../database_scaling.md`, `../data/cdn_and_edge.md`, `../System Design Challenge Simulator.md` (practice these numbers there)

## Practice Rep (60 min, pass/fail) — Session 22 [INTERVIEW-CRITICAL]

**Three timed estimates, five minutes each, out loud, recorded.** Use the 5-step method; no calculator beyond rough powers of ten:

1. **Instagram-scale photo upload:** 500M DAU, 10% post 1 photo/day, 2 MB avg → uploads/s, storage/year, bandwidth at peak (×5).
2. **Your rate limiter (session 23):** 50k RPS API, token bucket per key in Redis → Redis ops/s, memory for 10M active keys (~100 B/bucket), shard count at 100k ops/s/instance.
3. **WhatsApp-scale message fan-out:** 2B messages/day → messages/s avg and peak, connection-server count at 500k idle conns/box, delivery-receipt amplification (×3).

Then 10 min: check each against the anchors in this doc (requests/s per server, storage ladder) and mark where you were >10× off.

**Pass:** all three completed inside 5 min each with assumptions stated *before* arithmetic; final numbers within 10× of reference (uploads ~600/s avg, ~35 TB/day photos, limiter ~1 GB + 1 shard headroom→2, messages ~23k/s avg); each ends with an architectural conclusion ("fits N boxes"), not a bare number.
**Fail:** any estimate that starts computing before stating assumptions, or a result presented without the so-what conclusion.
