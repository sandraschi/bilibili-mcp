# build-mcpb.ps1 - bilibili-mcp MCPB pack that ships the real 3-4-100 prompts.
#
# The fleet make-mcpb.ps1 stages manifest/src/icon but ALWAYS writes stub
# prompt templates. This wrapper re-stages, then injects the repo's real
# assets/prompts/*, verifies the 3-4-100 rule, and builds the .mcpb.
#
# Usage:  powershell -ExecutionPolicy Bypass -File scripts/build-mcpb.ps1 [-RepoPath <dir>]

param(
    [string]$RepoPath = "."
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path $RepoPath).Path
$name = "bilibili-mcp"
$promptsSrc = Join-Path $repo "assets\prompts"
$promptsDst = Join-Path $repo "mcpb\assets\prompts"

Write-Host "=== build-mcpb.ps1 - $name ===" -ForegroundColor Cyan

# 1. Stage manifest + src + icon + .mcpbignore via the fleet script.
& "D:\Dev\repos\mcp-central-docs\scripts\make-mcpb.ps1" -RepoPath $repo

# 2. Inject the real prompts over the stubs.
New-Item -ItemType Directory -Force -Path $promptsDst | Out-Null
Copy-Item (Join-Path $promptsSrc "system.md") $promptsDst -Force
Copy-Item (Join-Path $promptsSrc "user.md") $promptsDst -Force
Copy-Item (Join-Path $promptsSrc "examples.json") $promptsDst -Force
Write-Host "  Injected real prompts into mcpb/assets/prompts" -ForegroundColor Green

# 3. Verify 3-4-100 (system >= 3000 words, user >= 4000 words, examples >= 100).
function Count-Words($p) {
    $raw = Get-Content $p -Raw
    return ($raw -split '\s+' | Where-Object { $_ -ne '' }).Count
}
function Count-Json($p) {
    try {
        $parsed = Get-Content $p -Raw | ConvertFrom-Json
        return @($parsed).Count
    } catch {
        return 0
    }
}

$sysWc = Count-Words (Join-Path $promptsDst "system.md")
$usrWc = Count-Words (Join-Path $promptsDst "user.md")
$exLen = Count-Json (Join-Path $promptsDst "examples.json")
Write-Host "  system.md: $sysWc words (need >= 3000)"
Write-Host "  user.md:   $usrWc words (need >= 4000)"
Write-Host "  examples.json: $exLen entries (need >= 100)"
if ($sysWc -lt 3000 -or $usrWc -lt 4000 -or $exLen -lt 100) {
    throw "MCPB 3-4-100 gate FAILED - prompts are not complete."
}
Write-Host "  3-4-100 verified" -ForegroundColor Green

# 4. Determine version from pyproject and pack.
$version = if ((Get-Content (Join-Path $repo "pyproject.toml") -Raw) -match '(?m)^version = "(.*)"') { $matches[1] } else { "0.1.0" }
$outFile = Join-Path $repo "dist\$name-v$version.mcpb"
New-Item -ItemType Directory -Force -Path (Join-Path $repo "dist") | Out-Null
Write-Host "  Packing -> $outFile" -ForegroundColor Yellow
$mcpbDir = Join-Path $repo "mcpb"
$packOut = npx.cmd --yes @anthropic-ai/mcpb pack "$mcpbDir" "$outFile" 2>&1 | Out-String
$packOut | Write-Host
if (Test-Path $outFile) {
    $kb = [math]::Round((Get-Item $outFile).Length / 1KB)
    Write-Host "  BUILT: $outFile ($kb KB)" -ForegroundColor Green
} else {
    Write-Host "  mcpb pack command finished - check output above" -ForegroundColor Yellow
}
