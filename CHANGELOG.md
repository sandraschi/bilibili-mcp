# Changelog - bilibili-mcp

All notable changes to this project are documented in this file.

## [Unreleased] - 2026-09-17

### Fixed (assfix — Tauri drift)

- Added `@tauri-apps/api` dependency to `webapp/package.json` (was missing despite
  `src-tauri/` existing).
- Added Tauri `backend-status` `listen()` event subscription in `Layout.tsx`, with
  HTTP polling kept as the non-Tauri fallback.

## [0.1.0] - 2026-08-27

### Added (initial scaffold)

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

### Added (assfix - fleet-standard conformance)

- `GET /api/llm/discover` + `GET /api/llm/providers` - local LLM auto-detect.
- `POST /api/chat` - chat completion via local LLM (honest 503 when none).
- Chat page rewritten to fleet standard: skill-first, 4+ personalities,
  6 example prompts, localStorage history (100 cap), export/clear, empty state.
- Settings page LLM provider/model selector dropdowns
  (`llm-provider-select` / `llm-model-select`).
- Session-context injection: `.claude-plugin/hooks/hooks.json`, `.cursorrules`
  `## Session Context`, `.windsurfrules`, `.github/copilot-instructions.md`,
  `.opencode/skills/`.
- `.gitattributes` (eol=lf) fixing CRLF Biome failures on Windows CI.
- Biome pre-commit hook (`scripts/pre-commit-biome.ps1`) + materialised hook.
- `renovate.json`, `just gates-green`, `biome:ci` script.
- Font/contrast and data-testid fixes across webapp pages.
- Playwright webServer now serves backend + frontend; 3 e2e tests green.
- Fleet registration: ports 11185/11186, starts launcher + README row,
  fleet manifest + registry + FLEET_INDEX entries.
