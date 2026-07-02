# Connection Management: HTTP Versions, Keep-Alive & Pooling

**Overview:** Connections are expensive to create (TCP handshake + TLS handshake = 2–4 round trips before the first byte of your request) and cheap to reuse. Most "mysterious latency" and "connection refused under load" problems trace back to connection lifecycle mismanagement.

---

## The Cost of a New Connection

```
TCP handshake:        1 RTT   (SYN → SYN-ACK → ACK)
TLS 1.3 handshake:    1 RTT   (TLS 1.2: 2 RTTs)
= 2 RTTs before any data.  At 50ms RTT → 100ms of pure overhead per new connection.
```
Plus **TCP slow start**: new connections begin with a small congestion window and ramp up — a fresh connection is *slow* even after it's established. Conclusion: **reuse connections** (keep-alive, pooling) is the single biggest cheap win for service-to-service latency.

---

## HTTP/1.1 → HTTP/2 → HTTP/3

### HTTP/1.1
- **Keep-alive** (default): connection reused for sequential requests.
- **One request at a time per connection** → browsers open ~6 parallel connections per host; services need connection pools.
- **Head-of-line (HOL) blocking at the HTTP level:** a slow response blocks everything queued behind it on that connection.

### HTTP/2
- **Multiplexing:** many concurrent streams over ONE TCP connection — HTTP-level HOL blocking gone; header compression (HPACK); server push (deprecated in practice).
- **Remaining flaw — TCP-level HOL:** one lost packet stalls *all* streams (TCP delivers bytes in order). Noticeable on lossy networks (mobile).
- **gRPC runs on HTTP/2** — that's where its multiplexed, streaming RPC comes from.
- Internal services: h2 (often h2c, cleartext) between gateway and services cuts connection counts dramatically.

### HTTP/3 (QUIC)
- Runs over **UDP**; QUIC reimplements reliability *per-stream* → packet loss stalls only its own stream. TLS 1.3 built into the transport → **0–1 RTT** setup; **connection migration** (WiFi→cellular without reconnecting).
- Where it wins: mobile, lossy, high-latency edges. CDNs/browsers already default to it; internal service traffic mostly remains h2.

---

## Connection Pooling (the service-side discipline)

### HTTP client pools
Creating a client per request = handshake tax per request. **One shared client per process:**
```python
# One AsyncClient for the app lifetime (FastAPI lifespan), not per request
client = httpx.AsyncClient(
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
    timeout=httpx.Timeout(5.0, connect=2.0),
)
```

### Database pools — the sizing math
```
total DB connections = pool_size × workers_per_pod × pods
must be  <  Postgres max_connections (default 100!) with headroom
```
- Every Postgres connection is a **process** (~5–10MB + scheduler cost) — more connections ≠ more throughput; past ~2–4× cores, throughput *drops*.
- At scale: **PgBouncer** (transaction-mode pooling) multiplexes thousands of client connections onto tens of server connections. Note: transaction mode breaks session state (prepared statements config, advisory locks) — know the caveats.
- Pool exhaustion symptom: requests hang waiting for a connection → configure pool timeout so it fails fast and visibly instead.

---

## TCP Gotchas That Bite in Production

- **TIME_WAIT exhaustion:** the side that *closes* a connection holds the port in TIME_WAIT ~60s. A proxy opening/closing thousands of short connections/sec runs out of ephemeral ports → "cannot assign requested address." Fix: keep-alive/pooling (fewer closes), more ephemeral ports, `tcp_tw_reuse`.
- **Idle timeout mismatches:** LB kills idle connections at 60s, client pool keeps them 120s → client sends on a dead connection → reset/latency spike. Rule: **client idle timeout < server/LB idle timeout**, plus TCP keepalive probes.
- **Nagle vs delayed ACK** (`TCP_NODELAY`): small-write latency interactions — most HTTP libraries set NODELAY already; relevant for custom protocols.
- **Half-open connections:** peer died without FIN — only detected on next write or via keepalive probes; another reason for aggressive client timeouts.

---

## WebSockets & Long-Lived Connections at Scale
- Each open socket holds memory + a file descriptor server-side; 1M idle connections is a memory/fd problem before a CPU one (raise `ulimit`, tune kernel).
- LBs must support them (L7 with upgrade handling); idle timeouts need ping/pong heartbeats.
- Horizontal scaling problem: user A on node 1, user B on node 2 → cross-node delivery via Redis pub/sub or a message broker (see `async_request_patterns.md`).

## Related
- `async_request_patterns.md`, `queueing_theory.md`, `../../system-design/productionizing.md` §7 (pool sizing)
