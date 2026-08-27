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

# Bundle for Claude Desktop (MCPB) - stages + injects real 3-4-100 prompts + packs
mcpb-pack:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\build-mcpb.ps1" -RepoPath "."

# Build the wheel
build:
    uv build

# Quick stdio smoke test of the MCP server
smoke:
    uv run python -c "import asyncio; from bilibili_mcp.server_state import mcp; import bilibili_mcp.tools; print('tools:', len(asyncio.run(mcp.list_tools())))"
