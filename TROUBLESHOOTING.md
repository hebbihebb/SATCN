# SATCN Troubleshooting Guide

Solutions to common issues when installing and using SATCN.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Runtime Issues](#runtime-issues)
- [GUI Issues](#gui-issues)
- [GPU/CUDA Issues](#gpucuda-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [Getting Help](#getting-help)

---

## Installation Issues

### "command not found: satcn" or "command not found: satcn-gui"

**Symptoms:**
```bash
$ satcn --help
bash: satcn: command not found
```

**Causes:**
1. SATCN not installed
2. Entry points not in PATH
3. Virtual environment not activated

**Solutions:**

```bash
# 1. Verify SATCN is installed
python -c "import satcn; print(satcn.__file__)"

# 2. If not installed, install it
pip install -e .

# 3. If installed, use direct invocation
python -m satcn.cli.main --help
python -m satcn.gui.satcn_gui

# 4. Check if venv is activated (if using one)
which python  # Should point to venv
```

---

### "ModuleNotFoundError: No module named 'customtkinter'"

**Symptoms:**
```python
ModuleNotFoundError: No module named 'customtkinter'
```

**Cause:** GUI extra not installed

**Solution:**
```bash
pip install -e ".[gui]"
```

---

### "ModuleNotFoundError: No module named '_tkinter'" (Linux)

**Symptoms:**
```python
ModuleNotFoundError: No module named '_tkinter'
```

**Cause:** System tkinter package not installed

**Solution:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk

# Verify
python3 -c "import tkinter; print('tkinter OK')"
```

---

### "ModuleNotFoundError: No module named 'llama_cpp'"

**Symptoms:**
```python
ModuleNotFoundError: No module named 'llama_cpp'
```

**Cause:** GRMR extra not installed

**Solution:**
```bash
pip install -e ".[grmr]"
```

---

### "No space left on device"

**Symptoms:**
```
OSError: [Errno 28] No space left on device
```

**Cause:** Insufficient disk space (especially with `[all]` extra)

**Solutions:**

```bash
# 1. Check disk space
df -h

# 2. Install only what you need
pip install -e ".[gui]"        # ~50MB
pip install -e ".[grmr,gui]"   # ~500MB

# 3. Clean pip cache if needed
pip cache purge

# 4. Don't install [all] unless you have 5GB+ free
```

---

### "pip install" fails with wheel build errors

**Symptoms:**
```
error: could not build wheels for llama-cpp-python
```

**Causes:**
1. Missing C++ compiler
2. Python version incompatibility

**Solutions:**

**Windows:**
```powershell
# Install Visual Studio 2022 with C++ tools
# Download from: https://visualstudio.microsoft.com/downloads/
```

**Linux:**
```bash
# Install build tools
sudo apt-get install build-essential  # Ubuntu/Debian
sudo dnf install gcc gcc-c++          # Fedora
```

**Python 3.13:**
```bash
# Use Python 3.11 or 3.12 instead
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[grmr]"
```

---

## Runtime Issues

### "FileNotFoundError: [Errno 2] No such file or directory: '.GRMR-V3-Q4B-GGUF/...'"

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: '.GRMR-V3-Q4B-GGUF/GRMR-V3-Q4B.Q4_K_M.gguf'
```

**Cause:** Running `satcn` from wrong directory (model path is relative)

**Solutions:**

```bash
# 1. Run from project root
cd /path/to/SATCN
satcn --use-grmr input.md

# 2. Or use absolute paths
satcn --use-grmr /full/path/to/input.md

# 3. Check if model exists
ls .GRMR-V3-Q4B-GGUF/
```

**Note:** This is a known issue being addressed by another developer. A fix is in progress to allow configurable model paths.

---

### "ImportError: cannot import name 'X' from 'satcn'"

**Symptoms:**
```python
ImportError: cannot import name 'satcn_gui' from 'satcn'
```

**Cause:** Stale installation or import cache

**Solutions:**

```bash
# 1. Reinstall package
pip install -e . --force-reinstall --no-deps

# 2. Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# 3. Restart Python interpreter
```

---

## GUI Issues

### GUI window doesn't appear (Linux)

**Symptoms:** Command runs but no window appears

**Causes:**
1. No display server (SSH/remote session)
2. Wayland compatibility issues
3. tkinter not working

**Solutions:**

```bash
# 1. Check DISPLAY variable
echo $DISPLAY  # Should show :0 or similar

# 2. If using SSH, enable X11 forwarding
ssh -X user@host

# 3. Try setting DISPLAY manually
export DISPLAY=:0
satcn-gui

# 4. Test tkinter
python3 -c "import tkinter; tkinter.Tk().mainloop()"
```

---

### GUI crashes on startup

**Symptoms:**
```
Segmentation fault (core dumped)
```

**Causes:**
1. tkinter/customtkinter incompatibility
2. Graphics driver issues

**Solutions:**

```bash
# 1. Update customtkinter
pip install --upgrade customtkinter

# 2. Try running with software rendering
export LIBGL_ALWAYS_SOFTWARE=1
satcn-gui

# 3. Check Python tkinter
python3 -c "import tkinter; print(tkinter.TkVersion)"
```

---

### GUI is slow or unresponsive

**Symptoms:** GUI takes a long time to start or respond

**Causes:**
1. Processing large files
2. AI model loading (GRMR/T5)
3. Insufficient RAM

**Solutions:**

```bash
# 1. Check system resources
top  # or htop

# 2. Process smaller files first

# 3. Disable AI models for testing
# (uncheck GRMR/T5 options in GUI)

# 4. Increase available RAM
# Close other applications
```

---

## GPU/CUDA Issues

### "CUDA not found" or "GPU not detected"

**Symptoms:**
```
WARNING: CUDA not found at C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0
```

**Causes:**
1. CUDA not installed
2. CUDA path incorrect
3. NVIDIA drivers not installed

**Solutions:**

**Check GPU:**
```bash
# Windows/Linux
nvidia-smi

# Should show GPU name and driver version
```

**Install CUDA:**
```bash
# Download from: https://developer.nvidia.com/cuda-downloads

# Verify installation
nvcc --version
```

**Set CUDA path (Windows):**
```powershell
$env:CUDA_PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0"
$env:PATH = "$env:CUDA_PATH\bin;$env:PATH"
```

**Set CUDA path (Linux):**
```bash
export CUDA_PATH=/usr/local/cuda
export PATH=$CUDA_PATH/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_PATH/lib64:$LD_LIBRARY_PATH
```

---

### llama-cpp-python not using GPU

**Symptoms:** GPU usage at 0% when using GRMR

**Causes:**
1. CPU-only build installed
2. CUDA not found during build
3. Model not configured for GPU

**Solutions:**

```bash
# 1. Rebuild with CUDA (Linux)
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

# 2. Rebuild with CUDA (Windows)
# Use PowerShell script:
.\scripts\setup\install_llama_cpp_cuda.ps1

# 3. Verify GPU support
python -c "from llama_cpp import Llama; print('Check GPU in Task Manager/nvidia-smi')"

# 4. Check GPU usage while running
watch -n 1 nvidia-smi  # Linux
# or Task Manager → Performance → GPU (Windows)
```

---

### "Failed to build llama-cpp-python with CUDA"

**Symptoms:** Long build process (~30-40 min) fails

**Causes:**
1. Visual Studio not installed (Windows)
2. CUDA version mismatch
3. Python 3.13 (no prebuilt wheels)

**Solutions:**

**Windows:**
```powershell
# 1. Install Visual Studio 2022 Community Edition
# https://visualstudio.microsoft.com/downloads/
# Select "Desktop development with C++"

# 2. Install CUDA Toolkit 13.0
# https://developer.nvidia.com/cuda-downloads

# 3. Use Python 3.11 or 3.12 (NOT 3.13)

# 4. Run setup script
.\scripts\setup\install_llama_cpp_cuda.ps1
```

**Linux:**
```bash
# 1. Install build tools
sudo apt-get install build-essential cmake  # Ubuntu
sudo dnf install gcc cmake                  # Fedora

# 2. Install CUDA
# Follow: https://developer.nvidia.com/cuda-downloads

# 3. Build with CUDA
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

---

## Platform-Specific Issues

### Windows: "Python was not found"

**Symptoms:**
```
'python' is not recognized as an internal or external command
```

**Solutions:**

```powershell
# 1. Check if Python is installed
py --version

# 2. Use 'py' instead of 'python'
py -m pip install -e ".[gui]"

# 3. Or add Python to PATH
# Control Panel → System → Advanced → Environment Variables
# Add: C:\Users\YourName\AppData\Local\Programs\Python\Python311
```

---

### Windows: Batch files fail immediately

**Symptoms:** Double-clicking `.bat` files opens and closes immediately

**Causes:**
1. Python not in PATH
2. Errors in batch file
3. Package not installed

**Solutions:**

```powershell
# 1. Run from Command Prompt to see errors
cmd
cd C:\path\to\SATCN\launchers
launch_satcn_gui.bat

# 2. Check Python in PATH
python --version

# 3. Use updated batch files (they have better error handling)
```

---

### Linux: "Permission denied" when running scripts

**Symptoms:**
```bash
$ ./launchers/launch_satcn_gui.sh
bash: ./launchers/launch_satcn_gui.sh: Permission denied
```

**Solution:**
```bash
# Make script executable
chmod +x launchers/launch_satcn_gui.sh

# Or run with bash explicitly
bash launchers/launch_satcn_gui.sh
```

---

### macOS: "cannot be opened because the developer cannot be verified"

**Symptoms:** macOS Gatekeeper blocks Python scripts

**Solutions:**

```bash
# 1. Allow unsigned apps (not recommended)
# System Preferences → Security & Privacy → Allow

# 2. Or run from terminal
bash launchers/launch_llm_gui.sh

# 3. Or use Python directly
python3 launchers/launch_llm_gui.py
```

---

## Getting Help

If you're still having issues:

### 1. Run the Validation Script

```bash
python scripts/validate_installation.py
```

This will check your installation and suggest fixes.

### 2. Check Prerequisites

```bash
python scripts/check_prerequisites.py
```

### 3. Enable Debug Output

```bash
# Run with verbose output
satcn -v input.md

# Or with Python
python -m satcn.cli.main -v input.md
```

### 4. Check the Logs

Look for log files in:
- `~/.config/satcn/` (Linux/Mac)
- `%APPDATA%\satcn\` (Windows)

### 5. Search Existing Issues

Check if someone else has reported this issue:
https://github.com/hebbihebb/SATCN/issues

### 6. Report a New Issue

If you can't find a solution, open a new issue:
https://github.com/hebbihebb/SATCN/issues/new

**Include:**
- Python version: `python --version`
- OS and version
- SATCN version: `python -c "import satcn; print(satcn.__file__)"`
- Full error message
- Steps to reproduce
- Output of `python scripts/validate_installation.py`

---

## Quick Reference

| Issue | Command |
|-------|---------|
| Validate installation | `python scripts/validate_installation.py` |
| Check prerequisites | `python scripts/check_prerequisites.py` |
| Test Python import | `python -c "import satcn; print('OK')"` |
| Test CLI | `satcn --help` |
| Test GUI | `satcn-gui` |
| Reinstall | `pip install -e . --force-reinstall` |
| Clear cache | `pip cache purge` |
| Check Python version | `python --version` |
| Check GPU | `nvidia-smi` |
| Check CUDA | `nvcc --version` |

---

**See also:**
- [INSTALLATION.md](INSTALLATION.md) - Installation instructions
- [README.md](README.md) - Project overview
- [docs/GPU_SETUP_GUIDE.md](docs/GPU_SETUP_GUIDE.md) - GPU setup
- [GitHub Issues](https://github.com/hebbihebb/SATCN/issues) - Report bugs
