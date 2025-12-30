@echo off
echo ==========================================
echo   SEED FIRESTORE DATABASE
echo ==========================================
echo.
echo [INFO] This script will populate your Firestore database 
echo        with initial data from 'backend/database/seed_data.json'.
echo.
echo [WARNING] This assumes you have 'service-account.json' configured
echo           and 'firebase-admin' installed.
echo.

set USE_MOCK_DB=false
set STORAGE_BACKEND=FIRESTORE
set GOOGLE_APPLICATION_CREDENTIALS=service-account.json
set PYTHONIOENCODING=utf-8

echo [ACTION] Running seeder in FIRESTORE mode...
echo.

python -m backend.database.seeder

echo.
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Seeding failed. Check errors above.
) else (
    echo [SUCCESS] Firestore populated! You can now run 'run_firestore.bat'.
)
echo.
pause
