@echo off
REM ---- JARVIS one-click launcher (Windows) ----
cd /d "%~dp0"

if not exist ".venv" (
  echo Creating virtual environment...
  python -m venv .venv
)
call .venv\Scripts\activate.bat

echo Installing / updating dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt

if not exist ".env" (
  echo.
  echo   No .env found. Copy .env.example to .env and add your keys first.
  echo.
  copy .env.example .env >nul
  echo   A blank .env was created for you. Open it, paste your keys, then re-run.
  pause
  exit /b
)

echo.
echo   Launching JARVIS at http://localhost:8000  (open in Chrome or Edge)
echo.
python server.py
pause
