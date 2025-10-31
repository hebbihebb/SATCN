# T5 Model Testing Session - October 31, 2025

## Summary

Tested multiple T5 models for spelling and grammar correction. Implemented model-specific prefix support and optimized loading performance. **Result:** Keeping `pszemraj/flan-t5-large-grammar-synthesis` as default despite name-changing issues.

## Models Tested

### 1. pszemraj/flan-t5-large-grammar-synthesis (DEFAULT)
- **Grade:** C/C+
- **Results:**
  - ✅ Good grammar corrections
  - ✅ Decent speed (~3-4 sec/block on RTX 4060)
  - ❌ Changes character names (Irina → Veronica)
  - ❌ Some meaning drift
- **Verdict:** ACCEPTABLE for personal use, best option available

### 2. ai-forever/T5-large-spell
- **Grade:** D+/C-
- **Results:**
  - ✅ Made 1 good correction (axe → axes)
  - ❌ Introduced 3 new errors:
    - Changed "sighed" → "sighted" (wrong word)
    - Changed "Audra" → "Autra" (surname error)
    - Duplicated quotes unnecessarily
  - ❌ Missed actual errors (woken, reared view mirror, grammar)
  - ❌ Very conservative but inaccurate
- **Verdict:** NOT RECOMMENDED - introduces more errors than it fixes

### 3. willwade/t5-small-spoken-typo
- **Status:** Not tested
- **Reason:** Previous models showed Russian-focused or truncation issues

## Technical Improvements Made

### Performance Optimizations
1. ✅ **Removed `device_map="auto"`** - Model loads in ~4s instead of hanging/crashing
2. ✅ **Direct device placement** - `model.to(device)` much faster for single GPU
3. ✅ **Reduced `num_beams` to 2** - Faster inference, still good quality
4. ✅ **Added `repetition_penalty=1.2`** - Prevents text duplication
5. ✅ **Added `no_repeat_ngram_size=3`** - Blocks 3-gram repetitions
6. ✅ **Added `length_penalty=1.0`** - Maintains original length
7. ✅ **Using float16 on CUDA** - Halves memory usage

### Code Enhancements
1. ✅ **Model prefix support** - Automatic prefix prepending for models that require it
2. ✅ **MODEL_PREFIXES dictionary** - Centralized prefix configuration
3. ✅ **Enhanced logging** - Per-block progress, word count diffs, correction decisions
4. ✅ **Truncation warnings** - Alerts when text exceeds 512 tokens

## Test Files Used

- `tools/test_short.md` - 5 text blocks, ~100 words
- `tools/pipeline_test_text.md` - 7 text blocks, ~244 words

## Environment

- **GPU:** NVIDIA GeForce RTX 4060 Laptop GPU
- **Torch:** 2.5.1+cu121 (CUDA-enabled)
- **Transformers:** 4.57.1
- **Python:** 3.10
- **OS:** Windows 11

## Conclusions

1. **No perfect model exists** - All tested models have significant issues
2. **Grammar-synthesis is least bad** - Despite name changes, provides useful corrections
3. **Spelling-only models fail** - ai-forever model introduced more errors than fixes
4. **Performance is good** - ~3-4 seconds per block acceptable for personal use
5. **Prefix support working** - Infrastructure ready for testing more models

## Recommendations

### Immediate
- ✅ Keep `pszemraj/flan-t5-large-grammar-synthesis` as default
- ✅ Document known issues (name changes, meaning drift)
- ✅ Accept "C grade" quality for personal project

### Future Enhancements
- 🔲 Test `vennify/t5-base-grammar-correction` (correction-focused, not synthesis)
- 🔲 Implement proper noun detection/masking (protect character names)
- 🔲 Add confidence thresholds (only apply high-confidence changes)
- 🔲 Create regression test suite with known good/bad examples
- 🔲 Try hybrid approach (T5 + rule-based post-processing)

## Known Issues

1. **Name changes:** grammar-synthesis changes character names unpredictably
2. **Meaning drift:** Synthesis models may alter meaning to fix grammar
3. **Conservative vs aggressive tradeoff:** Can't find model that's "just right"
4. **Model loading time:** ~4 seconds on first load (acceptable)

## Files Modified

- `satcn/correction/t5_corrector.py` - Added prefix support, reverted to grammar-synthesis
- `docs/T5_MODEL_GUIDE.md` - Updated with test results and recommendations
- `docs/T5_TESTING_SESSION_OCT2025.md` - This document

## Outcome

**Status:** DONE ✅

The T5 integration is functional and acceptable for personal use. While not perfect, the grammar-synthesis model provides useful corrections despite occasional name changes. The codebase is now well-documented and ready for future model experiments.
