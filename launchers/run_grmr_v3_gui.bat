@echo off
REM GRMR-V3 Test GUI Launcher
REM This script launches the GRMR-V3 test GUI

echo ================================================
echo  GRMR-V3 Test GUI
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.11+ from python.org
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Using Python:
python --version
echo.

REM Check if SATCN package with GRMR support is installed
python -c "import satcn.gui.grmr_v3_test_gui" 2>nul
if errorlevel 1 (
    echo WARNING: SATCN with GRMR and GUI support not installed!
    echo Installing now...
    echo.
    cd /d "%~dp0.."
    pip install -e ".[grmr,gui]"
    if errorlevel 1 (
        echo.
        echo ERROR: Installation failed!
        echo Please check the error messages above.
        pause
        exit /b 1
    )
    echo.
    echo Installation complete!
    echo.
)

REM Launch the GRMR-V3 Test GUI
echo Starting GRMR-V3 Test GUI...
echo.
python -m satcn.gui.grmr_v3_test_gui

if errorlevel 1 (
    echo.
    echo ================================================
    echo ERROR: Failed to launch GUI
    echo ================================================
    echo.
    echo Press any key to close...
    pause > nul
)
