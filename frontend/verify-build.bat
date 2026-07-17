@echo off
echo ========================================
echo AgriVision AI - Build Verification
echo ========================================
echo.

echo [1/4] Checking Node.js...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found
    exit /b 1
)

echo [2/4] Checking dependencies...
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)

echo [3/4] Verifying configuration files...
if not exist "vercel.json" (
    echo ERROR: vercel.json missing
    exit /b 1
)
if not exist "jsconfig.json" (
    echo ERROR: jsconfig.json missing
    exit /b 1
)
if not exist "src\lib\api.js" (
    echo ERROR: src\lib\api.js missing
    exit /b 1
)
echo All configuration files present!

echo [4/4] Running production build...
call npm run build
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo BUILD FAILED - Check errors above
    echo ========================================
    exit /b 1
)

echo.
echo ========================================
echo BUILD SUCCESSFUL!
echo Ready for Vercel deployment
echo ========================================
echo.
echo Next steps:
echo 1. Push code to GitHub
echo 2. Connect repository to Vercel
echo 3. Set NEXT_PUBLIC_API_URL in Vercel
echo 4. Deploy!
echo.
pause
