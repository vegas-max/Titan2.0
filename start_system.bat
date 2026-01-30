@echo off
TITLE Apex-Omega Titan
color 0B

REM Change to script directory to ensure correct working directory
cd /d "%~dp0"

echo ==================================================
echo    APEX-OMEGA TITAN: 10-CHAIN ARBITRAGE SYSTEM
echo ==================================================

echo [1] Installing Python Deps...
pip install -r requirements.txt >nul

echo [2] Installing Node Deps...
call npm install >nul

echo [3] Launching Modules...
start "Brain" cmd /k "python offchain/ml/brain.py"
start "Executor" cmd /k "node offchain/execution/bot.js"

echo [SUCCESS] System Live.
pause