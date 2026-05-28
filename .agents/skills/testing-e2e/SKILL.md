---
name: testing-ai-empower-coding-pilot-e2e
description: End-to-end testing of the AI-Empower-Coding-Pilot application. Use when verifying frontend UI, backend API, or pipeline orchestration changes.
---

# Testing AI-Empower-Coding-Pilot E2E

## Prerequisites

- Python 3.11+ with pip
- Node.js 20+ with npm

## Devin Secrets Needed

None required for basic testing. The application uses deterministic hash-based embeddings and in-memory storage, so no external API keys are needed.

If testing with real LLM integration, you would need `OPENAI_API_KEY`.

## Setup

1. Install backend dependencies:
   ```bash
   cd /home/ubuntu/repos/AI-Empower-Coding-Pilot-
   pip install -r requirements.txt
   ```

2. Install frontend dependencies:
   ```bash
   cd frontend && npm install
   ```

3. Start backend server (in background shell):
   ```bash
   cd /home/ubuntu/repos/AI-Empower-Coding-Pilot-
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

4. Start frontend dev server (in separate background shell):
   ```bash
   cd /home/ubuntu/repos/AI-Empower-Coding-Pilot-/frontend
   npm run dev -- --host 0.0.0.0
   ```

5. Verify servers are running:
   ```bash
   curl -s http://localhost:8000/api/health  # Should return {"status":"healthy","version":"2.0.0",...}
   curl -s http://localhost:5173 | head -3   # Should return HTML
   ```

**Important:** If the backend returns old data (e.g., version "1.0.0" instead of "2.0.0"), kill the process on port 8000 (`fuser -k 8000/tcp`) and restart. The backend may cache old bytecode if started before code changes were applied. Always verify `/api/health` version matches expected before proceeding.

## Key Test Flows

The app has 8 pages accessible via the sidebar navigation: Dashboard, Projects, Agents, Auto-Gen, Approvals, Compliance, Audit Log, Cost Tracker.

### 1. Dashboard Health Check
- Navigate to `http://localhost:5173`
- Verify: System Status = "healthy", Version = "2.0.0", Services = "3", Agents = "6"
- Verify: Platform Capabilities banner with badges (AutoGen Multi-Agent, Project Scaffolding, CI/CD Generation, Terraform IaC, Docker Configs, HIPAA/PCI/SOC2/GDPR)
- Verify: "83% more productive" text visible
- Verify: "Run Pipeline" button is disabled when textarea is empty

### 2. Quick Pipeline Run
- Type requirements into the textarea on the Dashboard
- Click "Run Pipeline"
- Expected result card: status "completed" (green), workflow UUID prefix, transitions > 0, duration > 0

### 3. Project CRUD
- Navigate to Projects page via sidebar
- Fill form: name, description, requirements
- Click "Create Project"
- Verify: form clears, project appears in table with "pending" status
- Click "Run Pipeline" on the project row

### 4. Agent Status
- Navigate to Agents page
- Verify: 6 agent cards — architect, coder, tester, security, docs, reviewer
- All should show "idle" status with green dots

### 5. Auto-Generation (v2.0+)
- Navigate to Auto-Gen page via sidebar (under "Automation" section)
- Verify: 4 engine capability cards — scaffolding (fastapi/react/database), cicd (github-actions), docker (python/node), terraform (aws)
- Type a project name (e.g., "my-test-app") in the input field
- Click "Generate All"
- Expected: "Generated Files" section appears with green badge showing total count (27 files)
- Verify 4 sections: Project Scaffolding (13 files), CI/CD Pipelines (3 files), Docker Configs (4 files), Terraform IaC (7 files)

### 6. Approval Gates (v2.0+)
- Navigate to Approvals page via sidebar (under "Automation" section)
- Verify: 4 stat cards — Total=0, Pending=0, Approved=0, Rejected=0
- Verify: "Available Gates" section with 4 gates: Pre Deployment, Security Review, Compliance Signoff, Production Release

### 7. Compliance
- Navigate to Compliance page
- Expected: green dot, "All Compliant", "0 violation(s) across 4 frameworks"
- Four framework cards: HIPAA, PCI-DSS, SOC 2, GDPR — all "Compliant"
- Note: v2.0 added GDPR (previously 3 frameworks, now 4)

### 8. Audit Log
- Navigate to Audit Log page
- Verify: shows total audit entries count (0 initially)
- Verify: integrity status shown (Valid/Broken chain)
- v2.0 added SHA-256 hash chain integrity verification display

### 9. Cost Tracker
- Navigate to Cost Tracker page
- Verify: Total Tokens = 0, Total Cost = $0.0000, Budget Remaining = $50.00
- Budget bar at 0.0%
- Recommendations section visible

### 10. Swagger API Docs
- Navigate to `http://localhost:8000/docs`
- Verify: Swagger UI loads with title "AI-Empower-Coding-Pilot" version 2.0.0
- Endpoint groups: health, projects, agents, compliance, audit, cost, auto-generation, approvals

### 11. Sidebar Navigation
- Verify 3 categorized sections: CORE (Dashboard, Projects, Agents), AUTOMATION (Auto-Gen, Approvals), GOVERNANCE (Compliance, Audit Log, Cost Tracker)
- Active page should have blue-purple gradient highlight
- Bottom shows "v2.0.0 — AutoGen" with green pulse dot

### 12. Recharts Data Visualization (v2.0+)
- **Dashboard Bar Chart:** Navigate to Dashboard, verify "Agent Task Distribution" bar chart renders 6 bars labeled Architect, Coder, Tester, Security, Docs, Reviewer
- **Dashboard Pie Chart:** Verify "Compliance Status" donut chart shows 4 labeled segments: HIPAA, PCI-DSS, SOC 2, GDPR with distinct colors
- **Cost Tracker Area Chart:** Navigate to Cost Tracker, verify "Cost Trend (7-Day)" area chart renders with Mon-Sun x-axis labels and gradient fill
- Recharts renders as SVG — the chart content won't appear in raw HTML fetched via curl. Use browser-based visual inspection.

### 13. JWT Authentication Flow (v2.0+)
Test the full auth lifecycle via curl:
```bash
# Signup — expect 201
curl -s -w "\nHTTP:%{http_code}" -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser1","email":"test1@example.com","password":"SecurePass123!"}'

# Login — expect 200
curl -s -w "\nHTTP:%{http_code}" -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser1","password":"SecurePass123!"}'

# Get current user (use token from login) — expect 200
curl -s -w "\nHTTP:%{http_code}" http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <TOKEN>"

# Duplicate signup — expect 409
curl -s -w "\nHTTP:%{http_code}" -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser1","email":"test1@example.com","password":"SecurePass123!"}'

# Wrong password — expect 401
curl -s -w "\nHTTP:%{http_code}" -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser1","password":"WrongPassword!"}'
```

### 14. LLM Fallback Integration (v2.0+)
Without an `OPENAI_API_KEY`, the LLM uses a keyword-based fallback system:
```bash
# Check LLM status — expect provider="fallback"
curl -s http://localhost:8000/api/llm/status | python3 -m json.tool

# Architect keyword → "Architecture Design" content
curl -s -X POST http://localhost:8000/api/llm/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"design the architecture"}' | python3 -m json.tool

# Test keyword → "Test Plan" content
curl -s -X POST http://localhost:8000/api/llm/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"write tests"}' | python3 -m json.tool

# Default → "Generated Code" content
curl -s -X POST http://localhost:8000/api/llm/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"hello world"}' | python3 -m json.tool
```
All fallback responses have `model="fallback"`, `cached=true`, `latency_ms=1.0`.

### 15. Real-Time Agent Monitoring (v2.0+)
- Navigate to Agents page
- Verify "Auto-Refresh Off" button appears (gray styling)
- Click toggle → should change to "Live" (green styling, starts 5-second polling)
- Click again → back to "Auto-Refresh Off" (gray)

### 16. CSS Animations (v2.0+)
- Verify `animate-slideIn` class on sidebar `<aside>` in `Layout.tsx`
- Verify `animate-fadeIn` class on main content `<div>` in `Layout.tsx`
- Check `tailwind.config.js` defines keyframes: `fadeIn`, `slideUp`, `slideIn`
- Verify compiled CSS in `frontend/dist/assets/*.css` contains these animation classes

## API Endpoints to Verify (curl)

```bash
# Health
curl -s http://localhost:8000/api/health | python3 -m json.tool

# New v2.0 endpoints
curl -s http://localhost:8000/api/autogen/capabilities | python3 -m json.tool
curl -s http://localhost:8000/api/approvals | python3 -m json.tool
curl -s http://localhost:8000/api/cost | python3 -m json.tool
curl -s http://localhost:8000/api/compliance | python3 -m json.tool  # Should include "gdpr" field

# Auth endpoints (v2.0+)
curl -s http://localhost:8000/api/auth/users | python3 -m json.tool
curl -s http://localhost:8000/api/llm/status | python3 -m json.tool
```

## Running Unit Tests

```bash
cd /home/ubuntu/repos/AI-Empower-Coding-Pilot-
pytest tests/ -v  # Should show 65 passing tests (42 original + 23 new v2.0 tests)
```

## Linting

```bash
ruff check backend/ tests/
ruff format --check backend/ tests/
cd frontend && npx tsc --noEmit
```

## Tips

- The backend uses in-memory storage — all data resets on server restart
- Pipeline execution is fast (~0.001s) because agents use rule-based logic, not actual LLM calls
- The frontend uses Vite with HMR, so changes are reflected immediately
- CORS is configured to allow all origins in dev mode
- If the backend server exits immediately, check that port 8000 is not already in use (`fuser -k 8000/tcp` to free port)
- `lsof` may not be available — use `fuser` instead to manage ports
- The `.github/workflows/ci.yml` file might not be in the repo due to OAuth scope limitations — CI may need to be configured manually
- When testing after code changes, always restart the backend to pick up new routes/schemas. Cached bytecode can cause 404s on new endpoints.
- Auto-gen engines produce template content — they don't require actual LLM calls or external services
- Approval gates default to auto_approve=True for demo mode

## Known Dependency Issues

- **bcrypt/passlib incompatibility:** `bcrypt>=5.0` removes the `__about__.__version__` attribute that `passlib` depends on. If auth endpoints crash with `"password cannot be longer than 72 bytes"` or similar errors, check `pip show bcrypt` — if version is 5.x, pin it: `pip install "bcrypt>=4.0.0,<5.0.0"`. The `requirements.txt` should already have this pin (`bcrypt>=4.0.0,<5.0.0`), but if dependencies are reinstalled without the constraint, this issue might resurface.
- **Recharts SVG rendering:** Recharts chart data won't appear in raw HTML fetched via curl/fetch since React renders them client-side as SVG. Always use browser-based visual inspection for chart testing.
- **Auth uses in-memory user store:** User data is lost on backend restart. Each test run starts fresh — there are no pre-existing users. Generate unique usernames per test run to avoid conflicts if the server wasn't restarted between runs.
