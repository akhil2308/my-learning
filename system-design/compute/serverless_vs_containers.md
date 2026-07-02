# Serverless vs Containers vs VMs

**Overview:** Three compute models trading control for operational simplicity. The right answer is workload-dependent — and most real architectures mix them (containers for the core API, functions for glue and spiky jobs).

---

## The Spectrum

```
More control / more ops                          Less control / less ops
VMs (EC2)  →  Containers on K8s (EKS)  →  Managed containers (Fargate, Cloud Run)  →  FaaS (Lambda)
```

### VMs (EC2, bare metal)
Full OS control. You patch, harden, scale, and babysit.
**Choose when:** special kernels/GPUs/licensing, extreme perf tuning, lift-and-shift legacy. Increasingly a niche default.

### Containers on Kubernetes
Your app + deps as an image; K8s handles scheduling, self-healing, scaling, rollouts.
**Pros:** portability, dense packing, rich ecosystem (HPA, meshes, operators), long-running processes, any runtime.
**Cons:** K8s operational complexity is real (upgrades, networking, RBAC) — it's a platform you *run*, worth it at team/multi-service scale.

### Managed container platforms (Fargate, Cloud Run, App Runner)
Containers without node management — you bring an image, platform runs it.
**The pragmatic middle:** container flexibility, near-serverless ops. Cloud Run even scales to zero. Costs more per compute-hour than self-managed nodes; fewer knobs.

### FaaS / Serverless (Lambda, Cloud Functions)
Upload a function; platform runs it per-event, scales 0→thousands automatically, bills per invocation-ms.
**Pros:** zero idle cost, zero server ops, instant elasticity, natural fit for event glue (S3 upload → thumbnail; queue → handler; cron).
**Cons & constraints:**
- **Cold starts** (ms→seconds; worse with VPC attachment/heavy runtimes) — provisioned concurrency fixes it *for money*
- **Time limits** (Lambda: 15 min), payload/memory caps, no long-lived connections (WebSockets need API Gateway's separate machinery)
- **Connection-pool hostility:** thousands of concurrent functions each opening DB connections melt Postgres → RDS Proxy / Data API / HTTP-native DBs required
- Local dev/debug friction, per-cloud lock-in (mitigate: keep business logic framework-free, thin handler adapters)
- **Cost inversion at sustained load:** per-ms pricing is a bargain at low/spiky volume and *more expensive* than reserved containers at steady high volume — do the math at your traffic

---

## Decision Matrix

| Dimension | VMs | K8s containers | Managed containers | FaaS |
|---|---|---|---|---|
| Ops burden | highest | high (platform) | low | lowest |
| Cold start | none | none (warm pods) | ~none / small | real |
| Scale-to-zero | no | not natively | Cloud Run: yes | yes |
| Long-running / streaming | ✓ | ✓ | ✓ | ✗ |
| Cost @ steady high load | good | best (dense) | ok | worst |
| Cost @ spiky/rare load | poor | poor | good | **best** |
| Startup constraint fit | any | any | any | short, event-shaped |

## Rules of Thumb
1. **Steady-traffic core API →** containers (K8s if you have platform muscle, Fargate/Cloud Run if not).
2. **Event glue, cron, spiky/rare workloads →** FaaS.
3. **Unpredictable startup, tiny team →** managed containers or FaaS; adopt K8s when its ecosystem pays for its complexity, not before.
4. Whatever the model: the disciplines don't change — statelessness, observability, timeouts, graceful shutdown apply everywhere (serverless just enforces some of them by force).

## Related
- `horizontal_scaling_autoscaling.md` (scale-to-zero, cold starts), `stateless_design.md` (FaaS mandates it), `../../system-design/productionizing.md`
