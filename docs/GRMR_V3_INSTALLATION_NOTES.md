# GRMR-V3 GGUF Integration - Installation Notes

## Date: October 31, 2025

## What Was Done

Successfully integrated the GRMR-V3-Q4B.Q4_K_M.gguf grammar correction model into SATCN.

### Files Created/Modified

1. **`requirements-grmr.txt`** - Dependencies for GRMR-V3 GGUF model
   - llama-cpp-python >= 0.2.90
   - numpy >= 1.24.0
   - diskcache >= 5.6.0

2. **`pipeline/filters/grmr_v3_filter.py`** - GRMR-V3 grammar filter implementation
   - Class: `GRMRV3GrammarFilter`
   - Uses llama.cpp runtime via Python bindings
   - Context window: 4096 tokens (vs T5's 512)
   - Deterministic decoding: temp=0.1, top_p=0.15

3. **`pipeline/filters/__init__.py`** - Updated to expose GRMR-V3 filter
   - Added conditional import (gracefully handles missing llama-cpp-python)
   - Exports `GRMRV3GrammarFilter` and `GRMR_V3_AVAILABLE` flag

### Installation Status

✅ **Installed (CPU-only)**: llama-cpp-python 0.3.16
- Installed in: `.venv/` (already in .gitignore)
- Backend: CPU with AVX512 optimization
- Build time: ~2.5 minutes
- Dependencies installed automatically: numpy, diskcache, typing-extensions, jinja2, markupsafe

❌ **Not installed: GPU acceleration**
- Requires: CUDA Toolkit 13.0+ (matching system CUDA version)
- Would need: `CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python --force-reinstall`
- Current limitation: CUDA toolkit not found during build

### Model File

✅ **Present**: `.GRMR-V3-Q4B-GGUF/GRMR-V3-Q4B.Q4_K_M.gguf`
- Size: Quantized 4-bit model
- Already excluded from git via `*.gguf` pattern in `.gitignore`
- Context trained: 32,768 tokens (using 4,096 for inference)

### Integration Test Results

✅ **All tests passed** (`test_grmr_v3_integration.py`)

**Sample corrections:**
- "Thiss sentnce have two speling errrors" → "This sentence has two spelling errors"
- "The crew was suppose to arrive yesteday" → "The crew was supposed to arrive yesterday"
- "Their going too fast for the narow bridge" → "They're going too fast for the narrow bridge"
- "I has forgotten where I put the keys" → "I have forgotten where I put the keys"

**Character name preservation:** ✅ Preserved "Irina" correctly (T5 had issues with this)

### Performance Notes

**CPU mode:**
- Model loads in ~2-3 seconds
- Inference: ~5-10 seconds per block (depending on text length)
- Memory: Reasonable for 4-bit quantized model
- Warning issued about CPU being slower than GPU

**Expected with GPU:**
- Would be ~10-20x faster
- Target: ~500ms per block on RTX 4060

## Next Steps

### Immediate (Documented in test plan)

1. ✅ Install llama-cpp runtime
2. ✅ Implement GRMRV3GrammarFilter wrapper
3. ⏳ Wire into pipeline_runner.py with `--use-grmr` flag
4. ⏳ Create unit tests (tests/unit/test_grmr_v3_filter.py)
5. ⏳ Create integration tests (tests/integration/)
6. ⏳ Run benchmark comparison vs T5

### Optional (GPU Acceleration)

To enable GPU support later:

```powershell
# Install CUDA Toolkit 13.0 from NVIDIA
# https://developer.nvidia.com/cuda-downloads

# Reinstall llama-cpp-python with CUDA support
$env:CMAKE_ARGS="-DLLAMA_CUDA=on"
.venv/Scripts/python.exe -m pip uninstall llama-cpp-python
.venv/Scripts/python.exe -m pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

## Reproducing This Setup

On a fresh clone:

```powershell
# Create virtual environment (if needed)
python -m venv .venv
.venv\Scripts\activate

# Install base requirements
pip install -r requirements.txt

# Install GRMR v3 dependencies (CPU-only)
pip install -r requirements-grmr.txt

# Test the integration
python test_grmr_v3_integration.py
```

## Comparison: T5 vs GRMR-V3

| Feature | T5 (flan-t5-large) | GRMR-V3 (Q4_K_M) |
|---------|-------------------|------------------|
| Runtime | Transformers (PyTorch) | llama.cpp |
| Context window | 512 tokens | 4,096 tokens |
| Model size | ~3GB (fp16) | ~2.5GB (4-bit) |
| CPU speed | Very slow | Acceptable |
| GPU speed | ~3-4s/block (RTX 4060) | Unknown (CPU only now) |
| Character names | ❌ Changes names | ✅ Preserves names |
| Quality | C/C+ grade | Testing needed |
| Setup complexity | Simple (pip install) | Complex (needs cmake) |

## Known Issues

1. **CPU-only installation**: GPU acceleration requires CUDA toolkit
2. **Context warning**: Model trained on 32K context, using only 4K (acceptable for now)
3. **No pipeline integration yet**: Filter exists but not wired into CLI runner

## References

- Test plan: `docs/GRMR_V3_GGUF_TEST_PLAN.md`
- Integration test: `test_grmr_v3_integration.py`
- Dependencies: `requirements-grmr.txt`
- Filter implementation: `pipeline/filters/grmr_v3_filter.py`
