@echo off
echo =======================================
echo   NOLLAA FIRESTORE DATABASE (Wrapper)
echo =======================================
echo.
echo Calling: uv run python backend/seed/seed_firestore.py
echo.
echo VAROITUS: Tuhoaa kaiken datan pilvessa!
pause
uv run python backend/seed/seed_firestore.py
pause
