@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8

REM --- CONFIGURATION ---
REM Mode: REAL LLM (Live APIs), LOCAL DB (TinyDB)
set USE_MOCK_LLM=false
set USE_MOCK_DB=false
set STORAGE_BACKEND=LOCAL

REM Start Backend
start "Cognitive Quorum Backend" cmd /k "chcp 65001 > nul && set USE_MOCK_LLM=false && set USE_MOCK_DB=false && set STORAGE_BACKEND=LOCAL && .venv\Scripts\python -m uvicorn backend.main:app --reload --port 8000"

REM Wait for backend warmup
timeout /t 8 > nul

REM Start Frontend
start "Cognitive Quorum Frontend" cmd /k "chcp 65001 > nul && set USE_MOCK_LLM=false && set USE_MOCK_DB=false && set STORAGE_BACKEND=LOCAL && .venv\Scripts\python -m streamlit run frontend/main.py"

echo.
echo [LAUNCHER] Services starting... check the Backend window for system status.
echo Frontend will open at: http://localhost:8501
echo.
pause