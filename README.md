# AI-Empower-Coding-Pilot

Enterprise-grade autonomous AI coding system that transforms requirements into production-ready code.

**83% more productive** with parallel 6-agent orchestration.

## Features

- **AutoGen Multi-Agent Orchestration** — 6 parallel agents (Architect, Coder, Tester, Security, Docs, Reviewer) with GroupChat coordination
- **Auto-Generation Engines** — Project scaffolding, CI/CD pipelines, Docker configs, Terraform IaC
- **LLM Integration** — OpenAI API with intelligent fallback mode
- **JWT Authentication** — Signup, login, role-based access control
- **Compliance Framework** — HIPAA, PCI-DSS, SOC 2, GDPR automated checks
- **Immutable Audit Logging** — SHA-256 hash chain with integrity verification
- **Cost Optimization** — Token budgeting, usage tracking, model recommendations
- **Human Approval Gates** — Pre-deployment, security review, compliance signoff, production release
- **Interactive Dashboard** — React/TypeScript/Tailwind with Recharts data visualization
- **Real-Time Monitoring** — Live agent status with auto-refresh
- **Docker Production Setup** — Multi-stage builds, health checks, resource limits
- **CI/CD Pipeline** — GitHub Actions with lint, test, build, and Docker verification

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│              Frontend (React + Vite + TypeScript + Tailwind)       │
│  Dashboard | Projects | Agents | AutoGen | Compliance | Cost      │
│  Recharts Visualization | JWT Auth | Real-Time Monitoring         │
├──────────────────────────────────────────────────────────────────┤
│                    REST API (FastAPI + Uvicorn)                    │
│  /health  /projects  /agents  /autogen  /compliance  /auth  /llm  │
├──────────┬──────────┬──────────┬──────────┬──────────┬───────────┤
│ Agents   │ AutoGen  │Compliance│ Audit    │ Cost     │ LLM       │
│ (6 roles)│ Engines  │ (4 fwks) │ (SHA-256)│ Tracking │ Client    │
├──────────┴──────────┴──────────┴──────────┴──────────┴───────────┤
│         Orchestration (State Machine + GroupChat + Parallel)       │
│         Approval Gates | RAG Engine | Vector Embeddings           │
└──────────────────────────────────────────────────────────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed diagrams.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional)

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn backend.main:app --reload
```

API at `http://localhost:8000` — Swagger docs at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard at `http://localhost:5173`

### Docker (Production)

```bash
docker compose -f docker-compose.prod.yml up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

## API Endpoints

| Method | Path                          | Description                     |
|--------|-------------------------------|---------------------------------|
| GET    | `/api/health`                 | Health check                    |
| POST   | `/api/auth/signup`            | Register new user               |
| POST   | `/api/auth/login`             | Login and get JWT token         |
| GET    | `/api/auth/me`                | Current user info               |
| GET    | `/api/agents`                 | List all 6 agents               |
| POST   | `/api/projects`               | Create a project                |
| GET    | `/api/projects`               | List projects                   |
| POST   | `/api/projects/{id}/run`      | Run 6-agent pipeline            |
| POST   | `/api/projects/run`           | Ad-hoc pipeline run             |
| GET    | `/api/autogen/capabilities`   | Auto-gen engine capabilities    |
| POST   | `/api/autogen/generate`       | Generate scaffolding/CI/Docker  |
| GET    | `/api/compliance`             | Compliance report (4 frameworks)|
| GET    | `/api/approvals`              | Approval gates status           |
| GET    | `/api/audit/summary`          | Audit log summary               |
| GET    | `/api/cost`                   | Cost and budget report          |
| POST   | `/api/llm/generate`           | Generate content via LLM        |
| GET    | `/api/llm/status`             | LLM provider status             |

Full API documentation: [docs/API.md](docs/API.md)

## Testing

```bash
pytest tests/ -v                          # Run all tests
ruff check backend/ tests/                # Lint
cd frontend && npx tsc --noEmit           # Type check
cd frontend && npm run build              # Build
```

## Project Structure

```
backend/
  agents/          6-agent system (architect, coder, tester, security, docs, reviewer)
  auth/            JWT authentication, user management
  llm/             OpenAI LLM client with fallback
  orchestration/   State machine, GroupChat, parallel execution, approval gates
  autogen/         Auto-generation engines (scaffolding, CI/CD, Docker, Terraform)
  rag/             Vector embeddings, retriever, vector store
  compliance/      HIPAA, PCI-DSS, SOC 2, GDPR checkers
  audit/           Immutable SHA-256 hash chain audit logging
  cost/            Token usage tracking and budget enforcement
  api/             FastAPI routes, schemas, middleware
  models/          Data models
frontend/
  src/components/  React dashboard with Recharts visualization
  src/services/    API client with JWT auth support
  src/hooks/       Custom React hooks
  src/types/       TypeScript interfaces
docs/
  API.md           Full API reference
  ARCHITECTURE.md  System architecture diagrams
  USER_GUIDE.md    Setup and usage guide
docker/            Dockerfiles and nginx config
tests/             Comprehensive test suite
.github/workflows/ CI/CD pipeline (GitHub Actions)
```

## Documentation

- [API Reference](docs/API.md) — Complete endpoint documentation
- [Architecture](docs/ARCHITECTURE.md) — System diagrams and data flow
- [User Guide](docs/USER_GUIDE.md) — Setup, features, and troubleshooting
- [Contributing](CONTRIBUTING.md) — Development guidelines

## Configuration

See `.env.example` for all configuration options. Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(empty)* | OpenAI API key |
| `JWT_SECRET_KEY` | `change-jwt-secret-in-production` | JWT signing secret |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/app.db` | Database URL |
| `MAX_PARALLEL_AGENTS` | `4` | Max concurrent agents |
| `MAX_COST_PER_PROJECT` | `50.00` | Budget cap (USD) |

## License

MIT License. See [LICENSE](LICENSE) for details.
