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

echo [3/4] Flushing Caches (Redis and File System)...
:: 1. Natiivi Windows Redis (ilman 2>nul, jotta näet jos komento puuttuu)
echo   - Flushing Native Redis...
redis-cli flushall
redis-cli save 2>nul

:: 2. WSL Fallback (jos Redis pyöriikin WSL2:n sisällä)
echo   - Flushing WSL Redis (fallback)...
wsl redis-cli flushall 2>nul

:: 3. Docker Fallback (jos Redis on Docker-kontissa, esim. run_local.bat kautta)
echo   - Flushing Docker Redis (quorum-redis-1)...
docker-compose exec redis redis-cli FLUSHALL >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    docker exec quorum-redis-1 redis-cli FLUSHALL 2>nul
)

:: 4. Paikallisten välimuistitiedostojen tuhoaminen
echo   - Clearing local file caches...
if exist "backend_v2\.cache" rmdir /s /q "backend_v2\.cache" 2>nul
if exist "backend_v2\__pycache__" rmdir /s /q "backend_v2\__pycache__" 2>nul

echo [4/4] Done. All backend and frontend services killed, and cache flushed.
echo You can now safely spin up the V3 environment.
echo.
if "%1" NEQ "--no-pause" pause
