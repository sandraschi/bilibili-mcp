# Configuration - bilibili-mcp

Single source of truth: one `.env` file at the repo root (copy `.env.example`
to `.env`). Environment variables always win over the `.env` file.

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `BILIBILI_COOKIE` | (empty) | Optional logged-in +86 SESSDATA cookie. Unlocks account tier + passes search risk control. |
| `BILIBILI_API_BASE` | `https://api.bilibili.com` | Bilibili API root. |
| `BILIBILI_LLM_BASE_URL` | `http://127.0.0.1:11434/v1` | Local LLM (Ollama) for /api/translate and /api/summarize. |
| `BILIBILI_LLM_MODEL` | `qwen2.5:7b` | Local LLM model name. |
| `BILIBILI_CACHE_TTL` | `600` | TTL (seconds) for the JSON response cache. |
| `BILIBILI_BACKEND_PORT` | `11185` | Backend (FastAPI + FastMCP) port. |
| `BILIBILI_FRONTEND_PORT` | `11186` | Frontend (Vite) port. |

## Tiers

| Tier | Trigger | Behavior |
|------|---------|----------|
| Anonymous | no `BILIBILI_COOKIE` | explore, search, video intel, transcript. Account tools return requires_login. |
| Account | `BILIBILI_COOKIE` set | account tier intended; search risk control relaxed. |

## Local data

- `data/cache/bilibili/` - TTL JSON cache of Bilibili responses.
- `data/backend.log` - backend stdout/stderr written by `start.ps1`.

## Local LLM

The `POST /api/translate` and `POST /api/summarize` endpoints use a local LLM
per the Local LLM First doctrine. Default is Ollama at
`http://127.0.0.1:11434/v1`. If no LLM is reachable:

- `translate` falls back to a small built-in glossary.
- `summarize` returns an explicit not-configured error (no fake summary).
