# SATCN – Spelling and Text Correction Normalizer# SATCN – Spelling and Text Correction Normalizer



**A personal project for one-shot document correction optimized for TTS preprocessing.****A personal project for one-shot document correction optimized for TTS preprocessing.**



SATCN is an experimental document correction pipeline designed to process long-form Markdown or EPUB content, repair spelling and grammar issues, and output clean corrected versions ready for Text-to-Speech (TTS) engines. This project explores different approaches to automated text correction—from rule-based filters to transformer models to GGUF quantized models—with a focus on privacy (local-only processing), performance (GPU acceleration), and quality (preserving author voice and character names).SATCN is an experimental document correction pipeline designed to process long-form Markdown or EPUB content, repair spelling and grammar issues, and output clean corrected versions ready for Text-to-Speech (TTS) engines. This project explores different approaches to automated text correction—from rule-based filters to transformer models to GGUF quantized models—with a focus on privacy (local-only processing), performance (GPU acceleration), and quality (preserving author voice and character names).



**Project Status:** Active Development | Personal/Educational Use | CPU & GPU Support**Project Status:** Active Development | Personal/Educational Use | CPU & GPU Support



------



## 1. Why This Project Exists## 1. Why This Project Exists



**Personal Motivation:** I wanted a local, privacy-respecting tool to clean up text documents before feeding them to TTS engines. Commercial solutions either require cloud uploads (privacy concerns) or produce inconsistent quality. This project explores building a flexible correction pipeline that:**Personal Motivation:** I wanted a local, privacy-respecting tool to clean up text documents before feeding them to TTS engines. Commercial solutions either require cloud uploads (privacy concerns) or produce inconsistent quality. This project explores building a flexible correction pipeline that:



1. **Runs locally** - No cloud dependencies, full privacy1. **Runs locally** - No cloud dependencies, full privacy

2. **Preserves formatting** - Maintains Markdown/EPUB structure and inline formatting2. **Preserves formatting** - Maintains Markdown/EPUB structure and inline formatting

3. **Handles long documents** - Novels (90K+ words), not just snippets3. **Handles long documents** - Novels (90K+ words), not just snippets

4. **Leverages modern ML** - Transformer models and quantized GGUF models4. **Leverages modern ML** - Transformer models and quantized GGUF models

5. **Optimizes for TTS** - Special handling for numbers, dates, currency5. **Optimizes for TTS** - Special handling for numbers, dates, currency

6. **Supports GPU acceleration** - 3-4x speedup for batch processing6. **Supports GPU acceleration** - 3-4x speedup for batch processing



## 2. Current Status## 2. Current Status



| Component | Status | Performance | Notes || Component | Status | Performance | Notes |

|-----------|--------|-------------|-------||-----------|--------|-------------|-------|

| **Core Pipeline** | ✅ Production | - | Pipes-and-Filters architecture working || **Core Pipeline** | ✅ Production | - | Pipes-and-Filters architecture working |

| **Markdown I/O** | ✅ Stable | - | Preserves structure, struggles with deep nesting || **Markdown I/O** | ✅ Stable | - | Preserves structure, struggles with deep nesting |

| **EPUB I/O** | ✅ Stable | - | Handles `<p>` tags, metadata preservation || **EPUB I/O** | ✅ Stable | - | Handles `<p>` tags, metadata preservation |

| **Spelling Filter** | ✅ Working | Fast | `pyspellchecker` - basic but functional || **Spelling Filter** | ✅ Working | Fast | `pyspellchecker` - basic but functional |

| **Grammar Filter (Safe)** | ✅ Working | Slow | LanguageTool public API (conservative ruleset) || **Grammar Filter (Safe)** | ✅ Working | Slow | LanguageTool public API (conservative ruleset) |

| **GRMR-V3 GGUF** | ✅ **Production** | **438 wpm CPU<br>1,587 wpm GPU** | **Best quality, GPU-ready, 100% test accuracy** || **GRMR-V3 GGUF** | ✅ **Production** | **438 wpm CPU<br>1,587 wpm GPU** | **Best quality, GPU-ready, 100% test accuracy** |

| **T5 Transformer** | ⚠️ Experimental | Slow | Works but memory-intensive || **T5 Transformer** | ⚠️ Experimental | Slow | Works but memory-intensive |

| **TTS Normalizer** | ✅ Working | Fast | Converts numbers, dates, currency || **TTS Normalizer** | ✅ Working | Fast | Converts numbers, dates, currency |

| **GPU Acceleration** | ✅ Validated | **3.62x speedup** | CUDA 13.0, works with GRMR-V3 || **GPU Acceleration** | ✅ Validated | **3.62x speedup** | CUDA 13.0, works with GRMR-V3 |

| **Test Suite** | ✅ Comprehensive | - | Unit, integration, regression tests || **Test Suite** | ✅ Comprehensive | - | Unit, integration, regression tests |



### What Works Best### What Works Best



**Recommended Configuration (GPU):****Recommended Configuration (GPU):**

```bash```bash

python -m pipeline.pipeline_runner --use-grmr input.mdpython -m pipeline.pipeline_runner --use-grmr input.md

``````

- **Quality:** Grade A (95/100) - Production ready- **Quality:** Grade A (95/100) - Production ready

- **Speed:** 1,587 words/minute (GPU) or 438 wpm (CPU)- **Speed:** 1,587 words/minute (GPU) or 438 wpm (CPU)

- **Privacy:** Fully local, no network calls- **Privacy:** Fully local, no network calls

- **Reliability:** 100% test accuracy, 99%+ character name preservation- **Reliability:** 100% test accuracy, 99%+ character name preservation



------



## 3. Architecture: Pipes-and-Filters Design## 3. Architecture: Pipes-and-Filters Design



The pipeline implements a classic Pipes-and-Filters pattern where each stage transforms a shared `data` dictionary:The pipeline implements a classic Pipes-and-Filters pattern where each stage transforms a shared `data` dictionary:



``````

Input File → Parser → [Correction Filters] → TTS Normalizer → Output GeneratorInput File → Parser → [Correction Filters] → TTS Normalizer → Output Generator

``````



### 3.1 Pipeline Stages### 3.1 Pipeline Stages



**1. Parser** (`MarkdownParserFilter` or `EpubParserFilter`)**1. Parser** (`MarkdownParserFilter` or `EpubParserFilter`)

- Converts input file into structured `text_blocks`- Converts input file into structured `text_blocks`

- Preserves formatting metadata (bold, italic, links)- Preserves formatting metadata (bold, italic, links)

- Maintains document tree for round-trip output- Maintains document tree for round-trip output



**2. Correction Filters** (pluggable, mode-dependent)**2. Correction Filters** (pluggable, mode-dependent)

- **Default:** `SpellingCorrectionFilter` → `GrammarCorrectionFilterSafe`- **Default:** `SpellingCorrectionFilter` → `GrammarCorrectionFilterSafe`

- **GRMR-V3:** `GRMRV3GrammarFilter` (recommended, GPU-ready)- **GRMR-V3:** `GRMRV3GrammarFilter` (recommended, GPU-ready)

- **T5:** `T5CorrectionFilter` (experimental, memory-intensive)- **T5:** `T5CorrectionFilter` (experimental, memory-intensive)

- Each filter receives `text_blocks`, modifies `content`, returns modified data- Each filter receives `text_blocks`, modifies `content`, returns modified data



**3. TTS Normalizer** (`TTSNormalizer`)**3. TTS Normalizer** (`TTSNormalizer`)

- Converts "$99.99" → "ninety-nine dollars and ninety-nine cents"- Converts "$99.99" → "ninety-nine dollars and ninety-nine cents"

- Expands "3rd" → "third", "10:30 AM" → "ten thirty AM"- Expands "3rd" → "third", "10:30 AM" → "ten thirty AM"

- Ensures TTS engines pronounce text naturally- Ensures TTS engines pronounce text naturally



**4. Output Generator** (`MarkdownOutputGenerator` or `EpubOutputGenerator`)**4. Output Generator** (`MarkdownOutputGenerator` or `EpubOutputGenerator`)

- Reconstructs document from corrected `text_blocks`- Reconstructs document from corrected `text_blocks`

- Writes `input_corrected.md` or `input_corrected.epub`- Writes `input_corrected.md` or `input_corrected.epub`

- Preserves original structure and formatting- Preserves original structure and formatting



### 3.2 Key Design Decisions### 3.2 Key Design Decisions



✅ **Separation of concerns** - Each filter has one job  ✅ **Separation of concerns** - Each filter has one job  

✅ **Metadata preservation** - Formatting survives correction  ✅ **Metadata preservation** - Formatting survives correction  

✅ **Mode flexibility** - Swap filters at runtime (`--use-grmr`, `--use-t5`)  ✅ **Mode flexibility** - Swap filters at runtime (`--use-grmr`, `--use-t5`)  

✅ **Fail-fast support** - Stop on first error or continue  ✅ **Fail-fast support** - Stop on first error or continue  

✅ **JSON logging** - Structured logs with per-filter statistics  ✅ **JSON logging** - Structured logs with per-filter statistics  



------



## 4. Grammar Correction Approaches## 4. Grammar Correction Approaches



The project has explored three approaches to grammar correction:The project has explored three approaches to grammar correction:



### 4.1 LanguageTool (Rule-Based) - Baseline### 4.1 LanguageTool (Rule-Based) - Baseline



**Status:** ✅ Working, but slow  **Status:** ✅ Working, but slow  

**Implementation:** `GrammarCorrectionFilterSafe`  **Implementation:** `GrammarCorrectionFilterSafe`  

**Backend:** LanguageTool public API with conservative ruleset**Backend:** LanguageTool public API with conservative ruleset



**Pros:****Pros:**

- Deterministic, explainable corrections- Deterministic, explainable corrections

- Low memory footprint- Low memory footprint

- No model downloads- No model downloads



**Cons:****Cons:**

- Slow (network API calls)- Slow (network API calls)

- Limited context awareness- Limited context awareness

- Conservative (misses many errors)- Conservative (misses many errors)



**Use case:** Fallback option, development testing**Use case:** Fallback option, development testing



### 4.2 T5 Transformer (ML-Based) - Experimental### 4.2 T5 Transformer (ML-Based) - Experimental



**Status:** ⚠️ Experimental, memory-intensive  **Status:** ⚠️ Experimental, memory-intensive  

**Implementation:** `T5CorrectionFilter`  **Implementation:** `T5CorrectionFilter`  

**Model:** FLAN-T5 (Hugging Face)**Model:** FLAN-T5 (Hugging Face)



**Pros:****Pros:**

- Context-aware corrections- Context-aware corrections

- Can handle complex grammar- Can handle complex grammar



**Cons:****Cons:**

- Large memory footprint (6-8 GB VRAM)- Large memory footprint (6-8 GB VRAM)

- Slower than GGUF models- Slower than GGUF models

- Requires PyTorch/Transformers- Requires PyTorch/Transformers

- Can alter author voice- Can alter author voice



**Use case:** Experimentation, comparison studies**Use case:** Experimentation, comparison studies



**Modes:****Modes:**

- `--use-t5 --t5-mode replace` - T5 only (fastest)- `--use-t5 --t5-mode replace` - T5 only (fastest)

- `--use-t5 --t5-mode hybrid` - T5 + rule-based cleanup- `--use-t5 --t5-mode hybrid` - T5 + rule-based cleanup

- `--use-t5 --t5-mode supplement` - Rule-based + T5 polish- `--use-t5 --t5-mode supplement` - Rule-based + T5 polish



### 4.3 GRMR-V3 GGUF (Quantized ML) - **Recommended** ⭐### 4.3 GRMR-V3 GGUF (Quantized ML) - **Recommended** ⭐



**Status:** ✅ Production-ready, GPU-accelerated  **Status:** ✅ Production-ready, GPU-accelerated  

**Implementation:** `GRMRV3GrammarFilter`  **Implementation:** `GRMRV3GrammarFilter`  

**Model:** GRMR-V3-Q4B (Qwen3 4B, 4-bit quantized, 2.5GB)**Model:** GRMR-V3-Q4B (Qwen3 4B, 4-bit quantized, 2.5GB)



**Pros:****Pros:**

- **High quality:** 100% test accuracy, Grade A quality (95/100)- **High quality:** 100% test accuracy, Grade A quality (95/100)

- **GPU-ready:** 3.62x speedup (1,587 wpm vs 438 wpm CPU)- **GPU-ready:** 3.62x speedup (1,587 wpm vs 438 wpm CPU)

- **Memory efficient:** ~3.2GB VRAM (4-bit quantization)- **Memory efficient:** ~3.2GB VRAM (4-bit quantization)

- **Preserves voice:** 99%+ character name preservation- **Preserves voice:** 99%+ character name preservation

- **Local-only:** No network calls, full privacy- **Local-only:** No network calls, full privacy

- **Context-aware:** 4096 token context window- **Context-aware:** 4096 token context window



**Cons:****Cons:**

- Requires llama-cpp-python with CUDA (38-min build)- Requires llama-cpp-python with CUDA (38-min build)

- CPU-only mode is slower than T5 (but higher quality)- CPU-only mode is slower than T5 (but higher quality)



**Performance (Real-world 15,927-word test):****Performance (Real-world 15,927-word test):**

- CPU: 36.4 minutes (438 words/minute)- CPU: 36.4 minutes (438 words/minute)

- GPU: 10.0 minutes (1,587 words/minute)- GPU: 10.0 minutes (1,587 words/minute)

- Novel (90K words): 3.4 hours (CPU) → 57 minutes (GPU)- Novel (90K words): 3.4 hours (CPU) → 57 minutes (GPU)



**Usage:****Usage:**

```bash```bash

# Full pipeline with GRMR-V3 (GPU)# Full pipeline with GRMR-V3 (GPU)

python -m pipeline.pipeline_runner --use-grmr input.mdpython -m pipeline.pipeline_runner --use-grmr input.md



# Hybrid mode (GRMR + spell-check)# Hybrid mode (GRMR + spell-check)

python -m pipeline.pipeline_runner --use-grmr --grmr-mode hybrid input.epubpython -m pipeline.pipeline_runner --use-grmr --grmr-mode hybrid input.epub

``````



**Documentation:****Documentation:**

- `docs/GRMR_V3_GGUF_TEST_PLAN.md` - Quality benchmarks- `docs/GRMR_V3_GGUF_TEST_PLAN.md` - Quality benchmarks

- `GRMR_V3_QUALITY_REPORT.md` - Detailed quality analysis- `GRMR_V3_QUALITY_REPORT.md` - Detailed quality analysis

- `docs/GPU_SETUP_GUIDE.md` - GPU setup guide- `docs/GPU_SETUP_GUIDE.md` - GPU setup guide



------



## 5. Lessons Learned## 5. Lessons Learned



### 5.1 What Worked### 5.1 What Worked



✅ **Pipes-and-Filters architecture** - Clean separation of concerns, easy to test  ✅ **Pipes-and-Filters architecture** - Clean separation of concerns, easy to test  

✅ **GGUF quantized models** - Best balance of quality, speed, and memory  ✅ **GGUF quantized models** - Best balance of quality, speed, and memory  

✅ **GPU acceleration** - 3.62x speedup makes batch processing practical  ✅ **GPU acceleration** - 3.62x speedup makes batch processing practical  

✅ **Paragraph-level chunking** - Fits within context windows, preserves context  ✅ **Paragraph-level chunking** - Fits within context windows, preserves context  

✅ **Deterministic parameters** - `temperature=0.1` ensures consistent output  ✅ **Deterministic parameters** - `temperature=0.1` ensures consistent output  

✅ **Comprehensive testing** - Unit, integration, regression tests caught issues early  ✅ **Comprehensive testing** - Unit, integration, regression tests caught issues early  

✅ **JSON logging** - Made debugging and optimization much easier  ✅ **JSON logging** - Made debugging and optimization much easier  



### 5.2 What Didn't Work### 5.2 What Didn't Work



❌ **JamSpell** - Never got it working reliably, abandoned  ❌ **JamSpell** - Never got it working reliably, abandoned  

❌ **T5 GPU inference via GGUF** - Runtime crashes with T5 architecture  ❌ **T5 GPU inference via GGUF** - Runtime crashes with T5 architecture  

❌ **Higher temperature** - `temperature=0.7` introduced grammar errors  ❌ **Higher temperature** - `temperature=0.7` introduced grammar errors  

❌ **Deep Markdown nesting** - Parser/writer struggles with complex inline formatting  ❌ **Deep Markdown nesting** - Parser/writer struggles with complex inline formatting  

❌ **EPUB full coverage** - Only handles `<p>` tags, skips headers/lists  ❌ **EPUB full coverage** - Only handles `<p>` tags, skips headers/lists  

❌ **LanguageTool local JVM** - Too slow, switched to public API  ❌ **LanguageTool local JVM** - Too slow, switched to public API  



### 5.3 Key Insights### 5.3 Key Insights



**Model Selection:****Model Selection:**

- GGUF quantized models >> Transformers for this use case- GGUF quantized models >> Transformers for this use case

- 4-bit quantization sufficient for grammar correction- 4-bit quantization sufficient for grammar correction

- Qwen3 architecture more stable than T5 on GPU- Qwen3 architecture more stable than T5 on GPU



**Performance:****Performance:**

- GPU acceleration worth the 38-minute build time- GPU acceleration worth the 38-minute build time

- Paragraph-level chunking better than sentence-level- Paragraph-level chunking better than sentence-level

- Batch processing not necessary with GPU speed- Batch processing not necessary with GPU speed



**Quality:****Quality:**

- Lower temperature (0.1) >> higher temperature (0.7) for consistency- Lower temperature (0.1) >> higher temperature (0.7) for consistency

- Character name preservation requires explicit prompt engineering- Character name preservation requires explicit prompt engineering

- Test-driven development essential for quality validation- Test-driven development essential for quality validation



**Architecture:****Architecture:**

- Pluggable filters >> monolithic correction engine- Pluggable filters >> monolithic correction engine

- Metadata preservation crucial for Markdown/EPUB round-trip- Metadata preservation crucial for Markdown/EPUB round-trip

- JSON logging >> text logs for debugging ML pipelines- JSON logging >> text logs for debugging ML pipelines



------



## 6. Dependencies## 6. Dependencies



### 6.1 Core Dependencies (requirements.txt)### 6.1 Core Dependencies (requirements.txt)



``````

Markdown>=3.3.0           # Markdown parsing/generationMarkdown>=3.3.0           # Markdown parsing/generation

language-tool-python>=2.7 # Grammar checking (LanguageTool API)language-tool-python>=2.7 # Grammar checking (LanguageTool API)

pytest>=7.0.0             # Testing frameworkpytest>=7.0.0             # Testing framework

num2words>=0.5.12         # Number to words conversion (TTS)num2words>=0.5.12         # Number to words conversion (TTS)

ebooklib>=0.18            # EPUB parsing/generationebooklib>=0.18            # EPUB parsing/generation

beautifulsoup4>=4.11.0    # HTML parsing for EPUBbeautifulsoup4>=4.11.0    # HTML parsing for EPUB

pyspellchecker>=0.7.0     # Spell checkingpyspellchecker>=0.7.0     # Spell checking

``````



### 6.2 T5 Transformer (requirements-t5.txt)### 6.2 T5 Transformer (requirements-t5.txt)



``````

torch>=2.0.0              # PyTorch for T5 modelstorch>=2.0.0              # PyTorch for T5 models

transformers>=4.30.0      # Hugging Face Transformerstransformers>=4.30.0      # Hugging Face Transformers

``````



**Note:** T5 support is experimental. GRMR-V3 is recommended for production use.**Note:** T5 support is experimental. GRMR-V3 is recommended for production use.



### 6.3 GRMR-V3 GGUF (GPU-enabled)### 6.3 GRMR-V3 GGUF (GPU-enabled)



**CPU-only (pre-built wheels):****CPU-only (pre-built wheels):**

```bash```bash

pip install llama-cpp-pythonpip install llama-cpp-python

``````



**GPU-accelerated (build from source):****GPU-accelerated (build from source):**

- Visual Studio 2022 with C++ tools- Visual Studio 2022 with C++ tools

- CUDA Toolkit 13.0+- CUDA Toolkit 13.0+

- Python 3.11 (3.13 not yet supported for GPU builds)- Python 3.11 (3.13 not yet supported for GPU builds)

- ~38 minute compilation time- ~38 minute compilation time



**Build script:** `install_llama_cpp_cuda.ps1`  **Build script:** `install_llama_cpp_cuda.ps1`  

**Setup guide:** `docs/GPU_SETUP_GUIDE.md`**Setup guide:** `docs/GPU_SETUP_GUIDE.md`



### 6.4 System Requirements### 6.4 System Requirements



**Minimum (CPU-only):****Minimum (CPU-only):**

- Python 3.11+- Python 3.11+

- 8GB RAM- 8GB RAM

- 5GB disk space (models)- 5GB disk space (models)



**Recommended (GPU):****Recommended (GPU):**

- Python 3.11 (for GPU builds)- Python 3.11 (for GPU builds)

- NVIDIA GPU with 8GB+ VRAM (Compute Capability 7.0+)- NVIDIA GPU with 8GB+ VRAM (Compute Capability 7.0+)

- CUDA 13.0- CUDA 13.0

- Visual Studio 2022 (Windows) or GCC 11+ (Linux)- Visual Studio 2022 (Windows) or GCC 11+ (Linux)

- 16GB system RAM- 16GB system RAM



------



## 7. Testing & Validation## 7. Testing & Validation



### 7.1 Test Structure### 7.1 Test Structure



``````

tests/tests/

├── unit/                    # Unit tests for individual filters├── unit/                    # Unit tests for individual filters

│   ├── test_grmr_v3_filter.py     (20 tests - GRMR-V3 filter)│   ├── test_grmr_v3_filter.py     (20 tests - GRMR-V3 filter)

│   ├── test_t5_corrector.py       (T5 corrector module)│   ├── test_t5_corrector.py       (T5 corrector module)

│   ├── test_spelling_filter.py    (Spell checker)│   ├── test_spelling_filter.py    (Spell checker)

│   └── test_markdown_parser.py    (Markdown parsing)│   └── test_markdown_parser.py    (Markdown parsing)

├── integration/             # End-to-end pipeline tests├── integration/             # End-to-end pipeline tests

│   └── test_pipeline.py           (Full Markdown/EPUB workflows)│   └── test_pipeline.py           (Full Markdown/EPUB workflows)

└── regression_corpus/       # Golden input/output pairs└── regression_corpus/       # Golden input/output pairs

    ├── input_*.md               (Test inputs)    ├── input_*.md               (Test inputs)

    └── golden_*.md              (Expected outputs)    └── golden_*.md              (Expected outputs)

``````



### 7.2 Running Tests### 7.2 Running Tests



```bash```bash

# All tests# All tests

pytestpytest



# Fast tests only (skip slow model downloads)# Fast tests only (skip slow model downloads)

pytest -m "not slow"pytest -m "not slow"



# Specific test suite# Specific test suite

pytest tests/unit/test_grmr_v3_filter.pypytest tests/unit/test_grmr_v3_filter.py



# With coverage# With coverage

pytest --cov=pipeline --cov-report=htmlpytest --cov=pipeline --cov-report=html

``````



### 7.3 Quality Benchmarks### 7.3 Quality Benchmarks



**GRMR-V3 Quality Tests:****GRMR-V3 Quality Tests:**

```bash```bash

# Run 31-test quality benchmark (100% pass rate)# Run 31-test quality benchmark (100% pass rate)

python benchmark_grmr_quality.pypython benchmark_grmr_quality.py



# Long document test (15K+ words)# Long document test (15K+ words)

python test_long_document_gpu.pypython test_long_document_gpu.py

``````



**Results:****Results:**

- **Accuracy:** 100% (51/51 tests passing)- **Accuracy:** 100% (51/51 tests passing)

- **Character preservation:** 99%+- **Character preservation:** 99%+

- **Quality grade:** A (95/100)- **Quality grade:** A (95/100)

- **Correction rate:** 92% of paragraphs improved- **Correction rate:** 92% of paragraphs improved



### 7.4 Regression Testing### 7.4 Regression Testing



The `tests/regression_corpus/` directory contains golden input/output pairs to prevent quality regressions. Each commit is validated against these samples to ensure consistency.The `tests/regression_corpus/` directory contains golden input/output pairs to prevent quality regressions. Each commit is validated against these samples to ensure consistency.



------



## 8. Getting Started## 6. Alpha Performance Target



### 8.1 Quick Start (CPU - No GPU Required)The alpha milestone focuses on processing a 300-page manuscript (~9k sentences) within 30 minutes on a GTX-class GPU with ≤8 GB VRAM. The current T5 integration already exposes:



```bash- Half-precision inference and automatic CPU/GPU/MPS selection.

# 1. Clone repository- Batch APIs for sentence-level and block-level correction.

git clone https://github.com/hebbihebb/SATCN.git- Mode switches that let operators trade accuracy for throughput (e.g., `replace` versus `hybrid`).

cd SATCN

Empirical guidance from `docs/T5_CORRECTOR_GUIDE.md` reports 0.5–2 seconds per sentence on NVIDIA GPUs with roughly 6–8 GB VRAM usage, indicating the throughput goal is attainable once batching and concurrency are tuned for long-form runs.

# 2. Create virtual environment

python -m venv .venv---

.venv\Scripts\activate  # Windows

# source .venv/bin/activate  # Linux/Mac## 7. Roadmap Toward TTS-Centric Enhancements



# 3. Install dependencies1. **TTS-specific error surfacing** – exploit `T5Corrector` confidence hooks and pipeline statistics to flag sentences that still break downstream TTS playback (e.g., abbreviations, numerics, phonetic anomalies).

pip install -r requirements.txt2. **Targeted normalization strategies** – expand `TTSNormalizer` coverage using insights from logged transformer corrections and TTS regression results.

3. **Spell-check upgrade** – evaluate JamSpell or other context-aware engines to reduce false positives before transformer passes.

# 4. Run pipeline on sample file4. **Runbook recipes** – formalize operational guidance for switching T5 modes, adjusting batch sizes, or falling back to deterministic filters when GPU memory is scarce.

python -m pipeline.pipeline_runner tests/samples/sample_markdown_basic.md5. **Fine-tuning & prompt engineering** – experiment with domain-specific corpora, penalty prompts, or lightweight LoRA adapters once the baseline alpha workflow is stable.



# 5. Check output---

ls *_corrected.md

```## 8. Getting Started



### 8.2 Enable GRMR-V3 (Recommended)1. Install dependencies (CPU baseline):

   ```bash

```bash   pip install -r requirements.txt

# CPU-only (fast install)   ```

pip install llama-cpp-python2. For transformer work, install the T5 extras:

   ```bash

# Run with GRMR-V3   pip install -r requirements-t5.txt

python -m pipeline.pipeline_runner --use-grmr input.md   ```

```3. Run the pipeline on a sample Markdown file:

   ```bash

### 8.3 GPU Acceleration (Advanced)   python -m pipeline.pipeline_runner tests/samples/sample.md

   ```

**Prerequisites:** NVIDIA GPU, CUDA 13.0, Visual Studio 20224. Explore T5 integration by toggling `--use-t5` and reviewing the JSON logs for per-filter statistics.



```bashThe repository also ships helper scripts (`setup_t5_env.sh`, `check_cuda.py`, `fix_cuda.sh`) to validate CUDA availability and bootstrap GPU environments when running on workstations with limited VRAM.

# 1. Create Python 3.11 environment

python3.11 -m venv .venv-gpu---

.venv-gpu\Scripts\activate

## 9. References & Further Reading

# 2. Build llama-cpp-python with CUDA (~38 minutes)

.\install_llama_cpp_cuda.ps1- `docs/T5_CORRECTOR_GUIDE.md` – comprehensive T5 usage guide, performance tuning, and troubleshooting.

- `docs/GPU_SETUP_GUIDE.md` – GPU acceleration setup, CUDA compilation, and troubleshooting.

# 3. Run with GPU acceleration- `docs/GRMR_V3_GGUF_TEST_PLAN.md` – GRMR-V3 test plan and quality benchmarks.

python -m pipeline.pipeline_runner --use-grmr input.md- `T5_INTEGRATION_SUMMARY.md` – high-level summary of the transformer milestone.

```- `T5_INTEGRATION_GUIDE.md` – step-by-step walkthrough for environment setup and regression validation.

- `tests/samples/` – miniature documents for experimenting with pipeline behaviour.

**Full setup guide:** `docs/GPU_SETUP_GUIDE.md`

With the T5 pipeline merged, SATCN is positioned to deliver an end-to-end alpha capable of correcting full-length books on commodity GPUs while laying the groundwork for the next phase of TTS-focused quality improvements.

### 8.4 GUI Tools

**Full Pipeline GUI:**
```bash
python tools\pipeline_test_gui.py
```
- Browse files (.md, .epub, .txt)
- Select filters (spelling, grammar, T5, GRMR-V3)
- Configure modes (replace, hybrid, supplement)
- View real-time logs and statistics

**GRMR-V3 Quick Test GUI:**
```bash
run_grmr_v3_gui.bat
# or
python tools\grmr_v3_test_gui.py
```
- Test GRMR-V3 model directly (no pipeline)
- Adjust GPU parameters (temperature, top-p)
- Quick corrections for testing
- Performance benchmarking

---

## 9. Future Work & Roadmap

### 9.1 Planned Improvements

**High Priority:**
- [ ] Fix deep Markdown nesting in parser/writer
- [ ] Expand EPUB support beyond `<p>` tags (headers, lists)
- [ ] Add batch processing CLI (process entire directories)
- [ ] Streaming mode for real-time correction

**Medium Priority:**
- [ ] Better spell-checker (context-aware, not just dictionary)
- [ ] TTS-specific error detection (abbreviations, phonetics)
- [ ] Confidence scores for corrections
- [ ] Undo/diff view for corrections

**Low Priority / Research:**
- [ ] Fine-tune GRMR-V3 on domain-specific corpus
- [ ] Experiment with LoRA adapters
- [ ] Multi-language support
- [ ] Custom prompt templates per genre

### 9.2 Known Limitations

**Document Formats:**
- Markdown: Struggles with deeply nested inline formatting
- EPUB: Only processes `<p>` tags, skips headers/lists/tables
- No support for: DOCX, PDF, HTML, RTF

**Performance:**
- GPU requires 38-minute build (one-time setup)
- T5 GPU not working (architecture compatibility issue)
- No batch sentence processing (processes paragraph-by-paragraph)

**Quality:**
- May alter author voice if prompt not tuned
- Conservative on proper nouns (safety vs. accuracy trade-off)
- No confidence scores (binary correct/no-change)

### 9.3 Not Planned

❌ **Cloud/API integration** - Privacy-first, local-only by design  
❌ **Real-time collaborative editing** - Batch processing focus  
❌ **Mobile app** - Desktop/server workstation tool  
❌ **JamSpell integration** - Never worked reliably, abandoned  

---

## 10. Project Philosophy

**This is a personal/educational project with specific goals:**

1. **Privacy-first** - All processing local, no cloud uploads
2. **Quality over speed** - GPU makes it fast enough, but quality comes first
3. **Transparent & explainable** - Test-driven, documented, observable
4. **TTS-optimized** - Designed for text-to-speech preprocessing
5. **Learning platform** - Exploring ML model quantization, GPU optimization, pipeline architecture

**Not intended for:**
- Production SaaS deployment
- Real-time interactive editing
- Enterprise-scale batch processing
- Multi-user collaborative workflows

---

## 11. Documentation

### 11.1 Core Documentation

- **README.md** (this file) - Project overview and getting started
- **docs/GPU_SETUP_GUIDE.md** - Complete GPU setup instructions
- **docs/GRMR_V3_GGUF_TEST_PLAN.md** - Quality benchmarks and test plan
- **GRMR_V3_QUALITY_REPORT.md** - Detailed quality analysis (Grade A)

### 11.2 Technical Documentation

- **docs/T5_CORRECTOR_GUIDE.md** - T5 transformer usage (experimental)
- **T5_INTEGRATION_SUMMARY.md** - T5 milestone summary
- **T5_INTEGRATION_GUIDE.md** - T5 environment setup

### 11.3 Development Files

- **CONTRIBUTING.md** - Contribution guidelines
- **pytest.ini** - Test configuration
- **requirements.txt** - Core dependencies
- **requirements-t5.txt** - T5 transformer dependencies

---

## 12. Acknowledgments

**Models:**
- GRMR-V3-Q4B by qingy2024 (Hugging Face)
- FLAN-T5 by Google (experimental support)

**Libraries:**
- llama-cpp-python for GGUF inference
- LanguageTool for rule-based grammar
- PySpellChecker for spell checking
- Beautiful Soup & ebooklib for EPUB handling

**Inspirations:**
- This project explores local-first ML for text processing
- Built to solve a personal need for TTS preprocessing
- Educational journey into quantized models and GPU optimization

---

## 13. License & Usage

**License:** MIT (see LICENSE file)

**Usage:** Personal/educational use encouraged. Not intended for commercial SaaS deployment.

**Attribution:** If you use this project or build on it, attribution appreciated but not required.

---

## 14. Contact & Contributing

**Repository:** https://github.com/hebbihebb/SATCN

**Issues:** Bug reports and feature requests welcome via GitHub Issues

**Contributions:** See CONTRIBUTING.md for guidelines

**Note:** This is a personal project maintained as time permits. Response times may vary.
