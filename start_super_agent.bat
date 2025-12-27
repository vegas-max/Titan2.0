@echo off
REM APEX-OMEGA TITAN: Super Agent Startup Script (Windows)
REM ========================================================

echo ================================
echo 🤖 TITAN SUPER AGENT SYSTEM
echo ================================
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)
python --version
echo.

REM Check Node.js
echo Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Node.js not found (optional for full features)
) else (
    node --version
)
echo.

REM Create logs directory
if not exist "logs" mkdir logs

echo Starting Super Agent Manager...
echo ================================
echo.

REM Parse command line arguments
set MODE=%1
if "%MODE%"=="" set MODE=interactive

set ACTION=%2
set SYSTEM_MODE=%3
if "%SYSTEM_MODE%"=="" set SYSTEM_MODE=paper

REM Run the super agent manager
if "%MODE%"=="interactive" (
    python agents\super_agent_manager.py --mode interactive
) else if "%MODE%"=="daemon" (
    echo Starting in background mode...
    start /B python agents\super_agent_manager.py --mode daemon > logs\super_agent_daemon.log 2>&1
    echo Super Agent started in background
    echo Check logs\super_agent_daemon.log for output
) else if "%MODE%"=="once" (
    if "%ACTION%"=="" (
        echo [ERROR] Action required for 'once' mode
        echo Usage: %0 once ^<action^> [system-mode]
        echo Actions: health, start, stop, test, build, status
        pause
        exit /b 1
    )
    python agents\super_agent_manager.py --mode once --action %ACTION% --system-mode %SYSTEM_MODE%
) else (
    echo [ERROR] Unknown mode: %MODE%
    echo Usage: %0 [interactive^|daemon^|once] [action] [system-mode]
    pause
    exit /b 1
)

if "%MODE%"=="interactive" pause
