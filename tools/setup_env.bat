@echo off
echo ============================================================
echo  COMPLEX QUORUM - ENVIRONMENT SETUP & UPDATE
echo ============================================================

echo [INFO] Syncing environment with uv (Python 3.14+)...
call uv sync

IF ERRORLEVEL 1 (
    echo.
    echo [ERROR] uv sync failed. Please check errors above.
    echo Ensure 'uv' is installed and valid.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  [SUCCESS] Environment is ready!
echo  You can now run: run_locally.bat
echo ============================================================
pause
