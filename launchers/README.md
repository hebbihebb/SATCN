# 🚀 SATCN Launchers

Quick-launch utilities for SATCN's GUI applications across all platforms.

---

## 📋 Available Launchers

### 🪟 Windows Launchers (.bat files)

| Launcher | Purpose | Status |
|----------|---------|--------|
| **`launch_satcn_gui.bat`** | 🎨 Main Pipeline GUI (production) | ⭐ Updated |
| **`launch_llm_gui.bat`** | 🤖 LLM Model GUI (GPU-enabled) | ✅ Ready |
| **`run_grmr_v3_gui.bat`** | 🔬 GRMR-V3 Test GUI | ✅ Fixed |
| **`run_test_gui.bat`** | 🧪 Pipeline Test GUI | ✅ Fixed |
| **`setup_gpu_env.bat`** | ⚙️ Setup GPU environment | ✅ Enhanced |
| **`validate_installation.bat`** | ✔️ Validate installation | 🆕 New |

**All batch files now include:**
- ✅ Python existence checking
- ✅ Automatic package installation if missing
- ✅ Better error messages
- ✅ Fail-safe error handling

### 🐧🍎 Linux/Mac Launchers (.sh files)

| Launcher | Purpose | Status |
|----------|---------|--------|
| **`launch_satcn_gui.sh`** | 🎨 Main Pipeline GUI | 🆕 New |
| **`launch_llm_gui.sh`** | 🤖 LLM Model GUI | 🆕 New |
| **`launch_grmr_gui.sh`** | 🔬 GRMR-V3 Test GUI | 🆕 New |
| **`validate_installation.sh`** | ✔️ Validate installation | 🆕 New |

**Usage:**
```bash
# Make executable (first time only)
chmod +x launchers/*.sh

# Run
./launchers/launch_satcn_gui.sh
./launchers/launch_llm_gui.sh
./launchers/launch_grmr_gui.sh
```

### 🐍 Cross-Platform Python Launchers (.py files)

| Launcher | Purpose | Platform |
|----------|---------|----------|
| **`launch_llm_gui.py`** | 🤖 LLM Model GUI | All |
| **`launch_grmr_gui.py`** | 🔬 GRMR-V3 Test GUI | All |
| **`launch_pipeline_gui.py`** | 🧪 Pipeline Test GUI | All |

**Usage:**
```bash
python3 launchers/launch_llm_gui.py    # Linux/Mac
python launchers\launch_llm_gui.py     # Windows
```

---

## 🎯 Usage

### Windows Users

**Option 1: Double-click** (Easiest)
1. Navigate to `launchers/` folder
2. Double-click desired `.bat` file
3. GUI launches automatically

**Option 2: Command line**
```cmd
# From project root
launchers\launch_satcn_gui.bat
launchers\launch_llm_gui.bat
```

### Linux/Mac Users

**Option 1: Shell scripts** (Easiest - 🆕 New!)
```bash
# Make executable (first time only)
chmod +x launchers/*.sh

# Main Pipeline GUI
./launchers/launch_satcn_gui.sh

# LLM Model GUI
./launchers/launch_llm_gui.sh

# GRMR-V3 Test GUI
./launchers/launch_grmr_gui.sh

# Validate installation
./launchers/validate_installation.sh
```

**Option 2: Python scripts**
```bash
# Main Pipeline GUI (recommended)
satcn-gui
# Alternative: python3 -m satcn.gui.satcn_gui

# LLM Model GUI
python3 launchers/launch_llm_gui.py

# GRMR-V3 Test GUI
python3 launchers/launch_grmr_gui.py

# Pipeline Test GUI
python3 launchers/launch_pipeline_gui.py
```

---

## 🔍 GUI Comparison Guide

Choose the right interface for your workflow:

### 🎨 SATCN Pipeline GUI – **RECOMMENDED FOR MOST USERS**

<table>
<tr>
<td width="40%">

**✨ Best For**
- Daily document processing
- Production workflows
- Complete pipeline control
- Batch processing needs

</td>
<td width="60%">

**🎯 Key Features**
- ✅ All grammar engines (GRMR, T5, LanguageTool, None)
- ✅ Full filter configuration
- ✅ Real-time progress tracking
- ✅ Keyboard shortcuts (`Ctrl+O`, `Ctrl+R`, etc.)
- ✅ Persistent settings
- ✅ Fail-fast mode

</td>
</tr>
</table>

**Launch:** `launch_satcn_gui.bat` (Windows) or `satcn-gui` (Linux/Mac)

---

### 🤖 LLM Model GUI – **NEW: MODEL MANAGEMENT** 🆕

<table>
<tr>
<td width="40%">

**✨ Best For**
- Downloading models from HuggingFace
- Testing different quantizations (Q4, Q8, etc.)
- GPU performance testing
- Model quality comparisons

</td>
<td width="60%">

**🎯 Key Features**
- ✅ HuggingFace model downloader (paste URL)
- ✅ Auto-detect GGUF files in repos
- ✅ Multi-file selection (choose quantization)
- ✅ Parameter tuning (temperature, max_tokens)
- ✅ Side-by-side diff viewer
- ✅ GPU status display

</td>
</tr>
</table>

**Launch:** `launch_llm_gui.bat` (Windows) or `python launchers/launch_llm_gui.py` (Linux/Mac)

**Documentation:** See [`docs/LLM_GUI_README.md`](../docs/LLM_GUI_README.md)

---

### 🔬 GRMR-V3 Test GUI – **GPU DIAGNOSTICS**

<table>
<tr>
<td width="40%">

**✨ Best For**
- GPU troubleshooting
- Performance benchmarking
- CUDA configuration testing
- Model accuracy validation

</td>
<td width="60%">

**🎯 Key Features**
- ✅ GPU detection and status
- ✅ Performance metrics (words/min)
- ✅ Quick test sentences
- ✅ Accuracy validation
- ✅ CUDA diagnostics

</td>
</tr>
</table>

**Launch:** `run_grmr_v3_gui.bat` (Windows) or `python launchers/launch_grmr_gui.py` (Linux/Mac)

---

### 🧪 Pipeline Test GUI – **LEGACY TESTING**

<table>
<tr>
<td width="40%">

**✨ Best For**
- Development debugging
- Filter testing
- Legacy compatibility
- Advanced troubleshooting

</td>
<td width="60%">

**🎯 Key Features**
- ✅ Direct filter access
- ✅ Detailed error logging
- ✅ Step-by-step processing
- ✅ Development mode

</td>
</tr>
</table>

**Launch:** `run_test_gui.bat` (Windows) or `python launchers/launch_pipeline_gui.py` (Linux/Mac)

---

## 💡 Quick Decision Guide

```
┌─────────────────────────────────────────┐
│  What do you want to do?               │
└─────────────────────────────────────────┘

📄 Process documents for TTS?
   → Use: SATCN Pipeline GUI ⭐

📥 Download models from HuggingFace?
   → Use: LLM Model GUI 🆕

⚡ Test GPU performance?
   → Use: GRMR-V3 Test GUI 🔬

🐛 Debug pipeline issues?
   → Use: Pipeline Test GUI 🧪
```

---

## 🔗 Related Documentation

| Document | Link |
|----------|------|
| 📖 **Main README** | [`../README.md`](../README.md) |
| 🤖 **LLM GUI Guide** | [`../docs/LLM_GUI_README.md`](../docs/LLM_GUI_README.md) |
| 🚀 **GPU Setup** | [`../docs/GPU_SETUP_GUIDE.md`](../docs/GPU_SETUP_GUIDE.md) |
| 🛠️ **Contributing** | [`../docs/CONTRIBUTING.md`](../docs/CONTRIBUTING.md) |

---

## ❓ Troubleshooting

**Issue:** Double-clicking `.bat` files does nothing
- **Solution:** Right-click → "Run as Administrator" or open in Command Prompt

**Issue:** Python launcher fails with "module not found"
- **Solution:** Install SATCN first: `pip install -e .` or `pip install -e ".[gui]"`

**Issue:** GUI launches but model missing
- **Solution:** Install GRMR extras: `pip install -e ".[grmr]"` and download model

---

<div align="center">

**Need help?** Open an issue: https://github.com/hebbihebb/SATCN/issues

</div>
