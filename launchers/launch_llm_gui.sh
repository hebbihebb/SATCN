#!/usr/bin/env bash
# Launch SATCN LLM GUI
# This script launches the LLM model management GUI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "================================================"
echo " SATCN LLM GUI (Model Management)"
echo "================================================"
echo ""

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found"
    echo ""
    echo "Please install Python 3.11+ using your package manager"
    exit 1
fi

echo "Using Python:"
python3 --version
echo ""

# Check if .venv-gpu exists
VENV_GPU="$PROJECT_ROOT/.venv-gpu"
if [ -d "$VENV_GPU" ] && [ -f "$VENV_GPU/bin/python3" ]; then
    echo "Using GPU environment: .venv-gpu"
    echo ""

    # Check if satcn is installed in venv
    if ! "$VENV_GPU/bin/python3" -c "import satcn" 2>/dev/null; then
        echo "WARNING: SATCN package not installed in .venv-gpu!"
        echo "Installing now..."
        echo ""
        cd "$PROJECT_ROOT"
        "$VENV_GPU/bin/pip" install -e ".[gui]" --quiet
        echo "Installation complete."
        echo ""
    fi

    # Launch with venv python
    "$VENV_GPU/bin/python3" -m satcn.gui.llm_gui
else
    echo "Note: .venv-gpu not found, using system Python"
    echo "For GPU support, run: bash scripts/setup/setup_t5_env.sh"
    echo ""

    # Check if satcn is installed
    if ! python3 -c "import satcn" 2>/dev/null; then
        echo "WARNING: SATCN package not installed!"
        echo "Installing now with GUI support..."
        echo ""
        cd "$PROJECT_ROOT"
        pip install -e ".[gui]"
        if [ $? -ne 0 ]; then
            echo ""
            echo "ERROR: Installation failed!"
            exit 1
        fi
        echo ""
        echo "Installation complete!"
        echo ""
    fi

    # Launch with system python
    python3 -m satcn.gui.llm_gui
fi

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "================================================"
    echo "ERROR: An error occurred"
    echo "================================================"
    exit 1
fi
