# Changelog - bilibili-mcp

All notable changes to this project are documented in this file.

## [0.1.0] - 2026-08-27

### Added

- Initial bilibili-mcp scaffold (New Repo Gate, assfix-zero target).
- **Anonymous content-intelligence tier:** `bilibili_explore` (trending /
  rank / hot_search), `bilibili_search` (video / user), `bilibili_video`
  (info / comments / pages), `bilibili_transcript` (subtitle text).
- **Account tier** (honest requires_login until a +86 cookie is set):
  `bilibili_account` (status / following / favorites).
- Thin httpx client for Bilibili public web APIs with honest error mapping
  (-412 risk control, -101 not logged in, -403 denied).
- JSON TTL cache for rate-limit etiquette.
- FastAPI + FastMCP dual transport (backend 11185), REST surface, CORS.
- Local LLM integration (`/api/translate` with glossary fallback,
  `/api/summarize`) - Local LLM First doctrine.
- Prefab UI cards (trending, status, cache).
- React + Vite + TS webapp (frontend 11186) with catch-them-all pages and
  mock-until-onboarded Dashboard.
- Test suite (pytest + respx), ruff + pyright green, 60%+ coverage.
- MCPB packaging: `system.md` (3,810 words), `user.md` (4,357 words),
  `examples.json` (109 entries).
- Full docs stack (ONBOARDING, CONFIGURATION, TOOLS, DEVELOPMENT,
  TROUBLESHOOTING, WRAPPEE), README, INSTALL, llms.txt pair.
