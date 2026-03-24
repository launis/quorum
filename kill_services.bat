@echo off
echo ===================================================
echo   COGNITIVE QUORUM V3 - FORCE KILL SERVICES
echo   Use this if "Port 8000 is already in use" or Flutter hangs
echo ===================================================
echo.

echo [1/3] Killing Python processes (FastAPI Backend / Workers)...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM uvicorn.exe /T 2>nul

echo [2/3] Killing Dart/Flutter processes (Client App V2)...
taskkill /F /IM dart.exe /T 2>nul
taskkill /F /IM flutter.exe /T 2>nul
taskkill /F /IM client_app.exe /T 2>nul
taskkill /F /IM client_app_v2.exe /T 2>nul

echo [3/3] Done. All backend and frontend services killed.
echo You can now safely spin up the V3 environment.
echo.
pause
