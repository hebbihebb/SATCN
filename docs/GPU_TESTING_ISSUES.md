# GPU Testing Issues and Solutions

## The Problem

**Issue:** GPU tests keep getting interrupted mid-execution, causing test failures and data loss.

**Root Causes:**
1. **Long execution times** - GPU tests take 5-10 minutes, easy to accidentally interrupt
2. **No progress feedback** - Tests appear frozen, tempting users to interrupt
3. **No intermediate saves** - Interruption loses all test data
4. **Silent failures** - KeyboardInterrupt exceptions not handled gracefully

## Why It Keeps Repeating

The pattern occurs because:
1. User starts GPU test
2. Test takes several minutes with minimal feedback
3. User thinks it's frozen/stuck
4. User presses Ctrl+C to interrupt
5. All progress is lost, must restart from beginning

This creates a frustrating cycle where you never complete a full GPU run.

## Solutions Implemented

### 1. Better Progress Reporting
```python
# Before: Silent processing
output_text = filter_instance.correct_text(input_text)

# After: Real-time feedback
print(f"  Testing: {test_case['name']}", end=" ", flush=True)
output_text = filter_instance.correct_text(input_text)
print(f"✓ PASS ({processing_time*1000:.0f}ms)")
```

### 2. Graceful Interrupt Handling
```python
try:
    output_text = filter_instance.correct_text(input_text)
except KeyboardInterrupt:
    print("\n⚠️  Test interrupted by user")
    raise  # Re-raise to allow cleanup
except Exception as e:
    print(f"\n    ✗ ERROR: {e}")
    # Return partial results instead of crashing
```

### 3. Output Logging
```bash
# Capture all output to file so we can review even if interrupted
python scripts/compare_q4_vs_q8.py --gpu 2>&1 | Tee-Object -FilePath "results/gpu_test_output.txt"
```

## Temperature Settings: Q4 vs Q8

### Model Card Recommendations

**From HuggingFace (qingy2024/GRMR-V3-Q4B):**
- **temperature = 0.7** (NOT 0.1)
- top_p = 0.95 (NOT 0.15)
- top_k = 40
- min_p = 0.01

**Current Implementation:**
- temperature = 0.1 (for determinism in testing)
- top_p = 0.15

### Does Q8 Need Different Settings?

**Answer:** Probably not quantization-specific, but worth testing.

**Theory:**
- Q8 has higher precision than Q4
- Might handle higher temperature (0.7) better
- Could produce more natural corrections at 0.7

**Testing Plan:**
1. Run Q4 at temperature=0.1 (current default)
2. Run Q8 at temperature=0.1 (same conditions)
3. Run Q8 at temperature=0.7 (model card recommended)
4. Compare all three for quality and naturalness

## How to Complete GPU Test Successfully

### Option 1: Let It Run Uninterrupted (Recommended)
```bash
# Start test and walk away for 10-15 minutes
python scripts/compare_q4_vs_q8.py --gpu --long-doc corpus/large.md

# Or run in background with output logging
Start-Job -ScriptBlock {
    python scripts/compare_q4_vs_q8.py --gpu --long-doc corpus/large.md
} | Wait-Job | Receive-Job
```

### Option 2: Run Without Long Document Test
```bash
# Faster test (2-3 minutes instead of 10-15)
python scripts/compare_q4_vs_q8.py --gpu
# Then run long doc separately if needed
```

### Option 3: Use Automated Script
```bash
# Runs both CPU and GPU, handles interruptions better
python scripts/run_full_model_comparison.py
```

## Typical GPU Test Timeline

**Q4 Model (2.33GB):**
- Load: ~5-7 seconds
- 16 quality tests: ~1-2 seconds each = ~30 seconds total
- Consistency test: ~3-5 seconds
- Long document: ~1-2 minutes (51 paragraphs)
- **Total: ~2-3 minutes**

**Q8 Model (3.99GB):**
- Load: ~5-7 seconds
- 16 quality tests: ~1.5-2.5 seconds each = ~40 seconds total
- Consistency test: ~3-5 seconds
- Long document: ~2-3 minutes (51 paragraphs)
- **Total: ~3-4 minutes**

**Complete Test: ~6-8 minutes**

## Expected GPU vs CPU Performance

### CPU Results (Actual):
- Q4: 66.62s for 952 words = 14 words/sec
- Q8: 100.20s for 952 words = 10 words/sec

### GPU Results (Expected):
- Q4: ~18-25s for 952 words = **40-50 words/sec** (3-4x speedup)
- Q8: ~30-40s for 952 words = **25-30 words/sec** (2.5-3x speedup)

If GPU results match expectations:
- Q8 on GPU (30s) faster than Q4 on CPU (66s)
- Makes Q8's better quality (93.8% vs 87.5%) more attractive
- **Recommendation:** Switch to Q8 with GPU acceleration

## Next Steps

1. ✅ **Wait for current GPU test to complete** (DO NOT INTERRUPT)
2. Review GPU results vs CPU results
3. Test Q8 with temperature=0.7 for quality comparison
4. Make final decision: Q4 vs Q8 for production
5. Update pipeline defaults based on findings

## Pro Tip: Monitoring Progress

While GPU test runs, open another terminal:
```bash
# Watch results file grow
Get-Content results/gpu_test_output.txt -Wait

# Or check if process is still running
Get-Process python
```

This confirms the test is progressing without interrupting it!
