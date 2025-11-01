@echo off
REM GRMR-V3 GPU Test GUI Launcher
REM This script launches the GPU-enabled GRMR-V3 test GUI

echo ================================================
echo  GRMR-V3 GPU Test GUI
echo ================================================
echo.
echo Activating GPU-enabled environment (.venv)...
echo.

call .venv\Scripts\activate.bat

echo Starting GRMR-V3 Test GUI...
echo.

python tools\grmr_v3_test_gui.py

if errorlevel 1 (
    echo.
    echo ================================================
    echo ERROR: Failed to launch GUI
    echo ================================================
    pause
)
