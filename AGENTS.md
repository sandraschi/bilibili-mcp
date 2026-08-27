# bilibili-mcp

MCP server bridging **Bilibili (B站)**, China's largest video platform:
search, trending, video intel, and transcript summarisation. Backend FastMCP
3.4.4 + FastAPI on **11185**, React webapp on **11186**. Anonymous tier
works out of the box (no account); a `BILIBILI_COOKIE` (+86 login) unlocks
the account tier.

## Reading order

1. `docs/ONBOARDING.md` - accounts, the +86 number question, first-run setup
2. `docs/TOOLS.md` - full tool + REST reference
3. `SPEC.md` - feature spec + stage plan
4. `src/bilibili_mcp/` - source map below

## Directory map

```
src/bilibili_mcp/
├── server.py        FastMCP + FastAPI app, REST routes, dual transport entry
├── server_state.py  shared FastMCP instance
├── config.py        env config (one .env source of truth)
├── client.py        thin httpx client for Bilibili public web APIs
├── cache.py         JSON TTL cache (data/cache)
├── errors.py        shared error_response() + requires_login() + annotations
├── helpers.py       bvid/aid parsing + slim video/comment shaping
├── llm.py           local LLM (translate + summarize) with glossary fallback
├── skills/          bilibili-expert SKILL.md
└── tools/           portmanteaus: explore, search, video, transcript, account,
                     prefab, help_tool, shutdown_tool
```

## Entry points

- `bilibili_mcp.server:main` - CLI (stdio default; `--mode http`).
- `bilibili_mcp.server:app` - ASGI app (uvicorn).
- `run_server.py` - PyInstaller / MCPB entry, `MCP_PORT` / `PORT` switch.

## Key rules

- Portmanteau tools with operation enums; Annotated + Field docs, no Args.
- Anonymous-first: explore/search/video/transcript need no account. Account
  tools return honest `requires_login` - never fake data.
- Never fabricate: stats, views and transcripts come only from the API; if
  subtitles are unavailable or login-gated, say so.
- Rate-limit etiquette: Bilibili blocks scrapers (-412). Small page sizes,
  TTL cache, never hammer in a loop.
- `uv run python` only; PowerShell 7; ASCII in scripts (no em dashes).
- MCPB pack script wipes+recopies mcpb/src; prompts verified 3-4-100.
- Git operations via gitops/git, never fileops.

## Gate commands

```powershell
just ci          # ruff + pyright + pytest (cov>=60) + tsc + biome
just mcpb-pack   # fresh-stage bundle
just smoke       # stdio tool-registration smoke test
```

## Next (reading order)

1. `src/bilibili_mcp/client.py` - the API truth (what works anonymously)
2. `docs/TOOLS.md` - full tool + REST reference
3. `docs/CONFIGURATION.md` - env vars + tiers
