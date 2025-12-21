# GPU Setup Guide for SATCN

## Overview

This guide covers setting up GPU acceleration for llama-cpp-python to speed up grammar correction processing. GPU acceleration can provide 3-7x speedup over CPU-only processing.

## Status

✅ **GPU compilation successful** - CUDA 13.0 build completed
✅ **GPU detection working** - NVIDIA GeForce RTX 4060 detected
⚠️ **Model compatibility** - T5 models have runtime issues with GPU inference
✅ **CPU performance** - Excellent baseline at 438 words/minute

## Requirements

### Hardware
- NVIDIA GPU with CUDA support (Compute Capability 7.0+)
- 8GB+ VRAM recommended for larger models
- Tested with: NVIDIA GeForce RTX 4060 Laptop GPU (8GB VRAM)

### Software (Windows)
- Windows 10/11
- Visual Studio 2022 Community Edition with C++ tools
  - Desktop development with C++ workload
  - MSVC v142 or later build tools
  - Windows 10/11 SDK
- CUDA Toolkit 13.0 or later
  - Download from: https://developer.nvidia.com/cuda-downloads
  - **Important:** Visual Studio 2022 requires CUDA 12.4+ or CUDA 13.0+
  - CUDA 12.1 and earlier are NOT compatible with VS 2022's latest compiler
- Python 3.11 (Python 3.13 GPU builds not yet available)

### Software (Linux)
- Ubuntu 20.04+, Fedora 36+, or other modern Linux distribution
- Build tools: `gcc`, `g++`, `cmake`, `make`
- NVIDIA drivers (latest recommended)
- CUDA Toolkit 12.0 or later
  - Download from: https://developer.nvidia.com/cuda-downloads
- Python 3.11 or 3.12

## Installation Steps (Windows)

### 1. Install Prerequisites

1. **Install Visual Studio 2022 Community**
   ```powershell
   # Download from: https://visualstudio.microsoft.com/downloads/
   # During installation, select:
   # - Desktop development with C++
   # - MSVC v143 build tools
   # - Windows 11 SDK
   ```

2. **Install CUDA Toolkit 13.0**
   ```powershell
   # Download from: https://developer.nvidia.com/cuda-downloads
   # Choose: Windows -> x86_64 -> 11 -> exe (local)
   # Install with default options
   ```

3. **Install Python 3.11**
   ```powershell
   # Download from: https://www.python.org/downloads/
   # Install to: C:\Users\<username>\AppData\Local\Programs\Python\Python311
   ```

### 2. Create GPU Environment

```powershell
# Create Python 3.11 virtual environment
$py311 = "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
& $py311 -m venv .venv-gpu
```

### 3. Build llama-cpp-python with CUDA

```powershell
# Run the automated installation script
.\install_llama_cpp_cuda.ps1
```

This script will:
- Auto-detect your CUDA installation
- Configure Visual Studio build environment
- Set CMake flags for CUDA support
- Compile llama-cpp-python from source (~30-40 minutes)
- Test GPU availability

**Expected compilation time:** 30-40 minutes

### 4. Verify Installation

```powershell
# Activate GPU environment
.\.venv-gpu\Scripts\Activate.ps1

# Add CUDA DLLs to PATH
$env:PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64;$env:PATH"

# Test GPU support
python -c "from llama_cpp import Llama; print('✅ GPU support working!')"
```

---

## Installation Steps (Linux)

### 1. Check Prerequisites

```bash
# Check NVIDIA GPU
nvidia-smi
# Should show GPU name and driver version

# Check CUDA installation
nvcc --version
# Should show CUDA version
```

### 2. Install Build Tools

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install build-essential cmake python3-dev
```

**Fedora/RHEL:**
```bash
sudo dnf install gcc gcc-c++ cmake python3-devel
```

### 3. Install NVIDIA Drivers and CUDA (if not installed)

**Ubuntu:**
```bash
# Install NVIDIA drivers
sudo apt-get install nvidia-driver-535

# Install CUDA Toolkit
# Download from: https://developer.nvidia.com/cuda-downloads
# Or use package manager:
sudo apt-get install nvidia-cuda-toolkit

# Verify
nvidia-smi
nvcc --version
```

**Fedora:**
```bash
# Add RPM Fusion repository
sudo dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm

# Install NVIDIA drivers
sudo dnf install akmod-nvidia xorg-x11-drv-nvidia-cuda

# Install CUDA
# Download from: https://developer.nvidia.com/cuda-downloads
```

### 4. Create Virtual Environment (Optional but Recommended)

```bash
# Create venv
python3 -m venv .venv-gpu

# Activate
source .venv-gpu/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 5. Build llama-cpp-python with CUDA

```bash
# Install with CUDA support
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

# This will compile from source (~10-20 minutes on Linux)
```

**Alternative: Use the setup script**

```bash
# Use the T5 environment setup script (includes CUDA support)
bash scripts/setup/setup_t5_env.sh
```

### 6. Set CUDA Environment Variables

```bash
# Add to ~/.bashrc or ~/.zshrc for persistence
export CUDA_PATH=/usr/local/cuda
export PATH=$CUDA_PATH/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_PATH/lib64:$LD_LIBRARY_PATH

# Reload shell or source the file
source ~/.bashrc
```

### 7. Verify Installation

```bash
# Test GPU support
python3 -c "from llama_cpp import Llama; print('✅ GPU support working!')"

# Monitor GPU usage while testing
watch -n 1 nvidia-smi
```

---

## Usage

### Always Set CUDA Path

Before using GPU-accelerated models, add CUDA to your PATH:

```powershell
$env:PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64;$env:PATH"
```

### Loading Models with GPU

```python
from llama_cpp import Llama

model = Llama(
    model_path="path/to/model.gguf",
    n_ctx=4096,
    n_gpu_layers=35,  # Number of layers to offload to GPU
    verbose=False
)
```

**GPU Layer Guidelines:**
- Start with `n_gpu_layers=10` for testing
- Increase gradually based on VRAM availability
- Monitor GPU memory usage with `nvidia-smi`
- For 8GB VRAM: typically 20-35 layers depending on model size

## Known Issues

### T5 Model Runtime Crash

**Issue:** T5-based models (like flan-t5-large-grammar-synthesis) load successfully with GPU layers but crash during inference with "access violation" errors.

**Status:** Under investigation. This appears to be a compatibility issue between:
- llama-cpp-python 0.3.16
- Python 3.11
- T5 model architecture on CUDA

**Workaround:** Use CPU-only mode for T5 models (still achieves 438 words/minute)

**Models Tested:**
- ❌ T5-based: flan-t5-large-grammar-synthesis (GPU crash)
- ✅ CPU fallback: flan-t5-large-grammar-synthesis (438 words/min)

### CUDA Version Compatibility

**Critical:** Visual Studio 2022 (MSVC 19.44) requires CUDA 12.4+ or CUDA 13.0+

**Error with CUDA 12.1:**
```
error: "STL1002: Unexpected compiler version, expected CUDA 12.4 or newer"
```

**Solution:** Upgrade to CUDA 13.0

## Performance Expectations

### CPU Baseline (Python 3.13, no GPU)
- **Speed:** 438 words/minute (7 words/second)
- **Time per sentence:** ~0.73 seconds
- **50 paragraphs:** ~6.6 minutes
- **90KB document:** ~20-30 minutes

### GPU Target (Not yet achieved with T5)
- **Expected speed:** 1,500-3,000+ words/minute
- **Expected speedup:** 3-7x faster than CPU
- **50 paragraphs:** ~1-2 minutes (estimated)
- **90KB document:** ~5-10 minutes (estimated)

## Troubleshooting

### Missing DLL: cublas64_13.dll

**Symptom:**
```
FileNotFoundError: Could not find module 'llama.dll' (or one of its dependencies)
```

**Solution:**
```powershell
$env:PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64;$env:PATH"
```

### Compilation Failures

**Missing source files during build:**
- Usually transient - try running `.\install_llama_cpp_cuda.ps1` again
- Ensure adequate disk space in `%TEMP%` directory

**Visual Studio not found:**
```powershell
# Verify installation
Test-Path "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"
```

### GPU Not Detected

Check GPU and CUDA installation:
```powershell
# Check GPU
nvidia-smi

# Check CUDA version
nvcc --version
```

## Environment Comparison

| Feature | .venv (CPU) | .venv-gpu (GPU) |
|---------|-------------|-----------------|
| Python Version | 3.13.4 | 3.11.0 |
| llama-cpp-python | 0.3.16 (CPU) | 0.3.16 (CUDA) |
| GPU Support | ❌ No | ✅ Yes |
| T5 Compatible | ✅ Yes | ⚠️ Crashes |
| Performance | 438 wpm | TBD |
| Compilation | Pre-built | From source |
| Build Time | Instant | ~40 minutes |

## Recommendations

### Current Best Practice

**For production use:** Stick with CPU environment (`.venv`) until T5 GPU issues are resolved.

**Reasons:**
1. ✅ CPU performance is already excellent (438 words/minute)
2. ✅ Reliable and stable
3. ✅ Python 3.13 support
4. ✅ No CUDA dependencies
5. ✅ Works overnight for large documents

**Example:** A 90,000-word novel takes ~3.4 hours on CPU - perfectly reasonable for batch processing.

### Future GPU Testing

When testing GPU with different models:
1. Start with Llama 2/3 or Mistral GGUF models (better GPU support)
2. Avoid T5 architecture until runtime issues are fixed
3. Monitor VRAM usage during inference
4. Compare CPU vs GPU performance on real workloads

## References

- [llama-cpp-python GitHub](https://github.com/abetlen/llama-cpp-python)
- [CUDA Toolkit Download](https://developer.nvidia.com/cuda-downloads)
- [Visual Studio 2022 Download](https://visualstudio.microsoft.com/downloads/)
- [GGUF Model Format](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md)

## Contributing

If you successfully resolve the T5 GPU runtime issue, please:
1. Document the solution
2. Update this guide
3. Share configuration details (Python version, CUDA version, model file)
