@echo off
echo ===================================================
echo   COGNITIVE QUORUM - DEVELOPMENT LAUNCHER
echo   (MOCK DB: backend/database/db_mock.json)
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
echo       Mode: MOCK (OFFLINE DEV)
echo       Config: MOCK DB (db_mock.json), MOCK LLM, MOCK AUTH
echo       Notes:  No external connections. Good for UI dev and unit testing logic.

:: Backend
start "CQ Backend (MOCK)" cmd /k "set USE_MOCK_DB=true&& set USE_MOCK_LLM=true&& set STORAGE_BACKEND=MOCK&& uv run uvicorn backend.main:app --reload --port 8000"

:: Worker
start "CQ Worker (MOCK)" cmd /k "chcp 65001 > nul && set USE_MOCK_DB=true&& set USE_MOCK_LLM=true&& set STORAGE_BACKEND=MOCK&& uv run python -m backend.run_worker"

echo [3/3] Launching Client (Flutter)...
start "CQ Client (MOCK)" cmd /k "cd client_app && flutter run"

echo.
echo ---------------------------------------------------
echo  STATUS:
echo  - Backend: http://localhost:8000/docs
echo  - Client:  Select device in the new window
echo ---------------------------------------------------
echo.
pause
