# GRMR-V3 Parameter Update Summary

## What Changed

Updated `pipeline/filters/grmr_v3_filter.py` to match official GRMR-V3-Q4B model card recommendations.

## Parameters Added

### New Parameters (Previously Missing)
```python
top_k = 40              # Top-k sampling (limits to 40 most likely tokens)
min_p = 0.01            # Minimum probability threshold
frequency_penalty = 0.0  # Made configurable (was hardcoded)
presence_penalty = 0.0   # Made configurable (was hardcoded)
```

## Default Values Changed

### Temperature: 0.1 → 0.7
**Impact:** More creative/varied corrections vs deterministic
- Old (0.1): Highly deterministic, always picks most likely token
- New (0.7): More natural variation, follows model card recommendation
- **Use case:** 0.7 for optimal quality, 0.1 for reproducibility

### Top-P: 0.15 → 0.95
**Impact:** Wider token selection pool
- Old (0.15): Very conservative, top 15% probability mass
- New (0.95): Standard setting, top 95% probability mass
- **Use case:** 0.95 balances quality and diversity

## Backward Compatibility

Users wanting previous behavior (more deterministic) can override:

```python
from pipeline.filters.grmr_v3_filter import GRMRV3GrammarFilter

# Conservative/deterministic mode (previous defaults)
filter = GRMRV3GrammarFilter(
    temperature=0.1,
    top_p=0.15
)

# Optimal mode (new defaults, matches model card)
filter = GRMRV3GrammarFilter()  # Uses temperature=0.7, top_p=0.95
```

## Model Information Corrections

### Previously Stated (INCORRECT)
- Base model: Gemma 3 4B

### Actually Correct
- Base model: **Qwen3 4B** (unsloth/Qwen3-4B-Base)
- Model name: GRMR-V3-Q4B (not G4B)
- Architecture: Qwen3 Transformer decoder
- Training: Fine-tuned on qingy2024/grmr-v4-60k

## Testing Needed

### 1. Quality Benchmark Comparison
```bash
# Test with new defaults
python benchmark_grmr_quality.py

# Save results for comparison
```

**Expected:** Similar quality but potentially more varied phrasing

### 2. Temperature Sensitivity Test
```bash
# Test temperature range
for temp in 0.1 0.3 0.5 0.7 0.9; do
    python test_grmr_v3_gpu.py --temperature $temp
done
```

**Expected:** 
- 0.1: Very consistent, deterministic
- 0.7: Optimal quality (per model card)
- 0.9: More creative but potentially less accurate

### 3. Long Document Test
```bash
# With new parameters
python test_long_document_gpu.py > output_temp0.7.txt

# With old parameters for comparison
python test_long_document_gpu.py --temperature 0.1 --top-p 0.15 > output_temp0.1.txt

# Compare outputs
diff output_temp0.7.txt output_temp0.1.txt
```

## Implementation Details

### Complete Parameter List (New Defaults)
```python
GRMRV3GrammarFilter(
    model_path=None,                    # Auto-detect
    n_ctx=4096,                         # Context window
    max_new_tokens=256,                 # Max generation length
    temperature=0.7,                    # ✨ NEW DEFAULT (was 0.1)
    top_p=0.95,                         # ✨ NEW DEFAULT (was 0.15)
    top_k=40,                           # ✨ NEW PARAMETER
    min_p=0.01,                         # ✨ NEW PARAMETER
    repeat_penalty=1.05,                # Unchanged
    frequency_penalty=0.0,              # ✨ NOW CONFIGURABLE
    presence_penalty=0.0,               # ✨ NOW CONFIGURABLE
    device=None,                        # Auto-detect GPU
    logger=None                         # Auto-create
)
```

### Generation Call (Updated)
```python
response = self.llm(
    prompt,
    max_tokens=self.max_new_tokens,
    temperature=self.temperature,          # Now 0.7
    top_p=self.top_p,                      # Now 0.95
    top_k=self.top_k,                      # ✨ NEW: 40
    min_p=self.min_p,                      # ✨ NEW: 0.01
    repeat_penalty=self.repeat_penalty,
    frequency_penalty=self.frequency_penalty,  # ✨ Configurable
    presence_penalty=self.presence_penalty,    # ✨ Configurable
    stop=["###", "\n\n\n"],
    echo=False
)
```

## Documentation Updates

### Files Updated
1. ✅ `pipeline/filters/grmr_v3_filter.py` - Implementation
2. ✅ `docs/GRMR_V3_PARAMETER_ANALYSIS.md` - Complete analysis
3. ✅ `GRMR_V3_QUALITY_REPORT.md` - Corrected base model info

### Files to Update (If Testing Shows Differences)
- [ ] `README.md` - Add note about parameter optimization
- [ ] `docs/GRMR_V3_GGUF_TEST_PLAN.md` - Update with new parameters
- [ ] `benchmark_grmr_quality.py` - Add temperature parameter option

## Risk Assessment

### Low Risk
- All parameters are configurable
- Backward compatibility maintained
- Model card officially recommends these settings
- No breaking API changes

### Medium Risk
- Output may be less deterministic (not reproducible)
- Slight variation in corrections possible
- May affect regression tests if they expect exact outputs

### Mitigation
- Test thoroughly before merging to main
- Document temperature trade-offs clearly
- Provide configuration examples for both modes
- Consider adding `--deterministic` flag to scripts

## Commit Message Template

```
feat: update GRMR-V3 parameters to match official model card

- Add missing parameters: top_k=40, min_p=0.01
- Update defaults: temperature 0.1→0.7, top_p 0.15→0.95
- Make frequency_penalty and presence_penalty configurable
- Correct base model info (Qwen3, not Gemma)
- Maintain backward compatibility via parameter overrides

Parameters now match qingy2024/GRMR-V3-Q4B recommendations.
Previous deterministic behavior available via temperature=0.1.

Refs: https://huggingface.co/qingy2024/GRMR-V3-Q4B
```

## References

- **Model Card:** https://huggingface.co/qingy2024/GRMR-V3-Q4B
- **Base Model:** unsloth/Qwen3-4B-Base
- **Training Dataset:** qingy2024/grmr-v4-60k
- **Paper:** Qwen3 Technical Report (arXiv:2505.09388)
