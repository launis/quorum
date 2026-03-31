@echo off
echo ===================================================
echo   COGNITIVE QUORUM - LOCAL PRODUCTION LAUNCHER
echo   (LOCAL DB: data\db_v2.json)
echo ===================================================
echo.

:: Aggressive cleanup: Kill lingering processes that might hold file locks
echo [Cleaning orphaned processes...]
:: Snipe headless Python workers that lost window headers, preventing database/log file locks
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_Process | ? { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'backend_v2|uvicorn' } | Stop-Process -Force -ErrorAction SilentlyContinue"
taskkill /F /IM uvicorn.exe >nul 2>&1
FOR /F "tokens=5" %%P IN ('netstat -a -n -o ^| findstr :8000 ^| findstr LISTENING') DO taskkill /F /T /PID %%P >nul 2>&1
taskkill /F /T /FI "WINDOWTITLE eq CQ Backend V2*" >nul 2>&1
taskkill /F /T /FI "WINDOWTITLE eq CQ Worker V2*" >nul 2>&1
taskkill /F /T /FI "WINDOWTITLE eq CQ Client*" >nul 2>&1
:: Note: Not killing brute python.exe to avoid killing the user's IDE terminal environments.

:: Clear old logs to ensure clean debug session
if exist backend_debug.log del /F /Q backend_debug.log
if exist backend_v2_debug.log del /F /Q backend_v2_debug.log
if exist client_debug.log del /F /Q client_debug.log
if exist client_app_v2\client_debug.log del /F /Q client_app_v2\client_debug.log
echo [Logs Cleared]

echo [1/3] Starting Infrastructure (Redis)...

:: Check if Docker is running
call scripts\get_docker_path.bat

:: Check if Docker is running
docker info >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Docker is not running. Starting Docker Desktop...
    start "" "%DOCKER_EXE%"
    echo Waiting for Docker to initialize...
    :wait_docker
    timeout /t 5 /nobreak >nul
    docker info >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 GOTO wait_docker
    echo Docker started.
)

:: Check if Redis is already running on port 6379
netstat -an | findstr "6379.*LISTENING" >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo [+] Redis already running on port 6379 - reusing existing instance.
) ELSE (
    docker-compose up -d redis
    echo [Debug] Waiting 2 seconds for Redis startup...
    timeout /t 2 /nobreak >nul
)

:: =========================================================================
:: VÄLIAIKAINEN KORJAUS: REDIS JONON TYHJENNYS
:: Estää aiempien kaatumisten jumiuttamat Arq-haamuajot heräämästä eloon
:: ja tukkimasta Google Vertex AI:n 5 RPM rajoitusta heti käynnistyksessä.
:: =========================================================================
echo [!] Flushing Redis Queues to clear old ghost jobs...
docker-compose exec redis redis-cli FLUSHALL >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    docker exec -it quorum-redis-1 redis-cli FLUSHALL >nul 2>&1
)
echo [!] Redis Queues flushed!

echo [2/3] Launching Backend ^& Worker (Uvicorn + Arq)...
echo       Mode: LOCAL (POOR MAN'S PROD)
echo       Config: MOCK DB (db.json), REAL LLM, FIREBASE AUTH
echo       Notes:  Allows testing real logins ^& real LLM calls without touching Cloud Firestore.

set USE_FIREBASE_AUTH=true

:: Backend
start "CQ Backend V2 (LOCAL)" cmd /k "chcp 65001 > nul && set PYTHONUTF8=1&& set PYTHONIOENCODING=utf-8&& set USE_MOCK_DB=false&& set USE_MOCK_LLM=false&& set STORAGE_BACKEND=LOCAL&& set USE_VERTEX_LLM=true&& set GOOGLE_APPLICATION_CREDENTIALS=%CD%\service-account.json&& set USE_FIREBASE_AUTH=true&& uv run uvicorn backend_v2.main:app --reload --reload-dir backend_v2 --host 0.0.0.0 --port 8000 --log-config backend_v2/uvicorn_logging.yaml"

:: Worker
start "CQ Worker V2 (LOCAL)" cmd /k "chcp 65001 > nul && set PYTHONUTF8=1&& set PYTHONIOENCODING=utf-8&& set USE_MOCK_DB=false&& set USE_MOCK_LLM=false&& set STORAGE_BACKEND=LOCAL&& set USE_VERTEX_LLM=true&& set GOOGLE_APPLICATION_CREDENTIALS=%CD%\service-account.json&& uv run python -m backend_v2.run_worker"

echo [3/3] Launching Client (Flutter)...
if "%USE_JSON_LOGGING%"=="" set USE_JSON_LOGGING=false
start "CQ Client (LOCAL)" cmd /k "cd client_app_v2 && echo [Flutter] Resolving packages silently... && flutter pub get >nul 2>&1 && flutter run -d windows --no-pub --dart-define=USE_JSON_LOGGING=%USE_JSON_LOGGING%"

echo.
echo ---------------------------------------------------
echo  STATUS:
echo  - Backend: http://localhost:8000/docs
echo  - Client:  Select device in the new window
echo ---------------------------------------------------
echo.
pause
