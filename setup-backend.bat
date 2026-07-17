@echo off
echo ================================================
echo AgriVision AI - Backend Setup
echo ================================================
echo.

cd /d "%~dp0backend"

echo [1/5] Creating virtual environment...
python -m venv .venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment created
echo.

echo [2/5] Installing dependencies...
.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
.venv\Scripts\pip.exe install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

echo [3/5] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo ✓ .env file created
) else (
    echo ✓ .env file already exists
)
echo.

echo [4/5] Running database migrations...
.venv\Scripts\alembic.exe upgrade head
if %errorlevel% neq 0 (
    echo ERROR: Failed to run migrations
    pause
    exit /b 1
)
echo ✓ Database migrations completed
echo.

echo [5/5] Seeding database...
.venv\Scripts\python.exe seed.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to seed database
    pause
    exit /b 1
)
echo ✓ Database seeded
echo.

echo ================================================
echo Backend setup complete!
echo ================================================
echo.
echo To start the backend server, run:
echo   cd backend
echo   .venv\Scripts\activate
echo   uvicorn app.main:app --reload
echo.
echo Or use: start-backend.bat
echo.
pause
