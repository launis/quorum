@echo off
echo ===================================================
echo   COGNITIVE QUORUM - FULL DOCKER LAUNCHER
echo   (Simulated Production Environment)
echo ===================================================
echo.

echo [1/2] Checking Infrastructure...

:: Check if Docker is running
docker info >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Docker is not running. Starting Docker Desktop...
    call scripts\get_docker_path.bat
    start "" "%DOCKER_EXE%"
    echo Waiting for Docker to initialize...
    :wait_docker
    timeout /t 5 /nobreak >nul
    docker info >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 GOTO wait_docker
    echo Docker started.
)

echo [2/2] Launching Full Stack (Docker Compose)...
echo       - Redis:    quorum-redis-1 (6379)
echo       - Backend:  quorum-backend (8000)
echo       - Frontend: quorum-frontend (8080) [Flutter Web]

:: Force recreate to ensure fresh build and env vars
docker-compose up -d --build

echo.
echo ---------------------------------------------------
echo  STATUS:
echo  - Backend:  http://localhost:8000/docs
echo  - Frontend: http://localhost:8080
echo  - Redis:    Running in container
echo.
echo  NOTE: This launches the CONTAINERIZED backend + frontend.
echo        Code changes will NOT apply without rebuild.
echo        Services: Backend (8000), Frontend (8080), Redis (6379).
echo ---------------------------------------------------
echo.
pause
