@echo off
echo ===================================================
echo   COGNITIVE QUORUM - LOCAL PRODUCTION LAUNCHER
echo   (LOCAL DB: data\db.json)
echo ===================================================
echo.

echo [1/2] Launching Backend (Uvicorn)...
echo       Mode: LOCAL PROD (REAL LLM, NO MOCK, LOCAL STORAGE)
start "CQ Backend (LOCAL PROD)" cmd /k "chcp 65001 > nul && set USE_MOCK_DB=false && set USE_MOCK_LLM=false && set STORAGE_BACKEND=LOCAL && uv run uvicorn backend.main:app --reload --port 8000"

echo [2/2] Launching Client (Flutter)...
start "CQ Client (LOCAL PROD)" cmd /k "cd client_app && flutter run"

echo.
echo ---------------------------------------------------
echo  STATUS:
echo  - Backend: http://localhost:8000/docs
echo  - Client:  Select device in the new window
echo ---------------------------------------------------
echo.
pause
