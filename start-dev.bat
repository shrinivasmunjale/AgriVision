@echo off
echo ============================================
echo AgriVision AI - Development Mode
echo ============================================
echo.
echo This will start both backend and frontend servers
echo.
echo Backend will run on: http://localhost:8000
echo Frontend will run on: http://localhost:3000
echo.
echo Press Ctrl+C in each window to stop servers
echo.
pause

echo Starting Backend Server...
start "AgriVision Backend" cmd /k "cd /d %~dp0backend && call .venv\Scripts\activate.bat && uvicorn app.main:app --reload"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start "AgriVision Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ============================================
echo Both servers started!
echo ============================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
