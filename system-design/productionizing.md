# Productionizing an Application: The Complete Checklist

**Overview:** "It works on my machine" → "It runs reliably for strangers at 3 AM" is a longer journey than building the feature itself. This doc covers every dimension a production application needs, roughly ordered by the request lifecycle and then the operational lifecycle. Treat it as a checklist and a map — each section is a rabbit hole, but knowing the *categories* is what separates a demo from a product.

---

## 1. Configuration & Secrets

- **12-Factor config:** all environment-specific values (DB URLs, API keys, feature flags) come from **environment variables**, never hardcoded, never in git. Pydantic `BaseSettings` in FastAPI.
- **One build, many environments:** the same Docker image runs in dev/staging/prod — only config differs. If you rebuild per environment, you're testing a different artifact than you ship.
- **Secrets management:** env vars are the floor; the ceiling is a secrets manager (AWS Secrets Manager, Vault, K8s Secrets + external-secrets-operator) with rotation. Never log secrets; scrub them from error reports.
- **Feature flags:** decouple deploy from release. Ship dark, enable gradually, kill switch when things break.
- **Config validation at startup:** fail fast with a clear error if a required variable is missing — not 20 minutes later on the first request that needs it.

---

## 2. Observability (the big three + one)

You cannot fix what you cannot see. This is the single biggest gap between hobby and production code.

### Logging
- **Structured (JSON) logs** — machine-parseable, queryable. `{"level": "error", "trace_id": "...", "user_id": "...", "msg": "..."}`
- **Correlation/request IDs:** generate at the edge, propagate through every log line and downstream call. Without this, debugging distributed flows is archaeology.
- **Log levels used correctly:** DEBUG (off in prod), INFO (state changes), WARNING (handled anomalies), ERROR (needs human attention). Don't log every request at INFO — that's what access logs/metrics are for.
- **Never log:** passwords, tokens, full card numbers, PII beyond what's necessary (GDPR).
- **Centralize:** stdout → collector (Fluent Bit) → backend (Loki, ELK, CloudWatch). Grepping SSH'd boxes doesn't scale past one server.

### Metrics
- **RED method** for every service: **R**ate (req/s), **E**rrors (error rate), **D**uration (latency histograms — track p50/p95/**p99**, never just averages; averages hide the pain).
- **USE method** for resources: **U**tilization, **S**aturation, **E**rrors (CPU, memory, disk, connection pools).
- **Business metrics:** signups, orders, payments — often the first signal that something technical broke.
- Stack: Prometheus + Grafana, or OTel metrics → any backend.

### Tracing
- **Distributed tracing** (OpenTelemetry): a trace follows one request across services, showing where time was spent. Essential once you have >1 service or any async hops.
- Auto-instrument FastAPI, SQLAlchemy, Redis, httpx via OTel instrumentation libraries; export to Jaeger/Tempo/vendor.

### Error Tracking
- Sentry (or similar): aggregated exceptions with stack traces, release tagging, and alerting. Logs tell you *something* happened; Sentry tells you *what, how often, since which deploy*.

---

## 3. Health, Lifecycle & Deployability

- **Health endpoints, two kinds:**
  - `/health/live` (liveness): "is the process running?" — restarts the pod if failing
  - `/health/ready` (readiness): "can I serve traffic?" — checks DB/cache connectivity; removes pod from load balancer if failing. Confusing these causes restart loops during dependency outages.
- **Graceful shutdown:** on SIGTERM — stop accepting new requests, finish in-flight ones (with a deadline), close DB pools, then exit. Otherwise every deploy drops requests.
- **Startup order:** run migrations *before* the app starts (K8s Job / init container), validate config, warm critical caches if needed.
- **Zero-downtime deploys:** rolling updates (K8s default) or blue-green/canary. Requires: readiness probes working, graceful shutdown working, and **backwards-compatible changes** (see §7 on migrations).
- **Statelessness:** no session data, uploads, or locks on local disk/memory. State lives in the DB, Redis, or object storage — this is what makes horizontal scaling and rolling deploys possible at all.

---

## 4. Reliability & Resilience Patterns

Everything fails. Production code assumes it.

- **Timeouts on EVERYTHING:** every DB query, HTTP call, Redis op, queue publish. A missing timeout means one slow dependency exhausts your worker pool and takes down the whole service. This is the #1 unforced error.
- **Retries — but carefully:**
  - Only retry **idempotent** operations and **transient** errors (timeouts, 503s — not 400s)
  - **Exponential backoff + jitter** — synchronized retries are a self-inflicted DDoS
  - **Retry budget/cap** — retries amplify load exactly when the system is weakest
- **Circuit breakers:** after N consecutive failures to a dependency, stop calling it for a cooldown, fail fast, probe periodically. Prevents cascade failures.
- **Idempotency keys:** for any mutating endpoint a client might retry (payments!), accept an `Idempotency-Key` header and dedupe server-side. "Charged twice" is a resume-updating bug.
- **Graceful degradation:** define what happens when each dependency is down. Recommendations service dead → show defaults, not a 500. Cache down → slower, not broken.
- **Bulkheads:** isolate resource pools (separate connection pools/thread pools per dependency) so one failing dependency can't starve the others.
- **Backpressure & load shedding:** bounded queues, `429 Too Many Requests` when overloaded. Rejecting some traffic beats collapsing under all of it.
- **Dead letter queues:** async messages that keep failing go to a DLQ for inspection instead of poisoning the queue with infinite retries.

---

## 5. Security

- **AuthN vs AuthZ:** authenticate identity (JWT/OAuth2/sessions), then authorize *every* action server-side ("is user X allowed to touch resource Y" — the missing check is called BOLA/IDOR and it's the #1 API vulnerability).
- **JWT hygiene:** short-lived access tokens + refresh tokens, validate signature *and* expiry *and* audience, have a revocation story.
- **Input validation at the boundary:** Pydantic models with strict types, length limits, and enum constraints. Validate, don't sanitize.
- **The classic injuries:** SQL injection (use parameterized queries / ORM — never f-strings into SQL), XSS (escape output), CSRF (tokens for cookie-based auth), SSRF (never fetch user-supplied URLs without an allowlist).
- **Rate limiting:** per-user/per-IP, at the gateway or via Redis (sliding window). Protects against abuse, brute force, and accidental client retry storms.
- **TLS everywhere**, HSTS, secure/httponly cookies, sane CORS (never `*` with credentials).
- **Security headers:** CSP, X-Content-Type-Options, X-Frame-Options.
- **Dependency scanning:** `pip-audit`/Dependabot/Trivy in CI — most breaches come through known CVEs in dependencies, not novel attacks.
- **Least privilege:** the app's DB user can't DROP tables; the pod's IAM role can only touch its own bucket; no root in containers.
- **Audit logging:** who did what when, for sensitive operations — immutable, separate from app logs.

---

## 6. API Design & Contracts

- **Versioning strategy** (`/v1/`) decided *before* the first external consumer exists — you can't add it gracefully later.
- **Consistent error shape:** structured error responses (`{"error": {"code": "...", "message": "...", "trace_id": "..."}}`) — never leak stack traces or internal details to clients.
- **Correct status codes:** 400 vs 401 vs 403 vs 404 vs 409 vs 422 vs 429 vs 500 vs 503 — clients (and their retry logic) behave based on these.
- **Pagination on every list endpoint** from day one (cursor-based preferred over offset for large/changing datasets). Unbounded lists are a time bomb.
- **Documentation:** OpenAPI spec (FastAPI gives you this free — keep it accurate with response models and examples).
- **Deprecation policy:** how consumers learn an endpoint is going away (headers, changelog, timeline).

---

## 7. Data Layer Discipline

- **Migrations as code** (Alembic): versioned, reviewed, run automatically in the deploy pipeline, *never* hand-run SQL in prod.
- **Backwards-compatible migrations** for zero-downtime deploys — the old code version runs against the new schema during rollout. Expand-migrate-contract pattern: add nullable column → deploy code writing both → backfill → deploy code reading new → drop old. Never rename/drop in one step.
- **Connection pooling:** sized deliberately (pool_size × workers × pods ≤ DB max_connections, with headroom). PgBouncer when pod count grows.
- **Backups that are TESTED:** an untested backup is a hope, not a backup. Automate restore drills. Know your **RPO** (how much data you can lose) and **RTO** (how long recovery takes).
- **N+1 queries:** the classic ORM performance killer — eager load (`selectinload`) and watch query counts in traces.
- **Indexes:** every column in a WHERE/JOIN/ORDER BY of a hot query. `EXPLAIN ANALYZE` is your friend. But each index taxes writes — don't index speculatively.
- **Soft deletes vs hard deletes** decided per-entity, with GDPR erasure requirements in mind.
- **Data retention policy:** logs, events, and audit tables grow forever unless you decide otherwise (partitioning by date makes dropping old data trivial).

---

## 8. Async & Background Work

- **Never do slow work in the request path:** emails, PDFs, video processing, third-party syncs → queue (Celery/ARQ/SQS consumer) and return `202 Accepted` with a status-check mechanism.
- **At-least-once delivery is the default** → consumers must be **idempotent** (processing the same message twice must be safe).
- **Outbox pattern:** to atomically "update DB + publish event", write the event to an outbox table in the same transaction, and a relay publishes it. Solves the dual-write problem.
- **Scheduled jobs:** with distributed locking (Redis lock / K8s CronJob with concurrency policy) so two replicas don't both run the nightly job.
- **Monitor queue depth and consumer lag** — a silently growing queue is an outage in progress.

---

## 9. Performance & Scaling

- **Load test before launch** (k6, Locust): find the breaking point on purpose, in staging, not by surprise, in prod. Test realistic scenarios, not just one endpoint.
- **Know your numbers:** expected RPS, p99 latency target, payload sizes. "Fast" isn't a requirement; "p99 < 300ms at 500 RPS" is.
- **Horizontal scaling readiness:** stateless services (§3) + HPA on CPU/memory or custom metrics (queue depth, RPS).
- **Caching:** see `caching.md` — but measure before caching; premature caching adds invalidation bugs for no win.
- **CDN for static assets**, compression (gzip/brotli) for responses, HTTP keep-alive / connection reuse for outbound calls.
- **Profile before optimizing:** py-spy for CPU, tracing for I/O waits. Optimizing the wrong thing is the most common performance work.

---

## 10. CI/CD & Release Engineering

- **CI on every commit:** lint (ruff), type-check (mypy), tests, security scan, build image. Green pipeline = deployable artifact.
- **Testing pyramid:** many fast unit tests, fewer integration tests (real Postgres/Redis via testcontainers), a handful of E2E smoke tests. Test the failure paths — what your service does when the DB is down is *behavior you shipped*, tested or not.
- **Immutable, tagged images:** deploy `myapp:sha-abc123`, never `:latest` — you must know exactly what's running and be able to redeploy it.
- **Rollback in one command, rehearsed.** The deploy isn't done when the pipeline is green; it's done when you know you can undo it.
- **Small, frequent deploys** beat big-bang releases: smaller blast radius, easier bisection.
- **Post-deploy verification:** automated smoke tests + watching error rate/latency dashboards for the first minutes (or automated canary analysis).

---

## 11. Alerting & Incident Response

- **Alert on symptoms, not causes:** page on "error rate > 2%" and "p99 > 1s" (user pain), not "CPU > 80%" (maybe fine). Cause-based signals belong on dashboards, not pagers.
- **Every alert must be actionable** — an alert nobody acts on trains people to ignore alerts (alert fatigue kills real incidents).
- **SLOs and error budgets:** define target reliability (e.g., 99.9% success rate), alert on budget burn rate. This converts "is it reliable enough?" into a number.
- **Runbooks:** for each alert, a doc: what it means, how to diagnose, how to mitigate. 3 AM you is much dumber than 2 PM you.
- **Blameless postmortems** for real incidents: timeline, root cause(s), action items. The goal is a system that can't fail the same way twice.

---

## 12. Containerization & Runtime Hygiene

- **Small, secure images:** multi-stage builds, slim base images, non-root user, `.dockerignore`, pinned dependency versions (lock files).
- **Resource requests & limits** on every pod — without requests, scheduling is a lottery; without limits, one leaky service OOMs its neighbors.
- **Right worker model:** for K8s, 1 worker per pod + HPA scales cleaner than many workers per pod (scheduler visibility, granular scaling).
- **Log to stdout/stderr** — the platform collects; the app never manages log files.
- **Time in UTC everywhere**, timezone conversion only at display.

---

## 13. The Often-Forgotten

- **Cost awareness:** tag resources, set billing alerts, right-size instances. Unbounded log retention and forgotten dev environments are classic money leaks.
- **Compliance & privacy:** what PII do you store, where, why, for how long, and can you delete it on request (GDPR/DPDP)? Answer *before* launch.
- **Documentation:** architecture overview, ADRs (decision records — *why* you chose X), onboarding guide, runbooks. The system must be operable by someone who didn't write it.
- **Dependency ownership:** every third-party API you call — know its rate limits, SLA, failure behavior, and your fallback.
- **Single points of failure inventory:** walk the architecture and ask "what if this exact box/service/AZ dies?" for each component. Multi-AZ for anything stateful.
- **Chaos-lite:** you don't need Netflix's chaos monkey, but killing a pod in staging and watching what happens is free and eye-opening.

---

## The Priority Order (if starting from zero)

Not everything above is day-one. A sane sequence:

1. **Config from env + secrets out of git** (an hour, prevents catastrophe)
2. **Structured logging + error tracking (Sentry)** (you're blind without it)
3. **Health checks + graceful shutdown** (makes deploys safe)
4. **Timeouts on all I/O** (prevents the most common cascade failure)
5. **Migrations in pipeline + tested backups** (protects the data)
6. **Metrics + dashboards + 2-3 symptom alerts** (error rate, latency)
7. **CI with tests + one-command rollback**
8. **Rate limiting + input validation + authz checks on every endpoint**
9. **Tracing** (when service count > 1 or debugging gets hard)
10. Everything else, driven by actual incidents and load

**The meta-principle:** production readiness isn't a feature you add — it's the assumption that *every* component will fail, *every* deploy might be bad, and *every* input might be hostile, baked into every layer. The checklist above is just that assumption, enumerated.
