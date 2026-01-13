@echo off
echo ===================================================
echo   COGNITIVE QUORUM - LOCAL PRODUCTION LAUNCHER
echo   (LOCAL DB: data\db.json)
echo ===================================================
echo.

echo [1/3] Starting Infrastructure (Redis)...

set "DOCKER_EXE=C:\Program Files\Docker\Docker\Docker Desktop.exe"

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

echo [2/3] Launching Backend ^& Worker (Uvicorn + Arq)...
echo       Mode: LOCAL (POOR MAN'S PROD)
echo       Config: MOCK DB (db.json), REAL LLM, FIREBASE AUTH
echo       Notes:  Allows testing real logins ^& real LLM calls without touching Cloud Firestore.

set USE_FIREBASE_AUTH=true

:: Backend
start "CQ Backend (LOCAL)" cmd /k "chcp 65001 > nul && set USE_MOCK_DB=false&& set USE_MOCK_LLM=false&& set STORAGE_BACKEND=LOCAL&& set USE_VERTEX_LLM=true&& set GOOGLE_APPLICATION_CREDENTIALS=%CD%\service-account.json&& set USE_FIREBASE_AUTH=true&& uv run uvicorn backend.main:app --reload --port 8000"

:: Worker
start "CQ Worker (LOCAL)" cmd /k "chcp 65001 > nul && set USE_MOCK_DB=false&& set USE_MOCK_LLM=false&& set STORAGE_BACKEND=LOCAL&& set USE_VERTEX_LLM=true&& set GOOGLE_APPLICATION_CREDENTIALS=%CD%\service-account.json&& uv run python -m backend.run_worker"

echo [3/3] Launching Client (Flutter)...
start "CQ Client (LOCAL)" cmd /k "cd client_app && flutter run"

echo.
echo ---------------------------------------------------
echo  STATUS:
echo  - Backend: http://localhost:8000/docs
echo  - Client:  Select device in the new window
echo ---------------------------------------------------
echo.
pause
