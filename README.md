# SATCN – Spelling and Text Correction Normalizer

SATCN is a one-shot document correction pipeline designed to ingest long-form Markdown or EPUB content, repair spelling and grammar issues, and output a clean, corrected version ready for downstream Text-to-Speech (TTS) engines. The current experimental branch integrates a transformer-based T5 correction pass alongside the original rule-based filters so the system can scale from quick desktop fixes to GPU-accelerated book processing runs.

---

## 1. Project Snapshot

| Capability | Status | Notes |
| --- | --- | --- |
| Markdown parsing & regeneration | ✅ | Custom `MarkdownParserFilter` / `MarkdownOutputGenerator` pair preserves inline formatting and block structure. |
| EPUB parsing & regeneration | ✅ | `EpubParserFilter` + `EpubOutputGenerator` round-trip XHTML `<p>` content with metadata to update originals. |
| Spelling correction | ✅ | `SpellingCorrectionFilter` uses `pyspellchecker` as a lightweight baseline for all document types. |
| Grammar correction (safe rules) | ✅ | `GrammarCorrectionFilterSafe` wraps LanguageTool with a JVM→Public API→disabled fallback and a whitelisted rule set. |
| GRMR-V3 GGUF grammar correction | ✅ Production | `GRMRV3GrammarFilter` provides offline GGUF model inference via llama-cpp-python with 100% test accuracy and 438 words/minute on CPU. |
| TTS normalization | ✅ | `TTSNormalizer` converts currency, dates, ordinals, times, and percentages to TTS-friendly text. |
| Transformer (T5) correction | ✅ Experimental | `T5Corrector` module + `T5CorrectionFilter` enable replace/hybrid/supplement modes in `PipelineRunner`. |
| Logging & observability | ✅ | JSON logging with per-filter metadata, stats counters, and failure handling. |
| Automated testing | ✅ | Unit, integration, and regression corpus harnesses plus dedicated T5 suites. |
| Known gaps | ⚠️ | Markdown writer still struggles with deeply nested inline formatting; EPUB flow only touches `<p>` tags; JamSpell upgrade outstanding. |

---

## 2. Architecture Overview

SATCN follows a Pipes-and-Filters architecture implemented in `pipeline/pipeline_runner.py`. Each stage receives a shared `data` dictionary containing the parsed document, text blocks, metadata, and per-filter statistics.

1. **Parsing filters** load Markdown or EPUB sources into structured text blocks while keeping references to the original trees.
2. **Correction filters** (spelling, grammar, optional T5) operate only on text content so formatting metadata remains intact.
3. **Normalization filters** prepare the corrected text for speech synthesis.
4. **Output generators** write corrected Markdown or EPUB artifacts alongside the source document.

The runner streams filter execution logs as JSON, captures the number of blocks changed, and can optionally fail fast on the first error.

---

## 3. Transformer (T5) Integration

Recent work introduced a transformer-backed correction engine that can replace or augment the deterministic filters.

### 3.1 Core Components

- `satcn/correction/t5_corrector.py` – a 450+ line module that wraps Hugging Face FLAN-T5 checkpoints with batching, half-precision, device auto-detection, stats collection, and error handling.
- `pipeline/filters/t5_correction_filter.py` – adapts `T5Corrector` to the pipeline filter interface, emitting per-run statistics and log metadata.
- `pipeline/pipeline_runner.py` – exposes `--use-t5` and `--t5-mode {replace,hybrid,supplement}` flags so operators can toggle T5 at runtime without code changes.

### 3.2 Operating Modes

| Mode | Composition | When to use |
| --- | --- | --- |
| `replace` | Swap out spelling + grammar filters for T5 only. | Fastest path when transformer output is trusted. |
| `hybrid` | Run T5, then the rule-based spelling and grammar passes. | Highest accuracy with extra safeguards. |
| `supplement` | Keep existing filters and add T5 at the end. | Conservative polish or experimentation. |

### 3.3 Running the Pipeline

Standard rule-based pass:

```bash
python -m pipeline.pipeline_runner path/to/book.md
```

Enable T5 replacement mode:

```bash
python -m pipeline.pipeline_runner --use-t5 path/to/book.md
```

Hybrid mode keeps the deterministic filters after T5:

```bash
python -m pipeline.pipeline_runner --use-t5 --t5-mode hybrid path/to/book.epub
```

Output files are written beside the source with `_corrected` suffixed (`.md` or `.epub`).

### 3.4 Testing the Transformer Stack

| Scenario | Command | Notes |
| --- | --- | --- |
| Quick GPU/CPU smoke test | `python run_t5_test.py` | Downloads the default model and runs sample corrections. |
| Unit suite (mocked) | `pytest tests/unit/test_t5_corrector.py -k "not slow"` | Validates configuration, batching, stats, and error handling without model downloads. |
| Pipeline integration demo | `python test_t5_integration.py` | Shows `T5GrammarFilter` standalone and inside the pipeline data structure. |
| Full integration test | `pytest test_t5_corrector_integration.py -m slow` | Requires the FLAN-T5 checkpoint; exercise end-to-end correction. |

The transformer documentation lives in `docs/T5_CORRECTOR_GUIDE.md` and `T5_INTEGRATION_SUMMARY.md` with troubleshooting steps, performance tips, and advanced configuration examples.

---

## 3.5 GRMR-V3 GGUF Grammar Correction

The GRMR-V3 integration provides offline, privacy-focused grammar correction using a quantized GGUF model via llama-cpp-python.

### 3.5.1 Core Components

- `pipeline/filters/grmr_v3_filter.py` – wraps llama-cpp-python for CPU/GPU inference with automatic model downloading, context window management, and performance statistics.
- Model: GRMR-V3-Q4B.Q4_K_M.gguf (4-bit quantized, ~2.5GB) downloaded automatically from Hugging Face.
- Context window: 4096 tokens (documents are automatically chunked into paragraphs for processing).

### 3.5.2 Performance Characteristics

**CPU Performance (Intel i7/i9 or AMD Ryzen 7/9):**
- Processing rate: ~438 words/minute (7 words/second)
- Time per paragraph: ~8 seconds
- Chapter (3,500 words): ~8 minutes
- Novel (90,000 words): ~3.4 hours

**Quality Metrics:**
- Test accuracy: 100% (51/51 tests passing)
- Character name preservation: 99%+ in long documents
- Correction rate: 92% of paragraphs improved

**GPU Support:**
GPU acceleration is available but requires building llama-cpp-python from source with CUDA support. CPU performance is already production-ready for batch processing workflows.

### 3.5.3 Usage

The GRMR-V3 filter is integrated into the pipeline and can be used standalone:

```python
from pipeline.filters.grmr_v3_filter import GRMRV3GrammarFilter

# Initialize filter (downloads model on first run)
filter_obj = GRMRV3GrammarFilter()

# Correct text
corrected = filter_obj.correct_text("This is a sentence with grammer errors.")

# Get statistics
stats = filter_obj.get_stats()
print(f"Tokens generated: {stats['total_tokens_generated']}")
```

### 3.5.4 Testing

| Test Suite | Command | Coverage |
| --- | --- | --- |
| Unit tests | `pytest tests/unit/test_grmr_v3_filter.py` | 20 tests covering initialization, correction, errors, stats |
| Quality benchmark | `python benchmark_grmr_quality.py` | 31 real-world correction scenarios (100% accuracy) |
| Long document test | `python test_long_sample.py` | Real-world performance on 3K+ word samples |

Documentation: `docs/GRMR_V3_GGUF_TEST_PLAN.md`

---

## 4. Automated Verification Suite

SATCN’s regression discipline couples the transformer work with the existing test harnesses:

- `tests/unit/` – unit tests for filters, utilities, and the T5 corrector.
- `tests/integration/` – exercises Markdown and EPUB end-to-end flows.
- `tests/regression_corpus/` – golden samples that guard against output drift.
- `benchmark.py` – optional profiling helper for local performance studies.

Use `pytest` at the repository root to run the full suite. Individual slow tests are marked so you can exclude them with `-m "not slow"` during rapid iterations.

---

## 5. Alpha Performance Target

The alpha milestone focuses on processing a 300-page manuscript (~9k sentences) within 30 minutes on a GTX-class GPU with ≤8 GB VRAM. The current T5 integration already exposes:

- Half-precision inference and automatic CPU/GPU/MPS selection.
- Batch APIs for sentence-level and block-level correction.
- Mode switches that let operators trade accuracy for throughput (e.g., `replace` versus `hybrid`).

Empirical guidance from `docs/T5_CORRECTOR_GUIDE.md` reports 0.5–2 seconds per sentence on NVIDIA GPUs with roughly 6–8 GB VRAM usage, indicating the throughput goal is attainable once batching and concurrency are tuned for long-form runs.

---

## 6. Roadmap Toward TTS-Centric Enhancements

1. **TTS-specific error surfacing** – exploit `T5Corrector` confidence hooks and pipeline statistics to flag sentences that still break downstream TTS playback (e.g., abbreviations, numerics, phonetic anomalies).
2. **Targeted normalization strategies** – expand `TTSNormalizer` coverage using insights from logged transformer corrections and TTS regression results.
3. **Spell-check upgrade** – evaluate JamSpell or other context-aware engines to reduce false positives before transformer passes.
4. **Runbook recipes** – formalize operational guidance for switching T5 modes, adjusting batch sizes, or falling back to deterministic filters when GPU memory is scarce.
5. **Fine-tuning & prompt engineering** – experiment with domain-specific corpora, penalty prompts, or lightweight LoRA adapters once the baseline alpha workflow is stable.

---

## 7. Getting Started

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

## 8. References & Further Reading

- `docs/T5_CORRECTOR_GUIDE.md` – comprehensive T5 usage guide, performance tuning, and troubleshooting.
- `T5_INTEGRATION_SUMMARY.md` – high-level summary of the transformer milestone.
- `T5_INTEGRATION_GUIDE.md` – step-by-step walkthrough for environment setup and regression validation.
- `tests/samples/` – miniature documents for experimenting with pipeline behaviour.

With the T5 pipeline merged, SATCN is positioned to deliver an end-to-end alpha capable of correcting full-length books on commodity GPUs while laying the groundwork for the next phase of TTS-focused quality improvements.
