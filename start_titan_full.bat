@echo off
TITLE Apex-Omega Titan (Full Scale)
color 0B

echo ==================================================
echo    APEX-OMEGA TITAN: 10-CHAIN SYSTEM BOOT
echo ==================================================

echo [1] Installing Dependencies...
call npm install >nul
pip install -r requirements.txt >nul

echo [2] Running Li.Fi Discovery (Building Map)...
node offchain/execution/lifi_discovery.js
if %errorlevel% neq 0 (
    echo [ERROR] Discovery Failed. Check API Key.
    pause
    exit /b
)

echo [3] Launching Titan Engines...
start "Titan [BRAIN]" cmd /k "python3 offchain/ml/brain.py"
start "Titan [EXECUTOR]" cmd /k "node offchain/execution/bot.js"
start "Titan [API]" cmd /k "uvicorn offchain.ml.onnx_prediction_api:app --port 8000"

echo [SUCCESS] System Live.
pause