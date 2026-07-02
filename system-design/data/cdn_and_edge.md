# CDN & Edge Computing

**Overview:** Physics is the one latency you can't optimize away — ~80ms round trip India↔US-East no matter how fast your code is. CDNs attack it by moving content (and increasingly compute) to hundreds of **PoPs (points of presence)** near users. For most consumer apps, the CDN serves the majority of bytes; your origin serves the minority that's truly dynamic.

---

## How a CDN Request Works

```
User → DNS/anycast routes to nearest PoP → edge cache
  HIT  → served in ~10–30ms (never touches you)
  MISS → edge fetches from origin (possibly via a shield/regional tier), caches per policy, serves
```
- **Anycast:** many PoPs announce the same IP; internet routing (BGP) delivers each user to the nearest — that's the "closest server" magic.
- **Origin shield:** a designated mid-tier cache between edges and origin → N misses collapse into ~1 origin fetch (compare cache stampede, `../caching.md`).
- Even for **uncacheable** requests, CDNs help: user's TCP+TLS terminates at the nearby edge; edge→origin rides warm, tuned long-haul connections (dynamic acceleration).

---

## Cache-Control: the contract you write

```
Cache-Control: public, max-age=31536000, immutable      # fingerprinted assets
Cache-Control: public, max-age=0, s-maxage=300,
               stale-while-revalidate=600               # HTML/API edge caching
Cache-Control: private, no-store                        # per-user/sensitive
```
- `s-maxage` = shared-cache (CDN) TTL, separate from browser `max-age` — cache hard at the edge, short in browsers.
- **`stale-while-revalidate`** — serve stale instantly, refresh in background: the best latency/freshness trade for most content. `stale-if-error`: stale beats a 500 during origin outages (free resilience).
- `ETag`/`Last-Modified` → revalidation (`304 Not Modified`): "still fresh?" costs a round trip but no bytes.

### The fingerprinting pattern (solves invalidation)
Build emits `app.3f9a2c.js`; content change ⇒ new URL ⇒ old cache entries irrelevant. Assets: `max-age=1yr, immutable`; the small HTML that references them: short TTL. **Versioned URLs > purging** — purge APIs (or tag-based purge) are the fallback for emergencies, not the strategy.

### Cache keys & Vary
Default key ≈ URL. `Vary: Accept-Encoding` is fine; `Vary: Cookie` = zero hit rate. Normalize/strip irrelevant query params (`utm_*`) or every marketing link is a distinct miss.
**The classic CDN incident:** caching a response that varied by user (missing `private`) → users see each other's data. Any authenticated response defaults to `private, no-store` until proven safe.

---

## Caching Dynamic Content
- **API edge caching:** public, read-heavy, tolerant-of-staleness endpoints (product listings, feeds) with `s-maxage=30–300` + SWR can offload most read traffic. Per-user responses: don't (or key by auth — rarely worth it).
- **ESI/partial:** cache the page shell long, fetch the personalized fragment separately (often just client-side JS + a small API call).

## Edge Compute
Run code *at* the PoP: Cloudflare Workers (V8 isolates — ~0ms cold start), Lambda@Edge, Fastly Compute.
- **Good edge jobs:** AB-test bucketing/routing, auth token verification (reject bad JWTs before they cross the ocean), redirects/rewrites/headers, geo-personalization of cached content, edge-rendered frameworks (Next.js middleware).
- **Constraints:** tight CPU/memory/time budgets, and **your data isn't there** — an edge function calling your Mumbai Postgres re-pays the latency it saved (edge KV stores are eventually consistent; see `consistency_models.md`). Keep edge logic data-light.

## Operational Notes
- Protect the origin: accept traffic only from CDN IP ranges / signed origin header — otherwise attackers bypass the CDN (and its DDoS absorption, WAF, rate limiting — the CDN is also a security layer, see `../security/infrastructure_security.md`).
- **Signed URLs/cookies** for private media (paid videos): CDN-cacheable yet access-controlled, with expiry.
- Watch **cache hit ratio** per content type; a hit-ratio drop is either a deploy bug (keys/headers changed) or an attack (cache-busting query params).
- Video = HLS/DASH segments over CDN — the textbook CDN workload.

## Related
- `../caching.md` (same theory, different tier), `../requests/connection_management.md` (why edge TLS termination wins), `../resilience/multi_region_dr.md`
