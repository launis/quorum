@echo off
echo ===================================================
echo   COGNITIVE QUORUM - LOCAL PRODUCTION LAUNCHER
echo   (LOCAL DB: data\db.json)
echo ===================================================
echo.

:: Clear old logs to ensure clean debug session
if exist backend_debug.log del backend_debug.log
if exist client_debug.log del client_debug.log
echo [Logs Cleared]

echo [1/3] Starting Infrastructure (Redis)...

:: SURGICAL FIX (Smart Root Repair)
echo [0] Verifying Root Identity...
python backend/scripts/ensure_root_identity.py
echo [Fix] Root identity verified.

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

docker-compose up -d redis
echo [Debug] Docker command finished.
echo [Debug] Waiting 2 seconds...
timeout /t 2 /nobreak >nul

echo [2/3] Launching Backend ^& Worker (Uvicorn + Arq)...
echo       Mode: LOCAL (POOR MAN'S PROD)
echo       Config: MOCK DB (db.json), REAL LLM, FIREBASE AUTH
echo       Notes:  Allows testing real logins ^& real LLM calls without touching Cloud Firestore.

set USE_FIREBASE_AUTH=true

:: Backend
start "CQ Backend (LOCAL)" cmd /k "chcp 65001 > nul && set USE_MOCK_DB=false&& set USE_MOCK_LLM=false&& set STORAGE_BACKEND=LOCAL&& set USE_VERTEX_LLM=true&& set GOOGLE_APPLICATION_CREDENTIALS=%CD%\service-account.json&& set USE_FIREBASE_AUTH=true&& uv run uvicorn backend.main:app --reload --reload-dir backend --port 8000 --log-config backend/uvicorn_logging.yaml"

:: Worker
start "CQ Worker (LOCAL)" cmd /k "chcp 65001 > nul && set USE_MOCK_DB=false&& set USE_MOCK_LLM=false&& set STORAGE_BACKEND=LOCAL&& set USE_VERTEX_LLM=true&& set GOOGLE_APPLICATION_CREDENTIALS=%CD%\service-account.json&& uv run python -m backend.run_worker"

echo [3/3] Launching Client (Flutter)...
if "%USE_JSON_LOGGING%"=="" set USE_JSON_LOGGING=false
start "CQ Client (LOCAL)" cmd /k "cd client_app && flutter run -d windows --dart-define=USE_JSON_LOGGING=%USE_JSON_LOGGING%"

echo.
echo ---------------------------------------------------
echo  STATUS:
echo  - Backend: http://localhost:8000/docs
echo  - Client:  Select device in the new window
echo ---------------------------------------------------
echo.
pause
