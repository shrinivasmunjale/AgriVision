@echo off
cd /d "%~dp0backend"

if not exist .venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup-backend.bat first
    pause
    exit /b 1
)

echo Starting AgriVision AI Backend...
echo Backend will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.

.venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
