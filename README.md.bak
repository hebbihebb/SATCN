# SATCN – Spelling and Text Correction Normalizer

**A personal project for one-shot document correction optimized for TTS preprocessing.**

SATCN is an experimental document correction pipeline designed to process long-form Markdown or EPUB content, repair spelling and grammar issues, and output clean corrected versions ready for Text-to-Speech (TTS) engines. This project explores different approaches to automated text correction—from rule-based filters to transformer models to GGUF quantized models—with a focus on privacy (local-only processing), performance (GPU acceleration), and quality (preserving author voice and character names).

**Project Status:** Active Development | Personal/Educational Use | CPU & GPU Support

---

## 1. Why This Project Exists

**Personal Motivation:** I wanted a local, privacy-respecting tool to clean up text documents before feeding them to TTS engines. Commercial solutions either require cloud uploads (privacy concerns) or produce inconsistent quality. This project explores building a flexible correction pipeline that:

1. **Runs locally** - No cloud dependencies, full privacy
2. **Preserves formatting** - Maintains Markdown/EPUB structure and inline formatting
3. **Handles long documents** - Novels (90K+ words), not just snippets
4. **Leverages modern ML** - Transformer models and quantized GGUF models
5. **Optimizes for TTS** - Special handling for numbers, dates, currency
6. **Supports GPU acceleration** - 3-4x speedup for batch processing

## 2. Current Status

| Component | Status | Performance | Notes |
|-----------|--------|-------------|-------|
| **Core Pipeline** | ✅ Production | - | Pipes-and-Filters architecture working |
| **Markdown I/O** | ✅ Stable | - | Preserves structure, struggles with deep nesting |
| **EPUB I/O** | ✅ Stable | - | Handles `<p>` tags, metadata preservation |
| **Spelling Filter** | ✅ Working | Fast | `pyspellchecker` - basic but functional |
| **Grammar Filter (Safe)** | ✅ Working | Slow | LanguageTool public API (conservative ruleset) |
| **GRMR-V3 GGUF** | ✅ **Production** | **438 wpm CPU<br>1,587 wpm GPU** | **Best quality, GPU-ready, 100% test accuracy** |
| **T5 Transformer** | ⚠️ Experimental | Slow | Works but memory-intensive |
| **TTS Normalizer** | ✅ Working | Fast | Converts numbers, dates, currency |
| **GPU Acceleration** | ✅ Validated | **3.62x speedup** | CUDA 13.0, works with GRMR-V3 |
| **Test Suite** | ✅ Comprehensive | - | Unit, integration, regression tests |

### What Works Best

**Recommended Configuration (GPU):**
```bash
python -m pipeline.pipeline_runner --use-grmr input.md
```
- **Quality:** Grade A (95/100) - Production ready
- **Speed:** 1,587 words/minute (GPU) or 438 wpm (CPU)
- **Privacy:** Fully local, no network calls
- **Reliability:** 100% test accuracy, 99%+ character name preservation

---

## 3. Architecture: Pipes-and-Filters Design

The pipeline implements a classic Pipes-and-Filters pattern where each stage transforms a shared `data` dictionary:

```
Input File → Parser → [Correction Filters] → TTS Normalizer → Output Generator
```

### 3.1 Pipeline Stages

**1. Parser** (`MarkdownParserFilter` or `EpubParserFilter`)
- Converts input file into structured `text_blocks`
- Preserves formatting metadata (bold, italic, links)
- Maintains document tree for round-trip output

**2. Correction Filters** (pluggable, mode-dependent)
- **Default:** `SpellingCorrectionFilter` → `GrammarCorrectionFilterSafe`
- **GRMR-V3:** `GRMRV3GrammarFilter` (recommended, GPU-ready)
- **T5:** `T5CorrectionFilter` (experimental, memory-intensive)
- Each filter receives `text_blocks`, modifies `content`, returns modified data

**3. TTS Normalizer** (`TTSNormalizer`)
- Converts "$99.99" → "ninety-nine dollars and ninety-nine cents"
- Expands "3rd" → "third", "10:30 AM" → "ten thirty AM"
- Ensures TTS engines pronounce text naturally

**4. Output Generator** (`MarkdownOutputGenerator` or `EpubOutputGenerator`)
- Reconstructs document from corrected `text_blocks`
- Writes `input_corrected.md` or `input_corrected.epub`
- Preserves original structure and formatting

### 3.2 Key Design Decisions

✅ **Separation of concerns** - Each filter has one job
✅ **Metadata preservation** - Formatting survives correction
✅ **Mode flexibility** - Swap filters at runtime (`--use-grmr`, `--use-t5`)
✅ **Fail-fast support** - Stop on first error or continue
✅ **JSON logging** - Structured logs with per-filter statistics

---

## 4. Grammar Correction Approaches

The project has explored three approaches to grammar correction:

### 4.1 LanguageTool (Rule-Based) - Baseline

**Status:** ✅ Working, but slow
**Implementation:** `GrammarCorrectionFilterSafe`
**Backend:** LanguageTool public API with conservative ruleset

**Pros:**
- Deterministic, explainable corrections
- Low memory footprint
- No model downloads

**Cons:**
- Slow (network API calls)
- Limited context awareness
- Conservative (misses many errors)

**Use case:** Fallback option, development testing

### 4.2 T5 Transformer (ML-Based) - Experimental

**Status:** ⚠️ Experimental, memory-intensive
**Implementation:** `T5CorrectionFilter`
**Model:** FLAN-T5 (Hugging Face)

**Pros:**
- Context-aware corrections
- Can handle complex grammar

**Cons:**
- Large memory footprint (6-8 GB VRAM)
- Slower than GGUF models
- Requires PyTorch/Transformers
- Can alter author voice

**Use case:** Experimentation, comparison studies

**Modes:**
- `--use-t5 --t5-mode replace` - T5 only (fastest)
- `--use-t5 --t5-mode hybrid` - T5 + rule-based cleanup
- `--use-t5 --t5-mode supplement` - Rule-based + T5 polish

### 4.3 GRMR-V3 GGUF (Quantized ML) - **Recommended** ⭐

**Status:** ✅ Production-ready, GPU-accelerated
**Implementation:** `GRMRV3GrammarFilter`
**Model:** GRMR-V3-Q4B (Qwen3 4B, 4-bit quantized, 2.5GB)

**Pros:**
- **High quality:** 100% test accuracy, Grade A quality (95/100)
- **GPU-ready:** 3.62x speedup (1,587 wpm vs 438 wpm CPU)
- **Memory efficient:** ~3.2GB VRAM (4-bit quantization)
- **Preserves voice:** 99%+ character name preservation
- **Local-only:** No network calls, full privacy
- **Context-aware:** 4096 token context window

**Cons:**
- Requires llama-cpp-python with CUDA (38-min build)
- CPU-only mode is slower than T5 (but higher quality)

**Performance (Real-world 15,927-word test):**
- CPU: 36.4 minutes (438 words/minute)
- GPU: 10.0 minutes (1,587 words/minute)
- Novel (90K words): 3.4 hours (CPU) → 57 minutes (GPU)

**Usage:**
```bash
# Full pipeline with GRMR-V3 (GPU)
python -m pipeline.pipeline_runner --use-grmr input.md

# Hybrid mode (GRMR + spell-check)
python -m pipeline.pipeline_runner --use-grmr --grmr-mode hybrid input.epub
```

**Documentation:**
- `docs/GRMR_V3_GGUF_TEST_PLAN.md` - Quality benchmarks
- `GRMR_V3_QUALITY_REPORT.md` - Detailed quality analysis
- `docs/GPU_SETUP_GUIDE.md` - GPU setup guide

---

## 5. Lessons Learned

### 5.1 What Worked

✅ **Pipes-and-Filters architecture** - Clean separation of concerns, easy to test
✅ **GGUF quantized models** - Best balance of quality, speed, and memory
✅ **GPU acceleration** - 3.62x speedup makes batch processing practical
✅ **Paragraph-level chunking** - Fits within context windows, preserves context
✅ **Deterministic parameters** - `temperature=0.1` ensures consistent output
✅ **Comprehensive testing** - Unit, integration, regression tests caught issues early
✅ **JSON logging** - Made debugging and optimization much easier

### 5.2 What Didn't Work

❌ **JamSpell** - Never got it working reliably, abandoned
❌ **T5 GPU inference via GGUF** - Runtime crashes with T5 architecture
❌ **Higher temperature** - `temperature=0.7` introduced grammar errors
❌ **Deep Markdown nesting** - Parser/writer struggles with complex inline formatting
❌ **EPUB full coverage** - Only handles `<p>` tags, skips headers/lists
❌ **LanguageTool local JVM** - Too slow, switched to public API

### 5.3 Key Insights

**Model Selection:**
- GGUF quantized models >> Transformers for this use case
- 4-bit quantization sufficient for grammar correction
- Qwen3 architecture more stable than T5 on GPU

**Performance:**
- GPU acceleration worth the 38-minute build time
- Paragraph-level chunking better than sentence-level
- Batch processing not necessary with GPU speed

**Quality:**
- Lower temperature (0.1) >> higher temperature (0.7) for consistency
- Character name preservation requires explicit prompt engineering
- Test-driven development essential for quality validation

**Architecture:**
- Pluggable filters >> monolithic correction engine
- Metadata preservation crucial for Markdown/EPUB round-trip
- JSON logging >> text logs for debugging ML pipelines

---

## 6. Dependencies

### 6.1 Core Dependencies (requirements.txt)

```
Markdown>=3.3.0           # Markdown parsing/generation
language-tool-python>=2.7 # Grammar checking (LanguageTool API)
pytest>=7.0.0             # Testing framework
num2words>=0.5.12         # Number to words conversion (TTS)
ebooklib>=0.18            # EPUB parsing/generation
beautifulsoup4>=4.11.0    # HTML parsing for EPUB
pyspellchecker>=0.7.0     # Spell checking
```

### 6.2 T5 Transformer (requirements-t5.txt)

```
torch>=2.0.0              # PyTorch for T5 models
transformers>=4.30.0      # Hugging Face Transformers
```

**Note:** T5 support is experimental. GRMR-V3 is recommended for production use.

### 6.3 GRMR-V3 GGUF (GPU-enabled)

**CPU-only (pre-built wheels):**
```bash
pip install llama-cpp-python
```

**GPU-accelerated (build from source):**
- Visual Studio 2022 with C++ tools
- CUDA Toolkit 13.0+
- Python 3.11 (3.13 not yet supported for GPU builds)
- ~38 minute compilation time

**Build script:** `install_llama_cpp_cuda.ps1`
**Setup guide:** `docs/GPU_SETUP_GUIDE.md`

### 6.4 System Requirements

**Minimum (CPU-only):**
- Python 3.11+
- 8GB RAM
- 5GB disk space (models)

**Recommended (GPU):**
- Python 3.11 (for GPU builds)
- NVIDIA GPU with 8GB+ VRAM (Compute Capability 7.0+)
- CUDA 13.0
- Visual Studio 2022 (Windows) or GCC 11+ (Linux)
- 16GB system RAM

---

## 7. Testing & Validation

### 7.1 Test Structure

```
tests/
├── unit/                    # Unit tests for individual filters
│   ├── test_grmr_v3_filter.py     (20 tests - GRMR-V3 filter)
│   ├── test_t5_corrector.py       (T5 corrector module)
│   ├── test_spelling_filter.py    (Spell checker)
│   └── test_markdown_parser.py    (Markdown parsing)
├── integration/             # End-to-end pipeline tests
│   └── test_pipeline.py           (Full Markdown/EPUB workflows)
└── regression_corpus/       # Golden input/output pairs
    ├── input_*.md               (Test inputs)
    └── golden_*.md              (Expected outputs)
```

### 7.2 Running Tests

```bash
# All tests
pytest

# Fast tests only (skip slow model downloads)
pytest -m "not slow"

# Specific test suite
pytest tests/unit/test_grmr_v3_filter.py

# With coverage
pytest --cov=pipeline --cov-report=html
```

### 7.3 Quality Benchmarks

**GRMR-V3 Quality Tests:**
```bash
# Run 31-test quality benchmark (100% pass rate)
python benchmark_grmr_quality.py

# Long document test (15K+ words)
python test_long_document_gpu.py
```

**Results:**
- **Accuracy:** 100% (51/51 tests passing)
- **Character preservation:** 99%+
- **Quality grade:** A (95/100)
- **Correction rate:** 92% of paragraphs improved

### 7.4 Regression Testing

The `tests/regression_corpus/` directory contains golden input/output pairs to prevent quality regressions. Each commit is validated against these samples to ensure consistency.

---

## 6. Alpha Performance Target

The alpha milestone focuses on processing a 300-page manuscript (~9k sentences) within 30 minutes on a GTX-class GPU with ≤8 GB VRAM. The current T5 integration already exposes:

- Half-precision inference and automatic CPU/GPU/MPS selection.
- Batch APIs for sentence-level and block-level correction.
- Mode switches that let operators trade accuracy for throughput (e.g., `replace` versus `hybrid`).

Empirical guidance from `docs/T5_CORRECTOR_GUIDE.md` reports 0.5–2 seconds per sentence on NVIDIA GPUs with roughly 6–8 GB VRAM usage, indicating the throughput goal is attainable once batching and concurrency are tuned for long-form runs.

---

## 7. Roadmap Toward TTS-Centric Enhancements

1. **TTS-specific error surfacing** – exploit `T5Corrector` confidence hooks and pipeline statistics to flag sentences that still break downstream TTS playback (e.g., abbreviations, numerics, phonetic anomalies).
2. **Targeted normalization strategies** – expand `TTSNormalizer` coverage using insights from logged transformer corrections and TTS regression results.
3. **Spell-check upgrade** – evaluate JamSpell or other context-aware engines to reduce false positives before transformer passes.
4. **Runbook recipes** – formalize operational guidance for switching T5 modes, adjusting batch sizes, or falling back to deterministic filters when GPU memory is scarce.
5. **Fine-tuning & prompt engineering** – experiment with domain-specific corpora, penalty prompts, or lightweight LoRA adapters once the baseline alpha workflow is stable.

---

## 8. Getting Started

1. Install dependencies (CPU baseline):
   ```bash
   pip install -r requirements.txt
   ```
2. For transformer work, install the T5 extras:
   ```bash
   pip install -r requirements-t5.txt
   ```
3. Run the pipeline on a sample Markdown file:
   ```bash
   python -m pipeline.pipeline_runner tests/samples/sample.md
   ```
4. Explore T5 integration by toggling `--use-t5` and reviewing the JSON logs for per-filter statistics.

The repository also ships helper scripts (`setup_t5_env.sh`, `check_cuda.py`, `fix_cuda.sh`) to validate CUDA availability and bootstrap GPU environments when running on workstations with limited VRAM.

---

## 9. References & Further Reading

- `docs/T5_CORRECTOR_GUIDE.md` – comprehensive T5 usage guide, performance tuning, and troubleshooting.
- `docs/GPU_SETUP_GUIDE.md` – GPU acceleration setup, CUDA compilation, and troubleshooting.
- `docs/GRMR_V3_GGUF_TEST_PLAN.md` – GRMR-V3 test plan and quality benchmarks.
- `T5_INTEGRATION_SUMMARY.md` – high-level summary of the transformer milestone.
- `T5_INTEGRATION_GUIDE.md` – step-by-step walkthrough for environment setup and regression validation.
- `tests/samples/` – miniature documents for experimenting with pipeline behaviour.

With the T5 pipeline merged, SATCN is positioned to deliver an end-to-end alpha capable of correcting full-length books on commodity GPUs while laying the groundwork for the next phase of TTS-focused quality improvements.
