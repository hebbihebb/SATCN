@echo off
REM SATCN Installation Validator (Windows Wrapper)

echo ================================================
echo  SATCN Installation Validator
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.11+ from python.org
    pause
    exit /b 1
)

REM Run the validation script
cd /d "%~dp0.."
python scripts\validate_installation.py

echo.
pause
