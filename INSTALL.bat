@echo off
echo ============================================
echo AgriVision AI - Complete Installation
echo ============================================
echo.
echo This will install both frontend and backend
echo.
pause

REM Step 1: Check Python
echo.
echo ============================================
echo Step 1: Checking Python Version
echo ============================================
call check-python.bat
if %errorlevel% neq 0 (
    echo.
    echo ✗ Python version incompatible
    echo.
    echo Please fix Python version first, then run:
    echo   .\INSTALL.bat
    echo.
    pause
    exit /b 1
)

REM Step 2: Install Frontend
echo.
echo ============================================
echo Step 2: Installing Frontend Dependencies
echo ============================================
echo.
pause
call install-frontend.bat

REM Step 3: Install Backend
echo.
echo ============================================
echo Step 3: Installing Backend Dependencies
echo ============================================
echo.
pause
call setup-backend.bat

REM Step 4: Check Status
echo.
echo ============================================
echo Step 4: Verifying Installation
echo ============================================
echo.
pause
call check-status.bat

echo.
echo ============================================
echo INSTALLATION COMPLETE!
echo ============================================
echo.
echo Next steps:
echo   1. Start development: .\start-dev.bat
echo   2. Open browser: http://localhost:3000
echo   3. Login with test account:
echo      - Email: farmer@example.com
echo      - Password: farmer123
echo.
echo For API docs: http://localhost:8000/docs
echo.
pause
