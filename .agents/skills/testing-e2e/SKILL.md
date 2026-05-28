---
name: testing-e2e
description: End-to-end testing of the AI-Empower-Coding-Pilot application. Use when verifying frontend UI, backend API, or pipeline orchestration changes.
---

# E2E Testing Skill — AI-Empower-Coding-Pilot

## Devin Secrets Needed
- None required for basic testing (app uses local SQLite + fallback LLM)
- `OPENAI_API_KEY` — optional, only needed to test real LLM integration (fallback works without it)

## Prerequisites
```bash
cd /home/ubuntu/repos/AI-Empower-Coding-Pilot-
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

## Starting the Backend
```bash
# Default config (rate limit 100/60s):
cd /home/ubuntu/repos/AI-Empower-Coding-Pilot- && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# For rate limiter boundary testing, override env vars:
RATE_LIMIT_REQUESTS=5 RATE_LIMIT_WINDOW_SECONDS=5 python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
```

Verify: `curl -s http://localhost:8000/api/health | python3 -m json.tool`
Expected: `{"status": "healthy", "version": "3.0.0", ...}`

## Starting the Frontend
```bash
cd /home/ubuntu/repos/AI-Empower-Coding-Pilot-/frontend && npm run dev -- --host 0.0.0.0 --port 5173 &
```

## Key Test Areas

### 1. Pipeline Orchestration (9 agents, parallel execution)
```bash
curl -s -X POST http://localhost:8000/api/projects/run \
  -H "Content-Type: application/json" \
  -d '{"requirements": "Build a REST API"}' | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'status: {data[\"status\"]}')
print(f'transitions: {data[\"transitions\"]}')
for key in ['devops_result', 'performance_result', 'accessibility_result']:
    r = data['data'].get(key, {})
    print(f'{key}: success={r.get(\"success\")}')
"
```
**Expected:** `status: completed`, `transitions: 8`, all 3 parallel agent results `success=True`.

**Important:** The pipeline uses `PARALLEL_ANALYSIS` state to run DevOps, Performance, and Accessibility concurrently via `asyncio.gather`. If transitions > 8, agents might be running sequentially (bug). If any of the 3 result keys are missing, the parallel node handler might not be wired correctly.

### 2. JWT Auth Flow
```bash
# Signup
curl -s -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"Test123!"}' | python3 -m json.tool

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test123!"}' | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")

# Profile
curl -s http://localhost:8000/api/auth/me -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Duplicate signup (expect 409)
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"Test123!"}'
```

**Gotcha:** `bcrypt` must be pinned `>=4.0.0,<5.0.0` in requirements.txt. bcrypt 5.x breaks `passlib` with `AttributeError: module 'bcrypt' has no attribute '__about__'`. If auth crashes, check `pip show bcrypt` version.

### 3. Rate Limiter Boundary
Start backend with low limit (`RATE_LIMIT_REQUESTS=5 RATE_LIMIT_WINDOW_SECONDS=5`), then:
```bash
for i in 1 2 3 4 5 6; do
  curl -s -o /dev/null -w "Request $i: HTTP %{http_code}\n" -D - http://localhost:8000/api/health 2>/dev/null | grep -E "(Request|x-ratelimit)"
done
```
**Expected:** Requests 1-5 return 200, request 6 returns 429 with `retry-after: 5`.

**Recovery test:** Wait past the window, then send another request — should return 200 with `remaining` reset. If remaining is lower than expected, rejected requests might be adding timestamps (bug was fixed to record timestamps AFTER the check, not before).

### 4. WebSocket
```bash
# Basic connect + ping (requires websocat or python script)
python3 -c "
import asyncio, websockets, json
async def test():
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        await ws.send(json.dumps({'type': 'ping'}))
        resp = await asyncio.wait_for(ws.recv(), timeout=5)
        print(f'Response: {resp}')
asyncio.run(test())
"
```

**Note:** The `useWebSocket.ts` frontend hook has a cleanup fix (nulling `onclose` before `close()`) to prevent reconnect loops on component unmount. This is a code-level fix that can't be easily E2E tested without Playwright/Jest component tests. Verify via code inspection: line 51 should have `wsRef.current.onclose = null;` before `wsRef.current.close();`.

### 5. Frontend UI (requires browser/recording)
If testing UI changes, start a recording and navigate through:
- Dashboard: v3.0.0 version, 8+ feature badges, LLM fallback status card
- Agents page: 9 agents (Architect, Coder, Tester, Security, Docs, Reviewer, DevOps, Performance, Accessibility)
- Login/Signup page: form renders, submit works
- Profile page: shows username, email, role after login
- Compliance: 4 frameworks (HIPAA, PCI-DSS, SOC 2, GDPR)
- Auto-Gen: 4 engine cards, "Generate All" produces files
- Cost Tracker: area chart with 7-day trend
- Sidebar: 3 sections, 8+ nav items, version label

### 6. LLM Fallback
```bash
curl -s -X POST http://localhost:8000/api/llm/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "design a system", "agent_role": "devops"}' | python3 -m json.tool
```
**Expected:** Returns content with `provider: "fallback"` and DevOps-specific text.

## Lessons Learned
- **bcrypt/passlib incompatibility**: Always pin `bcrypt>=4.0.0,<5.0.0`. bcrypt 5.x breaks passlib.
- **Port cleanup**: Use `fuser -k 8000/tcp` or `kill -9 $(ss -tlnp | grep 8000 | awk '{print $NF}' | grep -oP '\d+')` to free ports. `lsof` might not be installed.
- **Rate limiter env vars**: Pydantic `BaseSettings` reads from env vars automatically. Override with `RATE_LIMIT_REQUESTS=N` before starting uvicorn.
- **Pipeline transition count**: The count reflects edge traversals. With 8 states (INIT→...→COMPLETED), expect 8 transitions. If you see 10, the 3 parallel agents are likely running as separate sequential states.
- **No CI**: `.github/workflows/ci.yml` can't be pushed via the default OAuth token (missing `workflow` scope). This is expected — CI must be pushed manually with a PAT that has the `workflow` scope.
- **Shell testing vs GUI**: Pipeline, auth, rate limiter, and WebSocket tests are all shell-based (curl/python). Only frontend UI verification needs browser recording.
