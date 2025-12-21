#!/usr/bin/env bash
# Launch SATCN GRMR-V3 Test GUI
# This script launches the GRMR-V3 test GUI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "================================================"
echo " GRMR-V3 Test GUI"
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

# Check if SATCN with GRMR support is installed
if ! python3 -c "import satcn.gui.grmr_v3_test_gui" 2>/dev/null; then
    echo "WARNING: SATCN with GRMR and GUI support not installed!"
    echo "Installing now..."
    echo ""
    cd "$PROJECT_ROOT"
    pip install -e ".[grmr,gui]"
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Installation failed!"
        echo "Please check the error messages above."
        exit 1
    fi
    echo ""
    echo "Installation complete!"
    echo ""
fi

# Launch the GRMR-V3 Test GUI
echo "Starting GRMR-V3 Test GUI..."
echo ""
python3 -m satcn.gui.grmr_v3_test_gui

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "================================================"
    echo "ERROR: Failed to launch GUI"
    echo "================================================"
    exit 1
fi
