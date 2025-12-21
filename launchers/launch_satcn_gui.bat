@echo off
REM Launch SATCN Pipeline GUI
REM This batch file provides easy double-click access to the GUI

echo ================================================
echo  SATCN Pipeline GUI
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

REM Check if SATCN package is installed
python -c "import satcn" 2>nul
if errorlevel 1 (
    echo WARNING: SATCN package not installed!
    echo Installing now with GUI support...
    echo.
    cd /d "%~dp0.."
    pip install -e ".[gui]"
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

REM Launch the GUI
echo Starting SATCN Pipeline GUI...
echo.
python -m satcn.gui.satcn_gui

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo ================================================
    echo ERROR: An error occurred
    echo ================================================
    echo.
    echo Press any key to close...
    pause > nul
)
