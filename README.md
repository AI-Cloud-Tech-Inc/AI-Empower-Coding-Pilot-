# AI-Empower-Coding-Pilot

Enterprise-grade autonomous AI coding system that transforms requirements into production-ready code.

## Features

- **Multi-Agent Orchestration** — Architect, Coder, Tester, Security, Docs, and Reviewer agents working in concert
- **LangGraph State Machines** — Directed-graph workflow engine with conditional transitions
- **RAG with Vector Embeddings** — Retrieval-Augmented Generation for context-aware code understanding
- **Parallel Execution** — Bounded-concurrency engine for running agents simultaneously
- **Compliance Tracking** — HIPAA, PCI-DSS, and SOC 2 automated checks
- **Audit Logging** — Structured, append-only audit trail for every action
- **Cost Optimization** — Token usage tracking, budget enforcement, and model recommendations
- **REST API** — Full FastAPI backend with interactive Swagger docs
- **Dashboard UI** — React/TypeScript/Tailwind frontend for managing projects and monitoring agents

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
├─────────────────────────────────────────────────────────┤
│                    REST API (FastAPI)                     │
├──────────┬──────────┬──────────┬──────────┬──────────────┤
│ Agents   │ RAG      │Compliance│ Audit    │ Cost         │
│ System   │ Engine   │ Tracker  │ Logger   │ Optimizer    │
├──────────┴──────────┴──────────┴──────────┴──────────────┤
│              Orchestration (State Machine)                │
│              Parallel Execution Engine                    │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional)

### Backend

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Run the server
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000` with Swagger docs at `/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

### Docker

```bash
docker-compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

## API Endpoints

| Method | Path                          | Description                |
|--------|-------------------------------|----------------------------|
| GET    | `/api/health`                 | Health check               |
| GET    | `/api/agents`                 | List all agents            |
| POST   | `/api/projects`               | Create a project           |
| GET    | `/api/projects`               | List projects              |
| POST   | `/api/projects/{id}/run`      | Run pipeline for a project |
| POST   | `/api/projects/run`           | Ad-hoc pipeline run        |
| GET    | `/api/compliance`             | Compliance report          |
| GET    | `/api/audit/summary`          | Audit log summary          |
| GET    | `/api/audit/entries`          | Query audit entries        |

## Testing

```bash
# Run all tests
pytest tests/ -v

# Lint
ruff check backend/ tests/
ruff format --check backend/ tests/
```

## Project Structure

```
backend/
  agents/          Multi-agent system (architect, coder, tester, security, docs, reviewer)
  orchestration/   LangGraph state machine, parallel execution, orchestrator
  rag/             Vector embeddings, retriever, vector store
  compliance/      HIPAA, PCI-DSS, SOC 2 checkers
  audit/           Structured audit logging
  cost/            Token usage tracking and budget enforcement
  api/             FastAPI routes, schemas, middleware
  models/          Data models (project, task, audit log)
frontend/
  src/components/  React dashboard components
  src/services/    API client
  src/hooks/       Custom React hooks
tests/             Comprehensive test suite
docker/            Docker configurations
```

## Configuration

All configuration is via environment variables (see `.env.example`):

- `OPENAI_API_KEY` — LLM provider key
- `DATABASE_URL` — Database connection string
- `REDIS_URL` — Redis cache URL
- `COMPLIANCE_ENABLED` — Toggle compliance checks
- `MAX_PARALLEL_AGENTS` — Concurrency limit for agents
- `MAX_COST_PER_PROJECT` — Budget cap per project

## License

MIT License. See [LICENSE](LICENSE) for details.
