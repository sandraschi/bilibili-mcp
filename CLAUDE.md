# CLAUDE.md - bilibili-mcp

Quick agent context for this repo.

## Environment

- Windows 11, PowerShell 7. Python via **uv** (never naked `python`).
- Ports: backend **11185** (FastAPI + FastMCP `/mcp` + REST `/api`),
  frontend **11186** (Vite React).
- Python 3.11+; deps managed by `uv sync`.

## Run

```powershell
just serve    # full stack (backend + webapp + browser)
just test     # pytest
just ci       # ruff + pyright + pytest + tsc + biome
just smoke    # stdio tool-registration smoke test
```

## Stack

- Backend: FastMCP 3.4.4 + FastAPI, thin httpx client for Bilibili APIs.
- Webapp: React + Vite + TypeScript + Tailwind (dark) + Zustand + Framer
  Motion + Lucide. Backend proxy `/api` -> 11185.
- Tests: pytest + respx (mocked HTTP).

## Conventions

- Portmanteau tools with `operation: Literal[...]`; `Annotated` + `Field` for
  docs; no `Args:` section.
- Tool returns: `{success, message, error, error_type, suggestions}`.
- Anonymous-first tiering; account tools return `requires_login` honestly.
- No em/en dashes in any file; ASCII hyphens only.

## Don'ts

- Never run naked `python`; use `uv run python`.
- Never commit `.env`, `node_modules/`, `.venv`, `target/`, `*.mcpb`,
  `data/`, `*.bak*`.
- Don't fabricate stats/transcripts from the API.
- Don't hammer Bilibili in a loop - respect rate limits and the TTL cache.
