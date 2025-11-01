@echo off
REM Setup .venv-gpu environment with SATCN package installed
REM This ensures the GUI can find the satcn module

echo ========================================
echo Setting up GPU environment for SATCN
echo ========================================
echo.

REM Check if .venv-gpu exists
if not exist "%~dp0..\.venv-gpu\Scripts\python.exe" (
    echo ERROR: .venv-gpu environment not found!
    echo Creating .venv-gpu now...
    cd /d "%~dp0.."
    python -m venv .venv-gpu
    echo.
)

echo Installing SATCN package in editable mode...
cd /d "%~dp0.."
"%~dp0..\.venv-gpu\Scripts\pip.exe" install -e .

echo.
echo ========================================
echo Setup complete!
echo You can now run launch_llm_gui.bat
echo ========================================
echo.
pause
