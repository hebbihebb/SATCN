# GPU Performance Investigation - ROOT CAUSE IDENTIFIED

## 🔴 CRITICAL FINDING: Wrong Python Environment

### The Problem

GPU testing has been using the **wrong Python environment** that doesn't have CUDA support:

```powershell
# Current environment (.venv):
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
> CUDA: False
> CUDA device count: 0
```

**Evidence from llama.cpp logs:**
```
load_tensors: layer   0 assigned to device CPU, is_swa = 0
load_tensors: layer   1 assigned to device CPU, is_swa = 0
...
load_tensors: layer  35 assigned to device CPU, is_swa = 0
```

All 36 layers were assigned to **CPU**, not GPU!

### Environment Comparison

| Environment | CUDA Support | Status |
|-------------|--------------|--------|
| `.venv` | ❌ No | Currently active, broken for GPU |
| `.venv-gpu` | ❓ No torch | Incomplete setup |
| `.venv310` | ✅ Yes | **WORKING GPU ENVIRONMENT** |

### Why GPU Appeared "Slower"

**It wasn't using the GPU at all!** The "GPU tests" were actually running on CPU with additional overhead from:
1. Unnecessary CUDA checks/initialization attempts
2. Extra model loading steps (GPU layer assignment that fell back to CPU)
3. Memory repacking operations

## Solution

### Quick Fix: Use `.venv310` for GPU Testing

```powershell
# Activate GPU-enabled environment
.\.venv310\Scripts\Activate.ps1

# Verify CUDA is available
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
# Should print: CUDA: True

# Run GPU diagnostics
python scripts/diagnose_gpu_performance.py

# Run Q4 vs Q8 GPU comparison
python scripts/compare_q4_vs_q8.py --gpu --long-doc corpus/large.md
```

### Why This Happened

1. **Multiple environments:** Project has 3 different Python environments
2. **No CUDA in default:** The main `.venv` was created without CUDA-enabled PyTorch
3. **Silent fallback:** llama-cpp-python silently falls back to CPU when CUDA unavailable
4. **Misleading logs:** No clear error message that GPU isn't being used

### Expected Results After Fix

Once running in `.venv310` with actual GPU support:

**Current "GPU" Results (Actually CPU):**
- Q4: 103.51s (9.2 words/sec)
- Q8: ~155s estimated (6 words/sec)

**Expected Real GPU Results:**
- Q4: 20-30s (30-50 words/sec) ← **3-5x faster**
- Q8: 30-45s (20-35 words/sec) ← **3-5x faster**

**Real GPU should be 3-5x faster than CPU**, not slower!

## Long-Term Fix: Consolidate Environments

### Option 1: Fix `.venv` (Recommended)

```powershell
# Activate main environment
.\.venv\Scripts\Activate.ps1

# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
```

### Option 2: Make `.venv310` Default

Update all documentation and scripts to use `.venv310`:

```powershell
# Rename current .venv
Rename-Item .venv .venv-old

# Make .venv310 the new .venv
Copy-Item -Recurse .venv310 .venv

# Or use symlink (requires admin)
New-Item -ItemType SymbolicLink -Path .venv -Target .venv310
```

### Option 3: Environment Selector Script

Create `activate_gpu.ps1`:

```powershell
# activate_gpu.ps1
Write-Host "Activating GPU environment..." -ForegroundColor Green

# Check each environment for CUDA support
$envs = @(".venv310", ".venv-gpu", ".venv")
$found = $false

foreach ($env in $envs) {
    if (Test-Path "$env\Scripts\Activate.ps1") {
        & "$env\Scripts\python.exe" -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Using $env (CUDA available)" -ForegroundColor Green
            & "$env\Scripts\Activate.ps1"
            $found = $true
            break
        }
    }
}

if (-not $found) {
    Write-Host "✗ No GPU-enabled environment found!" -ForegroundColor Red
    Write-Host "  Run: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
}
```

## Testing Checklist

- [ ] Activate `.venv310` environment
- [ ] Verify CUDA available (`torch.cuda.is_available()`)
- [ ] Run GPU diagnostics script
- [ ] Confirm llama.cpp logs show "GPU" not "CPU" for layer assignment
- [ ] Re-run Q4 vs Q8 comparison with GPU
- [ ] Verify GPU is 3-5x faster than CPU
- [ ] Update production environment to use GPU-enabled setup

## Documentation Updates Needed

1. **README.md** - Add environment setup section
2. **GPU_SETUP_GUIDE.md** - Note about multiple environments
3. **All GPU test scripts** - Add environment check at startup
4. **.vscode/settings.json** - Set default Python interpreter to `.venv310`

## Prevention: Environment Check Function

Add to all GPU scripts:

```python
def verify_gpu_environment():
    """Verify we're in a CUDA-enabled environment."""
    import torch

    if not torch.cuda.is_available():
        print("❌ ERROR: CUDA not available in this Python environment!")
        print()
        print("Current environment does not have GPU support.")
        print()
        print("Solution: Activate GPU-enabled environment:")
        print("  .\.venv310\Scripts\Activate.ps1")
        print()
        print("Or install CUDA-enabled PyTorch:")
        print("  pip install torch --index-url https://download.pytorch.org/whl/cu121")
        sys.exit(1)

    print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
    print(f"  CUDA version: {torch.version.cuda}")
    print()
```

## Summary

**Root cause:** Using Python environment without CUDA-enabled PyTorch
**Evidence:** All model layers assigned to CPU, not GPU
**Impact:** "GPU tests" were actually CPU tests with overhead
**Solution:** Use `.venv310` which has CUDA support
**Expected improvement:** 3-5x speedup over current results

---

**Next Steps:**
1. Switch to `.venv310`
2. Re-run diagnostics
3. Celebrate actual GPU performance 🎉
