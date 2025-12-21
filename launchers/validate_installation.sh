#!/usr/bin/env bash
# SATCN Installation Validator
# Wrapper script for the validation tool

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "================================================"
echo " SATCN Installation Validator"
echo "================================================"
echo ""

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: python3 not found"
    echo ""
    echo "Please install Python 3.11+ first"
    exit 1
fi

# Run the validation script
python3 "$PROJECT_ROOT/scripts/validate_installation.py"
