# Contributing to AI-Empower-Coding-Pilot

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional, for containerised dev)

### Backend Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run the API server
uvicorn backend.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
pytest tests/ -v

# Lint
ruff check backend/ tests/
ruff format --check backend/ tests/
```

## Project Structure

```
backend/          Python backend (FastAPI)
  agents/         Multi-agent system
  orchestration/  State machine & parallel execution
  rag/            RAG with vector embeddings
  compliance/     HIPAA/PCI/SOC2 tracking
  audit/          Audit logging
  cost/           Cost optimisation
  api/            REST API routes
frontend/         React/TypeScript dashboard
tests/            Test suite
docker/           Docker configuration
```

## Code Style

- Python: Ruff for linting and formatting
- TypeScript: Strict mode, no `any`
- All code must pass CI before merging

## Pull Requests

1. Fork the repo and create a feature branch
2. Write tests for new functionality
3. Ensure all tests pass and lint is clean
4. Open a PR with a clear description
