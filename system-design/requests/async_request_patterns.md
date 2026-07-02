# Async Request Patterns: Polling, Webhooks, SSE, WebSockets

**Overview:** HTTP request/response assumes the answer is ready in milliseconds. Two situations break that: **long-running work** (video processing, LLM batch jobs, report generation) and **server-initiated updates** (notifications, live feeds, chat). This doc maps each pattern to its use case.

---

## Pattern 1: 202 + Polling (long-running work, baseline)

```
POST /reports            → 202 Accepted, {"job_id": "abc", "status_url": "/jobs/abc"}
GET  /jobs/abc           → {"status": "processing", "progress": 0.4}
GET  /jobs/abc  (later)  → {"status": "done", "result_url": "/reports/xyz"}
```
- Server: enqueue job (Celery/ARQ/SQS), store status keyed by job_id (Redis/DB), workers update it.
- Client polls with **backoff** (1s → 2s → 5s cap); server can hint via `Retry-After`.
- **Pros:** dead simple, firewall-proof, stateless, works for any client. **Cons:** latency = polling interval; wasted requests.
- **Long polling** variant: server holds the GET open until status changes or timeout (~30s), then client immediately re-requests. Near-real-time latency with plain HTTP; costs a held connection per waiting client.

## Pattern 2: Webhooks (server → *server* callbacks)

Client registers a URL; you POST to it when the job finishes / event occurs (Stripe, GitHub model).
- **Delivery is at-least-once** → consumers must be idempotent (dedupe on event ID).
- **Sign payloads** (HMAC header) so receivers can verify it's really you; receivers must verify timestamps (replay).
- **Retries with backoff** on non-2xx, then dead-letter + a reconciliation API ("list events since X") because some endpoint will always be down during your send.
- Receiver best practice: ACK fast (2xx immediately, process async) — slow receivers stall your dispatcher.
- Only works when the consumer *has* a server — not for browsers/mobile.

## Pattern 3: Server-Sent Events (SSE) (server → browser, one-way)

A single long-lived HTTP response streaming `data:` frames. Native browser API (`EventSource`) with **automatic reconnection + Last-Event-ID resume** built in.
- **The right tool for one-way streams:** notifications, live dashboards, progress updates, **LLM token streaming** (this is what ChatGPT-style UIs use).
- Plain HTTP → works through proxies/LBs (disable response buffering: `X-Accel-Buffering: no`), trivially load-balanced.
- Text-only, one-directional. Client→server still goes over normal POSTs.

```python
# FastAPI SSE
@app.get("/stream")
async def stream():
    async def gen():
        async for chunk in llm_tokens():
            yield f"data: {json.dumps(chunk)}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
```

## Pattern 4: WebSockets (full bidirectional)

Persistent TCP connection upgraded from HTTP; both sides send anytime.
- **The right tool when the *client* also streams:** chat, multiplayer games, collaborative editing, live trading UIs.
- Costs: stateful connections (scaling section below), heartbeats (ping/pong) to detect death, custom reconnection + missed-message recovery logic (nothing built in — you design resume semantics), LB/idle-timeout care.
- **Don't reach for WebSockets when SSE suffices** — one-way updates over WebSockets is paying bidirectional complexity for nothing.

---

## Scaling Stateful Connections (SSE & WS share this)

Problem: connections pin users to specific nodes; a message for user B must reach *B's node*.
```
API/worker → publish("user:B", msg) → Redis Pub/Sub / Kafka →
   every gateway node subscribed → the node holding B's socket delivers
```
- **Pub/sub backplane** (Redis pub/sub, NATS) is the standard answer; shard channels as fan-out grows.
- Presence/routing registry (`user → node`) in Redis if you need targeted routing instead of broadcast.
- Draining on deploy: notify clients, let them reconnect elsewhere (connection draining), resume via Last-Event-ID / sequence numbers.
- Managed escape hatches: Pusher, Ably, AWS API Gateway WebSockets, Socket.IO w/ Redis adapter.

---

## Decision Table

| Situation | Pattern |
|---|---|
| Long job, any client, simplest | 202 + polling |
| Long job, consumer is a server | Webhook (+ reconciliation API) |
| Server→browser one-way stream (LLM tokens, notifications) | **SSE** |
| True bidirectional realtime (chat, games, collab) | WebSocket |
| Massive fan-out broadcast (sports scores) | SSE/WS behind pub/sub, or push notifications |

## Related
- `connection_management.md` (long-lived connection mechanics), `../data/event_driven_kafka.md` (the backbone behind these), README WebSocket links
