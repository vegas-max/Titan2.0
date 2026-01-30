@echo off
REM ==============================================================================
REM APEX-OMEGA TITAN: QUICK START MAINNET (Windows)
REM ==============================================================================
REM One-command launcher for mainnet operations with full system checks

REM Change to script directory to ensure correct working directory
cd /d "%~dp0"

echo.
echo ===================================================
echo    APEX-OMEGA TITAN: QUICK START MAINNET
echo ===================================================
echo.

REM Check if mode argument provided
set MODE=%1
if "%MODE%"=="" set MODE=PAPER

echo [34mStarting in %MODE% mode...[0m
echo.

REM Run system diagnostics first
echo [34m===================================================[0m
echo [34m   STEP 1: SYSTEM DIAGNOSTICS[0m
echo [34m===================================================[0m
echo.

python system_wiring.py
if errorlevel 1 (
    echo.
    echo [31m❌ System diagnostics failed![0m
    echo [33mPlease fix the errors above and try again.[0m
    echo.
    pause
    exit /b 1
)

echo.
echo [32m✅ System diagnostics passed![0m
echo.

REM Ask user to confirm
echo [33m===================================================[0m
echo [33m   READY TO START MAINNET SYSTEM[0m
echo [33m===================================================[0m
echo.
echo Mode: %MODE%
echo.
if "%MODE%"=="LIVE" (
    echo [31m⚠️  WARNING: LIVE MODE - REAL FUNDS WILL BE USED![0m
    echo.
    set /p CONFIRM="Type 'YES' to confirm and start: "
    if not "!CONFIRM!"=="YES" (
        echo.
        echo [33mCancelled by user.[0m
        pause
        exit /b 0
    )
)

echo.
echo [32m🚀 Launching Titan Mainnet System...[0m
echo.

REM Launch the system
call mainnet_system_launcher.bat %MODE%

echo.
echo [32mLauncher complete.[0m
pause
