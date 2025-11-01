# GPU Performance Investigation Plan

## Problem Statement

GPU inference is **1.55x slower** than CPU for GRMR-V3 models:
- **Q4 CPU:** 66.62s (14 words/sec)
- **Q4 GPU:** 103.51s (9.2 words/sec) ❌

This is unexpected for an RTX 2070 with 8GB VRAM. The model (2.33GB Q4, 3.99GB Q8) easily fits in VRAM.

## Root Cause Hypothesis

Based on llama.cpp community research, GPU slowdowns are typically caused by:

1. **Suboptimal CUDA kernel selection** (MMQ vs cuBLAS)
2. **Small batch sizes** (GPU needs fat matmuls to shine)
3. **KV cache not on GPU** (spillover to system RAM)
4. **Single-paragraph processing** (context switching overhead)
5. **Wrong backend configuration** (CPU fallback not detected)

**Not the issue:** VRAM capacity (4GB model fits in 8GB VRAM)

## Investigation Strategy

### Phase 1: Systematic Configuration Testing

Test 8 different llama.cpp configurations to identify optimal settings:

| Config | Kernel | Batch | Ubatch | Context | KV Cache | Purpose |
|--------|--------|-------|--------|---------|----------|---------|
| 1 | Auto | 512 | 512 | 4096 | f16 | Baseline (current) |
| 2 | cuBLAS | 512 | 512 | 4096 | f16 | Force FP16 GEMM |
| 3 | MMQ | 512 | 512 | 4096 | f16 | Force int8 Tensor Core |
| 4 | Auto | 1024 | 256 | 4096 | f16 | Larger batch |
| 5 | Auto | 512 | 512 | 4096 | q8_0 | Quantized KV |
| 6 | cuBLAS | 1024 | 256 | 4096 | q8_0 | cuBLAS + batch + KV |
| 7 | MMQ | 1024 | 256 | 4096 | q8_0 | MMQ + batch + KV |
| 8 | cuBLAS | 2048 | 512 | 4096 | q8_0 | Extreme batch |

**Script:** `scripts/diagnose_gpu_performance.py`

**Estimated time:** 5-10 minutes (3 test sentences × 8 configs)

### Phase 2: Kernel Selection Deep Dive

#### MMQ (Mixed Matrix Quantization)
- **What:** int8 Tensor Core kernels for quantized models
- **Pros:** Optimized for Q4/Q8 models, faster on newer GPUs
- **Cons:** May underperform on older cards (RTX 20-series)
- **Activate:** `GGML_CUDA_FORCE_MMQ=1`

#### cuBLAS (CUDA BLAS)
- **What:** FP16 GEMM (matrix multiply) kernels
- **Pros:** Reliable on all NVIDIA GPUs, stable performance
- **Cons:** Doesn't leverage quantization, higher VRAM usage
- **Activate:** `GGML_CUDA_FORCE_CUBLAS=1`

**Expectation:** RTX 2070 (no Tensor Cores) may prefer cuBLAS

### Phase 3: Batch Size Optimization

**Current issue:** Processing one paragraph at a time (50-150 tokens)
- Small batches = **GPU starvation** (Tensor Cores idle between kernels)
- Large batches = **Better utilization** (amortize kernel launch overhead)

**llama.cpp parameters:**
- `n_batch`: Prompt processing batch size (how many tokens processed at once)
- `n_ubatch`: Physical batch size (actual GPU batch, must be ≤ n_batch)
- `n_ctx`: Total context window (4096 for GRMR-V3)

**Test progression:**
1. Default: 512 batch / 512 ubatch
2. Larger: 1024 batch / 256 ubatch
3. Extreme: 2048 batch / 512 ubatch

**Goal:** Find sweet spot before OOM (8GB VRAM limit)

### Phase 4: KV Cache Quantization

**Current:** KV cache in FP16 (default, ~2GB for 4096 context)
**Alternative:** KV cache in q8_0 (quantized, ~1GB)

**Benefits:**
- Halves KV memory usage
- More headroom for larger batches
- Keeps KV cache on-GPU

**Trade-off:**
- Slight quality degradation (usually negligible)
- Some GPU architectures have slower q8_0 attention kernels

**Test:** Compare f16 vs q8_0 KV cache with same batch size

### Phase 5: Architectural Analysis

If all optimizations fail, investigate:

1. **PCIe bottleneck:**
   - RTX 2070 on PCIe 3.0 x16 → ~16 GB/s bandwidth
   - Small model transfers may saturate bus
   - **Solution:** Batch multiple paragraphs

2. **Context switching overhead:**
   - Current: One model call per paragraph (51× for long doc)
   - Each call: KV cache reset, context setup, GPU kernel launch
   - **Solution:** Process multiple paragraphs in one call

3. **CPU/GPU synchronization:**
   - llama.cpp may be doing unnecessary CPU↔GPU syncs
   - **Solution:** Profile with `nvprof` or `nsys`

## Expected Outcomes

### Best Case
- Find optimal kernel + batch size → **2-3x GPU speedup over CPU**
- Example: cuBLAS + 1024 batch + q8_0 KV → 30-40 words/sec

### Realistic Case
- GPU matches or slightly exceeds CPU speed (~15 words/sec)
- Identify which config works best for RTX 2070

### Worst Case
- GPU remains slower than CPU for this workload
- **Reason:** Single-paragraph processing doesn't benefit from parallelization
- **Solution:** Batch process multiple paragraphs (architecture change)

## Implementation Plan

### Step 1: Run Diagnostics (Now)
```powershell
python scripts/diagnose_gpu_performance.py
```
**Output:** `results/gpu_diagnostics_{timestamp}.json`

### Step 2: Analyze Results
- Identify fastest configuration
- Compare tokens/sec across all configs
- Note any errors or OOM failures

### Step 3: Update GRMRV3GrammarFilter
Apply optimal parameters to `src/satcn/core/filters/grmr_v3_filter.py`:

```python
self.llm = Llama(
    model_path=str(self.model_path),
    n_ctx=4096,
    n_batch=1024,        # ← Updated
    n_ubatch=256,        # ← Updated
    n_gpu_layers=-1,
    type_k=8,            # ← q8_0 KV cache (if faster)
    type_v=8,
    use_mlock=True,
    use_mmap=True,
    verbose=False,
)
```

Set environment variable before launch:
```powershell
$env:GGML_CUDA_FORCE_CUBLAS = "1"  # Or FORCE_MMQ
```

### Step 4: Re-run Q4 vs Q8 Comparison
```powershell
python scripts/compare_q4_vs_q8.py --gpu --long-doc corpus/large.md
```

**Goal:** GPU speed now exceeds or matches CPU

### Step 5: Architecture Optimization (If Needed)
If GPU still slower, implement batched paragraph processing:

```python
# Instead of: for paragraph in paragraphs: model(paragraph)
# Do: batched_results = model(paragraphs_batch)
```

## Reference Links

1. **llama.cpp PR #8075:** MMQ vs cuBLAS discussion
   - https://github.com/ggerganov/llama.cpp/pull/8075

2. **Issue #3479:** Batched decoding performance
   - https://github.com/ggerganov/llama.cpp/issues/3479

3. **NVIDIA Blog:** CUDA Graphs optimization
   - https://developer.nvidia.com/blog/optimizing-llama-cpp-ai-inference-with-cuda-graphs/

4. **llama-cpp-python CUDA guide:**
   - https://github.com/abetlen/llama-cpp-python/discussions/871

5. **llama-server manpage:** Complete parameter reference
   - https://manpages.debian.org/unstable/llama.cpp-tools/llama-server.1.en.html

## Key Takeaways

1. **VRAM is not the issue** – 4GB model fits in 8GB VRAM
2. **Kernel selection matters** – MMQ may not be optimal for RTX 2070
3. **Batch size is critical** – Small batches starve GPU
4. **KV cache placement** – Must stay on-GPU for speed
5. **Architecture may need changes** – Single-paragraph processing doesn't parallelize well

## Success Criteria

- [ ] GPU speed ≥ CPU speed (14 words/sec baseline)
- [ ] Identify optimal kernel (cuBLAS or MMQ)
- [ ] Determine best batch size without OOM
- [ ] Confirm all layers + KV cache on GPU
- [ ] Document optimal settings for production

---

**Status:** Investigation in progress
**Next:** Run `diagnose_gpu_performance.py` and analyze results
