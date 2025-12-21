@echo off
REM Setup .venv-gpu environment with SATCN package installed
REM This ensures the GPU-enabled tools can find the satcn module

echo ========================================
echo Setting up GPU environment for SATCN
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.11 or 3.12 from python.org
    echo (Note: GPU builds not yet available for Python 3.13)
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Using Python:
python --version
echo.

REM Warn about Python 3.13
python -c "import sys; exit(0 if sys.version_info >= (3, 13) else 1)" 2>nul
if not errorlevel 1 (
    echo WARNING: You are using Python 3.13+
    echo GPU builds of llama-cpp-python may not be available yet.
    echo Consider using Python 3.11 or 3.12 for GPU support.
    echo.
    echo Press any key to continue anyway, or Ctrl+C to cancel...
    pause > nul
    echo.
)

REM Check if .venv-gpu exists
if not exist "%~dp0..\.venv-gpu\Scripts\python.exe" (
    echo Creating .venv-gpu environment...
    cd /d "%~dp0.."
    python -m venv .venv-gpu
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo.
)

echo Installing SATCN package in editable mode...
cd /d "%~dp0.."
"%~dp0..\.venv-gpu\Scripts\pip.exe" install -e .
if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup complete!
echo You can now run launch_llm_gui.bat
echo ========================================
echo.
pause
