#!/usr/bin/env bash
# Launch SATCN Pipeline GUI
# This script provides easy access to the GUI on Linux/Mac

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "================================================"
echo " SATCN Pipeline GUI"
echo "================================================"
echo ""

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found"
    echo ""
    echo "Please install Python 3.11+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt-get install python3"
    echo "  Fedora:        sudo dnf install python3"
    echo "  macOS:         brew install python3"
    echo ""
    exit 1
fi

# Display Python version
echo "Using Python:"
python3 --version
echo ""

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python version: $PYTHON_VERSION"

# Warn if Python 3.13+ (GPU builds may not be available)
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 13) else 1)" 2>/dev/null; then
    echo "⚠️  WARNING: Python 3.13+ detected"
    echo "   GPU builds may not be available yet"
    echo ""
fi

# Check if SATCN is installed
if ! python3 -c "import satcn" 2>/dev/null; then
    echo "WARNING: SATCN package not installed!"
    echo "Installing now with GUI support..."
    echo ""
    cd "$PROJECT_ROOT"
    pip install -e ".[gui]"
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

# Launch the GUI
echo "Starting SATCN Pipeline GUI..."
echo ""
python3 -m satcn.gui.satcn_gui

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "================================================"
    echo "ERROR: An error occurred"
    echo "================================================"
    exit 1
fi
