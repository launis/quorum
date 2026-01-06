@echo off
echo ===================================================
echo   COGNITIVE QUORUM - DEVELOPMENT LAUNCHER
echo ===================================================
echo.

echo [1/2] Launching Backend (Uvicorn)...
REM Enable "Hybrid Mode": Mock DB + Real Firebase Auth
set USE_FIREBASE_AUTH=true
start "CQ Backend" cmd /k "uv run uvicorn backend.main:app --reload --port 8000"

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
