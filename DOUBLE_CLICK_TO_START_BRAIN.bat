@echo off
title TITAN BRAIN - LIVE MAINNET SCANNING
color 0A

REM Change to script directory to ensure correct working directory
cd /d "%~dp0"

echo.
echo ========================================================================
echo   APEX-OMEGA TITAN: BRAIN STARTING
echo ========================================================================
echo.
echo   You will see live scanning activity below...
echo   Press Ctrl+C to stop
echo.
echo ========================================================================
echo.

set EXECUTION_MODE=PAPER
python mainnet_orchestrator.py

pause
