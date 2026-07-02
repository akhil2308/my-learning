# API Gateway & Reverse Proxy Patterns

**Overview:** A reverse proxy sits in front of servers and forwards requests to them; an **API gateway** is a reverse proxy with API-management brains. It's the single front door — the one place to solve cross-cutting concerns so every microservice doesn't reimplement them.

---

## Reverse Proxy vs Load Balancer vs API Gateway

- **Reverse proxy** (Nginx, Envoy, HAProxy): forwards, terminates TLS, buffers, caches, compresses. Generic.
- **Load balancer:** a reverse proxy whose main job is distribution across replicas (see `load balancer.md`). L4 (TCP) vs L7 (HTTP-aware).
- **API gateway** (Kong, Envoy+control plane, AWS API Gateway, Apache APISIX): adds authN/Z, rate limiting, routing rules, transformations, API keys, analytics. In practice these blur — Nginx with enough Lua *is* a gateway.

---

## What Belongs in the Gateway (cross-cutting concerns)

1. **TLS termination** — decrypt once at the edge; internal traffic re-encrypted via mTLS/mesh if required
2. **Authentication** — validate JWT/API key once; pass verified identity to services as trusted headers (services still do *authorization* — object-level checks can't live at the gateway)
3. **Rate limiting & quotas** — the natural chokepoint
4. **Routing** — path/host/header-based (`/api/orders/* → orders-svc`), including canary splits (5% → v2)
5. **Resilience defaults** — timeouts, retries, circuit breaking per upstream (Envoy excels here)
6. **Request/response shaping** — compression, size caps, header injection (request ID!), CORS
7. **Observability** — access logs, RED metrics, trace initiation happen here uniformly

**What does NOT belong:** business logic. A gateway that transforms payloads per-endpoint and enforces business rules has become a monolith in a trench coat ("smart pipes" anti-pattern — keep the gateway dumb-ish, endpoints smart).

---

## Patterns

### Backend-for-Frontend (BFF)
One gateway/aggregation layer **per client type** (mobile BFF, web BFF). Each BFF aggregates and shapes service calls for its client's exact needs (mobile wants small payloads, fewer round trips). Solves the "one-size-fits-none general API" problem; costs another layer to own.

### Gateway Aggregation
Client makes 1 call; gateway fans out to N services and merges. Cuts client round trips (huge on mobile/high-latency links); the aggregate is only as fast as the slowest branch — set per-branch timeouts and degrade gracefully.

### Service Mesh vs Gateway
Not competitors: gateway = **north-south** traffic (edge → cluster); mesh sidecars (Istio/Linkerd) = **east-west** (service → service: mTLS, retries, traffic shifting). Big systems use both; small systems need neither a mesh nor the pain.

---

## Operational Notes

- The gateway is a **SPOF by design** → run replicated behind DNS/L4 LB, scale horizontally (it's stateless), monitor it harder than anything else.
- **Added latency** is real but small (~1ms per hop) — fan-out amplification matters more than the hop itself.
- **Config as code:** routing rules in git, deployed via CI — a hand-edited gateway config is an outage generator.
- **Header hygiene:** strip client-supplied `X-User-Id`-style headers at the edge before injecting your own — otherwise clients can impersonate (classic vulnerability).

## Related
- `load balancer.md`, `rate_limiting.md`, `../security/authn_authz.md` (service-to-service auth)
