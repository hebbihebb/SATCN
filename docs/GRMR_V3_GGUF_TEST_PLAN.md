# GRMR-V3 Q4B GGUF Integration & Test Plan

## Purpose

Follow up on the October 2025 T5 evaluation by outlining how to integrate and
validate the **GRMR-V3-Q4B.Q4_K_M.gguf** local model inside SATCN. The goal is to
replicate the successful parts of the T5 experiment (clean architecture hooks,
repeatable tests, rich logging) while accounting for the llama.cpp runtime that
GGUF models require.

## Model Assets

| Item | Notes |
| --- | --- |
| Model file | `.GRMR-V3-Q4B-GGUF/GRMR-V3-Q4B.Q4_K_M.gguf` (quantized 4-bit) |
| Runtime | [`llama-cpp-python`](https://github.com/abetlen/llama-cpp-python) bindings or native `llama.cpp` binary |
| Context window | Plan around **4096 tokens** (confirm once model loads) |
| Suggested precision | Keep Q4_K_M as-is; upgrading to Q5/Q6 later for quality comparison |
| License | Confirm redistribution constraints before bundling |

Store the model directory at the repository root (next to `flan-t5-large-grammar-synthesis/`).

## Implementation Overview

1. **Add runtime dependencies**
   - Create a new optional requirements file (e.g. `requirements-grmr.txt`) listing:
     - `llama-cpp-python>=0.2.90`
     - `numpy>=1.24`
     - `diskcache` (optional prompt caching)
   - Document GPU build flags (e.g. `CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python`).

2. **Wrap the GGUF model in a filter class**
   - Add `pipeline/filters/grmr_v3_filter.py`.
   - Mirror the public API of `pipeline.filters.t5_grammar_filter.T5GrammarFilter`:
     - `__init__(model_path, device, max_new_tokens, temperature, top_p, repeat_penalty, logger)`
     - `correct_text(text: str) -> str`
     - `process(data: dict) -> dict`
   - Use `llama_cpp.Llama` for inference. Suggested configuration:

     ```python
     from llama_cpp import Llama

     class GRMRV3GrammarFilter:
         DEFAULT_MODEL_PATH = Path('.GRMR-V3-Q4B-GGUF/GRMR-V3-Q4B.Q4_K_M.gguf')

         def __init__(self, model_path=None, n_ctx=4096, max_new_tokens=256, temperature=0.1,
                      top_p=0.15, repeat_penalty=1.05, device=None, logger=None):
             ...
             self.llm = Llama(
                 model_path=str(Path(model_path or self.DEFAULT_MODEL_PATH)),
                 n_ctx=n_ctx,
                 n_gpu_layers=-1 if device == 'cuda' else 0,
                 use_mlock=True,
                 use_mmap=True,
             )
     ```

   - Prompt template (revise after sampling outputs):

     ```text
     ### Instruction
     You are a copy editor. Fix grammar, spelling, and punctuation while keeping
     character names, slang, and factual content unchanged. Respond with the
     corrected text only.

     ### Input
     {text}

     ### Response
     ```

   - Enforce deterministic decoding for repeatability: `temperature=0.1`, `top_p=0.15`, `frequency_penalty=0.0`, `presence_penalty=0.0`.
   - Track stats similar to `T5CorrectionFilter` (tokens generated, latency, edits made).

3. **Pipeline wiring**
   - Add a feature flag to `pipeline/pipeline_runner.py`:
     - CLI option `--use-grmr` with modes (`replace`, `hybrid`, `supplement`), parallel to the T5 flags.
     - Instantiate `GRMRV3GrammarFilter` when the flag is active.
   - Expose the filter at the correction layer (e.g. in `satcn/correction/__init__.py`).
   - Provide configuration knobs (model path, device) via environment variables or CLI arguments.

4. **Logging and observability**
   - Use per-block logging identical to `T5CorrectionFilter` statistics (`duration_ms`, `changes`).
   - Emit warnings when:
     - Context length would exceed `n_ctx` (truncate input with notice).
     - Model path is missing.
     - llama.cpp falls back to CPU.
   - Optional: write generated tokens to `.cache/grmr_v3/` for debugging.

5. **Documentation updates**
   - Add a new section to `docs/T5_MODEL_GUIDE.md` summarizing the GGUF experiment.
   - Create a quick-start doc describing how to build llama-cpp with GPU acceleration (Windows + Linux instructions).
   - Update `README.md` with a short blurb and link to this plan.

## Test Plan

### Test Environment Matrix

| Environment | Notes |
| --- | --- |
| **CUDA GPU** (preferred) | Verify `n_gpu_layers=-1` and ~2–3s per block latency |
| **CPU only** | Expect ~20–40s per block; ensure graceful warnings |
| **Apple Silicon (MPS)** | llama.cpp supports Metal; verify `GGML_METAL_PATH` instructions |

### Automated Tests (PyTest)

| Test ID | Type | Description |
| --- | --- | --- |
| `UT-GRMR-INIT` | Unit | Ensure `GRMRV3GrammarFilter` loads when model file exists; skip if llama-cpp unavailable |
| `UT-GRMR-PROMPT` | Unit | Validate prompt builder preserves placeholders, forbids empty responses |
| `UT-GRMR-CORRECT` | Unit | Feed a short faulty sentence, assert deterministic correction (baseline string stored in fixture) |
| `UT-GRMR-PROCESS` | Unit | Mirror `tests/unit/test_t5_grammar_filter.py::test_process_pipeline_data` |
| `UT-GRMR-DEVICE` | Unit | Force CPU/GPU selection, ensure config passed to llama.cpp |
| `IT-GRMR-PIPELINE` | Integration | Run through `pipeline.runner` with `--use-grmr replace` on `tools/test_short.md` |
| `IT-GRMR-HYBRID` | Integration | Run `--use-grmr hybrid` and assert both GGUF + rule-based filters fire |
| `IT-GRMR-REGRESSION` | Regression | Diff corrected output for `tools/pipeline_test_text.md` against approved snapshot |
| `PERF-GRMR-LATENCY` | Benchmark | Use `pytest-benchmark` to log time per block (compare to T5 results) |

### Manual / Exploratory Tests

1. **Smoke Script (`test_grmr_v3_integration.py`)**
   - Mirrors `test_t5_integration.py`.
   - Steps:
     1. Verify that `GRMRV3GrammarFilter` can import.
     2. Run standalone corrections over 5 canned sentences.
     3. Run pipeline-style data to confirm block-level edits.
     4. Print integration guide (installation commands, CLI usage).

2. **Character-name preservation**
   - Use `tests/samples/sample_story.md`; ensure protagonist names remain unchanged.
   - Compare with T5 output to determine regressions.

3. **Edge-case prompts**
   - Very short text (`"ok"`), markdown lists, dialogue-heavy passages.
   - Confirm model doesn't hallucinate formatting or add explanations.

4. **Long context stress test**
   - Feed `tools/pipeline_test_text.md` concatenated twice (~500+ tokens).
   - Verify truncation warnings and stability.

### Acceptance Criteria

- Model initializes in < 15 seconds on GPU, < 60 seconds on CPU.
- Average latency ≤ 5 seconds per 200-token block on GPU (benchmark target).
- Corrections do not change more than 5% of tokens when input already clean.
- Proper nouns identical between input and output for regression corpus (diff via `difflib`).
- Zero critical exceptions across automated suite.

## Risk & Mitigations

| Risk | Mitigation |
| --- | --- |
| llama-cpp build complexity | Provide pre-built wheel instructions; include CPU-only fallback |
| Determinism of sampling | Use low temperature & greedy decoding; add integration snapshot tests |
| Memory pressure on low-end GPUs | Allow `n_gpu_layers` override and CPU fallback with warning |
| Model quality unknown | Keep T5 as default, guard behind `--use-grmr` flag until validated |

## Next Steps Checklist

1. [ ] Install llama-cpp runtime and validate `llama_cpp` import.
2. [ ] Implement `GRMRV3GrammarFilter` wrapper (see Implementation Overview).
3. [ ] Add automated tests outlined above (unit + integration + regression).
4. [ ] Fill out `test_grmr_v3_integration.py` expected outputs once model tuned.
5. [ ] Run benchmark suite; compare against `docs/T5_TESTING_SESSION_OCT2025.md` metrics.
6. [ ] Update documentation and announce experimental availability.

Once these steps pass, schedule a follow-up evaluation session mirroring the
structure used for the October 2025 T5 trial.
