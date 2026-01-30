@echo off
REM TITAN Interactive Dashboard Launcher for Windows

echo ===============================================================
echo    TITAN Multi-Page Interactive Dashboard Launcher
echo ===============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3 is required but not installed
    echo Please install Python 3 from https://www.python.org/
    pause
    exit /b 1
)

echo Checking Python version...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python %PYTHON_VERSION% found

echo.
echo Checking dependencies...

REM Check for aiohttp
python -c "import aiohttp" 2>nul
if errorlevel 1 (
    echo Installing aiohttp...
    pip install aiohttp aiohttp-cors
)

REM Check for redis (optional)
python -c "import redis" 2>nul
if errorlevel 1 (
    echo Warning: redis-py not found - dashboard will run in simulation mode
    echo To connect to live system, install redis: pip install redis
)

echo.
echo Starting TITAN Interactive Dashboard...
echo.
echo Dashboard will be available at:
echo   Local:   http://localhost:8080
echo.
echo Features:
echo   - Multi-page navigation (5 pages)
echo   - Real-time market opportunity scanner
echo   - Executable transaction queue
echo   - Live execution monitor
echo   - Performance analytics
echo   - Interactive control buttons
echo   - WebSocket live updates
echo.
echo Press Ctrl+C to stop
echo.

REM Start the dashboard server
python dashboard_server.py --host 0.0.0.0 --port 8080

pause
