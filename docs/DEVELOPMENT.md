# Development - bilibili-mcp

## Layout

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
webapp/              React + Vite + TS webapp (frontend 11186)
tests/               pytest suite (respx-mocked HTTP)
```

## Entry points

- `bilibili_mcp.server:main` - CLI (stdio default; `--mode http`).
- `bilibili_mcp.server:app` - ASGI app (uvicorn).
- `run_server.py` - PyInstaller / MCPB entry, `MCP_PORT` / `PORT` switch.

## Running

```powershell
uv sync
just serve         # full stack (backend + webapp + browser)
just test          # pytest
just ci            # ruff + pyright + pytest + tsc + biome
```

## Design notes

- **Direct httpx client, not a third-party wrapper.** Bilibili has no stable
  public REST contract and aggressively rate-limits scrapers. The client is
  deliberately minimal, independent of fragile libraries, and honest about
  failure (-412, -101, -403 map to actionable errors).
- **Anonymous first.** Explore, search, video intel and transcripts work with
  no account. Account-tier tools are gated behind `requires_login` (honest
  state, not fake data).
- **Rate-limit etiquette.** Default page sizes are small and responses are
  TTL-cached (default 10 min). Never hammer an endpoint in a loop.
- **ASCII hygiene.** No em/en dashes anywhere; ASCII hyphens only.

## Onboarding

Onboarding: **YES** - the account tier needs a +86 login. The anonymous tier
needs nothing. See [docs/ONBOARDING.md](ONBOARDING.md). Not N/A because an
online account (Bilibili) exists for the full tier.
