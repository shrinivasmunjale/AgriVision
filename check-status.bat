@echo off
echo ============================================
echo AgriVision AI - Installation Status Check
echo ============================================
echo.

set FRONTEND_OK=0
set BACKEND_OK=0
set PYTHON_OK=0

REM Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python installed
    python --version
    set PYTHON_OK=1
) else (
    echo ✗ Python not found
)
echo.

REM Check Node/npm
echo [2/5] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Node.js installed
    node --version
) else (
    echo ✗ Node.js not found
)
npm --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ npm installed
    npm --version
) else (
    echo ✗ npm not found
)
echo.

REM Check Frontend
echo [3/5] Checking Frontend installation...
if exist "frontend\node_modules\" (
    echo ✓ Frontend dependencies installed
    set FRONTEND_OK=1
) else (
    echo ✗ Frontend dependencies not installed
    echo   Run: .\install-frontend.bat
)
echo.

REM Check Backend
echo [4/5] Checking Backend installation...
if exist "backend\.venv\" (
    echo ✓ Backend virtual environment exists
    if exist "backend\.venv\Scripts\uvicorn.exe" (
        echo ✓ Backend dependencies installed
        set BACKEND_OK=1
    ) else (
        echo ✗ Backend dependencies not fully installed
        echo   Run: .\setup-backend.bat
    )
) else (
    echo ✗ Backend virtual environment not created
    echo   Run: .\setup-backend.bat
)
echo.

REM Check Database
echo [5/5] Checking Database...
if exist "backend\agrivision.db" (
    echo ✓ Database file exists
) else (
    echo ✗ Database not created
    echo   Run: .\setup-backend.bat
)
echo.

REM Summary
echo ============================================
echo SUMMARY
echo ============================================
if %FRONTEND_OK% equ 1 if %BACKEND_OK% equ 1 (
    echo.
    echo ✓✓✓ ALL SYSTEMS READY! ✓✓✓
    echo.
    echo You can now start development:
    echo   .\start-dev.bat
    echo.
) else (
    echo.
    echo ⚠ INSTALLATION INCOMPLETE
    echo.
    if %PYTHON_OK% equ 0 (
        echo 1. Install Python 3.11 or 3.12
        echo    https://www.python.org/downloads/
        echo.
    )
    if %FRONTEND_OK% equ 0 (
        echo 2. Install Frontend dependencies:
        echo    .\install-frontend.bat
        echo.
    )
    if %BACKEND_OK% equ 0 (
        echo 3. Install Backend dependencies:
        echo    .\setup-backend.bat
        echo.
    )
)
echo.
echo See QUICK_START.md for detailed instructions
echo.
pause
