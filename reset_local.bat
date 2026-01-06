@echo off
echo =======================================
echo   RESET LOCAL PROD DB (Wrapper)
echo =======================================
echo.
echo Calling: uv run python backend/seed/seed_prod.py
echo.
uv run python backend/seed/seed_prod.py
pause
