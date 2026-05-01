@echo off
:: scripts/get_docker_path.bat
:: Refactored Jan 2026 to centralization Docker path logic.

:: 1. Check if DOCKER_EXE is already set (e.g. system env var)
if defined DOCKER_EXE (
    if exist "%DOCKER_EXE%" (
        goto :eof
    )
)

:: 2. Check if .env file exists and contains DOCKER_EXE
if exist ".env" (
    for /f "usebackq tokens=1* delims==" %%A in (".env") do (
        if /i "%%A"=="DOCKER_EXE" (
            set "DOCKER_EXE=%%B"
        )
    )
)

:: Verify if .env set it correctly
if defined DOCKER_EXE (
    if exist "%DOCKER_EXE%" (
        goto :eof
    )
)

:: 3. Fallback to Default Location
set "DOCKER_EXE=C:\Program Files\Docker\Docker\Docker Desktop.exe"

if not exist "%DOCKER_EXE%" (
    echo [WARNING] Docker Executable not found at default location: %DOCKER_EXE%
    echo           Please set DOCKER_EXE in your .env file or system variables.
)
