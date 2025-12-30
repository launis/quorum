@echo off
echo Starting Cognitive Quorum v2 (FIRESTORE MODE)...
echo.
echo [INFO] MODE: REAL LLM + FIRESTORE DATABASE
echo [INFO] connecting to Google Firebase Cloud Firestore.
echo [INFO] Data is saved to your configured Firestore project.
echo [INFO] Requires: service-account.json and GOOGLE_APPLICATION_CREDENTIALS in .env
echo.
set USE_MOCK_LLM=false
set USE_MOCK_DB=false
set STORAGE_BACKEND=FIRESTORE
set GOOGLE_APPLICATION_CREDENTIALS=service-account.json
chcp 65001
set PYTHONIOENCODING=utf-8

REM Start Backend
start "Cognitive Quorum Backend (FIRESTORE)" cmd /k "chcp 65001 && set USE_MOCK_LLM=false && set USE_MOCK_DB=false && set STORAGE_BACKEND=FIRESTORE&& echo [CHECK] BACKEND: %STORAGE_BACKEND% && uvicorn backend.main:app --reload --port 8000"

REM Wait a bit for backend to start
timeout /t 15

REM Start Frontend
start "Cognitive Quorum Frontend (FIRESTORE)" cmd /k "chcp 65001 && set USE_MOCK_LLM=false && set USE_MOCK_DB=false && set STORAGE_BACKEND=FIRESTORE&& streamlit run frontend/main.py"

echo.
echo Services started in FIRESTORE mode!
echo Backend: http://localhost:8000/docs
echo Frontend: http://localhost:8501
echo.
pause
