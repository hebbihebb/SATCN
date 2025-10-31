# GRMR-V3 GPU Acceleration Setup Guide

**Date:** October 31, 2025  
**GPU:** NVIDIA GeForce RTX 4060 Laptop GPU  
**CUDA Version:** 13.0 (Driver)  
**Current Status:** CPU-only llama-cpp-python installed

## Quick Start (Try This First)

### Option A: Pre-built CUDA Wheel (Fastest)

Try installing a pre-built wheel with CUDA support:

```powershell
# Activate virtual environment
.venv\Scripts\activate

# Uninstall CPU-only version
pip uninstall llama-cpp-python -y

# Try installing pre-built CUDA wheel
pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121

# If that fails, try CUDA 12.4
pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124
```

**Test if GPU is working:**
```powershell
python test_grmr_v3_integration.py
```

Look for: "Using CUDA for GRMR-V3 inference (GPU acceleration)" instead of CPU warning.

---

## Option B: Install CUDA Toolkit + Build from Source (Most Reliable)

If pre-built wheels don't work or don't detect GPU, you'll need the CUDA Toolkit.

### Step 1: Download CUDA Toolkit

**For CUDA 12.1 (recommended for widest compatibility):**
- URL: https://developer.nvidia.com/cuda-12-1-0-download-archive
- Choose: Windows → x86_64 → 11 → exe (local)
- Size: ~3.5 GB download, ~8 GB installed

**For CUDA 12.4 (newer):**
- URL: https://developer.nvidia.com/cuda-12-4-0-download-archive

**For CUDA 13.0 (matches your driver, but may not be officially released yet):**
- Check: https://developer.nvidia.com/cuda-downloads

### Step 2: Install CUDA Toolkit

1. Run the downloaded installer
2. Choose "Custom" installation
3. Required components:
   - ✅ CUDA Toolkit
   - ✅ CUDA Development
   - ✅ Visual Studio Integration (if you have VS 2019/2022)
   - ⬜ CUDA Documentation (optional)
   - ⬜ CUDA Samples (optional)
   - ✅ NSight Systems (helpful for profiling, optional)

4. Installation directory (default): `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1\`

**Installation time:** ~10-15 minutes

### Step 3: Verify CUDA Installation

```powershell
# Check nvcc is available
nvcc --version

# Should show something like:
# Cuda compilation tools, release 12.1, V12.1.xxx
```

### Step 4: Rebuild llama-cpp-python with CUDA

```powershell
# Activate virtual environment
.venv\Scripts\activate

# Uninstall CPU-only version
pip uninstall llama-cpp-python -y

# Build with CUDA support
$env:CMAKE_ARGS="-DGGML_CUDA=on"
pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --verbose

# Note: This will take 5-10 minutes to compile
```

**Expected output:**
- CMake should detect CUDA
- You'll see CUDA compilation messages
- Build should complete successfully

### Step 5: Test GPU Acceleration

```powershell
# Run integration test
python test_grmr_v3_integration.py

# Run benchmark
python benchmark_grmr_vs_t5.py
```

**Expected results:**
- "Using CUDA for GRMR-V3 inference (GPU acceleration)"
- Model load time: ~3-5s (similar to CPU)
- **Inference speed: ~0.1-0.2s per sentence** (vs 0.84s on CPU)
- **5-10x speedup expected**

---

## Troubleshooting

### Issue: "Could not find nvcc"

**Solution:** CUDA Toolkit not in PATH. Add manually:

```powershell
# Add to PATH (adjust version number)
$env:Path += ";C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1\bin"

# Verify
nvcc --version

# Make permanent (optional):
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1\bin", "User")
```

### Issue: "CUDA Toolkit not found" during build

**Solution:** Set CUDA_PATH:

```powershell
$env:CUDA_PATH="C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1"
$env:CMAKE_ARGS="-DGGML_CUDA=on"
pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

### Issue: Build fails with Visual Studio errors

**Solution:** Install Visual Studio Build Tools:

1. Download: https://visualstudio.microsoft.com/downloads/
2. Install "Build Tools for Visual Studio 2019" or 2022
3. Required components:
   - Desktop development with C++
   - Windows 10/11 SDK
   - MSVC v142 or v143 compiler

### Issue: GPU not being used even after installation

**Check device in code:**
```python
from pipeline.filters.grmr_v3_filter import GRMRV3GrammarFilter

# Force CUDA
filter = GRMRV3GrammarFilter(device='cuda')

# Check if GPU layers are set
print(f"Using device: {filter.device}")
```

### Issue: Out of memory errors

**Solution:** Reduce context window or batch size:

```python
# Smaller context window
filter = GRMRV3GrammarFilter(n_ctx=2048)  # default is 4096

# Or use CPU fallback for large texts
filter = GRMRV3GrammarFilter(device='cpu')
```

---

## Performance Expectations

### Current (CPU-only on RTX 4060):
- Model load: 3.6s
- Inference: 0.84s per sentence
- Block processing: ~2s per block

### Expected with GPU (RTX 4060):
- Model load: 3-5s (similar)
- Inference: **0.08-0.15s per sentence** (5-10x faster)
- Block processing: **~0.2-0.4s per block** (5-10x faster)

### Expected Speedup by GPU:
- RTX 4060: 5-10x
- RTX 3080: 8-15x
- RTX 4090: 15-25x

---

## Quick Decision Guide

**Use Pre-built Wheels If:**
- ✅ You want to try GPU quickly without installing CUDA Toolkit
- ✅ Pre-built wheels are available for your CUDA version
- ✅ You don't need to customize the build

**Install CUDA Toolkit If:**
- ✅ Pre-built wheels don't work
- ✅ You need maximum performance
- ✅ You want to build other CUDA projects
- ✅ You're okay with ~8GB disk space + 15 min installation

---

## Rollback to CPU-only

If GPU acceleration causes issues:

```powershell
# Uninstall GPU version
pip uninstall llama-cpp-python -y

# Reinstall CPU-only
$env:CMAKE_ARGS=""
pip install llama-cpp-python numpy diskcache
```

---

## References

- llama-cpp-python: https://github.com/abetlen/llama-cpp-python
- CUDA Toolkit Downloads: https://developer.nvidia.com/cuda-downloads
- llama.cpp GPU docs: https://github.com/ggerganov/llama.cpp#cuda

---

**Next Steps After GPU Setup:**
1. Re-run benchmark: `python benchmark_grmr_vs_t5.py`
2. Update session report with GPU metrics
3. Compare CPU vs GPU performance
4. Consider GPU as default for interactive use
