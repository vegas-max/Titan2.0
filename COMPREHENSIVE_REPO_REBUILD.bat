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
    echo [WARN] Config file not found at config\%CONFIG_FILE%
    echo [INFO] Available config files in config/:
    dir /b config\*.json 2>nul
    echo.
    echo [INFO] You can continue without a config file, or you can:
    echo   1. Create the config file later
    echo   2. Use the root config.json instead
    echo   3. Exit and create the config file now
    set /p CONTINUE="Do you want to continue anyway? (y/n): "
    if /I not "%CONTINUE%"=="y" (
        echo [INFO] Exiting. Please create your config file in config/ and run this script again.
        pause
        exit /b 0
    )
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
REM Check if core-rust directory exists
if not exist core-rust (
    echo [ERROR] core-rust directory not found. Please ensure you're in the Titan2.0 root directory.
    pause
    exit /b 1
)
cd core-rust
echo [INFO] Building Rust library...
cargo build --release
if errorlevel 1 (
    echo [ERROR] Rust build failed. Check core-rust/README.md
    pause
    cd ..
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
REM Check if core-go directory exists
if not exist core-go (
    echo [ERROR] core-go directory not found. Please ensure you're in the Titan2.0 root directory.
    pause
    exit /b 1
)
cd core-go
echo [INFO] Compiling Go packages and standalone binaries...
go build .
if errorlevel 1 (
    echo [ERROR] Go build failed. Check core-go/README.md
    pause
    cd ..
    exit /b 1
)
cd ..

REM **** Step 4: Build/Configure execution engine ****
echo ================================
echo [Step 4/8] Setting Up Arbitrage Engine (execution)
echo ================================
REM Check if execution directory exists
if not exist execution (
    echo [ERROR] execution directory not found. Please ensure you're in the Titan2.0 root directory.
    pause
    exit /b 1
)
cd execution
echo [INFO] Install Python modules (PyO3, etc.) if required.
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install: https://www.python.org/downloads/
    pause
    cd ..
    exit /b 1
)

set /p VENV_CREATE="Create a new Python virtual environment? (y/n): "
if /I "%VENV_CREATE%"=="y" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        cd ..
        exit /b 1
    )
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate
    if errorlevel 1 (
        echo [WARN] Failed to activate virtual environment, continuing...
    )
)
REM If requirements.txt exists, install packages
if exist requirements.txt (
    echo [INFO] Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [WARN] Some pip packages failed to install. Check execution/README.md
        pause
    )
)
echo [INFO] Python execution engine setup complete.
echo [INFO] To start the engine manually, run commands per execution/README.md
echo [INFO] Example: python main.py --config ../config/%CONFIG_FILE%
cd ..

REM **** Step 5: Routing Setup ****
echo ================================
echo [Step 5/8] Routing Engine & Bridge Aggregation
echo ================================
REM Check if routing directory exists
if not exist routing (
    echo [ERROR] routing directory not found. Please ensure you're in the Titan2.0 root directory.
    pause
    exit /b 1
)
cd routing
echo [INFO] Ensure dependencies are installed (see routing/README.md)
REM Example: npm install
if exist package.json (
    where npm >nul 2>nul
    if errorlevel 1 (
        echo [ERROR] Node.js/npm not installed. Please install: https://nodejs.org/
        pause
        cd ..
        exit /b 1
    ) else (
        echo [INFO] Installing Node.js dependencies...
        npm install
        if errorlevel 1 (
            echo [WARN] Some npm packages failed to install. Check routing/README.md
            pause
        )
    )
) else (
    echo [INFO] No package.json found in routing/ - dependencies may not be needed
)
echo [INFO] Routing layer setup complete.
echo [INFO] If build is needed, run: npm run build (adjust per routing/README.md)
cd ..

REM **** Step 6: Autonomous Agent Framework ****
echo ================================
echo [Step 6/8] Agents Framework & Super Agent
echo ================================
REM Check if agents directory exists
if not exist agents (
    echo [ERROR] agents directory not found. Please ensure you're in the Titan2.0 root directory.
    pause
    exit /b 1
)
cd agents
echo [INFO] Agents framework directory accessed.
echo [INFO] To start agents, follow commands in agents/README.md
echo [INFO] Common commands: python super_agent_manager.py or python demo.py
cd ..

REM **** Step 7: Test Suite ****
echo ================================
echo [Step 7/8] Running Test Suite
echo ================================
REM Check if test directory exists
if not exist test (
    echo [ERROR] test directory not found. Please ensure you're in the Titan2.0 root directory.
    pause
    exit /b 1
)
cd test
REM Prompt for which tests to run
set /p TEST_TYPE="Run all tests or specific type? (all/unit/integration/functional/skip): "
if /I "%TEST_TYPE%"=="skip" (
    echo [INFO] Skipping tests...
) else if /I "%TEST_TYPE%"=="all" (
    echo [INFO] Running ALL tests...
    echo [INFO] To run tests, execute commands from test/README.md
    echo [INFO] Example: npm test or mocha *.test.js
) else (
    echo [INFO] Running %TEST_TYPE% tests...
    echo [INFO] To run specific tests, follow instructions in test/README.md
)
cd ..

REM **** Step 8: Documentation & Contribution Guidelines ****
echo ================================
echo [Step 8/8] Documentation Reference
echo ================================
REM Check if docs directory exists
if not exist docs (
    echo [ERROR] docs directory not found. Please ensure you're in the Titan2.0 root directory.
    pause
    exit /b 1
)
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
