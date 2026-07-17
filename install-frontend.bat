@echo off
echo ============================================
echo AgriVision AI - Frontend Installation
echo ============================================
echo.

cd /d "%~dp0frontend"

echo Cleaning npm cache and node_modules...
rmdir /s /q node_modules 2>nul
del package-lock.json 2>nul
call npm cache clean --force

echo.
echo Installing dependencies...
call npm install

echo.
echo ============================================
echo Frontend installation complete!
echo ============================================
echo.
echo To start the frontend:
echo   cd frontend
echo   npm run dev
echo.
pause
