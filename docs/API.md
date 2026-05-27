# API Reference

AI-Empower-Coding-Pilot REST API — powered by FastAPI with interactive Swagger docs at `/docs`.

**Base URL:** `http://localhost:8000/api`

---

## Health

### `GET /api/health`
Returns system health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "services": {
    "api": "running",
    "orchestrator": "ready",
    "vector_store": "ready"
  }
}
```

### `GET /api/readiness`
Kubernetes-style readiness probe.

---

## Authentication

### `POST /api/auth/signup`
Register a new user.

**Request:**
```json
{
  "username": "john",
  "email": "john@example.com",
  "password": "securepass123",
  "role": "developer"
}
```

**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiI...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "username": "john",
    "email": "john@example.com",
    "role": "developer",
    "is_active": true
  }
}
```

### `POST /api/auth/login`
Authenticate and receive a JWT token.

**Request:**
```json
{
  "username": "john",
  "password": "securepass123"
}
```

### `GET /api/auth/me`
Get current authenticated user info. Requires `Authorization: Bearer <token>` header.

### `GET /api/auth/users`
List all registered users.

---

## Projects

### `GET /api/projects`
List all projects.

### `POST /api/projects`
Create a new project.

**Request:**
```json
{
  "name": "my-api",
  "description": "REST API service",
  "requirements": "Build a user management API with CRUD operations"
}
```

### `POST /api/projects/{project_id}/run`
Execute the full 6-agent pipeline on a project.

### `POST /api/projects/run`
Ad-hoc pipeline run with inline requirements.

**Request:**
```json
{
  "requirements": "Build a REST API with authentication"
}
```

**Response:**
```json
{
  "workflow_id": "uuid",
  "status": "completed",
  "data": {},
  "errors": [],
  "transitions": 7,
  "duration_s": 0.023
}
```

---

## Agents

### `GET /api/agents`
List all 6 agents and their current status.

**Response:**
```json
[
  { "role": "architect", "agent_id": "uuid", "status": "idle" },
  { "role": "coder", "agent_id": "uuid", "status": "idle" },
  { "role": "tester", "agent_id": "uuid", "status": "idle" },
  { "role": "security", "agent_id": "uuid", "status": "idle" },
  { "role": "docs", "agent_id": "uuid", "status": "idle" },
  { "role": "reviewer", "agent_id": "uuid", "status": "idle" }
]
```

---

## Auto-Generation

### `GET /api/autogen/capabilities`
List available auto-generation engines and their supported templates.

### `POST /api/autogen/generate`
Generate scaffolding, CI/CD, Docker, and Terraform files.

**Request:**
```json
{
  "architecture": {
    "components": [
      { "name": "api", "type": "service", "description": "REST API" }
    ],
    "tech_stack": {
      "frameworks": ["FastAPI"],
      "databases": ["PostgreSQL"],
      "languages": ["Python"]
    }
  },
  "project_name": "my-project"
}
```

**Response:**
```json
{
  "scaffolding": { "files": ["..."], "count": 13 },
  "cicd": { "files": ["..."], "count": 3 },
  "docker": { "files": ["..."], "count": 4 },
  "terraform": { "files": ["..."], "count": 7 },
  "total_files_generated": 27
}
```

---

## Compliance

### `GET /api/compliance`
Get compliance status across all 4 frameworks (HIPAA, PCI-DSS, SOC 2, GDPR).

---

## Approvals

### `GET /api/approvals`
Get human approval gate status and pending requests.

### `POST /api/approvals/request`
Submit an approval request for a checkpoint.

### `POST /api/approvals/action`
Approve or reject a pending request.

---

## Audit

### `GET /api/audit/summary`
Get audit log summary with event counts and integrity verification.

---

## Cost

### `GET /api/cost`
Get cost report with token usage, budget status, and recommendations.

### `POST /api/cost/record?tokens=100&model=gpt-4o`
Record token usage for cost tracking.

---

## LLM

### `POST /api/llm/generate`
Generate content using the configured LLM (OpenAI or fallback).

**Request:**
```json
{
  "prompt": "Design a REST API for user management",
  "agent_role": "architect",
  "system_prompt": "You are an expert software architect."
}
```

**Response:**
```json
{
  "content": "## Architecture Design\n...",
  "model": "gpt-4o",
  "tokens_used": 450,
  "latency_ms": 1200.5,
  "cached": false
}
```

### `GET /api/llm/status`
Get LLM provider status and configuration.

---

## Error Responses

All endpoints return standard HTTP error codes:

| Code | Description |
|------|-------------|
| 400  | Bad Request — invalid input |
| 401  | Unauthorized — invalid or missing token |
| 404  | Not Found |
| 409  | Conflict — duplicate resource |
| 422  | Validation Error — request body validation failed |
| 500  | Internal Server Error |

Error response format:
```json
{
  "detail": "Error description"
}
```
