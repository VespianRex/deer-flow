# AGENTS.md

**Generated:** 2026-03-29
**Package:** deerflow-harness

## OVERVIEW

Core publishable agent framework. Import: `deerflow.*`. Contains orchestration, tools, sandbox, models, MCP, skills, config.

## STRUCTURE

```
deerflow/
├── agents/lead_agent/     # Main agent factory
├── agents/middlewares/    # 12 middleware components
├── agents/memory/         # Memory extraction, queue
├── sandbox/               # Sandbox execution (Local/Docker)
├── subagents/            # Subagent delegation
├── tools/builtins/        # Built-in tools
├── mcp/                  # MCP integration
├── models/               # Model factory
├── skills/               # Skills system
└── client.py             # Embedded DeerFlowClient
```

## KEY CONCEPTS

**Lead Agent**: `make_lead_agent(config)` from `langgraph.json`. Dynamic model via `create_chat_model()`.

**Middleware Chain** (12 total):
1. ThreadData → 2. Uploads → 3. Sandbox → 4. DanglingToolCall → 5. Guardrail → 6. Summarization → 7. TodoList → 8. Title → 9. Memory → 10. ViewImage → 11. SubagentLimit → 12. Clarification

**ThreadState**: Extends `AgentState` with `sandbox`, `thread_data`, `title`, `artifacts`, `todos`, `uploaded_files`, `viewed_images`.

## CONVENTIONS

```python
from deerflow.agents import make_lead_agent
from deerflow.models import create_chat_model
from deerflow.config import get_app_config
```

**NEVER import from `app.*`** (enforced by test_harness_boundary.py)

## SANDBOX

Virtual paths: Agent `/mnt/user-data/{workspace,uploads,outputs}`, `/mnt/skills` → Physical `backend/.deer-flow/threads/{thread_id}/user-data/...`

Tools: `bash`, `ls`, `read_file`, `write_file`, `str_replace`

## SUBAGENTS

- Built-in: `general-purpose`, `bash`
- `MAX_CONCURRENT_SUBAGENTS = 3`, 15-min timeout
- Dual thread pool: `_scheduler_pool` (3) + `_execution_pool` (3)

## NOTES

- MCP: `MultiServerMCPClient` with lazy loading + mtime invalidation
- Skills: directory with `SKILL.md` (YAML frontmatter)
- Memory: `backend/.deer-flow/memory.json`
