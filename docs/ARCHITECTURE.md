# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Frontend (React + Vite)                        │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┬────────────┐  │
│  │Dashboard │ Projects │ Agents   │ AutoGen  │Compliance│ Cost/Audit │  │
│  │(Charts)  │          │(Live)    │          │          │ (Charts)   │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┴────────────┘  │
│  Recharts | Tailwind CSS | TypeScript | JWT Auth Client                  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ REST API (JSON)
                                 │
┌────────────────────────────────┴────────────────────────────────────────┐
│                        Backend (FastAPI + Uvicorn)                       │
│                                                                         │
│  ┌─── API Layer ──────────────────────────────────────────────────────┐  │
│  │  /health  /projects  /agents  /autogen  /compliance                │  │
│  │  /audit   /cost      /approvals  /auth  /llm                      │  │
│  │  JWT Authentication  |  CORS  |  Request Tracking Middleware       │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─── Core Services ─────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────────┐ │  │
│  │  │ LLM Client  │  │ Auth Module  │  │ AutoGen Engines           │ │  │
│  │  │ OpenAI +    │  │ JWT + Bcrypt │  │ Scaffolding | CI/CD       │ │  │
│  │  │ Fallback    │  │ User Store   │  │ Docker | Terraform        │ │  │
│  │  └─────────────┘  └──────────────┘  └───────────────────────────┘ │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─── Orchestration ─────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  State Machine (LangGraph-inspired)                               │  │
│  │  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐│  │
│  │  │Archi-│──>│Coder │──>│Tester│──>│Secur-│──>│ Docs │──>│Review││  │
│  │  │tect  │   │      │   │      │   │ ity  │   │      │   │  er  ││  │
│  │  └──────┘   └──────┘   └──────┘   └──────┘   └──────┘   └──────┘│  │
│  │                                                                    │  │
│  │  GroupChat Orchestrator | Parallel Executor | Approval Gates       │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─── Cross-Cutting ─────────────────────────────────────────────────┐  │
│  │  Compliance (HIPAA/PCI/SOC2/GDPR) | Audit Logger (SHA-256 chain) │  │
│  │  Cost Optimizer (Token budgeting) | RAG Engine (Vector embeddings)│  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │     Infrastructure      │
                    │  Docker | Redis | SQLite │
                    │  Nginx (prod frontend)  │
                    └─────────────────────────┘
```

## Agent Pipeline

The 6-agent pipeline processes requirements through sequential and parallel stages:

```
Stage 1 (Sequential):
  Architect  ──  Analyzes requirements, produces system design

Stage 2 (Sequential):
  Coder      ──  Generates production code from architecture

Stage 3 (Parallel):
  Tester     ──┬──  Creates test plans and test code
  Security   ──┘──  Runs SAST scans, checks vulnerabilities

Stage 4 (Parallel):
  Docs       ──┬──  Generates documentation
  Reviewer   ──┘──  Reviews code quality and best practices
```

## Data Flow

```
User Request
    │
    ▼
┌─────────────────┐
│  API Gateway     │──── JWT Validation
│  (FastAPI)       │──── Rate Limiting
└────────┬────────┘──── Request Tracking
         │
         ▼
┌─────────────────┐
│  Orchestrator    │──── State Machine transitions
│                  │──── GroupChat message routing
└────────┬────────┘──── Parallel execution scheduling
         │
    ┌────┼────┐
    ▼    ▼    ▼
  Agent Agent Agent ──── LLM Client (OpenAI / fallback)
    │    │    │
    └────┼────┘
         │
         ▼
┌─────────────────┐
│  Post-Processing │
│  - Audit Log     │──── SHA-256 hash chain
│  - Cost Track    │──── Token usage recording
│  - Compliance    │──── Framework checks
└────────┬────────┘
         │
         ▼
    API Response
```

## Security Model

```
┌──────────────────────────────────────┐
│           Security Layers            │
├──────────────────────────────────────┤
│  1. JWT Authentication               │
│     - HS256 token signing            │
│     - Configurable expiry            │
│     - Role-based claims              │
│                                      │
│  2. Password Security                │
│     - Bcrypt hashing                 │
│     - Salt per password              │
│                                      │
│  3. API Security                     │
│     - CORS configuration             │
│     - Input validation (Pydantic)    │
│     - Request tracking               │
│                                      │
│  4. Compliance Frameworks            │
│     - HIPAA health data protection   │
│     - PCI-DSS payment card security  │
│     - SOC 2 trust services           │
│     - GDPR data privacy              │
│                                      │
│  5. Audit Trail                      │
│     - Immutable SHA-256 hash chain   │
│     - Integrity verification         │
│     - Event-level logging            │
└──────────────────────────────────────┘
```

## Technology Stack

| Layer        | Technology                    | Purpose                          |
|-------------|-------------------------------|----------------------------------|
| Frontend    | React 18 + TypeScript         | UI framework                     |
| Styling     | Tailwind CSS 3                | Utility-first CSS                |
| Charts      | Recharts                      | Data visualization               |
| Build       | Vite 5                        | Frontend bundler                 |
| Backend     | FastAPI + Uvicorn             | REST API server                  |
| Auth        | python-jose + passlib         | JWT tokens + password hashing    |
| LLM         | OpenAI API / httpx            | AI code generation               |
| Validation  | Pydantic v2                   | Request/response schemas         |
| Database    | SQLAlchemy + aiosqlite        | Async ORM + SQLite               |
| Cache       | Redis 7                       | Session and query caching        |
| Vector DB   | ChromaDB                      | RAG embeddings storage           |
| Container   | Docker + docker-compose       | Containerization                 |
| CI/CD       | GitHub Actions                | Automated testing and builds     |
| IaC         | Terraform (auto-generated)    | Infrastructure provisioning      |
| Lint        | Ruff                          | Python linting and formatting    |
| Test        | pytest                        | Python test framework            |
