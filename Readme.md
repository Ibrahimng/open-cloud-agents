---
name: OpenIDE
description: OpenIDE is a thin IDE client over a small set of backend services, focusing on a local-first, multi-agent IDE for software development and AI-assisted coding with the aim for to bring your own llm-provider.
environments:
  - local
  - remote
  - any
components:
  - IDE Host
  - Agent API
  - Model Router
  - MCP Gateway
  - Memory Service
  - Sandbox Runner
contributors:
  - name: Ibraheem Jimoh
    email: ibrahim.jimoh@outlook.com
---

# MVP stack

For a deployment-ready MVP, I'd use this stack because it minimizes moving parts while preserving clean service boundaries:

| Layer | Recommended choice | Why |
|---|---|---|
| **UI / IDE** | Electron or Tauri desktop app + Monaco Editor + React/Next-style frontend shell | Gives you a local-first editor experience, file access UX, terminal panes, and diff review in one host app.  [snyk](https://snyk.io/articles/a-beginners-guide-to-visually-understanding-mcp-architecture/) |
| **Agent API** | TypeScript, NestJS or Fastify | Good fit for streaming, structured APIs, orchestration logic, and shared types across frontend/backend. |
| **Model Router** | Separate TypeScript service with provider adapters | Keeps Anthropic/OpenAI-compatible/Gemini/local backends swappable behind one interface.  [arxiv](https://arxiv.org/abs/2504.08999) |
| **MCP Gateway** | TypeScript or Go microservice | Good for managing multiple MCP client connections, schemas, auth, and routing. MCP clients can be separated from the host for flexible deployment.  [obot](https://obot.ai/resources/learning-center/mcp-architecture/) |
| **Memory** | Postgres + pgvector | A Postgres table with JSONB plus vector search covers most agent-memory needs without extra infrastructure.  [mindstudio](https://www.mindstudio.ai/blog/ai-agent-hybrid-memory-architecture) |
| **Sandbox** | Docker-based isolated runners, later gVisor/Firecracker | Gives you command execution, tests, and builds in a controlled environment.  [cloud.google](https://cloud.google.com/discover/what-is-model-context-protocol) |
| **Queue / jobs** | Redis + BullMQ | Useful for long-running tasks like indexing, summarization, test runs, and repo scans. |
| **Observability** | OpenTelemetry + Grafana/Tempo/Loki or Datadog | You need tracing across model calls, MCP tools, and sandbox jobs.  [truefoundry](https://www.truefoundry.com/blog/mcp-server-security-best-practices) |
| **Auth** | Auth0, Clerk, or self-hosted OIDC | Needed for multi-user orgs, RBAC, and workspace isolation.  [truefoundry](https://www.truefoundry.com/blog/mcp-server-security-best-practices) |
| **Deployment** | Cloud Run for stateless services, Kubernetes only later | Serverless/container-managed deployments are a strong fit for many MCP components early on.  [cloud.google](https://cloud.google.com/discover/what-is-model-context-protocol) |

## Service boundaries

Keep the boundaries strict so each service has one job:

### 1. IDE Host
The desktop or web client should own editor UX, patch rendering, user approvals, local file visibility, and session interaction. In MCP terms, this is the host layer where the user sees and authorizes actions. [snyk](https://snyk.io/articles/a-beginners-guide-to-visually-understanding-mcp-architecture/)

**Owns**
- Editor tabs, file tree, terminal UI, chat UI
- Diff review and approve/reject flows
- Workspace selection
- Streaming output rendering
- Local telemetry and crash handling

**Does not own**
- Tool execution policy
- LLM provider logic
- Durable memory
- Secret storage

### 2. Agent API
This is the orchestrator. It should own the session loop, prompt assembly, context packing, planning, retries, tool-call sequencing, and approval checkpoints. The host/client/server split in MCP leaves room for a dedicated coordination layer, and this is where it belongs. [obot](https://obot.ai/resources/learning-center/mcp-architecture/)

**Owns**
- Session lifecycle
- Conversation state
- Plan state
- Prompt construction
- Risk scoring
- Approval gating
- Final response synthesis

**Does not own**
- Model vendor SDK specifics
- Raw MCP transports
- Long-running code execution

### 3. Model Router
This service abstracts providers so the Agent API calls one internal interface, not five vendor SDKs. Provider-agnostic architectures are easier to benchmark, cheaper to optimize, and less risky strategically. [arxiv](https://arxiv.org/abs/2504.08999)

**Owns**
- Provider adapters
- Model capability registry
- Routing policies, failover, fallback
- Cost accounting and rate limiting
- Prompt/model compatibility transforms

**Does not own**
- Business workflow
- Memory retrieval logic
- Tool policy

### 4. MCP Gateway
The gateway should maintain server registry, schemas, credentials, client sessions, and access rules. MCP deployments often separate the client layer from the host for operational flexibility, which is exactly what this service formalizes. [obot](https://obot.ai/resources/learning-center/mcp-architecture/)

**Owns**
- MCP server registration
- Health checks
- Capability discovery
- Tool schema caching
- Transport abstraction, stdio/HTTP
- Tool ACLs and audit logs
- Request validation

**Does not own**
- User-facing orchestration
- High-level planning
- File rendering

### 5. Memory Service
Use a hybrid memory approach: store structured state, transcripts, and embeddings separately. Production agent memory is often described as episodic, semantic, and stateful rather than as a single vector store. [mindstudio](https://www.mindstudio.ai/blog/ai-agent-hybrid-memory-architecture)

**Owns**
- Session transcripts
- Summaries
- User/workspace/project facts
- Embedding generation pipeline
- Vector retrieval
- Repo metadata snapshots

**Does not own**
- Direct model inference
- MCP tool execution
- UI session rendering

### 6. Sandbox Runner
The sandbox must be the only place where code execution, shell commands, builds, installs, and browser automation happen. Security guidance for MCP environments stresses isolation, least privilege, validation, and private networking for sensitive tool execution. [christian-schneider](https://christian-schneider.net/blog/securing-mcp-defense-first-architecture/)

**Owns**
- Ephemeral execution environments
- Filesystem mounts
- CPU/RAM/time/network quotas
- Command execution
- Test/build output
- Snapshotting and teardown

**Does not own**
- Tool selection
- User auth
- Long-term storage

## API shape

A clean MVP can work with 6 main API surfaces.

### IDE Host <-> Agent API

```http
POST /v1/sessions
POST /v1/sessions/{id}/messages
GET  /v1/sessions/{id}/stream
POST /v1/sessions/{id}/approve
POST /v1/sessions/{id}/cancel
GET  /v1/sessions/{id}/state
```

**Example message payload**
```json
{
  "message": "Refactor auth module and update tests",
  "workspaceId": "ws_123",
  "openFiles": ["src/auth.ts", "tests/auth.test.ts"],
  "selection": {
    "file": "src/auth.ts",
    "startLine": 12,
    "endLine": 88
  },
  "mode": "agent"
}
```

### Agent API <-> Model Router

```http
POST /v1/generate
POST /v1/stream
POST /v1/embeddings
GET  /v1/models
```

**Internal generate contract**
```json
{
  "taskType": "planning|editing|review|completion",
  "modelPolicy": "cheap_first|best_reasoning|privacy_local",
  "messages": [],
  "tools": [],
  "responseFormat": "json_schema",
  "maxTokens": 12000
}
```

### Agent API <-> MCP Gateway

```http
GET  /v1/tools
POST /v1/tools/invoke
GET  /v1/servers
POST /v1/servers/{id}/refresh
GET  /v1/tool-policies
```

**Tool invoke payload**
```json
{
  "sessionId": "sess_123",
  "toolName": "filesystem.read_file",
  "arguments": {
    "path": "src/auth.ts"
  },
  "approvalToken": null
}
```

### Agent API <-> Memory Service

```http
POST /v1/memory/query
POST /v1/memory/write
POST /v1/memory/summarize
GET  /v1/workspaces/{id}/facts
POST /v1/workspaces/{id}/index
```

### Agent API / MCP Gateway <-> Sandbox

```http
POST /v1/runs
GET  /v1/runs/{id}
POST /v1/runs/{id}/cancel
GET  /v1/runs/{id}/logs
POST /v1/runs/{id}/snapshot
```

**Run payload**
```json
{
  "workspaceId": "ws_123",
  "image": "node-python:18-3.12",
  "command": ["bash", "-lc", "npm test"],
  "limits": {
    "cpu": 2,
    "memoryMb": 4096,
    "timeoutSec": 600,
    "network": "restricted"
  }
}
```

### Admin / control plane

```http
POST /v1/workspaces
POST /v1/mcp-servers
POST /v1/secrets
GET  /v1/audit/events
POST /v1/policies
```

## Database choices

For MVP, use **one primary relational database** and add specialized systems only where necessary.

### Primary DB: Postgres
Postgres is the best default because it handles transactional state, JSONB metadata, audit logs, and vector search extensions well enough for early-stage systems. Several memory architecture guides note that Postgres plus JSONB gets you most of the way without needless complexity. [mindstudio](https://www.mindstudio.ai/blog/ai-agent-hybrid-memory-architecture)

Use Postgres for:
- users
- orgs
- workspaces
- sessions
- messages
- plans
- tool calls
- approvals
- audit events
- MCP server registry
- model usage records
- memory facts
- repo indexing metadata

### Vector search: pgvector
Use pgvector first, not a separate vector DB. Vector memory is common in agent systems, but an MVP usually does not need Pinecone/Weaviate unless scale or retrieval complexity forces it. [mem0](https://mem0.ai/blog/what-is-ai-agent-memory)

Store:
- conversation summaries
- repo chunks
- docs chunks
- issue/ticket chunks
- memory facts embeddings

### Redis
Use Redis for:
- short-lived session caches
- stream fan-out
- background job queues
- rate-limit counters
- transient tool locks

### Object storage
Use S3-compatible storage for:
- repo snapshots
- build artifacts
- logs over retention threshold
- patch bundles
- exported transcripts

## Suggested schema

A minimal relational schema could be:

- `users`
- `organizations`
- `workspaces`
- `workspace_members`
- `sessions`
- `session_messages`
- `plans`
- `plan_steps`
- `tool_invocations`
- `tool_outputs`
- `approvals`
- `mcp_servers`
- `mcp_tools`
- `workspace_facts`
- `memory_entries`
- `memory_embeddings`
- `sandbox_runs`
- `sandbox_artifacts`
- `model_requests`
- `audit_events`

A useful memory split is:
- **episodic memory** = session history and tool traces,
- **semantic memory** = summarized facts and embeddings,
- **state memory** = current authoritative workspace state and execution state. [tacnode](https://tacnode.io/post/ai-agent-memory-architecture-explained)

## Recommended MCP set

For the MVP, keep the MCP surface intentionally small:

| Category | Start with | Why |
|---|---|---|
| **Code access** | Filesystem MCP | Required for read/write/search in repo.  [github](https://github.com/punkpeye/awesome-mcp-servers) |
| **Versioning** | Git MCP | Needed for diffs, branch context, and commit-aware reasoning.  [github](https://github.com/punkpeye/awesome-mcp-servers) |
| **Web/docs** | Fetch or HTTP MCP | Lets the model pull docs and API references.  [modelcontextprotocol](https://modelcontextprotocol.io/docs/learn/architecture) |
| **Memory** | Custom memory MCP or internal service bridge | Useful if you want memory exposed uniformly as tools.  [obot](https://obot.ai/resources/learning-center/mcp-architecture/) |
| **Execution** | Internal sandbox bridge, optionally MCP-wrapped later | Better to keep execution tightly controlled first.  [truefoundry](https://www.truefoundry.com/blog/mcp-server-security-best-practices) |
| **Browser** | Optional in phase 2 | Valuable, but not necessary for initial coding workflows.  [firecrawl](https://www.firecrawl.dev/blog/best-mcp-servers-for-cursor) |

## Security baseline

Your MVP should ship with security controls from day one because MCP introduces new trust boundaries and tool attack paths. Security guidance consistently recommends least privilege, schema validation, RBAC, isolated environments, private networking, TLS, logging, and monitoring. [truefoundry](https://www.truefoundry.com/blog/mcp-server-security-best-practices)

Minimum controls:
- Per-tool RBAC.
- JSON schema validation for every tool call. [truefoundry](https://www.truefoundry.com/blog/mcp-server-security-best-practices)
- Human approval for destructive actions, package installs, networked shell, and write operations outside the workspace. [christian-schneider](https://christian-schneider.net/blog/securing-mcp-defense-first-architecture/)
- Sandbox network egress policy: default deny, allowlist where needed. [arxiv](https://arxiv.org/html/2511.20920v1)
- Secrets stored in a secrets manager, never in prompts or logs.
- Full audit trail: prompt hash, selected model, tool calls, outputs, approvals, final patch. [truefoundry](https://www.truefoundry.com/blog/mcp-server-security-best-practices)

## Deployment plan

For a real MVP rollout, I'd deploy it in two planes:

### Control plane
- Auth
- workspace management
- billing
- policy management
- MCP server registry
- admin APIs

### Data plane
- Agent API
- Model Router
- MCP Gateway
- Memory Service
- Sandbox Runner
- Postgres/Redis/Object storage

A good first deployment is:
- **Cloud Run** for Agent API, Model Router, Memory Service, and MCP Gateway if they are mostly stateless. Serverless containers are often a strong fit for MCP infrastructure early on. [cloud.google](https://cloud.google.com/discover/what-is-model-context-protocol)
- **Dedicated VM pool or Kubernetes jobs** for Sandbox Runner because execution workloads are heavier and more stateful. [cloud.google](https://cloud.google.com/discover/what-is-model-context-protocol)
- **Managed Postgres** and **managed Redis** for operational simplicity.

## Build order

I'd build it in this order:

1. **IDE host + Agent API**
2. **Model Router**
3. **Filesystem/Git MCP integration**
4. **Sandbox Runner**
5. **Memory Service with Postgres + pgvector**
6. **Audit/policy layer**
7. **Optional browser/docs/team integrations**

That sequence gets you to a usable Composer quickly while keeping the hardest risk area — execution — behind a controlled boundary early. [modelcontextprotocol](https://modelcontextprotocol.io/docs/learn/architecture)

## Default MVP choices

If I had to pick one concrete stack today, I'd use:

- **Desktop app:** Electron + React + Monaco
- **Backend:** TypeScript + Fastify
- **DB:** Postgres 16 + pgvector
- **Cache/queue:** Redis
- **Sandbox:** Docker runners on isolated worker nodes
- **Infra:** Cloud Run for APIs, managed Postgres, managed Redis, S3-compatible blob storage
- **Observability:** OpenTelemetry + Grafana stack
- **Auth:** OIDC provider + workspace RBAC
- **MCP servers:** filesystem, git, fetch, custom memory bridge

## Agent skills, rules, safety and content moderation
Agent skills are the building blocks of agent capabilities, but they require a rigorous internal verification and approval process by Google teams to ensure quality, security, and compliance. We do not accept direct contributions to the skill repository from external contributors due to the sensitive nature of these components and the need for a high level of technical accuracy and security assurance.

Decentralized location for all skills that would be used by the agent, with a clear specification for how they should be structured and documented. This allows for consistent development and maintenance of skills across different agent teams/orchestrations and products within cloud service providers (CSPs), across different domains and use cases.

```treetable
- skills/
  - csp/
    - gcp/
      - skills/
    - azure/
      - skills/
    - aws/
      - skills/
  - Programming/
    - python/
      - skills/
    - javascript/
      - skills/
    - go/
      - skills/
    - java/
      - skills/
  - DevOps/
    - kubernetes/
      - skills/
    - docker/
      - skills/
    - ci-cd/
      - skills/
  - DataScience/
    - ml/
      - skills/
    - data-analysis/
      - skills/
```

**However, we welcome your feedback and suggestions for improving the skills. If you find any issues, have ideas for new skills, or want to share your remixes, please let us know through the issue tracker. Your input is invaluable in helping us enhance the quality and coverage of these skills for the entire community.**