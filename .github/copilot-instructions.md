# SATCN – AI Coding Agent Instructions

## Project Overview

SATCN is a **local-only text correction pipeline** for preprocessing long-form documents (novels, manuscripts) before TTS playback. It uses a **Pipes-and-Filters architecture** where each filter transforms a shared `data` dictionary containing `text_blocks` (paragraph-level chunks with formatting metadata).

**Key principle:** Privacy-first, local-only processing. No cloud dependencies.

## Project Structure (src/ Layout)

```
SATCN/
├─ src/satcn/              # All application code
│  ├─ cli/                 # CLI entrypoint (main.py)
│  ├─ gui/                 # Tkinter GUI tools
│  └─ core/                # Core pipeline logic
│     ├─ filters/          # Correction filters (grammar, spelling, parsers)
│     ├─ utils/            # Logging, utilities
│     └─ pipeline_runner.py
├─ tests/                  # pytest tests (mirrors src structure)
├─ scripts/                # Dev scripts (benchmarks, GPU tests)
├─ docs/                   # Documentation
├─ data/samples/           # Sample input files
├─ pyproject.toml          # Build config, dependencies, tool settings
└─ .pre-commit-config.yaml # Automated code quality checks
```

**Important:** This project uses a **src/ layout**. Always import as `from satcn.core.filters import ...`, not relative imports.

## Architecture: Pipes-and-Filters Pattern

```
Input File → Parser → [Correction Filters] → TTS Normalizer → Output Generator
```

### Core Flow

1. **Parser** (`MarkdownParserFilter`/`EpubParserFilter`) extracts `text_blocks` from input
2. **Correction Filters** modify `text_blocks[i]['content']` while preserving `metadata`
3. **TTSNormalizer** expands numbers/dates/currency for TTS engines
4. **Output Generator** reconstructs document from corrected `text_blocks`

### Filter Protocol

Every filter implements `process(data)` where `data` is a dict with:

- `text_blocks`: List of `{'content': str, 'metadata': dict}` dictionaries
- `tree`: Parsed document tree (Markdown ElementTree or EPUB soup)
- `format`: `'markdown'` or `'epub'`
- `filepath`: Original input path

**Critical:** Filters MUST preserve `metadata` – it contains element references needed for round-trip output.

## Grammar Correction Models (3 Options)

### 1. GRMR-V3 GGUF ⭐ RECOMMENDED

- **File:** `src/satcn/core/filters/grmr_v3_filter.py`
- **Model:** `.GRMR-V3-Q4B-GGUF/GRMR-V3-Q4B.Q4_K_M.gguf` (2.5GB, 4-bit quantized)
- **Status:** Production-ready, GPU-accelerated (3.62x speedup)
- **Quality:** Grade A (95/100), 100% test accuracy
- **Usage:** `satcn --use-grmr input.md` or `python -m satcn.cli.main --use-grmr input.md`
- **Parameters:** `temperature=0.1` for determinism (model card recommends 0.7, but 0.1 prevents grammar errors)
- **GPU setup:** Requires `llama-cpp-python` with CUDA (~38-min build via `install_llama_cpp_cuda.ps1`)

### 2. T5 Transformer (Experimental)

- **File:** `src/satcn/core/filters/t5_correction_filter.py`
- **Status:** ⚠️ Experimental, memory-intensive (6-8GB VRAM)
- **Usage:** `satcn --use-t5 --t5-mode replace input.md`
- **Modes:** `replace` (T5 only), `hybrid` (T5 + cleanup), `supplement` (rules + T5)

### 3. LanguageTool (Rule-Based Fallback)

- **File:** `src/satcn/core/filters/grammar_filter_safe.py`
- **Status:** ✅ Working but slow (network API calls)
- **Usage:** Default pipeline without `--use-grmr` or `--use-t5`

## Developer Workflows

### Running the Pipeline

```powershell
# Install package first (editable mode for development)
pip install -e .

# CPU-only (any model)
satcn input.md

# GRMR-V3 with GPU acceleration
satcn --use-grmr input.md

# Hybrid mode (GRMR + spell-check + rule-based cleanup)
satcn --use-grmr --grmr-mode hybrid input.epub
```

### Testing Commands

```powershell
# Run all tests
pytest

# Unit tests only
pytest tests/unit/

# GRMR-V3 quality benchmark (31 tests, 100% pass rate expected)
python scripts/benchmark_grmr_quality.py

# Long document test (15K+ words, GPU recommended)
python scripts/test_long_document_gpu.py

# Regression tests (prevent quality regressions)
pytest tests/test_regression.py
```

### GPU Acceleration Setup

**Prerequisites:** Windows 10/11, NVIDIA GPU, CUDA 13.0, Visual Studio 2022, Python 3.11

```powershell
# Automated CUDA build (~38 minutes)
.\install_llama_cpp_cuda.ps1

# Always add CUDA to PATH before running GPU models
$env:PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64;$env:PATH"
```

**Important:** Python 3.13 GPU builds not yet available. Use Python 3.11 for GPU work.

### GUI Tools (Debugging/Testing)

```powershell
# Full pipeline GUI (browse files, configure filters, view logs)
python -m satcn.gui.pipeline_test_gui

# GRMR-V3 quick test GUI (adjust parameters, benchmark)
python -m satcn.gui.grmr_v3_test_gui
```

## Project-Specific Conventions

### 1. Optional Dependencies via Try/Except

```python
# See src/satcn/core/filters/__init__.py
try:
    from satcn.core.filters.grmr_v3_filter import GRMRV3GrammarFilter
    GRMR_V3_AVAILABLE = True
except ImportError:
    GRMRV3GrammarFilter = None
    GRMR_V3_AVAILABLE = False
```

**Pattern:** Always provide `*_AVAILABLE` flags for optional ML models. Raise helpful errors with install instructions.

### 2. Filter Return Values

- **Most filters:** Return modified `data` dict (no stats)
- **Grammar filters:** Return `(modified_data, changes_count)` tuple
- **Check:** `src/satcn/core/pipeline_runner.py` stores `(filter, returns_stats)` tuples in filter list

### 3. Prompt Engineering for GRMR-V3

```python
# See src/satcn/core/filters/grmr_v3_filter.py
PROMPT_TEMPLATE = """### Instruction
You are a copy editor. Fix grammar, spelling, and punctuation while keeping character names, slang, and factual content unchanged. Respond with the corrected text only.

### Input
{text}

### Response
"""
```

**Critical:** This prompt preserves character names and author voice. Changes require re-running quality benchmarks.

### 4. JSON Logging with Per-Filter Stats

```python
# See src/satcn/core/pipeline_runner.py
log_extra = {
    "filter": f.__class__.__name__,
    "file": os.path.basename(self.input_filepath),
    "changes": 0,
    "duration_ms": None,
    "status": "ok",
    "error": None
}
```

**Pattern:** All filters log structured JSON for observability. `gui_logs/` directory contains runtime logs.

### 5. Paragraph-Level Chunking (Not Sentence)

- **Why:** 4096-token context window allows full paragraphs, preserves context across sentences
- **Implementation:** Filters iterate over `text_blocks` (one per paragraph)
- **Never:** Don't chunk by sentence – context loss and slower processing

## Common Pitfalls & Solutions

### Problem: "GRMR-V3 not found" error

**Solution:** Model file `.GRMR-V3-Q4B-GGUF/GRMR-V3-Q4B.Q4_K_M.gguf` must exist. It's `.gitignore`d (2.5GB). Check if user has model file locally.

### Problem: Deep Markdown nesting breaks parser

**Known limitation:** Parser/writer struggle with complex inline formatting (e.g., `**bold _italic_ bold**`). EPUB handles this better.

### Problem: EPUB only processes `<p>` tags

**Known limitation:** Headers, lists, tables skipped. See `src/satcn/core/filters/epub_parser.py` – only `<p>` elements extracted into `text_blocks`.

### Problem: T5 GPU inference crashes

**Known issue:** T5 architecture incompatible with GGUF GPU inference. Use GRMR-V3 for GPU acceleration.

### Problem: Temperature=0.7 introduces grammar errors

**Solution:** Use `temperature=0.1` for deterministic corrections (already default in `src/satcn/core/filters/grmr_v3_filter.py`). Model card recommends 0.7 for creativity, but this project prioritizes accuracy.

## Testing Philosophy

### Test Structure

- `tests/unit/` – Isolated filter tests (mocked models)
- `tests/integration/` – Full pipeline end-to-end tests
- `tests/regression_corpus/` – Golden input/output pairs (prevent regressions)
- `tests/samples/` – Small test documents

### Quality Benchmarks

- **scripts/benchmark_grmr_quality.py:** 31 test cases covering grammar/spelling/punctuation
- **Expected:** 100% pass rate (51/51 tests)
- **Character preservation:** 99%+ (proper nouns intact)
- **Quality grade:** A (95/100)

### Running Tests Before Commits

```powershell
# Fast check
pytest tests/unit/ -v

# Full check (includes GRMR-V3 benchmarks)
pytest
python scripts/benchmark_grmr_quality.py
```

## Key Documentation Files

- **README.md:** Complete project overview, architecture, lessons learned
- **docs/GPU_SETUP_GUIDE.md:** CUDA setup, Visual Studio requirements, troubleshooting
- **docs/GRMR_V3_GGUF_TEST_PLAN.md:** Quality benchmarks, test methodology
- **GRMR_V3_QUALITY_REPORT.md:** Real-world 15K-word correction analysis (Grade A)
- **docs/GRMR_V3_PARAMETER_ANALYSIS.md:** Model card vs. implementation parameters
- **docs/T5_CORRECTOR_GUIDE.md:** T5 transformer usage (experimental)

## When Editing Core Components

### Modifying Pipeline Runner (`src/satcn/core/pipeline_runner.py`)

- **Test:** Run full integration tests: `pytest tests/integration/`
- **Check:** Ensure `--use-grmr`, `--use-t5`, and default modes all work
- **Verify:** JSON logging still outputs per-filter stats

### Modifying Filters (`src/satcn/core/filters/*.py`)

- **Test:** Run unit tests: `pytest tests/unit/test_<filter_name>.py`
- **Check:** Filter contract: `process(data)` returns modified `data` dict
- **Verify:** `metadata` preservation (critical for round-trip output)

### Modifying GRMR-V3 Filter (`src/satcn/core/filters/grmr_v3_filter.py`)

- **Test:** Run quality benchmark: `python scripts/benchmark_grmr_quality.py`
- **Check:** 100% pass rate (51/51 tests)
- **Verify:** `temperature=0.1` still default (prevents grammar errors)
- **Re-run:** Long document test: `python scripts/test_long_document_gpu.py`

### Modifying Parsers (`src/satcn/core/filters/*_parser.py`)

- **Test:** Check round-trip preservation: input → parse → correct → output
- **Verify:** Markdown formatting preserved (bold, italic, links, headers)
- **Known issue:** Deep nesting breaks – document in code comments

## Environment Management

### Multiple Virtual Environments

- `.venv` – Standard CPU environment (Python 3.11+)
- `.venv-gpu` – GPU environment (Python 3.11 only, CUDA-enabled llama-cpp-python)
- `.venv310` – Legacy Python 3.10 environment (deprecated)

### Dependencies (pyproject.toml)

All dependencies are now managed in `pyproject.toml` with optional extras:

```bash
pip install -e .              # Base dependencies only
pip install -e ".[grmr]"      # + GRMR-V3 support
pip install -e ".[t5]"        # + T5 transformer support
pip install -e ".[gui]"       # + GUI dependencies
pip install -e ".[dev]"       # + Dev tools (pytest, ruff, black, isort)
pip install -e ".[all]"       # Everything
```

Legacy `requirements*.txt` files may still exist but are deprecated.

## Project Philosophy Reminder

1. **Privacy-first:** Never add cloud APIs or telemetry
2. **Quality over speed:** GPU makes it fast enough, but accuracy comes first
3. **Test-driven:** Changes require passing benchmark (100% expected)
4. **TTS-optimized:** Designed for text-to-speech preprocessing, not general editing
5. **Local-only:** All processing happens on user's machine

**Not a goal:** Real-time editing, cloud SaaS, multi-user collaboration, mobile apps.
