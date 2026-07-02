# MCP: Model Context Protocol

**Overview:** MCP standardizes how LLM applications connect to tools and data — "USB-C for AI tools." Before it: every (app × integration) pair was custom glue (M×N problem). With it: a tool provider ships one **MCP server**; any MCP-capable client (Claude apps, IDEs, agent frameworks, your platform) can use it (M+N). Open-sourced by Anthropic (late 2024), since adopted across the ecosystem as *the* accepted way agents reach external tools.

---

## The Model

```
Host app (agent/chat/IDE)
  └── MCP client ↔ (JSON-RPC) ↔ MCP server(s)   — one per integration
                                    ├── GitHub server
                                    ├── Postgres server
                                    └── your internal-API server
```

A server exposes three primitive types:
- **Tools** — model-invoked functions (schemas + execution): the function-calling contract (`../building/tool_use.md`), standardized
- **Resources** — application-controlled data the host can read into context (files, rows, docs) — *context provisioning*, distinct from tools
- **Prompts** — reusable, parameterized prompt templates the server offers ("slash commands")

Plus: servers can request **sampling** (ask the host's LLM to complete something — enables server-side agentic steps without the server owning a model) and **elicitation** (ask the user for input mid-operation).

**Transports:** stdio (local child process — dev tools, IDE integrations) and streamable HTTP (remote servers — the production/enterprise path, with OAuth for auth). Sessions are stateful: capability negotiation at init, then discovery (`tools/list`) and invocation (`tools/call`).

## Why It Matters Architecturally

1. **Decouples tool development from agent development:** teams ship MCP servers independently; agents compose them at runtime. It's the microservices moment for agent tooling — with the same governance consequences (server sprawl, version drift, discovery/registry needs).
2. **Dynamic capability discovery:** clients learn available tools at connect time — agents can gain tools without redeploy. Powerful; also exactly the property that demands guardrails (below).
3. **Ecosystem leverage:** thousands of public servers exist; the build-vs-connect calculus for integrations shifted permanently.
4. For your platform: internal APIs wrapped once as MCP servers become usable by every agent (and every third-party MCP client your org adopts) — the integration work compounds instead of repeating per agent.

## The Security Reality (MCP concentrates the agent threat model)

Every concern in `../llm_agent_security.md` gets sharper because MCP is *designed* to attach powerful, third-party, dynamically-discovered capabilities:
- **Tool descriptions are prompt-injection carriers** — a malicious/compromised server's tool descriptions enter your model's context (tool poisoning). Vet and pin servers like dependencies (they ARE dependencies — supply chain rules apply, `../../security/web_api_attacks.md` §8).
- **Rug pulls:** a server you approved can change its tool definitions later → pin versions, alert on definition changes.
- **Confused deputy / trifecta assembly:** MCP makes it trivially easy to give one agent private-data access + untrusted content + egress — audit the *combination* of connected servers, not each alone.
- **Credential scope:** servers hold real credentials (DB, GitHub) — least-privilege per server, user-scoped tokens over god-mode service accounts, OAuth flows for remote servers.
- Baseline: allowlist servers, human-approve consequential tools, log every call (`../quality/llm_observability.md`).

## Practical Notes
- **Tool-count bloat is real:** connecting 6 servers × 15 tools = 90 schemas in every prompt → cost + selection-accuracy tax (`../building/tool_use.md`). Curate per agent/node; expose relevant subsets dynamically.
- Writing a server is easy (official SDKs; a FastAPI-wrapping Python server is an afternoon) — the effort goes into tool *design*: descriptions, distilled return values, error messages. Same skill, new envelope.
- Related-but-different: **A2A** (agent-to-agent protocol) targets agent↔agent interop; MCP targets agent↔tool/data. See `emerging_landscape.md`.

## Related
- `../building/tool_use.md` (the contract MCP standardizes), `../llm_agent_security.md`, `emerging_landscape.md`
