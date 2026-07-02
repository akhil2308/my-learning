# Horizontal Scaling & Autoscaling

**Overview:** Vertical scaling (bigger box) is simple but has a ceiling and a single point of failure. Horizontal scaling (more boxes) has no practical ceiling but demands architectural discipline (statelessness, load balancing, distributed state). Autoscaling automates the "more boxes" part — badly, unless you choose the signals carefully.

---

## Vertical vs Horizontal (honest economics)

- **Vertical first is legitimate:** a modern 64-core/512GB box is enormous; no code changes, no distributed-systems tax. Limits: hardware ceiling, price grows super-linearly at the top end, redundancy still requires ≥2 anyway, resize often means restart.
- **Horizontal** requirements: stateless services (see `stateless_design.md`), a load balancer, externalized state, and ideally N+1 thinking (any single node's death is a non-event).
- Real systems do both: scale *up* to a sweet-spot instance size (best price/perf), then *out*.
- **Scaling reads ≠ scaling writes:** stateless compute scales out trivially; stateful stores need replication (reads) and sharding (writes) — `../data/../database_scaling.md`.

---

## Kubernetes Autoscaling (the three layers)

1. **HPA (Horizontal Pod Autoscaler):** adds/removes pod replicas. The workhorse.
2. **VPA (Vertical Pod Autoscaler):** adjusts pod requests/limits — mostly a *rightsizing recommendation* tool; avoid mixing with HPA on the same metric.
3. **Cluster Autoscaler / Karpenter:** adds/removes **nodes** when pods can't schedule. HPA without cluster autoscaling hits a wall at node capacity.

### Choosing HPA signals
- **CPU %:** default; fine for CPU-bound work. Misleading for I/O-bound services (low CPU while drowning in slow downstream calls).
- **Memory:** usually a *limit* concern, not a scaling signal (many runtimes don't return memory).
- **Custom/external metrics (the good ones):**
  - **Requests-per-second per pod** — direct demand signal
  - **Queue depth / consumer lag per worker** — THE signal for async workers (KEDA makes this easy, incl. scale-to-zero)
  - **In-flight concurrency** (what Knative uses)
- Rule: scale on the resource that actually saturates first. Find it by load testing (`../resilience/capacity_estimation.md`).

### Tuning realities
- **Scale up fast, scale down slow** (stabilization windows ~5min down): flapping wastes money and churns caches/connections.
- **Lag is inherent:** metric scrape → decision → pod schedule → image pull → readiness = 30s–minutes. Autoscaling absorbs *trends*, not *spikes* — spikes are handled by headroom + load shedding, not HPA.
- min replicas ≥ 2 (HA), and enough baseline headroom to survive the scale-up lag.
- **PodDisruptionBudgets** so autoscaler node drains don't take out all replicas.

---

## Cold Starts & Warm-Up

New capacity is *slow* capacity at first: image pull, process boot, JIT/import time, empty local caches, cold connection pools, TCP slow start.
- Readiness probe should pass only when genuinely ready (pool connected, caches primed if critical).
- **Slow-start / ramp:** some LBs (Envoy, ALB) send new backends a gradually increasing share — otherwise the LB dogpiles the cold pod and its latency spike triggers... more scaling.
- Keep images small; lazy-load what you can; consider pre-warmed spare capacity for spiky workloads.

## Scale-to-Zero & Predictive
- **Scale-to-zero** (KEDA/Knative/serverless): perfect for sporadic workers; unacceptable for latency-sensitive APIs unless cold start < SLO (rare).
- **Scheduled scaling** beats reactive for known patterns (9am weekday ramp, month-end batch): pre-scale before the wave. Predictive autoscaling (AWS) automates this from history.
- **Spot/preemptible instances** for stateless fleets = 60–90% cost cut; requires graceful termination handling and never putting *all* replicas on spot.

---

## The Checklist Before Turning Autoscaling On
- [ ] Service is stateless and drains gracefully (SIGTERM handling)
- [ ] Readiness probe is honest; startup is as fast as you can make it
- [ ] You know the true bottleneck resource from load tests, and scale on it
- [ ] min ≥ 2, scale-down stabilized, PDBs set
- [ ] Downstream can absorb it: **autoscaling your API multiplies pressure on the database** — pool math re-checked (pods × pool_size), PgBouncer in place. Scaling one tier moves the bottleneck, it doesn't remove it.

## Related
- `stateless_design.md`, `../requests/queueing_theory.md` (headroom math), `../requests/backpressure_load_shedding.md` (spikes), your K8s decisions in fastapi-large-app-template (1 worker/pod + HPA)
