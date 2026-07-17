@echo off
echo ============================================
echo Python Version Compatibility Check
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python is NOT installed
    echo.
    echo Please install Python 3.11 or 3.12 from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Current Python Version: %PYTHON_VERSION%
echo.

REM Extract major and minor version
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

REM Check compatibility
if "%MAJOR%"=="3" (
    if "%MINOR%"=="11" (
        echo ✓✓✓ PERFECT! Python 3.11 is fully compatible
        echo.
        echo You can proceed with backend installation:
        echo   .\setup-backend.bat
        echo.
        goto :compatible
    )
    if "%MINOR%"=="12" (
        echo ✓✓✓ PERFECT! Python 3.12 is fully compatible
        echo.
        echo You can proceed with backend installation:
        echo   .\setup-backend.bat
        echo.
        goto :compatible
    )
    if "%MINOR%"=="10" (
        echo ✓ Python 3.10 should work
        echo.
        echo You can try backend installation:
        echo   .\setup-backend.bat
        echo.
        goto :compatible
    )
    if "%MINOR%"=="14" (
        echo ⚠ WARNING: Python 3.14 detected
        echo.
        echo Python 3.14 is very new and requires C++ build tools
        echo to compile packages like pydantic-core.
        echo.
        echo RECOMMENDED OPTIONS:
        echo.
        echo Option 1: Install Python 3.11 or 3.12 [EASIEST]
        echo   1. Download from https://www.python.org/downloads/
        echo   2. Install with "Add to PATH" checked
        echo   3. Open NEW terminal
        echo   4. Run: .\setup-backend.bat
        echo.
        echo Option 2: Install Visual Studio Build Tools
        echo   1. Download: https://visualstudio.microsoft.com/downloads/
        echo   2. Install "Desktop development with C++"
        echo   3. Restart computer
        echo   4. Run: .\setup-backend.bat
        echo.
        echo See SETUP_INSTRUCTIONS.md for more details
        echo.
        goto :incompatible
    )
)

echo ⚠ Unknown Python version
echo.
echo Recommended: Python 3.11 or 3.12
echo You can try setup, but it may fail.
echo.

:compatible
set EXIT_CODE=0
goto :end

:incompatible
set EXIT_CODE=1
goto :end

:end
pause
exit /b %EXIT_CODE%
