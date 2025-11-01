# SATCN Launchers

Quick launchers for SATCN GUI applications.

## Available Launchers

### Windows (.bat files)
- **`launch_satcn_gui.bat`** - Main Pipeline GUI (full pipeline control)
- **`launch_llm_gui.bat`** - LLM GUI (model management, HuggingFace integration)
- **`run_grmr_v3_gui.bat`** - GRMR-V3 Test GUI (GPU testing and diagnostics)
- **`run_test_gui.bat`** - Pipeline Test GUI (legacy testing interface)

### Cross-Platform (.py files)
- **`launch_llm_gui.py`** - LLM GUI Python launcher
- **`launch_grmr_gui.py`** - GRMR-V3 Test GUI Python launcher
- **`launch_pipeline_gui.py`** - Pipeline Test GUI Python launcher

## Usage

### Windows
Double-click any `.bat` file or run from command line:
```cmd
launchers\launch_satcn_gui.bat
launchers\launch_llm_gui.bat
```

### Linux/Mac
Run Python launchers:
```bash
python launchers/launch_llm_gui.py
python launchers/launch_grmr_gui.py
python launchers/launch_pipeline_gui.py
```

## GUI Comparison

| GUI | Purpose | Best For |
|-----|---------|----------|
| **SATCN Pipeline GUI** | Full pipeline control with all filter options | Production use, complete customization |
| **LLM GUI** | LLM model management and GPU correction | Model testing, HuggingFace downloads |
| **GRMR-V3 Test GUI** | GPU diagnostics and performance testing | GPU troubleshooting, benchmarking |
| **Pipeline Test GUI** | Legacy testing interface | Development, debugging |

## Recommended Launcher

- **For most users:** `launch_satcn_gui.bat` (Windows) or `satcn-gui` command
- **For LLM/model work:** `launch_llm_gui.bat` or `python launchers/launch_llm_gui.py`
