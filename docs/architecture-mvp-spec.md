# OpenIDE: Full Architecture & MVP Specification

This document details the underlying service boundaries, API contracts, deployment models, and build sequence for the **OpenIDE** runtime architecture.

---

## 1. Architectural Philosophy

OpenIDE is designed as a thin IDE client over a small set of backend services, focusing on a local-first, multi-agent IDE for software development and AI-assisted coding with the aim to **bring your own LLM provider**.

### Core Tenets
1. **Strict Service Boundaries:** Separation of concerns between UI/Editor, Agent Orchestration, Model Routing, and Tool Execution.
2. **Local-First & Privacy:** Your code, embeddings, and workspace facts remain in your environment.
3. **Transport Agnostic:** First-class Model Context Protocol (MCP) gateway abstracting stdio, SSE, and HTTP transports.
4. **Isolated Sandboxing:** Unsafe commands, dependency builds, and code execution are strictly jailed in containerized runtimes.

---

## 2. MVP Stack & Service Boundaries

| Layer | Recommended Choice | Rationale |
|---|---|---|
| **UI / IDE** | Electron or Tauri + Monaco Editor + React Shell | Gives a local-first editor experience, file tree, terminal panes, and diff review. |
| **Agent API** | TypeScript (Fastify / NestJS) | Handles streaming, structured tool orchestration, and shared types. |
| **Model Router** | Provider-agnostic TypeScript service | Provider adapters (Anthropic, OpenAI, Gemini, Ollama, vLLM) behind one interface. |
| **MCP Gateway** | Microservice (Go or TypeScript) | Manages MCP connections, schema caching, tool ACLs, and transport abstraction. |
| **Memory Service** | Postgres 16 + pgvector | Hybrid storage: episodic transcripts, structured facts, and vector semantic search. |
| **Sandbox Runner** | Docker / gVisor / Firecracker | Isolated ephemeral runners for tests, builds, and shell execution. |
| **Queue / Jobs** | Redis + BullMQ | Background repository indexing, embeddings, and test runs. |
| **Observability** | OpenTelemetry + Grafana / Tempo / Loki | Cross-service distributed tracing across model calls, tools, and sandbox jobs. |
| **Auth & RBAC** | OIDC Provider (Clerk / Auth0 / Self-hosted Keycloak) | Workspace tenant isolation and permission boundaries. |

---

## 3. Detailed Service Ownership

### 1. IDE Host
* **Owns:** Editor UX, tabs, terminal panes, diff review, approve/reject UI, local workspace selection, streaming token rendering.
* **Does not own:** Tool execution policy, LLM provider logic, durable memory, secret storage.

### 2. Agent API (Orchestrator)
* **Owns:** Session lifecycle, prompt assembly, context packing, task planning, risk scoring, human-in-the-loop approval gating.
* **Does not own:** Model vendor SDK specifics, raw MCP transports, long-running code execution.

### 3. Model Router
* **Owns:** Provider adapters, model capability registry, routing policy (cheap-first, best-reasoning, privacy-local), cost accounting, rate limiting.
* **Does not own:** Business workflows, memory retrieval, tool execution.

### 4. MCP Gateway
* **Owns:** MCP server registry, health checks, tool schema discovery, stdio/HTTP transport bridges, tool ACLs, audit logs.
* **Does not own:** High-level planning, user-facing rendering.

### 5. Memory Service
* **Owns:** Session transcripts, periodic summarization, user/workspace fact extraction, embedding generation, vector search.
* **Does not own:** Direct inference, tool execution.

### 6. Sandbox Runner
* **Owns:** Ephemeral execution containers, filesystem mounts, resource quotas (CPU/RAM/timeout), command execution, teardown.
* **Does not own:** Tool selection, user auth, long-term persistence.

---

## 4. Main API Surfaces

### IDE Host <-> Agent API
```http
POST /v1/sessions
POST /v1/sessions/{id}/messages
GET  /v1/sessions/{id}/stream
POST /v1/sessions/{id}/approve
POST /v1/sessions/{id}/cancel
GET  /v1/sessions/{id}/state
```

### Agent API <-> Model Router
```http
POST /v1/generate
POST /v1/stream
POST /v1/embeddings
GET  /v1/models
```

### Agent API <-> MCP Gateway
```http
GET  /v1/tools
POST /v1/tools/invoke
GET  /v1/servers
POST /v1/servers/{id}/refresh
GET  /v1/tool-policies
```

---

## 5. Recommended Build Order

1. **IDE Host + Agent API:** Minimal editor with streaming chat and diff review.
2. **Model Router:** Swappable provider abstraction (Anthropic, OpenAI, Gemini, Local).
3. **Filesystem & Git MCP Integration:** Local file operations behind explicit user approvals.
4. **Sandbox Runner:** Dockerized execution environment for tests and shell tasks.
5. **Memory Service:** Postgres + pgvector for session indexing and workspace knowledge.
6. **Policy & Audit Layer:** Guardrails for destructive commands and sensitive data leaks.
