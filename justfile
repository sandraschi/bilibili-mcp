set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

# Bun lives in the user profile; PS 5.1 PATH may not include it after login
_bunpath := "$env:PATH = \"$env:USERPROFILE\\.bun\\bin;$env:PATH\""

default:
    @just --list

# One-time dev bootstrap: deps + pre-commit hook + webapp install
bootstrap:
    uv sync
    uv run pre-commit install
    {{_bunpath}}; cd webapp; bun install

# Start the full stack (backend + webapp) with the fleet start script
serve:
    ./start.ps1

# Run pytest suite
test:
    uv run pytest -q

# Ruff lint + format check
lint:
    uv run ruff check src/ tests/
    uv run ruff format src/ tests/ --check

# Auto-fix lint issues
fmt:
    uv run ruff check src/ tests/ --fix
    uv run ruff format src/ tests/

# Pyright typecheck
types:
    uv run pyright src/

# Webapp: TypeScript typecheck
tsc:
    {{_bunpath}}; cd webapp; bun run tsc --noEmit

# Webapp: Biome check
biome:
    {{_bunpath}}; cd webapp; bunx biome check src/

# Playwright e2e (starts its own backend)
e2e:
    {{_bunpath}}; cd webapp; bunx playwright test

# Local CI gate: lint + types + tests + tsc + biome
ci:
    uv run ruff check src/ tests/
    uv run ruff format src/ tests/ --check
    uv run pyright src/
    uv run pytest -q
    {{_bunpath}}; cd webapp; bun run tsc --noEmit
    {{_bunpath}}; cd webapp; bunx biome check src/

# Alias: all gates green (same as ci)
gates-green:
    just ci

# Bundle for Claude Desktop (MCPB) - stages + injects real 3-4-100 prompts + packs
mcpb-pack:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\build-mcpb.ps1" -RepoPath "."

# Build the wheel
build:
    uv build

# Quick stdio smoke test of the MCP server
smoke:
    uv run python -c "import asyncio; from bilibili_mcp.server_state import mcp; import bilibili_mcp.tools; print('tools:', len(asyncio.run(mcp.list_tools())))"

# Build the Tauri NSIS installer (frontend + PyInstaller backend + bundle)
build-native:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "src-tauri\build.ps1"

# CUA smoke test against the built NSIS installer (install -> launch -> nav -> uninstall)
cua-nsis-test:
    uv run python scripts/cua-smoke.py --config scripts/cua-nsis-config.json

# One command: pre-flight checks -> build -> genuine CUA verification.
tauri: tauri-preflight build-native cua-nsis-test

# Fails fast if pywinauto/pyinstaller aren't real project deps (both caused
# silent false passes fleet-wide on 2026-09-17 -- see mcp-central-docs
# HANDOVER.md). Seconds, not a multi-minute Rust compile, to catch it.
tauri-preflight:
    @echo "== Tauri pre-flight checks =="
    uv run python -c "import pywinauto"; if ($LASTEXITCODE -ne 0) { Write-Error "FATAL: pywinauto not importable -- run: uv add --dev pywinauto pillow pytesseract"; exit 1 }
    if (-not (Test-Path '.venv\Scripts\pyinstaller.exe')) { Write-Error "FATAL: pyinstaller missing from project venv -- run: uv add --dev pyinstaller pefile altgraph"; exit 1 }
    $gi = Get-Content .gitignore -Raw -ErrorAction SilentlyContinue; if ($gi -notmatch 'resources.*\.exe') { Write-Warning "gitignore may not cover resources/*.exe" }; if ($gi -notmatch 'cua-reports') { Write-Warning "gitignore may not cover cua-reports/" }
    @echo "== Pre-flight OK =="
