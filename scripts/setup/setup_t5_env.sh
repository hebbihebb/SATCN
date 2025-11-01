#!/bin/bash
# Setup script for T5 integration testing

set -e

echo "=========================================="
echo "T5 Integration - Environment Setup"
echo "=========================================="

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "1. Creating virtual environment..."
    python -m venv venv
    echo "   ✓ Virtual environment created"
else
    echo ""
    echo "1. Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "2. Activating virtual environment..."
source venv/bin/activate
echo "   ✓ Activated: $VIRTUAL_ENV"

# Upgrade pip
echo ""
echo "3. Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "   ✓ pip upgraded to $(pip --version)"

# Install existing requirements
echo ""
echo "4. Installing existing project requirements..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "   ✓ Installed: Markdown, language-tool-python, etc."
else
    echo "   ⚠ requirements.txt not found, skipping"
fi

# Install T5 requirements
echo ""
echo "5. Installing T5 requirements (this will take a while)..."
echo "   - transformers (Hugging Face)"
echo "   - torch (PyTorch - ~2-3 GB download)"
echo "   - accelerate (model optimization)"
echo "   - sentencepiece (tokenizer)"
echo ""
echo "   This may take 5-10 minutes depending on your connection..."
pip install transformers>=4.30.0 torch>=2.0.0 accelerate>=0.20.0 sentencepiece>=0.1.99 protobuf>=3.20.0

echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "To use this environment:"
echo "  source venv/bin/activate"
echo ""
echo "To test T5 integration:"
echo "  python test_t5_integration.py"
echo ""
echo "To deactivate when done:"
echo "  deactivate"
echo ""
