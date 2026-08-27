# Install - bilibili-mcp

> **First time?** Complete [docs/ONBOARDING.md](docs/ONBOARDING.md) before
> expecting live host calls (the anonymous tier needs nothing; the account
> tier needs a +86 login).

## Requirements

- Windows / macOS / Linux
- **uv** (Python 3.11+) - auto-installed by `start.ps1` if missing
- **Node.js** + **Bun** (for the webapp) - auto-installed by `start.ps1`
- A network route to `api.bilibili.com`

## Option A - Recommended (full stack)

```powershell
uv sync
.\start.ps1
```

Opens the webapp at `http://127.0.0.1:11186`. Backend is `http://127.0.0.1:11185`
(REST `/api`, MCP `/mcp`, Swagger `/docs`). Or double-click `start.bat`.

## Option B - Backend only (stdio, MCP over stdio)

```powershell
uv sync
uv run python -m bilibili_mcp.server
```

## Option C - Backend only (HTTP)

```powershell
uv sync
uv run python -m bilibili_mcp.server --mode http --port 11185
```

## Option D - MCPB bundle (Claude Desktop)

```powershell
uv run python scripts/build  # or: just mcpb-pack
```

Register the bundle in Claude Desktop.

## Verify

- `GET http://127.0.0.1:11185/api/health` returns `"status": "ok"`.
- Anonymous tier: `bilibili_explore(operation="trending")` returns items.

## What the start script does

`start.ps1` (naked-PC safe) installs `uv` + `node` via winget if missing,
clears ports 11185/11186, boots the backend, waits for health, resolves Bun,
boots the Vite frontend, opens the browser, and auto-restarts the backend if
it crashes (max 5 restarts).
