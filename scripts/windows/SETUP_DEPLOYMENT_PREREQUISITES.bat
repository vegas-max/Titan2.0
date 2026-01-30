@echo off
REM ==============================================================================
REM TITAN 2.0 - Interactive Deployment Prerequisites Setup (Windows)
REM ==============================================================================
REM This script guides you through collecting all prerequisite variables needed
REM for deploying TITAN 2.0
REM
REM Usage: Double-click this file or run from command prompt
REM ==============================================================================

title TITAN 2.0 - Deployment Prerequisites Setup

color 0B
cls

echo.
echo ========================================================================
echo           TITAN 2.0 - Deployment Prerequisites Setup Wizard
echo ========================================================================
echo.
echo This wizard will help you collect all the information needed to deploy
echo TITAN 2.0 to any environment (Google Colab, Oracle Cloud, Local, etc.)
echo.
echo You can skip optional fields by pressing Enter.
echo.
echo ========================================================================
echo.
pause

REM Check if we're in the Titan2.0 directory
if not exist "package.json" (
    echo.
    echo [ERROR] This script must be run from the Titan2.0 directory
    echo.
    echo Please:
    echo   1. Open Command Prompt or PowerShell
    echo   2. Navigate to the Titan2.0 folder: cd path\to\Titan2.0
    echo   3. Run this script again
    echo.
    pause
    exit /b 1
)

REM Check if WSL is available for running the bash script
where wsl >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [INFO] WSL detected. Running Linux version of setup script...
    echo.
    wsl bash ./deployment_prerequisites_setup.sh
    goto :end
)

REM If WSL not available, show instructions for manual setup
echo.
echo ========================================================================
echo                    WINDOWS SETUP INSTRUCTIONS
echo ========================================================================
echo.
echo WSL (Windows Subsystem for Linux) is not installed or not available.
echo.
echo You have two options:
echo.
echo OPTION 1: Install WSL and run the automated script (Recommended)
echo   1. Open PowerShell as Administrator
echo   2. Run: wsl --install
echo   3. Restart your computer
echo   4. Run this script again
echo.
echo OPTION 2: Manual setup with Google Colab (Easier for Windows users)
echo   1. Use the Google Colab setup (no installation needed)
echo   2. Double-click LAUNCH_GOOGLE_COLAB.bat
echo   3. Follow the interactive notebook
echo.
echo OPTION 3: Manual .env file creation
echo   1. Copy .env.example to .env
echo   2. Edit .env with Notepad
echo   3. Fill in your values using DEPLOYMENT_PREREQUISITES_CHECKLIST.md
echo.
echo ========================================================================
echo.
echo [?] What would you like to do?
echo.
echo   1 - Install WSL (requires admin privileges and restart)
echo   2 - Open Google Colab setup (easiest option)
echo   3 - Open .env.example for manual editing
echo   4 - Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto :install_wsl
if "%choice%"=="2" goto :launch_colab
if "%choice%"=="3" goto :manual_edit
if "%choice%"=="4" goto :end

echo Invalid choice. Exiting.
goto :end

:install_wsl
echo.
echo [INFO] Opening PowerShell to install WSL...
echo.
echo IMPORTANT:
echo   - You will need Administrator privileges
echo   - Your computer will need to restart
echo   - After restart, run this script again
echo.
pause
start powershell -Command "Start-Process powershell -Verb RunAs -ArgumentList 'wsl --install'"
goto :end

:launch_colab
echo.
echo [INFO] Launching Google Colab setup...
echo.
if exist "LAUNCH_GOOGLE_COLAB.bat" (
    call LAUNCH_GOOGLE_COLAB.bat
) else (
    echo [ERROR] LAUNCH_GOOGLE_COLAB.bat not found
    echo.
    echo Please open your browser and go to:
    echo   https://colab.research.google.com/
    echo.
    echo Then upload the file: Titan_Google_Colab.ipynb
    echo.
    start https://colab.research.google.com/
)
goto :end

:manual_edit
echo.
echo [INFO] Opening .env.example for manual editing...
echo.
if exist ".env.example" (
    if exist ".env" (
        echo.
        echo [WARNING] .env file already exists!
        set /p overwrite="Do you want to overwrite it? (yes/no): "
        if /i not "%overwrite%"=="yes" (
            echo.
            echo [INFO] Opening existing .env file instead...
            notepad .env
            goto :after_edit
        )
    )
    copy .env.example .env
    echo.
    echo [SUCCESS] Created .env file from template
    echo.
    echo Now opening .env in Notepad for editing...
    echo.
    echo INSTRUCTIONS:
    echo   1. Fill in your values (see DEPLOYMENT_PREREQUISITES_CHECKLIST.md)
    echo   2. Save the file (Ctrl+S)
    echo   3. Close Notepad
    echo.
    notepad .env
    :after_edit
    echo.
    echo [SUCCESS] .env file updated!
    echo.
    echo Next steps:
    echo   1. Review your configuration
    echo   2. Run: setup.bat (for local installation)
    echo      OR upload .env to Google Colab
    echo      OR copy .env to your cloud server
    echo.
) else (
    echo [ERROR] .env.example not found
    echo Please ensure you're in the Titan2.0 directory
)
goto :end

:end
echo.
echo ========================================================================
echo.
echo For more information, see:
echo   - GOOGLE_COLAB_STEP_BY_STEP.md (Step-by-step Colab guide)
echo   - DEPLOYMENT_PREREQUISITES_CHECKLIST.md (Quick reference)
echo   - QUICKSTART.md (Local installation guide)
echo   - README.md (Complete documentation)
echo.
echo ========================================================================
echo.
pause
