@echo off
REM bilibili-mcp double-click launcher (delegates to start.ps1)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" %*
if errorlevel 1 (
  echo.
  echo [bilibili-mcp start.bat] exited with error
  pause
  exit /b 1
)
