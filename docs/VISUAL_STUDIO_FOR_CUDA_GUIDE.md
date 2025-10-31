# Visual Studio Installation Guide for CUDA Development

## Required for Building llama-cpp-python with CUDA Support

### Option 1: Visual Studio 2022 Build Tools (Recommended - Lighter)

**Download:** https://visualstudio.microsoft.com/downloads/
- Scroll down to "All Downloads"
- Expand "Tools for Visual Studio"
- Download **"Build Tools for Visual Studio 2022"**

**Installation (~7-10 GB):**

1. Run the installer
2. In the "Workloads" tab, select:
   - ✅ **Desktop development with C++** (REQUIRED)
   
3. In the "Individual components" tab, verify these are checked:
   - ✅ **MSVC v143 - VS 2022 C++ x64/x86 build tools** (latest)
   - ✅ **Windows 10 SDK** or **Windows 11 SDK** (10.0.19041.0 or newer)
   - ✅ **C++ CMake tools for Windows**
   - ✅ **C++ ATL for latest v143 build tools (x86 & x64)**

4. Install (will take 15-30 minutes)

**Size:** ~7-10 GB

### Option 2: Full Visual Studio 2022 Community (More features)

**Download:** https://visualstudio.microsoft.com/vs/community/

**Installation (~20-30 GB):**

1. Run the installer
2. In the "Workloads" tab, select:
   - ✅ **Desktop development with C++** (REQUIRED)
   
3. On the right side under "Installation details", ensure these are included:
   - ✅ **MSVC v143 - VS 2022 C++ x64/x86 build tools** (latest)
   - ✅ **Windows 10 SDK** or **Windows 11 SDK**
   - ✅ **C++ CMake tools for Windows**
   - ✅ **C++ core features**

4. Install (will take 30-60 minutes)

**Size:** ~20-30 GB

## CUDA Integration

After installing Visual Studio:

1. **Reinstall CUDA Toolkit** (or repair existing installation)
   - The CUDA installer will detect Visual Studio
   - It will install Visual Studio CUDA integration automatically
   - This adds nvcc compiler support to Visual Studio

2. **Verify Integration:**
   ```powershell
   # Check if CUDA can find Visual Studio
   nvcc --version
   
   # Check Visual Studio version
   "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64
   ```

## Why This Matters

The error you encountered:
```
CMake Error: No CUDA toolset found.
```

This happens because:
1. ❌ CMake finds CUDA Toolkit (12.1) ✓
2. ❌ CMake cannot find Visual Studio C++ compiler for CUDA
3. ❌ CUDA nvcc needs Visual Studio C++ build tools to compile CUDA code

**The "Desktop development with C++" workload provides:**
- MSVC C++ compiler (cl.exe)
- Windows SDK headers and libraries
- CMake integration
- Build tools that CUDA nvcc wraps around

## Installation Steps (Recommended Order)

### If you want GPU support now:

1. **Install Visual Studio 2022 Build Tools** (~30 minutes)
   - Select "Desktop development with C++" workload
   - Download: ~3 GB
   - Install size: ~7-10 GB

2. **Repair/Reinstall CUDA Toolkit 12.1** (~15 minutes)
   - This ensures CUDA integrates with Visual Studio
   - Run CUDA installer again, choose "Repair" or "Custom Install"
   - Make sure "Visual Studio Integration" is checked

3. **Rebuild llama-cpp-python** (~5-10 minutes)
   ```powershell
   .venv\Scripts\Activate.ps1
   
   # Set environment variables
   $env:PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1\bin;" + $env:PATH
   $env:CUDA_PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1"
   $env:CMAKE_ARGS = "-DGGML_CUDA=on"
   
   # Build with CUDA
   python -m pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
   ```

4. **Verify GPU acceleration** (~2 minutes)
   ```powershell
   python verify_gpu_acceleration.py
   ```

**Total time:** ~1 hour
**Total download:** ~11 GB
**Total disk space:** ~20 GB (CUDA + VS Build Tools)

## Alternative: Use Python 3.11 (MUCH FASTER)

If you want GPU **without** building from source:

1. **Install Python 3.11** (~5 minutes)
   - Download: https://www.python.org/downloads/release/python-3119/
   - Install size: ~100 MB

2. **Create new venv with Python 3.11** (~2 minutes)
   ```powershell
   python3.11 -m venv .venv-py311
   .venv-py311\Scripts\Activate.ps1
   ```

3. **Install pre-built CUDA wheel** (~2 minutes)
   ```powershell
   # This downloads a pre-compiled wheel with CUDA support
   pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
   pip install -r requirements-grmr.txt
   ```

4. **Done!** No compilation needed.

**Total time:** ~10 minutes
**No Visual Studio needed**
**No building from source**

## Comparison

| Method | Time | Disk Space | Complexity | Recommended |
|--------|------|------------|------------|-------------|
| **Python 3.11 + pre-built wheel** | ~10 min | ~1 GB | Easy | ✅ YES |
| **Visual Studio + build from source** | ~1 hour | ~20 GB | Complex | Only if you need Python 3.13 |
| **Wait for Python 3.13 wheels** | Unknown | N/A | Easy | If not urgent |
| **Accept CPU performance** | 0 min | 0 GB | None | ✅ YES (already works great!) |

## My Recommendation

Given your situation:

### Short term (Now):
**Accept CPU performance** - It's production-ready with 100% accuracy and 0.73s/sentence

### When GPU becomes important:
**Use Python 3.11 method** - 10 minutes, no Visual Studio needed, instant results

### Only if you specifically need Python 3.13 + GPU:
Follow the Visual Studio installation above (1 hour investment)

## Questions?

**Q: Do I need the full Visual Studio IDE?**
A: No, Build Tools is sufficient (saves ~15 GB)

**Q: Which version - 2019 or 2022?**
A: Either works, but 2022 is recommended (better CUDA support)

**Q: Can I uninstall Visual Studio after building?**
A: No - you'll need it for future llama-cpp-python updates

**Q: What about Visual Studio Code?**
A: VS Code is NOT the same as Visual Studio - you still need Build Tools

**Q: Is there a lighter option?**
A: Yes! Use Python 3.11 with pre-built wheels (no Visual Studio needed)

---

**TL;DR:** Install Visual Studio 2022 Build Tools with "Desktop development with C++" workload (~30 min, 10 GB), then repair CUDA installation to add VS integration.

**BETTER TL;DR:** Use Python 3.11 with pre-built CUDA wheels instead (~10 min, no Visual Studio needed).
