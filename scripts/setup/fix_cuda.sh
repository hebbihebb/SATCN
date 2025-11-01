#!/bin/bash
# Fix CUDA support for PyTorch - Install GPU-enabled version

set -e

echo "=========================================="
echo "PyTorch CUDA Fix Script"
echo "=========================================="

# Check if nvidia-smi exists
if ! command -v nvidia-smi &> /dev/null; then
    echo ""
    echo "✗ nvidia-smi not found!"
    echo "  NVIDIA drivers are not installed or not in PATH."
    echo "  Please install NVIDIA drivers first."
    exit 1
fi

# Get CUDA version from nvidia-smi
echo ""
echo "1. Checking system CUDA version..."
CUDA_VERSION=$(nvidia-smi | grep "CUDA Version" | awk '{print $9}' | cut -d. -f1,2)
echo "   Detected CUDA: $CUDA_VERSION"

# Determine PyTorch CUDA version
if [[ $(echo "$CUDA_VERSION >= 12.1" | bc -l) -eq 1 ]]; then
    TORCH_CUDA="cu121"
    echo "   Will install PyTorch with CUDA 12.1 support"
elif [[ $(echo "$CUDA_VERSION >= 11.8" | bc -l) -eq 1 ]]; then
    TORCH_CUDA="cu118"
    echo "   Will install PyTorch with CUDA 11.8 support"
else
    TORCH_CUDA="cu118"
    echo "   ⚠ CUDA version is older, will try CUDA 11.8 build"
fi

# Show GPU info
echo ""
echo "2. GPU Information:"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

# Confirm with user
echo ""
echo "=========================================="
echo "This will:"
echo "  1. Uninstall current PyTorch (CPU-only)"
echo "  2. Install PyTorch with CUDA support ($TORCH_CUDA)"
echo "  3. Download ~2-3 GB of packages"
echo "=========================================="
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo ""
    echo "3. Activating virtual environment..."
    source venv/bin/activate
    echo "   ✓ Using: $VIRTUAL_ENV"
elif [ -n "$VIRTUAL_ENV" ]; then
    echo ""
    echo "3. Using existing virtual environment: $VIRTUAL_ENV"
else
    echo ""
    echo "⚠ No virtual environment detected!"
    echo "  Installing to system Python (not recommended)"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled. Create a venv first: python -m venv venv"
        exit 0
    fi
fi

# Uninstall existing PyTorch
echo ""
echo "4. Removing CPU-only PyTorch..."
pip uninstall -y torch torchvision torchaudio 2>/dev/null || true
echo "   ✓ Uninstalled"

# Install CUDA-enabled PyTorch
echo ""
echo "5. Installing PyTorch with CUDA support..."
echo "   This will download ~2-3 GB..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/$TORCH_CUDA

echo ""
echo "=========================================="
echo "6. Verifying CUDA support..."
echo "=========================================="
python check_cuda.py

echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "Your GPU is now ready for T5 inference!"
echo ""
echo "Test it:"
echo "  python test_t5_integration.py"
echo ""
echo "Expected performance:"
echo "  - CPU: 5-30 seconds per sentence"
echo "  - GPU: 0.5-2 seconds per sentence (10-50x faster!)"
echo ""
