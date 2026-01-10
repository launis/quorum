@echo off
echo ===================================================
echo   COGNITIVE QUORUM - DEVELOPMENT LAUNCHER
echo ===================================================
echo.

echo [0/2] Starting Infrastructure (Redis)...

:: Check if Docker is running
docker info >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Docker is not running. Starting Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo Waiting for Docker to initialize...
    :wait_docker
    timeout /t 5 /nobreak >nul
    docker info >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 GOTO wait_docker
    echo Docker started.
)

docker-compose up -d redis

echo [1/2] Launching Backend (Uvicorn)...
REM Enable "Hybrid Mode": Mock DB + Real Firebase Auth
set USE_FIREBASE_AUTH=true
start "CQ Backend" cmd /k "set USE_MOCK_DB=true&& set USE_MOCK_LLM=true&& set STORAGE_BACKEND=LOCAL&& uv run uvicorn backend.main:app --reload --port 8000"

echo [1.5/2] Launching Worker (Arq)...
start "CQ Worker (MOCK)" cmd /k "chcp 65001 > nul && set USE_MOCK_DB=true&& set USE_MOCK_LLM=true&& set STORAGE_BACKEND=LOCAL&& uv run python -m backend.run_worker"

echo [2/2] Launching Client (Flutter)...
start "CQ Client" cmd /k "cd client_app && flutter run"

echo.
echo ---------------------------------------------------
echo  STATUS:
echo  - Backend: http://localhost:8000/docs
echo  - Client:  Select device in the new window
echo ---------------------------------------------------
echo.
pause
