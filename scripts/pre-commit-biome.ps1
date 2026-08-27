# Fleet: mcp-central-docs/templates/pre-commit-biome.ps1 (bun variant)
# Runs the webapp Biome gate on every pre-commit. Detects webapp/, ensures
# node_modules, then runs `bun run biome:ci` (the same gate CI executes).

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

$webRoot = $null
foreach ($candidate in @("webapp", "web_sota", "web-sota", "webapp/frontend", "web")) {
    $path = Join-Path $repoRoot $candidate
    if (Test-Path (Join-Path $path "package.json")) {
        $webRoot = $path
        break
    }
}

if (-not $webRoot) {
    exit 0
}

# Resolve bun to a real exe (PS 5.1 cannot Start/& a bare shim command name).
$bun = $null
$cmd = Get-Command bun.exe -ErrorAction SilentlyContinue
if ($cmd) { $bun = $cmd.Source }
if (-not $bun) {
    $userBun = Join-Path $env:USERPROFILE ".bun\bin\bun.exe"
    if (Test-Path $userBun) { $bun = $userBun }
}
if (-not $bun) {
    Write-Host "[pre-commit-biome] bun not found - skipping biome gate" -ForegroundColor Yellow
    exit 0
}

Push-Location $webRoot
try {
    if (-not (Test-Path "node_modules")) {
        & $bun install
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    & $bun run biome:ci
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
