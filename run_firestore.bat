@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8

REM --- CONFIGURATION ---
REM Mode: REAL LLM (Live APIs), CLOUD DB (Firestore)
set USE_MOCK_LLM=false
set USE_MOCK_DB=false
set STORAGE_BACKEND=FIRESTORE

REM Start Backend
start "Cognitive Quorum Backend (PROD)" cmd /k "chcp 65001 > nul && set USE_MOCK_LLM=false && set USE_MOCK_DB=false && set STORAGE_BACKEND=FIRESTORE && uvicorn backend.main:app --reload --port 8000"

REM Wait for backend warmup
timeout /t 10 > nul

REM Start Frontend
start "Cognitive Quorum Frontend (PROD)" cmd /k "chcp 65001 > nul && set USE_MOCK_LLM=false && set USE_MOCK_DB=false && set STORAGE_BACKEND=FIRESTORE && streamlit run frontend/main.py"

echo.
echo [LAUNCHER] PRODUCTION ENV (Firestore) starting... check the Backend window for system status.
echo Frontend will open at: http://localhost:8501
echo.
pause
