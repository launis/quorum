@echo off
echo ===================================================
echo   COGNITIVE QUORUM V3 - FORCE KILL SERVICES
echo   Use this if "Port 8000 is already in use" or Flutter hangs
echo ===================================================
echo.

echo [1/4] Killing Python processes (FastAPI Backend / Workers)...
:: Kill only Quorum-related python processes to spare VS Code IDE extensions
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_Process | ? { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'backend_v2|uvicorn|arq' } | Stop-Process -Force -ErrorAction SilentlyContinue"
taskkill /F /IM uvicorn.exe /T 2>nul
taskkill /F /IM arq.exe /T 2>nul

echo [2/4] Killing Dart/Flutter processes (Client App V2)...
taskkill /F /IM dart.exe /T 2>nul
taskkill /F /IM flutter.exe /T 2>nul
taskkill /F /IM client_app.exe /T 2>nul
taskkill /F /IM client_app_v2.exe /T 2>nul

echo [3/4] Flushing Redis Context Cache...
redis-cli flushall 2>nul

echo [4/4] Done. All backend and frontend services killed, and cache flushed.
echo You can now safely spin up the V3 environment.
echo.
pause
