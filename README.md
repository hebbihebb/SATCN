# SATCN – Spelling and Text Correction Normalizer

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Status: Alpha](https://img.shields.io/badge/status-alpha-yellow.svg)

**Local-only text correction pipeline for preprocessing long-form documents before TTS playback.**

![SATCN GUI Screenshot](docs/screenshot-gui.png)
*SATCN Pipeline GUI - Configure filters, view real-time logs, process documents*

![SATCN LLM GUI Screenshot](docs/screenshot-llm-gui.png)
*SATCN LLM GUI - Model management, HuggingFace downloader, GPU-accelerated correction*

## What It Is

SATCN is a privacy-first document correction tool that:
- **Fixes grammar, spelling, and punctuation** using state-of-the-art ML models
- **Preserves formatting** (Markdown, EPUB) and author voice
- **Runs entirely offline** - no cloud APIs, full privacy
- **Supports GPU acceleration** - 3.6x faster with CUDA
- **Optimizes for TTS** - expands numbers, dates, currency for natural speech

## What It Does

```
Input Document  →  Parse  →  [Correction Filters]  →  TTS Normalize  →  Clean Output
```

**3 Grammar Correction Options:**
1. **GRMR-V3 GGUF** ⭐ (Recommended) - Quantized AI model, 100% test accuracy, GPU-ready
2. **T5 Transformer** (Experimental) - Context-aware but memory-intensive
3. **LanguageTool** (Fallback) - Rule-based, conservative

**Supported Formats:** Markdown (`.md`), EPUB (`.epub`)

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/hebbihebb/SATCN.git
cd SATCN

# Install package (editable mode recommended for development)
pip install -e .

# Optional: Install GRMR-V3 (recommended for best quality)
pip install -e ".[grmr]"

# Optional: Install T5 transformer support
pip install -e ".[t5]"

# Optional: Install all features + dev tools
pip install -e ".[all]"
```

### Basic Usage

```bash
# Process a document (default: rule-based correction)
satcn input.md

# Use GRMR-V3 AI model (recommended)
satcn --use-grmr input.md

# Hybrid mode (AI + spell-check + rules)
satcn --use-grmr --grmr-mode hybrid input.epub

# GUI mode (modern interface with all options)
satcn-gui
# Or: python -m satcn.gui.satcn_gui

# Windows: Double-click launch_satcn_gui.bat
```

### GUI Features ✨

**Two GUI Options:**

#### 1. SATCN Pipeline GUI (Full pipeline control)
The **SATCN Pipeline GUI** provides a modern, user-friendly interface with:

- **Complete grammar engine selection**: LanguageTool, GRMR-V3 GGUF, T5 Transformer, or None
- **Visual configuration**: Radio buttons for engines, contextual mode dropdown
- **Real-time feedback**: Progress bar, live output log with timestamps
- **File statistics**: Word count, page estimates, processing time predictions
- **Keyboard shortcuts**: `Ctrl+O` (open), `Ctrl+R` (run), `Esc` (cancel), `Ctrl+Q` (quit)
- **Persistent settings**: Remembers your preferences between sessions
- **Tooltips**: Hover over options for detailed explanations
- **Fail-fast mode**: Stop on first error or continue through pipeline
- **Dark theme**: Easy on the eyes during long editing sessions

Launch with:
```bash
satcn-gui                           # Recommended
python -m satcn.gui.satcn_gui       # Alternative
launchers/launch_satcn_gui.bat      # Windows double-click
```

#### 2. SATCN LLM GUI (Model-focused interface) 🆕
The **SATCN LLM GUI** focuses on LLM model management and GPU-accelerated correction:

- **Model selection**: Browse and select local GGUF models (Q4, Q8, etc.)
- **HuggingFace integration**: Download models directly from HuggingFace Hub
- **Multi-file selection**: Choose from multiple quantizations in repos
- **GPU detection**: Automatic CUDA detection and status display
- **Success dialog**: View correction stats and side-by-side diff viewer
- **Parameter tuning**: Adjust temperature, max_tokens for fine control
- **Progress tracking**: Real-time paragraph-by-paragraph processing

Launch with:
```bash
python launchers/launch_llm_gui.py  # Recommended
launchers/launch_llm_gui.bat        # Windows double-click
```

See [`docs/LLM_GUI_README.md`](docs/LLM_GUI_README.md) for detailed LLM GUI documentation.

Configuration saved to: `~/.config/satcn/gui_config.json` and `~/.config/satcn/llm_gui_config.json`

### GPU Acceleration (Optional)

For 3.6x speedup on NVIDIA GPUs:

```bash
# Prerequisites: CUDA 13.0, Visual Studio 2022, Python 3.11
# Run automated CUDA build (~38 minutes)
.\install_llama_cpp_cuda.ps1

# Add CUDA to PATH
$env:PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64;$env:PATH"

# Process with GPU
satcn --use-grmr input.md
```

See [`docs/GPU_SETUP_GUIDE.md`](docs/GPU_SETUP_GUIDE.md) for detailed GPU setup.

## How It Works

### Architecture: Pipes-and-Filters Pattern

Each filter transforms a shared `data` dictionary containing `text_blocks`:

```python
# Filter protocol
class Filter:
    def process(self, data: dict) -> dict:
        """
        data = {
            'text_blocks': [{'content': str, 'metadata': dict}, ...],
            'tree': parsed_document_tree,
            'format': 'markdown' | 'epub',
            'filepath': str
        }
        """
        # Transform text_blocks, preserve metadata
        return modified_data
```

**Critical:** Metadata must be preserved for round-trip document reconstruction.

### Quality Metrics (GRMR-V3)

| Metric | Result |
|--------|--------|
| **Test Accuracy** | 100% (51/51 tests) |
| **Quality Grade** | A (95/100) |
| **Character Preservation** | 99%+ (proper nouns intact) |
| **Speed (GPU)** | 1,587 words/minute |
| **Speed (CPU)** | 438 words/minute |

## GUI Workflow Guide

### First Time Setup

1. **Launch GUI**: Run `satcn-gui` or double-click `launch_satcn_gui.bat` (Windows)
2. **Browse for file**: Click "Browse..." and select your `.md`, `.txt`, or `.epub` file
3. **Select grammar engine**:
   - **GRMR-V3 GGUF** (recommended): Best quality, GPU-accelerated, 1587 wpm
   - **LanguageTool**: Conservative rule-based, slower but no setup required
   - **T5 Transformer**: Experimental, requires `pip install -e ".[t5]"`
   - **None**: Skip grammar correction (use only other filters)
4. **Choose mode** (for GRMR-V3/T5):
   - **Replace**: Use only AI model corrections
   - **Hybrid**: AI model + spell-check + rule-based cleanup
   - **Supplement**: Rule-based first, then AI model on remaining issues
5. **Click "Run Pipeline"**: Watch real-time progress and logs
6. **Find output**: `{input_name}_corrected.{ext}` in same directory

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open file browser |
| `Ctrl+R` | Run pipeline |
| `Esc` | Cancel processing |
| `Ctrl+Q` | Quit application |

### Configuration Persistence

Your settings are automatically saved to:
- **Linux/Mac**: `~/.config/satcn/gui_config.json`
- **Windows**: `C:\Users\<username>\.config\satcn\gui_config.json`

Next time you launch the GUI, it will remember your last file and preferences.

## Documentation

- **[GPU Setup Guide](docs/GPU_SETUP_GUIDE.md)** - CUDA installation, troubleshooting
- **[GRMR-V3 Quality Report](.md/GRMR_V3_QUALITY_REPORT.md)** - Real-world 15K-word analysis
- **[T5 Integration Guide](docs/T5_CORRECTOR_GUIDE.md)** - Transformer model usage
- **[Contributing Guidelines](docs/CONTRIBUTING.md)** - Development setup

## Testing

```bash
# Run all tests
pytest

# Unit tests only
pytest tests/unit/

# Quality benchmark (100% pass rate expected)
python scripts/benchmark_grmr_quality.py

# Long document test (15K+ words, GPU recommended)
python scripts/test_long_document_gpu.py
```

## Project Philosophy

1. **Privacy-first** - Never add cloud APIs or telemetry
2. **Quality over speed** - GPU makes it fast enough, accuracy comes first
3. **Test-driven** - Changes require passing 100% quality benchmark
4. **TTS-optimized** - Designed for text-to-speech preprocessing
5. **Local-only** - All processing happens on your machine

**Not a goal:** Real-time editing, cloud SaaS, multi-user collaboration, mobile apps

## Contributing

Contributions welcome! See [`CONTRIBUTING.md`](docs/CONTRIBUTING.md) for:
- Development setup
- Code style (Black, Ruff, isort)
- Testing requirements
- Pull request process

## License

MIT License - See repository for license details.

## Acknowledgments

- **GRMR-V3-Q4B** by qingy2024 (Hugging Face)
- **FLAN-T5** by Google (experimental support)
- **LanguageTool** for rule-based grammar checking

---

**Repository:** https://github.com/hebbihebb/SATCN
**Issues:** https://github.com/hebbihebb/SATCN/issues
