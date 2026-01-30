@echo off
REM ==============================================================================
REM TITAN 2.0 - Google Colab Launcher
REM ==============================================================================
REM Opens the Google Colab notebook for easy setup and deployment

echo.
echo ============================================================
echo    TITAN 2.0 - Google Colab Setup
echo ============================================================
echo.
echo This will open the TITAN Google Colab notebook in your browser.
echo.
echo The notebook provides:
echo   - One-click system installation
echo   - Interactive configuration interface
echo   - Full TITAN system (Brain + Bot + Dashboard)
echo   - Cloud deployment configuration
echo   - Oracle Free Tier deployment wizard
echo.
echo ============================================================
echo.

REM Check if the notebook file exists
if not exist "Titan_Google_Colab.ipynb" (
    echo Error: Titan_Google_Colab.ipynb not found
    echo Please ensure you're in the Titan2.0 directory
    pause
    exit /b 1
)

echo Opening Google Colab...
echo.
echo Instructions:
echo   1. Upload Titan_Google_Colab.ipynb to Google Colab
echo   2. Follow the step-by-step cells in the notebook
echo   3. Configure your API keys when prompted
echo   4. Start the system and access the dashboard
echo.
echo Alternatively, you can:
echo   - Go to https://colab.research.google.com/
echo   - Click "Upload" and select Titan_Google_Colab.ipynb
echo   - Or use the direct link (if shared publicly)
echo.

REM Open the local file (user will need to upload to Colab)
start "" "Titan_Google_Colab.ipynb"

echo.
echo Notebook file opened in default application.
echo Upload this file to Google Colab to get started.
echo.
pause
