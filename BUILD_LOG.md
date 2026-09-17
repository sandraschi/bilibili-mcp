# bilibili-mcp — Native (Tauri NSIS) Build Log

Running record of native installer builds. Newest entries first.

## 2026-09-17 — First Tauri NSIS build

**Context:** bilibili-mcp passed assfix (91/100, commit `0115869`) with the
Tauri frontend scaffolded but `@tauri-apps/api` missing and no `backend-status`
listener wired in. This was the first real attempt to build the NSIS
installer for this repo.

**Phase 1 (pre-flight audit) — fixes applied:**
- `src-tauri/src/backend.rs`: replaced the single `Stop-Process` port-free
  call with the fleet-standard multi-layer kill (image-name kill, port-holder
  kill, 240s poll with re-kill at 5s and UAC-elevated escalation at 15s) and
  added a TCP-connect health poll (30 attempts x 2s) as the authoritative
  backend-ready signal.
- `src-tauri/src/main.rs`: `spawn_backend()` now runs on its own OS thread
  from `setup()` instead of blocking it, so the window doesn't show as
  "(Not Responding)" while the backend starts.
- `src-tauri/capabilities/default.json`: filled an unsubstituted
  `{PRODUCT_NAME}` template placeholder.
- `webapp/src/lib/useZoom.ts` (new): fleet-standard zoom hook
  (Ctrl+Scroll / Ctrl+0 / `localStorage["tauri-zoom"]`) — was missing
  entirely since this is the repo's first Tauri integration. Wired into
  `Layout.tsx` with a visible zoom-% indicator.
- `justfile`: added `build-native` and `cua-nsis-test` recipes (neither
  existed).
- `scripts/cua-smoke.py` (new): copied from
  `mcp-central-docs/templates/tauri-native` (CUA_SMOKE_VERSION 7) — no
  smoke test script existed in this repo.
- `scripts/cua-nsis-config.json` (new): built by reading the actual
  `webapp/src/Layout.tsx` `NAV` array, not guessed. `nav_routes` labels and
  expected page headers match `pageTitle` derivation in `Layout.tsx`
  exactly. `bridge_ok_text` is `"Bilibili MCP"` (the productName, always
  rendered in the sidebar/title), verified present in source before use.

**Phase 2/3 — Build #1:** `just build-native` succeeded cleanly (first-ever
Rust compile for this repo, ~2m22s, no compile errors). Installer produced at
`src-tauri/target/release/bundle/nsis/Bilibili MCP_0.1.0_x64-setup.exe`,
37,719,114 bytes (~35.98 MB) — build gate passed (>= 1 MB).

**Phase 4 — CUA smoke test run #1: FAILED (genuine app bug, not config).**
`Phase 3: Launch app` -> `FATAL: Backend not reachable after 60s`. Diagnosed
via `backend-spawn.log`
(`%LOCALAPPDATA%\...\com.sandraschi.bilibili-mcp\logs\backend-spawn.log`):
the frozen backend exe crashed with
`AttributeError: 'NoneType' object has no attribute 'buffer'` inside
`mcp.run()` -> `stdio_server()`. Root cause: `bilibili-mcp-backend.spec`
built from `src/bilibili_mcp/__main__.py`, which calls `main()` with
`--mode` defaulting to `stdio`. `run_server.py` exists specifically to
translate `PORT`/`MCP_PORT` env vars (which `backend.rs` sets) into
`--mode http`, but the spec never used it — so the packaged backend always
tried stdio transport, which has no stdin buffer under Tauri's windowed
(no-console) subsystem.

**Fix:** `bilibili-mcp-backend.spec` Analysis entry point changed from
`src/bilibili_mcp/__main__.py` to `run_server.py`.

**Build #2 + smoke test #2: PASSED, all 11/11 phases.**
- Kill stale processes — PASS
- Install NSIS (silent `/S`) — PASS
- Launch app, backend healthy — PASS
- Verify window (pywinauto/UIA) — PASS
- Screenshot evidence — PASS
- Feature route (`/api/dashboard`) — PASS
- Diagnostics (`/api/capabilities`) — PASS
- WebView bridge OCR (found "Bilibili MCP") — PASS
- Nav click-through, all 11 sidebar routes (Dashboard, Explore, Search,
  Video, Tools, Skills, Chat, Inbox, Settings, Logs, Help) rendered the
  correct page header per OCR — PASS. Note: the Settings page OCR also
  matched the generic fail-keyword "not found", which is the app's own
  legitimate "Not found" LLM-provider-status badge text
  (`webapp/src/pages/Settings.tsx:116`), not an error. The script does not
  gate the phase result on this per-page keyword check, so it's a
  non-blocking cosmetic false-positive worth knowing about, not a bug.
- Analyze app logs — PASS
- Uninstall (`/S`) — PASS

**Installer (final, verified):**
`D:\Dev\repos\bilibili-mcp\src-tauri\target\release\bundle\nsis\Bilibili MCP_0.1.0_x64-setup.exe`
— 37,723,491 bytes (~35.98 MB).

**Note — gitignore gap found:** `bilibili-mcp-backend.spec` is excluded by
the repo's (fleet-standard) `.gitignore` rule `*.spec`, which is intended
for generated/build-output spec files but also catches this hand-maintained
PyInstaller recipe. The fix above was force-added (`git add -f`) so it
isn't silently lost on a fresh clone. Flagged for a fleet-wide gitignore
audit rather than fixed fleet-wide in this session (out of scope for a
single-repo NSIS build pass).
