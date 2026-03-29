# PROJECT KNOWLEDGE BASE

**Generated:** 2026-03-29
**Mode:** create-new

## OVERVIEW

DeerFlow is a LangGraph-based AI super agent with full-stack architecture. Backend provides lead agent with sandbox execution, persistent memory, subagent delegation, and extensible tools. Frontend is Next.js web interface.

## STRUCTURE

```
deer-flow/
├── backend/                 # FastAPI + LangGraph (port 2024/8001)
│   ├── app/                # Gateway API + channels
│   └── packages/harness/    # Core deerflow package (import: deerflow.*)
├── frontend/               # Next.js 16 (port 3000)
│   └── src/
│       ├── components/    # UI components
│       └── core/         # Business logic (threads, api, skills, etc.)
├── skills/               # Agent skills (public/, custom/)
└── docker/              # Docker + nginx configs
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Backend agent system | `backend/packages/harness/deerflow/agents/` | Lead agent, middlewares, memory |
| Sandbox execution | `backend/packages/harness/deerflow/sandbox/` | Local/Docker isolation |
| Gateway API | `backend/app/gateway/` | FastAPI routers |
| Frontend UI | `frontend/src/components/` | React components |
| Thread management | `frontend/src/core/threads/` | LangGraph SDK integration |
| Skills system | `backend/packages/harness/deerflow/skills/` | Discovery, loading |
| MCP integration | `backend/packages/harness/deerflow/mcp/` | Multi-server MCP |
| Subagent delegation | `backend/packages/harness/deerflow/subagents/` | Background execution |
| IM channels | `backend/app/channels/` | Feishu, Slack, Telegram |

## CONVENTIONS

**Documentation Update Policy**: Update README.md and CLAUDE.md after every code change.

**Harness/App Split**: `packages/harness/deerflow/` is publishable (`deerflow.*` imports). App (`app/*`) imports deerflow, but NEVER reverse. Enforced by `tests/test_harness_boundary.py`.

**TDD (MANDATORY)**: Every feature/bugfix requires unit tests. Run `make test` before/after changes.

**Config Priority**: `config.yaml` in project root is recommended. Supports `$VAR` environment variable resolution.

## ANTI-PATTERNS (THIS PROJECT)

- **NEVER** import `app.*` from `packages/harness/deerflow/` (violates harness/app boundary)
- **NEVER** skip tests when submitting PRs
- **NEVER** use `config.yaml` in backend/ subdirectory (not loaded by default)
- **NEVER** commit without running `make check` (lint + typecheck)

## UNIQUE STYLES

- **DooD Pattern**: Backend container mounts host Docker socket for sandbox provisioning
- **Apple Container**: `make dev` detects `container` command on macOS
- **LangGraph Dev**: Production uses unlicensed `langgraph dev` (TODO: switch when license available)
- **CLI Auth Mounts**: Containers mount `~/.claude` and `~/.codex` for seamless AI tool auth
- **Config Auto-Upgrade**: `scripts/config-upgrade.sh` merges new fields from config.example.yaml

## COMMANDS

```bash
# Root (full app)
make check      # Verify system requirements
make install     # Install all dependencies
make dev         # Start all services (nginx→2026, frontend→3000, gateway→8001, langgraph→2024)
make stop        # Stop all services

# Backend
cd backend && make dev      # LangGraph server only (port 2024)
make gateway                # Gateway API only (port 8001)
make test                   # Run pytest
make lint && make format    # Ruff lint + format

# Frontend
cd frontend && pnpm dev     # Dev server (port 3000)
pnpm check                  # Lint + typecheck
pnpm build                  # Production build
```

## NOTES

- Nginx routes: `/api/langgraph/*` → LangGraph (2024), `/api/*` → Gateway (8001), `/` → Frontend (3000)
- Frontend uses `@t3-oss/env-nextjs` for type-safe env vars in `src/env.js`
- Sandbox modes detected from `config.yaml`: `local`, `aio`, `provisioner`
