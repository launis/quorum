@echo off
echo ===================================================
echo   COGNITIVE QUORUM - CLIENT LAUNCHER (WEB)
echo ===================================================
echo.
echo Launching client in separate window (Chrome mode)...
start "CQ Client (WEB)" cmd /k "cd client_app && flutter run -d chrome"
