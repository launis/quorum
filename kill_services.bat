@echo off
echo ===================================================
echo   COGNITIVE QUORUM - FORCE KILL SERVICES
echo   Use this if "Port 8000 is already in use"
echo ===================================================
echo.

echo [1/3] Killing Python processes (Backend/Worker)...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM uvicorn.exe /T 2>nul

echo [2/3] Killing Dart/Flutter processes...
taskkill /F /IM dart.exe /T 2>nul
taskkill /F /IM flutter.exe /T 2>nul
taskkill /F /IM client_app.exe /T 2>nul

echo [3/3] Done. All backend services should be stopped.
echo You can now run run_local.bat or run_firestore.bat safely.
echo.
pause
