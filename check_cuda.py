#!/usr/bin/env python3
"""
CUDA Diagnostic Script - Check PyTorch and GPU availability
"""

import sys

print("=" * 60)
print("CUDA Availability Diagnostic")
print("=" * 60)

# Check Python version
print(f"\nPython version: {sys.version}")

# Check if torch is installed
try:
    import torch
    print(f"\n✓ PyTorch installed: version {torch.__version__}")
except ImportError:
    print("\n✗ PyTorch not installed!")
    print("  Install with: pip install torch torchvision torchaudio")
    sys.exit(1)

# Check CUDA availability in PyTorch
print(f"\nCUDA available in PyTorch: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"✓ CUDA detected!")
    print(f"  CUDA version: {torch.version.cuda}")
    print(f"  Number of GPUs: {torch.cuda.device_count()}")

    for i in range(torch.cuda.device_count()):
        print(f"\n  GPU {i}: {torch.cuda.get_device_name(i)}")
        props = torch.cuda.get_device_properties(i)
        print(f"    Total memory: {props.total_memory / 1024**3:.2f} GB")
        print(f"    Compute capability: {props.major}.{props.minor}")
else:
    print("✗ CUDA NOT detected by PyTorch")
    print("\nPossible reasons:")
    print("  1. CPU-only PyTorch installed (most likely)")
    print("  2. NVIDIA drivers not installed")
    print("  3. CUDA toolkit not installed")
    print("  4. PyTorch CUDA version doesn't match system CUDA")

# Check PyTorch build info
print(f"\nPyTorch build info:")
print(f"  Built with CUDA: {torch.version.cuda is not None}")
if torch.version.cuda:
    print(f"  CUDA version: {torch.version.cuda}")
else:
    print(f"  ⚠ This is a CPU-only build!")

# Check if NVIDIA GPU exists at system level
print("\n" + "=" * 60)
print("System GPU Check")
print("=" * 60)

try:
    import subprocess
    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print("\n✓ nvidia-smi output:")
        print(result.stdout)
    else:
        print("\n✗ nvidia-smi failed (NVIDIA drivers may not be installed)")
except FileNotFoundError:
    print("\n✗ nvidia-smi not found (NVIDIA drivers not installed)")
except Exception as e:
    print(f"\n⚠ Error running nvidia-smi: {e}")

# Recommendations
print("\n" + "=" * 60)
print("Recommendations")
print("=" * 60)

if not torch.cuda.is_available():
    print("\nTo enable GPU support:")
    print("\n1. Check NVIDIA drivers are installed:")
    print("   nvidia-smi")
    print("\n2. Reinstall PyTorch with CUDA support:")
    print("   pip uninstall torch torchvision torchaudio")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    print("\n   (cu118 = CUDA 11.8, use cu121 for CUDA 12.1, etc.)")
    print("\n3. Verify CUDA is detected:")
    print("   python check_cuda.py")
else:
    print("\n✓ Your GPU is ready to use!")
    print("  The T5 model will automatically use your GPU for inference.")
    print("  Expected speed: 0.5-2 seconds per sentence (vs 5-30s on CPU)")
