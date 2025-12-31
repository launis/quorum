@echo off
echo ============================================================
echo  COMPLEX QUORUM - ENVIRONMENT SETUP & UPDATE
echo ============================================================

REM Check if .venv314 exists
IF EXIST ".venv314" (
    echo [INFO] Virtual environment (.venv314) found. Checking for updates...
) ELSE (
    echo [INFO] Creating new virtual environment (.venv314)...
    REM Try creating with specific version (needs py launcher) or default python
    python -m venv .venv314
    
    IF ERRORLEVEL 1 (
         echo [ERROR] Failed to create venv. Make sure Python 3.14 is installed.
         pause
         exit /b 1
    )
    
    echo [INFO] Upgrading pip...
    .venv314\Scripts\python -m pip install --upgrade pip
)

echo.
echo [INFO] Installing/Updating Backend Dependencies...
.venv314\Scripts\pip install -r backend\requirements.txt

echo.
echo [INFO] Installing/Updating Frontend Dependencies...
.venv314\Scripts\pip install -r frontend\requirements.txt

echo.
echo ============================================================
echo  [SUCCESS] Environment is ready!
echo  You can now run: run_locally.bat
echo ============================================================
pause
