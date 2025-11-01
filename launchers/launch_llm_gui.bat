@echo off
REM Launch SATCN LLM GUI with GPU support
REM Uses .venv-gpu environment for CUDA-enabled llama-cpp-python

echo Starting SATCN LLM GUI (GPU-enabled)...
echo.

REM Set CUDA environment variables (required for GPU acceleration)
set "CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0"
set "CUDA_BIN=%CUDA_PATH%\bin"

if exist "%CUDA_PATH%" (
    echo Setting CUDA_PATH: %CUDA_PATH%
    echo Adding CUDA bin to PATH: %CUDA_BIN%
    set "PATH=%CUDA_BIN%;%PATH%"
) else (
    echo WARNING: CUDA not found at %CUDA_PATH%
    echo GPU acceleration may not work!
)
echo.

REM Check if .venv-gpu exists
if not exist "%~dp0..\.venv-gpu\Scripts\python.exe" (
    echo ERROR: .venv-gpu environment not found!
    echo Please create it with: python -m venv .venv-gpu
    echo Then run: launchers\setup_gpu_env.bat
    echo.
    echo Falling back to default Python environment...
    echo.
    python -m satcn.gui.llm_gui
) else (
    echo Using GPU environment: .venv-gpu
    echo.

    REM Check if satcn package is installed
    "%~dp0..\.venv-gpu\Scripts\python.exe" -c "import satcn" 2>nul
    if errorlevel 1 (
        echo WARNING: SATCN package not installed in .venv-gpu!
        echo Installing now...
        echo.
        cd /d "%~dp0.."
        "%~dp0..\.venv-gpu\Scripts\pip.exe" install -e . --quiet
        echo Installation complete.
        echo.
    )

    "%~dp0..\.venv-gpu\Scripts\python.exe" -m satcn.gui.llm_gui
)

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to close...
    pause > nul
)
