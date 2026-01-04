@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8

REM --- CONFIGURATION ---
REM Mode: MOCK LLM (Free/Offline), LOCAL DB (TinyDB)
set USE_MOCK_LLM=true
set USE_MOCK_DB=true
set STORAGE_BACKEND=LOCAL

REM Start Backend
REM Start Backend
start "Cognitive Quorum Backend (MOCK)" cmd /k "chcp 65001 > nul && set USE_MOCK_LLM=true && set USE_MOCK_DB=true && set STORAGE_BACKEND=LOCAL && .venv\Scripts\python -m uvicorn backend.main:app --reload --port 8000"

REM Wait for backend warmup
timeout /t 10 > nul

REM Start Frontend
start "Cognitive Quorum Frontend (MOCK)" cmd /k "chcp 65001 > nul && set USE_MOCK_LLM=true && set USE_MOCK_DB=true && set STORAGE_BACKEND=LOCAL && .venv\Scripts\python -m streamlit run frontend/main.py"

echo.
echo [LAUNCHER] MOCK ENV starting... check the Backend window for system status.
echo Frontend will open at: http://localhost:8501
echo.
pause