# User Guide

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional, for production)

### Installation

```bash
# Clone the repository
git clone https://github.com/AI-Cloud-Tech-Inc/AI-Empower-Coding-Pilot-.git
cd AI-Empower-Coding-Pilot-

# Backend setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Frontend setup
cd frontend
npm install
cd ..
```

### Running the Application

**Backend:**
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
API available at `http://localhost:8000` — Swagger docs at `http://localhost:8000/docs`

**Frontend:**
```bash
cd frontend
npm run dev -- --host 0.0.0.0
```
UI available at `http://localhost:5173`

**Docker (production):**
```bash
docker compose -f docker-compose.prod.yml up --build
```
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

---

## Features Walkthrough

### 1. Dashboard

The main control center displays:
- System health status and version
- LLM provider status (OpenAI or fallback)
- Agent task distribution chart (bar chart)
- Compliance status (pie chart)
- Quick pipeline runner

**Quick Pipeline Run:**
1. Enter project requirements in the text area
2. Click "Run Pipeline"
3. View results: status, transitions, duration, workflow ID

### 2. Projects

Create and manage AI-powered development projects:
1. Fill in project name, description, and requirements
2. Click "Create Project"
3. Click "Run Pipeline" on any project to execute the 6-agent workflow

### 3. Agent Status

Monitor all 6 agents in real-time:
- **Architect** — System design & architecture
- **Coder** — Code generation & implementation
- **Tester** — Test generation & execution
- **Security** — SAST scanning & vulnerability detection
- **Docs** — Auto-documentation generation
- **Reviewer** — Code review & quality checks

Toggle **Auto-Refresh** for live status updates (polls every 5 seconds).

### 4. Auto-Generation

Generate project infrastructure files automatically:
1. Enter a project name
2. Click "Generate All"
3. Outputs: scaffolding (13 files), CI/CD (3 files), Docker (4 files), Terraform (7 files)

### 5. Compliance

View compliance status across 4 enterprise frameworks:
- **HIPAA** — Health data protection
- **PCI-DSS** — Payment card security
- **SOC 2** — Trust service criteria
- **GDPR** — Data privacy regulation

### 6. Approval Gates

Human approval checkpoints for deployment workflows:
- Pre-deployment review
- Security review
- Compliance signoff
- Production release

### 7. Audit Log

Immutable cryptographic audit trail:
- Total entries and event type counts
- SHA-256 hash chain integrity verification
- Tamper detection

### 8. Cost Tracker

Token budgeting and cost optimization:
- Real-time token usage tracking
- Budget progress bar with alert thresholds
- 7-day cost trend chart
- Optimization recommendations

---

## Authentication

### Sign Up

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "email": "admin@example.com", "password": "securepass123"}'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "securepass123"}'
```

### Use Token

```bash
curl -H "Authorization: Bearer <your_token>" http://localhost:8000/api/auth/me
```

---

## LLM Integration

### Configuration

Set your OpenAI API key in `.env`:
```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o
```

Without an API key, the system uses intelligent fallback responses.

### Generate Content

```bash
curl -X POST http://localhost:8000/api/llm/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Design a REST API", "agent_role": "architect"}'
```

### Check LLM Status

```bash
curl http://localhost:8000/api/llm/status
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(empty)* | OpenAI API key for LLM integration |
| `OPENAI_MODEL` | `gpt-4o` | Default LLM model |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/app.db` | Database connection string |
| `JWT_SECRET_KEY` | `change-jwt-secret-in-production` | JWT signing secret |
| `JWT_EXPIRE_MINUTES` | `60` | Token expiry time |
| `API_SECRET_KEY` | `change-me-in-production` | API secret key |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `MAX_COST_PER_PROJECT` | `50.00` | Budget limit per project (USD) |
| `MAX_PARALLEL_AGENTS` | `4` | Maximum concurrent agents |

---

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Linting

```bash
ruff check backend/ tests/
ruff format --check backend/ tests/
```

### Type Checking

```bash
cd frontend && npx tsc --noEmit
```

### Building for Production

```bash
cd frontend && npm run build
```

---

## Troubleshooting

**Backend won't start:**
- Ensure Python 3.11+ is installed
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify `.env` file exists (copy from `.env.example`)

**Frontend won't start:**
- Ensure Node.js 20+ is installed
- Run `npm install` in the `frontend/` directory
- Check that the backend is running if you see API errors

**LLM not responding:**
- Without `OPENAI_API_KEY`, the system uses fallback responses (expected behavior)
- Check API key validity at `GET /api/llm/status`

**Docker build fails:**
- Ensure Docker and Docker Compose are installed
- Check that ports 8000, 3000, and 6379 are not in use
