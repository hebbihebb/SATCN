@echo off
REM Launch SATCN LLM GUI
REM LLM-focused interface with model management and HuggingFace downloader

echo Starting SATCN LLM GUI...
python -m satcn.gui.llm_gui

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to close...
    pause > nul
)
