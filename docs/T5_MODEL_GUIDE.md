# T5 Model Configuration Guide

## Current Settings (Optimized for Personal Use)

### Generation Parameters
- `num_beams=2` - Faster, less creative (was 4)
- `do_sample=False` - Deterministic output
- `length_penalty=1.0` - Maintain original length
- `repetition_penalty=1.2` - Prevent duplications
- `no_repeat_ngram_size=3` - Block 3-gram repetitions

These parameters prioritize speed and consistency over creative rewriting.

## Available Models

### Current Default
```python
DEFAULT_MODEL = "pszemraj/flan-t5-large-grammar-synthesis"
```
- **Size:** 783M parameters
- **Purpose:** Grammar synthesis (REWRITING focused)
- **Pros:** Strong grammar corrections
- **Cons:** Tends to hallucinate names and over-correct
- **Best for:** Documents where creative rephrasing is acceptable

### Alternative Models

#### 1. Grammar Correction (Recommended Alternative)
```python
model_name = "vennify/t5-base-grammar-correction"
```
- **Size:** ~220M parameters (smaller, faster)
- **Purpose:** Grammar CORRECTION only
- **Pros:** Less aggressive, more conservative edits
- **Cons:** May miss some corrections
- **Best for:** Fiction, dialogue, preserving author voice

#### 2. Base Grammar Synthesis
```python
model_name = "pszemraj/flan-t5-base-grammar-synthesis"
```
- **Size:** ~220M parameters
- **Purpose:** Similar to default but smaller
- **Pros:** Faster than large model
- **Cons:** Same hallucination issues as large
- **Best for:** Testing, faster processing

#### 3. Spelling Focused (NOT RECOMMENDED)
```python
model_name = "ai-forever/T5-large-spell"
```
- **Size:** 738M parameters
- **Purpose:** Spelling correction (Russian-focused)
- **Requires prefix:** `"grammar: "` (automatically added by corrector)
- **Test Results:** Grade D+/C-
  - Made 1 good correction (axe → axes)
  - Introduced 3 new errors (sighed → sighted, Audra → Autra, duplicated quotes)
  - Missed several actual errors (woken, reared view mirror, grammar issues)
  - Very conservative (exact word count preservation)
- **Cons:** Introduces more errors than it fixes for English text
- **NOT RECOMMENDED** - Use grammar-synthesis or correction models instead

## How to Switch Models

### Option 1: Modify the code
Edit `satcn/correction/t5_corrector.py`:
```python
DEFAULT_MODEL = "vennify/t5-base-grammar-correction"  # Change this line
```

### Option 2: Pass model at initialization
If using programmatically:
```python
from satcn.correction import T5Corrector

corrector = T5Corrector(model_name="vennify/t5-base-grammar-correction")
```

### Option 3: Environment variable (future enhancement)
Could add support for:
```bash
export SATCN_T5_MODEL="vennify/t5-base-grammar-correction"
```

## Model Testing Results (October 2025)

### pszemraj/flan-t5-large-grammar-synthesis (DEFAULT)
- **Grade:** C/C+ 
- **Changes names:** Yes (Irina → Veronica, etc.)
- **Preserves meaning:** Mostly (some drift)
- **Grammar fixes:** Good
- **Speed:** ~3-4 seconds per block on RTX 4060
- **Verdict:** Acceptable for personal use, needs name protection

### ai-forever/T5-large-spell
- **Grade:** D+/C-
- **Changes names:** Yes (Audra → Autra)
- **Introduces errors:** Yes (sighed → sighted)
- **Duplicates text:** Yes (quotes repeated)
- **Speed:** ~3-4 seconds per block on RTX 4060
- **Verdict:** NOT RECOMMENDED - introduces more errors than fixes

### willwade/t5-small-spoken-typo
- **Status:** Not yet tested
- **Purpose:** Spoken language typo correction

## Troubleshooting

### Model is changing character names
- **Problem:** Synthesis model is too creative
- **Solution:** Switch to `vennify/t5-base-grammar-correction`
- **OR:** Increase `num_beams` back to 4 (slower but more conservative)
- **OR:** Implement proper noun detection/masking (future enhancement)

### Model is too slow
- **Problem:** Large model on GPU
- **Solution:** Switch to base model or reduce `num_beams` to 1
- **Note:** Model loading takes ~4 seconds with direct device placement

### Model output has duplications
- **Problem:** Repetition penalty too low
- **Solution:** Increase `repetition_penalty` from 1.2 to 1.5
- **Note:** `no_repeat_ngram_size=3` helps prevent this

### Model changes meaning of sentences
- **Problem:** Model trained for synthesis not correction
- **Solution:** Switch to correction-focused model
- **OR:** Use hybrid mode with rule-based cleanup

### Model introduces new errors
- **Problem:** Model not well-suited for English or wrong task
- **Solution:** Stick with grammar-synthesis models, avoid spelling-only models
- **Tested:** ai-forever/T5-large-spell introduces more errors than it fixes

## Testing New Models

Always test new models with your content:
```bash
python -m pipeline.pipeline_runner your_test_file.md --use-t5 --t5-mode replace
```

Compare output carefully for:
1. Name preservation
2. Meaning preservation  
3. Grammar improvements
4. Spelling improvements
5. Processing speed

## Performance Optimizations Done

1. ✅ **Removed device_map="auto"** - Model loads in ~4s instead of hanging
2. ✅ **Reduced num_beams to 2** - Faster inference, still good quality
3. ✅ **Added repetition_penalty=1.2** - Prevents text duplication
4. ✅ **Added no_repeat_ngram_size=3** - Blocks 3-gram repetitions
5. ✅ **Added length_penalty=1.0** - Maintains original length
6. ✅ **Using float16 on CUDA** - Halves memory usage
7. ✅ **Model prefix support** - Automatic prefix for models that require it

## Recommended Next Steps

1. **Try the correction-focused model** - Less hallucination (vennify/t5-base-grammar-correction)
2. **Create a test suite** - Standardized test cases with known inputs/outputs
3. **Add proper noun protection** - Detect and mask character names before T5 processing
4. **Implement confidence thresholds** - Only apply high-confidence changes
5. **Test willwade/t5-small-spoken-typo** - May be better for dialogue-heavy fiction

## Known Issues

1. **Name changes:** grammar-synthesis model changes character names (Irina → Veronica)
2. **Model loading:** Takes ~4 seconds on first load (cached after that)
3. **Conservative corrections:** Models with exact word count preservation may miss errors
4. **Aggressive corrections:** Synthesis models may change meaning to fix grammar
