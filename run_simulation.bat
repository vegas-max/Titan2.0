@echo off
REM Quick launcher for Titan Robust 90-Day Live Simulation (Windows)
REM
REM Usage:
REM   run_simulation.bat              - Quick 7-day test in PAPER mode
REM   run_simulation.bat live         - Quick 7-day test in LIVE mode
REM   run_simulation.bat full         - Full 90-day simulation in LIVE mode
REM   run_simulation.bat full paper   - Full 90-day simulation in PAPER mode

setlocal

echo ===============================================================
echo   TITAN ROBUST 90-DAY SIMULATION LAUNCHER
echo ===============================================================

REM Parse arguments
set MODE=PAPER
set QUICK_TEST=--quick-test

if "%1"=="live" (
    set MODE=LIVE
    echo WARNING: Running in LIVE mode
) else if "%1"=="full" (
    set QUICK_TEST=
    if "%2"=="paper" (
        set MODE=PAPER
    ) else (
        set MODE=LIVE
    )
    echo Running full 90-day simulation
) else (
    echo Running quick 7-day test
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Python found

REM Check dependencies
echo Checking dependencies...
python -c "import pandas, numpy, web3" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -q pandas numpy web3 python-dotenv rustworkx scikit-learn
    echo Dependencies installed
) else (
    echo Dependencies OK
)

REM Run simulation
echo ===============================================================
echo Starting simulation...
echo Mode: %MODE%
echo ===============================================================
echo.

python run_robust_90day_live_simulation.py --mode %MODE% %QUICK_TEST%

if errorlevel 1 (
    echo.
    echo ERROR: Simulation failed
    pause
    exit /b 1
)

echo.
echo ===============================================================
echo Simulation completed successfully!
echo ===============================================================
echo.
echo Results saved to: data\robust_live_simulation_results\
echo.

REM Find latest report
for /f "delims=" %%i in ('dir /b /od data\robust_live_simulation_results\REPORT_*.md 2^>nul') do set LATEST_REPORT=%%i
if defined LATEST_REPORT (
    echo Latest report: data\robust_live_simulation_results\%LATEST_REPORT%
)

echo.
pause
