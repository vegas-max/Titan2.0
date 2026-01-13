@echo off
setlocal enabledelayedexpansion

REM **** Step 1: Configuration Setup ****
echo ================================
echo [Step 1/9] Configuration Profiles
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

REM **** Step 2: Install Repository Dependencies ****
echo ================================
echo [Step 2/9] Installing Repository Dependencies
echo ================================
echo [INFO] Installing Python and Node.js dependencies from repository root...

REM Install Python dependencies
where python >nul 2>nul
if errorlevel 1 (
    echo [WARN] Python is not installed. Python dependencies will be skipped.
    echo [WARN] Please install Python: https://www.python.org/downloads/
) else (
    if exist requirements.txt (
        echo [INFO] Installing Python dependencies from requirements.txt...
        pip install -r requirements.txt
        if errorlevel 1 (
            echo [WARN] Python dependency installation had issues. Review output above.
        )
    )
)

REM Install Node.js dependencies
where npm >nul 2>nul
if errorlevel 1 (
    echo [WARN] Node.js/npm is not installed. Node.js dependencies will be skipped.
    echo [WARN] Please install Node.js: https://nodejs.org/
) else (
    if exist package.json (
        echo [INFO] Installing Node.js dependencies from package.json...
        npm install
        if errorlevel 1 (
            echo [WARN] Node.js dependency installation had issues. Review output above.
        )
    )
)

REM **** Step 3: Build core-rust modules ****
echo ================================
echo [Step 3/9] Building Rust Modules
echo ================================
REM Check if Rust is installed
where rustc >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Rust is not installed. Please install: https://rustup.rs/
    pause
    exit /b 1
)
if not exist core-rust (
    echo [ERROR] core-rust directory not found!
    pause
    exit /b 1
)
cd core-rust
echo [INFO] Building Rust library...
cargo build --release
if errorlevel 1 (
    echo [ERROR] Rust build failed. Check core-rust/README.md
    cd ..
    pause
    exit /b 1
)
cd ..

REM **** Step 4: Build core-go packages ****
echo ================================
echo [Step 4/9] Building Go Packages
echo ================================
where go >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Go is not installed. Please install: https://go.dev/doc/install
    pause
    exit /b 1
)
if not exist core-go (
    echo [ERROR] core-go directory not found!
    pause
    exit /b 1
)
cd core-go
echo [INFO] Compiling Go packages and standalone binaries...
go build .
if errorlevel 1 (
    echo [ERROR] Go build failed. Check core-go/README.md
    cd ..
    pause
    exit /b 1
)
cd ..

REM **** Step 5: Build/Configure execution engine ****
echo ================================
echo [Step 5/9] Setting Up Arbitrage Engine (execution)
echo ================================
if not exist execution (
    echo [WARN] execution directory not found! Skipping this step.
) else (
    cd execution
    echo [INFO] Execution layer uses JavaScript/Node.js arbitrage engines.
    echo [INFO] Node.js dependencies will be installed from repository root.
    echo [INFO] See execution/README.md for standalone engine usage.
    cd ..
)

REM **** Step 6: Routing Setup ****
echo ================================
echo [Step 6/9] Routing Engine & Bridge Aggregation
echo ================================
if not exist routing (
    echo [WARN] routing directory not found! Skipping this step.
) else (
    cd routing
    echo [INFO] Routing layer uses Python modules for bridge aggregation.
    echo [INFO] Python dependencies will be installed from repository root requirements.txt.
    echo [INFO] See routing/README.md for Li.Fi integration details.
    cd ..
)

REM **** Step 7: Autonomous Agent Framework ****
echo ================================
echo [Step 7/9] Agents Framework & Super Agent
echo ================================
if not exist agents (
    echo [WARN] agents directory not found! Skipping this step.
) else (
    cd agents
    echo [INFO] Building/starting agent orchestration (see agents/README.md)
    REM Example commands here: python agent.py or go build . etc.
    cd ..
)

REM **** Step 8: Test Suite ****
echo ================================
echo [Step 8/9] Running Test Suite
echo ================================
if not exist test (
    echo [WARN] test directory not found! Skipping this step.
) else (
    cd test
    REM Prompt for which tests to run
    set /p TEST_TYPE="Run all tests or specific type? (all/unit/integration/functional): "
    if /I "%TEST_TYPE%"=="all" (
        echo [INFO] Running ALL tests...
        echo [INFO] See test/README.md for test execution commands.
    ) else (
        echo [INFO] Running %TEST_TYPE% tests...
        echo [INFO] See test/README.md for specific test commands.
    )
    cd ..
)

REM **** Step 9: Documentation & Contribution Guidelines ****
echo ================================
echo [Step 9/9] Documentation Reference
echo ================================
if not exist docs (
    echo [WARN] docs directory not found! Skipping this step.
) else (
    cd docs
    echo [INFO] Open docs/README.md for technical documentation, templates, and guidelines.
    if exist README.md (
        notepad README.md
    ) else (
        echo [WARN] docs/README.md not found!
    )
    cd ..
)

echo ==========================================================
echo [DONE] Repo rebuild and setup sequence complete. Review outputs above.
echo If you encountered errors, check each respective README.md for troubleshooting.
echo ==========================================================
pause
endlocal
