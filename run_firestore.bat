@echo off
echo ===================================================
echo   COGNITIVE QUORUM - PRODUCTION LAUNCHER
echo   (FIRESTORE CLOUD DATABASE)
echo ===================================================
echo.

echo [1/2] Launching Backend (Uvicorn)...
echo       Mode: FIRESTORE, REAL LLM, NO MOCK
start "CQ Backend (PROD)" cmd /k "chcp 65001 > nul && set USE_MOCK_DB=false && set USE_MOCK_LLM=false && set STORAGE_BACKEND=FIRESTORE && set GOOGLE_APPLICATION_CREDENTIALS=service-account.json && uv run uvicorn backend.main:app --reload --port 8000"

echo [2/2] Launching Client (Flutter)...
start "CQ Client (PROD)" cmd /k "cd client_app && flutter run"

echo.
echo ---------------------------------------------------
echo  STATUS:
echo  - Backend: http://localhost:8000/docs
echo  - Client:  Select device in the new window
echo ---------------------------------------------------
echo.
pause
