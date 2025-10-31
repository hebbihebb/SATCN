@echo off
REM Launch SATCN Pipeline GUI
REM This batch file provides easy double-click access to the GUI

echo Starting SATCN Pipeline GUI...
python -m satcn.gui.satcn_gui

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to close...
    pause > nul
)
