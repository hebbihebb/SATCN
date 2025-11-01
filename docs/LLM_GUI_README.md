# SATCN LLM GUI - Model-Focused Interface

**Created:** November 1, 2025
**File:** `src/satcn/gui/llm_gui.py`
**Launchers:** `launch_llm_gui.bat`, `launch_llm_gui.py`

## Overview

The LLM GUI is a specialized interface focused on **LLM model management and selection** for grammar correction. Unlike the main SATCN GUI which offers multiple correction engines, this GUI is dedicated to working with local GGUF models.

## Features

### 1. **Model Management**
- 📁 **Model Directory Configuration**: Set custom folder for model storage
- 🔍 **Automatic Model Discovery**: Scans for `.gguf` files in:
  - User-configured `models/` folder
  - Project root `.GRMR-V3-Q4B-GGUF/` folder
- 🔄 **Refresh Models**: Rescan directories for new models
- 📊 **Model Selection Dropdown**: Choose from available models

### 2. **HuggingFace Downloader** ✅ IMPLEMENTED
- ⬇️ **Direct Download**: Paste HuggingFace model URLs
- 🔍 **Auto-Detect GGUF**: Automatically finds `.gguf` files in repo
- 📋 **Multi-File Selection**: Choose from multiple models if available
- 💾 **Auto-Save**: Downloads saved to models folder
- 🔄 **Resume Support**: Can resume interrupted downloads
- 📦 **Model Organization**: Keeps models organized by folder

### 3. **LLM Parameters**
- 🌡️ **Temperature Slider**: Adjust creativity (0.0 - 1.0)
- ⚙️ **Max Tokens**: Configure output length
- ✅ **Fail Fast**: Stop on first error

### 4. **GPU Detection**
- Automatic GPU detection on startup
- Shows llama-cpp CUDA support status
- Displays VRAM and GPU model if available

## Usage

### Launch the GUI

```powershell
# Option 1: Batch file
.\launch_llm_gui.bat

# Option 2: Python launcher
python launch_llm_gui.py

# Option 3: Direct module
python -m satcn.gui.llm_gui
```

### Workflow

1. **Select Input File**: Click "Browse..." to choose a `.txt`, `.md`, or `.epub` file
2. **Configure Model Directory**: Click "Change..." to set where models are stored
3. **Download Model** (optional):
   - Paste HuggingFace URL (e.g., `https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF`)
   - Click "Download"
   - If multiple GGUF files exist, choose from the dialog
   - Wait for download to complete
4. **Select Model**: Choose from dropdown of available `.gguf` models
5. **Adjust Parameters**: Set temperature and other LLM settings
6. **Run Correction**: Click "▶️ Run Correction" to process the file

### HuggingFace URL Examples

**Repo URL** (auto-detects GGUF files):
```
https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
https://huggingface.co/TheBloke/GRMR-V3-GGUF
https://huggingface.co/bartowski/gemma-2-9b-it-GGUF
```

**Specific File URL**:
```
https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/blob/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q8_0.gguf
```

**Tips:**
- Repo URLs are easier - the GUI will scan and let you choose
- Q4_K_M quantizations are good balance of quality/size
- Q8_0 quantizations are higher quality but larger
- Check model card for recommended quantization

### Model Directory Structure

Default structure:
```
SATCN/
├─ models/                          # User models (configurable)
│  ├─ model1.gguf
│  ├─ model2-q4.gguf
│  └─ subfolder/
│     └─ model3-q8.gguf
├─ .GRMR-V3-Q4B-GGUF/              # Built-in GRMR-V3
│  ├─ GRMR-V3-Q4B.Q4_K_M.gguf
│  └─ GRMR-V3-Q4B.Q8_0.gguf
```

## Configuration

Settings are saved to: `~/.satcn/llm_gui_config.json`

Stored settings:
- Last input file
- Model directory path
- Selected model
- Temperature setting
- Max tokens
- Fail fast preference

## Keyboard Shortcuts

- `Ctrl+O`: Open file browser
- `Ctrl+R`: Run correction
- `Esc`: Cancel processing

## Differences from Main GUI

| Feature | Main GUI (`satcn_gui.py`) | LLM GUI (`llm_gui.py`) |
|---------|---------------------------|-------------------------|
| **Focus** | Multi-engine (LanguageTool, GRMR-V3, T5, None) | LLM-only (GGUF models) |
| **Model Selection** | Fixed engine choice | Dynamic model dropdown |
| **Model Management** | No | Yes (browse, download, organize) |
| **HuggingFace Downloads** | No | Yes (coming soon) |
| **Parameters** | Basic | LLM-specific (temperature, tokens) |
| **Use Case** | General correction | LLM experimentation |

## Future Enhancements

### Planned Features

1. **HuggingFace Integration**
   - Direct downloads from HuggingFace Hub
   - Progress tracking for large downloads
   - Automatic GGUF conversion (if needed)

2. **Model Info Panel**
   - Model size display
   - Quantization level indicator
   - Performance estimates

3. **Batch Processing**
   - Process multiple files
   - Queue management

4. **Model Comparison**
   - Side-by-side output comparison
   - Quality metrics (like Q4 vs Q8 comparison)

5. **Custom Prompts**
   - Edit system prompts
   - Save prompt templates
   - A/B test different prompts

## Technical Details

### Dependencies

```python
customtkinter  # Modern UI framework
llama-cpp-python  # GGUF model inference
huggingface_hub  # (Future) Model downloads
```

### Class Structure

```python
LLMConfig  # Configuration management
  ├─ input_file: Path
  ├─ model_path: Path
  ├─ model_dir: Path
  ├─ temperature: float
  └─ max_tokens: int

SATCNLLMGui  # Main GUI class
  ├─ scan_for_models()  # Find available .gguf files
  ├─ _download_model()  # HuggingFace download
  ├─ _run_pipeline()    # Process with selected model
  └─ _log_gpu_status()  # GPU detection
```

## Development Notes

### Adding New Model Formats

To support additional model formats (e.g., `.safetensors`, `.bin`):

1. Update `scan_for_models()` to include new extensions:
   ```python
   self.available_models.extend(self.config.model_dir.rglob("*.safetensors"))
   ```

2. Add format-specific loading logic in `_process_file()`

### HuggingFace Download Implementation ✅

The downloader is now fully implemented with these features:

**Supported URL Formats:**
1. **Repo URL**: `https://huggingface.co/username/repo-name`
   - Auto-scans for `.gguf` files
   - Shows selection dialog if multiple files found

2. **Direct File URL**: `https://huggingface.co/username/repo-name/blob/main/file.gguf`
   - Downloads specific file directly

**Implementation Details:**
```python
from huggingface_hub import hf_hub_download, list_repo_files

# List repo files and filter GGUF
files = list_repo_files(repo_id)
gguf_files = [f for f in files if f.endswith('.gguf')]

# Download with resume support
local_path = hf_hub_download(
    repo_id=repo_id,
    filename=filename,
    local_dir=self.config.model_dir,
    local_dir_use_symlinks=False,
    resume_download=True  # Can resume interrupted downloads
)
```

**Threading:**
- Downloads run in background thread
- UI remains responsive during download
- Progress updates sent via queue

## Testing

```powershell
# Test with .venv-gpu (has customtkinter and llama-cpp-python)
.\.venv-gpu\Scripts\python.exe launch_llm_gui.py

# Check GPU detection
# Should show: "✓ llama-cpp-python built with GPU support"
```

## Troubleshooting

### "No models found"
- Check model directory path
- Ensure `.gguf` files exist in `models/` or `.GRMR-V3-Q4B-GGUF/`
- Click "🔄 Refresh" to rescan

### GPU not detected
- Verify llama-cpp-python is compiled with CUDA
- Use `.venv-gpu` environment
- Check GPU status in output log on startup

### Download feature not working
- Feature is currently a placeholder
- Will be implemented with `huggingface_hub` integration
- For now, download models manually

## Related Files

- **Main GUI**: `src/satcn/gui/satcn_gui.py` - Multi-engine interface
- **Config**: `src/satcn/gui/components/config.py` - Configuration dataclass
- **Pipeline**: `src/satcn/core/pipeline_runner.py` - Processing logic
- **Filters**: `src/satcn/core/filters/grmr_v3_filter.py` - GRMR-V3 implementation

## See Also

- [GPU Setup Guide](GPU_SETUP_GUIDE.md)
- [GRMR-V3 Integration](GRMR_V3_INTEGRATION_SUMMARY.md)
- [GUI Implementation Summary](GUI_IMPLEMENTATION_SUMMARY.md)
