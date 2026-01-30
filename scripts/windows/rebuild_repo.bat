@echo off
setlocal enabledelayedexpansion

REM **** Step 1: Configuration Setup ****
echo ================================
echo [Step 1/8] Configuration Profiles
echo ================================
set /p CONFIG_PROFILE="Enter your configuration profile (lightweight/ARM/high-performance): "
echo [INFO] Using configuration profile: %CONFIG_PROFILE%
REM If configuration uses a JSON, prompt for file
set /p CONFIG_FILE="Enter the config JSON filename (e.g., config.json): "
if exist config\%CONFIG_FILE% (
    echo [INFO] Found config file: config\%CONFIG_FILE%
) else (
    echo [WARN] Config file not found, please create or verify location in config/README.md
    pause
)
REM Optionally let the user edit/view the config file
set /p EDIT_CONFIG="Do you want to edit the config file? (y/n): "
if /I "%EDIT_CONFIG%"=="y" (
    notepad config\%CONFIG_FILE%
)

REM **** Step 2: Build core-rust modules ****
echo ================================
echo [Step 2/8] Building Rust Modules
echo ================================
REM Check if Rust is installed
where rustc >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Rust is not installed. Please install: https://rustup.rs/
    pause
    exit /b 1
)
cd core-rust
echo [INFO] Building Rust library...
cargo build --release
if errorlevel 1 (
    echo [ERROR] Rust build failed. Check core-rust/README.md
    pause
    exit /b 1
)
cd ..

REM **** Step 3: Build core-go packages ****
echo ================================
echo [Step 3/8] Building Go Packages
echo ================================
where go >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Go is not installed. Please install: https://go.dev/doc/install
    pause
    exit /b 1
)
cd core-go
echo [INFO] Compiling Go packages and standalone binaries...
go build .
if errorlevel 1 (
    echo [ERROR] Go build failed. Check core-go/README.md
    pause
    exit /b 1
)
cd ..

REM **** Step 4: Build/Configure execution engine ****
echo ================================
echo [Step 4/8] Setting Up Arbitrage Engine (execution)
echo ================================
cd execution
echo [INFO] Install Python modules (PyO3, etc.) if required.
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install: https://www.python.org/downloads/
    pause
    exit /b 1
)

set /p VENV_CREATE="Create a new Python virtual environment? (y/n): "
if /I "%VENV_CREATE%"=="y" (
    python -m venv venv
    call venv\Scripts\activate
)
REM If requirements.txt exists, install packages
if exist requirements.txt (
    pip install -r requirements.txt
)
echo [INFO] Building/Starting execution API...
REM Example: python main.py --config ../config/%CONFIG_FILE%
echo [INFO] (Adjust launch command as per execution/README.md)
cd ..

REM **** Step 5: Routing Setup ****
echo ================================
echo [Step 5/8] Routing Engine & Bridge Aggregation
echo ================================
cd routing
echo [INFO] Ensure dependencies are installed (see routing/README.md)
REM Example: npm install
if exist package.json (
    where npm >nul 2>nul
    if errorlevel 1 (
        echo [ERROR] Node.js/npm not installed. Please install: https://nodejs.org/
        pause
        exit /b 1
    ) else (
        npm install
    )
)
REM Example build/run, adjust as needed
REM npm run build
cd ..

REM **** Step 6: Autonomous Agent Framework ****
echo ================================
echo [Step 6/8] Agents Framework & Super Agent
echo ================================
cd agents
echo [INFO] Building/starting agent orchestration (see agents/README.md)
REM Example commands here: python agent.py or go build . etc.
cd ..

REM **** Step 7: Test Suite ****
echo ================================
echo [Step 7/8] Running Test Suite
echo ================================
cd test
REM Prompt for which tests to run
set /p TEST_TYPE="Run all tests or specific type? (all/unit/integration/functional): "
if /I "%TEST_TYPE%"=="all" (
    echo [INFO] Running ALL tests...
    REM Example: python -m unittest discover
) else (
    echo [INFO] Running %TEST_TYPE% tests...
    REM Implement actual test commands by reading test/README.md
)
cd ..

REM **** Step 8: Documentation & Contribution Guidelines ****
echo ================================
echo [Step 8/8] Documentation Reference
echo ================================
cd docs
echo [INFO] Open docs/README.md for technical documentation, templates, and guidelines.
notepad README.md
cd ..

echo ==========================================================
echo [DONE] Repo rebuild and setup sequence complete. Review outputs above.
echo If you encountered errors, check each respective README.md for troubleshooting.
echo ==========================================================
pause
endlocal
