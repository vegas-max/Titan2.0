@echo off
title TITAN BOT - SIGNAL EXECUTOR
color 0B

REM Change to script directory to ensure correct working directory
cd /d "%~dp0"

echo.
echo ========================================================================
echo   APEX-OMEGA TITAN: BOT STARTING
echo ========================================================================
echo.
echo   Monitoring for signals from Brain...
echo   Press Ctrl+C to stop
echo.
echo ========================================================================
echo.

set EXECUTION_MODE=PAPER
node offchain\execution\bot.js

pause
