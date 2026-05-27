# AI Agents

This document describes the multi-agent system used in AI-Empower-Coding-Pilot.

## Agent Roles

| Agent      | Role        | Description                                        |
|------------|-------------|----------------------------------------------------|
| Architect  | `architect` | Analyses requirements and produces system design   |
| Coder      | `coder`     | Generates production-ready code from architecture  |
| Tester     | `tester`    | Creates and runs test cases                        |
| Security   | `security`  | Scans code for vulnerabilities and compliance      |
| Docs       | `docs`      | Generates project documentation                   |
| Reviewer   | `reviewer`  | Reviews code for quality and best practices        |

## Pipeline Flow

```
Requirements ──> Architect ──> Coder ──> Tester ──> Security ──> Docs ──> Reviewer ──> Done
```

## State Machine

The pipeline is orchestrated via a LangGraph-inspired state machine:

- **INIT** — Parse and validate requirements
- **ARCHITECTURE** — Design system components
- **CODING** — Generate code files
- **TESTING** — Create and evaluate tests
- **SECURITY_SCAN** — Run vulnerability analysis
- **DOCUMENTATION** — Generate docs
- **REVIEW** — Final quality check
- **COMPLETED / FAILED** — Terminal states

## Parallel Execution

Agents that do not depend on each other can run concurrently via the
`ParallelExecutor`. Concurrency is bounded by `MAX_PARALLEL_AGENTS`.

## Extending

To add a new agent:

1. Create a class extending `BaseAgent` in `backend/agents/`
2. Implement the `execute(context)` method
3. Register the agent in `backend/agents/__init__.py`
4. Wire it into the orchestrator's state machine
