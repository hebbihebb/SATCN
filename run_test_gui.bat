@echo off
REM Activate the CUDA-enabled venv and launch the SATCN pipeline test GUI
cd /d %~dp0
call .venv310\Scripts\activate.bat

echo Checking dependencies...

REM Check and install each dependency individually
python -c "import ebooklib" 2>NUL
if errorlevel 1 (
    echo Installing missing dependency: ebooklib
    pip install ebooklib
)

python -c "import bs4" 2>NUL
if errorlevel 1 (
    echo Installing missing dependency: beautifulsoup4
    pip install beautifulsoup4
)

python -c "import markdown" 2>NUL
if errorlevel 1 (
    echo Installing missing dependency: markdown
    pip install markdown
)

python -c "import language_tool_python" 2>NUL
if errorlevel 1 (
    echo Installing missing dependency: language_tool_python
    pip install language_tool_python
)

python -c "import spellchecker" 2>NUL
if errorlevel 1 (
    echo Installing missing dependency: pyspellchecker
    pip install pyspellchecker
)

python -c "import num2words" 2>NUL
if errorlevel 1 (
    echo Installing missing dependency: num2words
    pip install num2words
)

python -c "import torch" 2>NUL
if errorlevel 1 (
    echo Installing missing dependency: torch
    pip install torch
)

python -c "import transformers" 2>NUL
if errorlevel 1 (
    echo Installing missing dependency: transformers
    pip install transformers
)

REM Check for tkinter (should be included with Python, but check)
python -c "import tkinter" 2>NUL
if errorlevel 1 (
    echo ERROR: tkinter is not installed. Please install it with your Python distribution.
    pause
    exit /b 1
)

echo All dependencies are installed. Launching GUI...
python tools\pipeline_test_gui.py
