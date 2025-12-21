# SATCN Installation Guide

Complete installation instructions for SATCN (Spelling and Text Correction Normalizer).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation Types](#installation-types)
- [Verification](#verification)
- [Platform-Specific Notes](#platform-specific-notes)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### All Platforms

**Required:**
- **Python 3.11 or 3.12** (NOT 3.13 - GPU builds not yet available)
  - Check your version: `python --version` or `python3 --version`
  - Download: https://www.python.org/downloads/
- **pip** (included with Python)
- **Git** (for cloning the repository)

**Optional:**
- NVIDIA GPU with CUDA support (for GPU acceleration)

### Linux Additional Requirements

**For GUI support**, you need tkinter (Python's GUI library):

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

### Windows Additional Requirements

**For GPU support**, you need:
- NVIDIA GPU with CUDA support
- CUDA Toolkit 13.0 (or 12.4+)
- Visual Studio 2022 with C++ tools

See [docs/GPU_SETUP_GUIDE.md](docs/GPU_SETUP_GUIDE.md) for detailed GPU setup instructions.

---

## Quick Start

### 1. Check Prerequisites

Run the prerequisites checker to verify your system is ready:

```bash
# Clone the repository first
git clone https://github.com/hebbihebb/SATCN.git
cd SATCN

# Check prerequisites
python scripts/check_prerequisites.py
```

### 2. Install SATCN

**Recommended: Install with GUI support**

```bash
pip install -e ".[gui]"
```

**Minimal: Base package only**

```bash
pip install -e .
```

**Full: Everything (requires ~2GB disk space)**

```bash
pip install -e ".[all]"
```

### 3. Verify Installation

```bash
# Validate installation
python scripts/validate_installation.py

# Or test manually
satcn --help
satcn-gui
```

---

## Installation Types

SATCN uses optional "extras" for modular installation. Choose what you need:

### Base Package

```bash
pip install -e .
```

**Includes:**
- Core text processing pipeline
- CLI tool (`satcn`)
- Basic filters (spell-check, grammar rules, number formatting)
- No AI models, no GUI

**Use case:** Automated batch processing, CI/CD pipelines

---

### GUI Extra

```bash
pip install -e ".[gui]"
```

**Adds:**
- CustomTkinter-based GUI (`satcn-gui`)
- Visual pipeline configuration
- Real-time processing preview

**Use case:** Interactive document processing

---

### GRMR Extra (AI Grammar Correction)

```bash
pip install -e ".[grmr]"
```

**Adds:**
- GRMR-V3 GGUF model support
- llama-cpp-python (CPU or GPU)
- Advanced grammar correction
- ~2.5GB model download

**Use case:** High-quality grammar correction

---

### T5 Extra (Transformer-based Correction)

```bash
pip install -e ".[t5]"
```

**Adds:**
- T5 transformer support
- PyTorch, transformers
- Experimental grammar correction
- ~2-3GB downloads

**Use case:** Experimental features, research

---

### Dev Extra (Development Tools)

```bash
pip install -e ".[dev]"
```

**Adds:**
- pytest, pytest-cov (testing)
- ruff, black, isort (code quality)
- pre-commit hooks

**Use case:** Contributing to SATCN development

---

### Combined Extras

Install multiple extras at once:

```bash
# GUI + GRMR (most common)
pip install -e ".[gui,grmr]"

# Everything
pip install -e ".[all]"
```

---

## Verification

### Automatic Validation

Run the validation script to check your installation:

```bash
python scripts/validate_installation.py
```

This checks:
- ✅ Python version
- ✅ SATCN package installed
- ✅ Entry points working (`satcn`, `satcn-gui`)
- ✅ Which extras are installed
- ✅ System dependencies (tkinter)

### Manual Testing

**Test CLI:**
```bash
satcn --help
```

**Test GUI:**
```bash
satcn-gui
```

**Test GRMR (if installed):**
```bash
satcn --use-grmr tests/samples/sample.md
```

---

## Platform-Specific Notes

### Windows

#### Using Launcher Scripts

Double-click batch files in `launchers/`:

- **launch_satcn_gui.bat** - Main GUI
- **launch_llm_gui.bat** - LLM model management GUI (GPU-enabled)
- **run_grmr_v3_gui.bat** - GRMR test GUI
- **validate_installation.bat** - Validate installation

All batch files now include:
- Python existence checking
- Automatic package installation if missing
- Better error messages

#### GPU Setup

See [docs/GPU_SETUP_GUIDE.md](docs/GPU_SETUP_GUIDE.md) for:
- CUDA Toolkit installation
- Visual Studio setup
- llama-cpp-python CUDA build (~38 minutes)

### Linux

#### Using Launcher Scripts

Make scripts executable and run:

```bash
chmod +x launchers/*.sh

# Launch GUI
./launchers/launch_satcn_gui.sh

# Launch LLM GUI
./launchers/launch_llm_gui.sh

# Validate installation
./launchers/validate_installation.sh
```

#### GPU Setup (NVIDIA)

```bash
# Check GPU
nvidia-smi

# Install CUDA-enabled llama-cpp-python
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

# Verify
python -c "from llama_cpp import Llama; print('GPU support available')"
```

### macOS

Similar to Linux, but GPU support is not available (no NVIDIA GPUs on modern Macs).

```bash
# Install with GUI
pip install -e ".[gui]"

# Use Python launchers
python3 launchers/launch_llm_gui.py
```

---

## Troubleshooting

### "command not found: satcn"

**Problem:** Entry points not in PATH or not installed

**Fix:**
```bash
# Reinstall package
pip install -e .

# Or use direct invocation
python -m satcn.cli.main --help
```

### "ModuleNotFoundError: No module named 'customtkinter'"

**Problem:** GUI extra not installed

**Fix:**
```bash
pip install -e ".[gui]"
```

### "ModuleNotFoundError: No module named '_tkinter'" (Linux)

**Problem:** System tkinter package not installed

**Fix:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

### Batch files failing on Windows

**Problem:** Python not in PATH, or package not installed

**Fix:**
1. Verify Python is installed: `python --version`
2. Reinstall SATCN: `pip install -e ".[gui]"`
3. Use the updated batch files in `launchers/`

### "pip install" fails with "No space left on device"

**Problem:** Insufficient disk space

**Fix:**
```bash
# Install only what you need
pip install -e ".[gui]"  # ~50MB

# NOT the [all] extra (~2GB)
```

### GPU builds not available for Python 3.13

**Problem:** llama-cpp-python GPU builds require Python 3.11 or 3.12

**Fix:**
- Install Python 3.11 or 3.12 alongside Python 3.13
- Create venv with specific Python version:
  ```bash
  python3.11 -m venv .venv-gpu
  source .venv-gpu/bin/activate
  pip install -e ".[grmr]"
  ```

---

## Next Steps

After successful installation:

1. **Read the documentation:**
   - [README.md](README.md) - Project overview and usage
   - [docs/GPU_SETUP_GUIDE.md](docs/GPU_SETUP_GUIDE.md) - GPU acceleration setup
   - [docs/LLM_GUI_README.md](docs/LLM_GUI_README.md) - LLM GUI guide

2. **Try the examples:**
   ```bash
   satcn tests/samples/sample.md
   satcn --use-grmr tests/samples/sample.md
   ```

3. **Explore the GUI:**
   ```bash
   satcn-gui
   ```

4. **Get help:**
   - GitHub Issues: https://github.com/hebbihebb/SATCN/issues
   - Documentation: `docs/` directory

---

## Advanced Installation

### Editable vs. Non-Editable Install

**Editable install** (recommended for development):
```bash
pip install -e ".[gui]"
```
- Changes to source code take effect immediately
- No reinstall needed after editing

**Non-editable install** (for production use):
```bash
pip install ".[gui]"
```
- Installs a copy of the package
- Faster import times
- Requires reinstall after updates

### Installing from GitHub Directly

Without cloning:
```bash
pip install "git+https://github.com/hebbihebb/SATCN.git#egg=satcn[gui]"
```

### Virtual Environments

**Recommended:** Use a virtual environment to avoid conflicts:

```bash
# Create venv
python -m venv .venv

# Activate
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install
pip install -e ".[gui]"

# Deactivate when done
deactivate
```

---

## System Requirements Summary

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.11 | 3.11 or 3.12 |
| RAM | 4GB | 8GB+ (16GB for T5) |
| Disk Space | 500MB | 5GB (for full install) |
| GPU (Optional) | NVIDIA CUDA 7.0+ | 8GB+ VRAM |
| OS | Windows 10, Linux, macOS 10.15+ | Latest versions |

---

For more help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or open an issue on GitHub.
