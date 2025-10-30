# GPU Not Detected - Quick Fix Guide

## Problem

You're seeing this in the log:
```
CUDA not available, using CPU (this will be slow)
```

But you have a **GTX 2070 (8GB VRAM)** that should work perfectly!

## Why This Happens

When you run:
```bash
pip install torch
```

...it installs the **CPU-only version** by default. PyTorch requires a special installation command to enable GPU support.

## Impact

**Without GPU (current state)**:
- ❌ 5-30 seconds per sentence
- ❌ 100% CPU usage
- ❌ Very slow for large documents

**With GPU (after fix)**:
- ✅ 0.5-2 seconds per sentence (**10-50x faster!**)
- ✅ GPU accelerated
- ✅ Fast enough for production use

Your GTX 2070 has 8GB VRAM which is perfect for this model (needs ~6-8GB).

## Quick Fix (Automated)

```bash
# 1. Diagnose the issue
python check_cuda.py

# 2. Fix it (installs GPU-enabled PyTorch)
./fix_cuda.sh

# 3. Test it works
python test_t5_integration.py
```

The `fix_cuda.sh` script will:
1. Detect your CUDA version from `nvidia-smi`
2. Uninstall CPU-only PyTorch
3. Install GPU-enabled PyTorch (~2-3 GB download)
4. Verify CUDA is working

## Manual Fix

If you prefer to do it manually:

```bash
# Check your GPU and CUDA version
nvidia-smi

# Uninstall CPU-only PyTorch
pip uninstall torch torchvision torchaudio

# Install with CUDA support (choose based on your CUDA version)
# For CUDA 11.8:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1+:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify it works
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

## After the Fix

Once CUDA is detected, the log will show:
```
Using CUDA for T5 inference
✓ Model loaded successfully!
```

And the model will run **10-50x faster** on your GPU!

## Files Added

Three new diagnostic/fix tools:
- `check_cuda.py` - Diagnose CUDA detection issues
- `fix_cuda.sh` - Automated fix script
- `CUDA_FIX_README.md` - This guide

## Note About the Download

You mentioned the model is still downloading:
```
model.safetensors:  15%|█▏      | 472M/3.13G
```

This is the model weights (3.13 GB), separate from PyTorch. Let that finish downloading, then run the CUDA fix, and you'll be all set!

## Expected Final Behavior

After both downloads complete and CUDA is fixed:

```bash
$ python test_t5_integration.py

1. Loading T5 model...
Using CUDA for T5 inference  # ✅ GPU detected
✓ Model loaded successfully!

2. Testing grammar/spelling corrections:

Test 1:
  Original:  Thiss sentnce have many speling errrors.
  Corrected: This sentence has many spelling errors.  # ✅ Fast (0.5-2s)
```

## Questions?

See the full troubleshooting guide in `T5_INTEGRATION_GUIDE.md` (line 247+).
