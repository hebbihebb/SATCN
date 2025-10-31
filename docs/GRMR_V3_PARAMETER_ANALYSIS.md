# GRMR-V3 Model Card Parameter Analysis

## Comparison: Model Card vs Implementation

### Official Model Card Recommendations (GRMR-V3-Q4B)
From HuggingFace: `qingy2024/GRMR-V3-Q4B`

**Base Model:** unsloth/Qwen3-4B-Base (NOT Gemma)

**Required Sampler Settings:**
```python
temperature = 0.7
frequency_penalty = 0.0
presence_penalty = 0.0
min_p = 0.01
top_p = 0.95
top_k = 40
```

### Previous Implementation

**Missing Parameters:**
- ❌ `min_p` - Not implemented
- ❌ `top_k` - Not implemented

**Different Values:**
- ⚠️ `temperature = 0.1` (model card: 0.7)
- ⚠️ `top_p = 0.15` (model card: 0.95)

**Already Correct:**
- ✅ `frequency_penalty = 0.0`
- ✅ `presence_penalty = 0.0`

**Additional Parameters:**
- `repeat_penalty = 1.05` (not in model card, kept for compatibility)

---

## Updates Made

### 1. Added Missing Parameters
- ✅ Added `top_k = 40` parameter
- ✅ Added `min_p = 0.01` parameter
- ✅ Made `frequency_penalty` and `presence_penalty` configurable (defaults: 0.0)

### 2. Updated Default Values
Changed defaults to match model card recommendations:
- `temperature: 0.1 → 0.7`
- `top_p: 0.15 → 0.95`

**Note:** These changes make the model more creative/varied in corrections.
For deterministic/conservative corrections, users can override with `temperature=0.1`.

### 3. Enhanced Documentation
- Added note about official model card parameters
- Documented when to use lower temperature (0.1 for determinism)
- Clarified parameter purposes

---

## Parameter Explanations

### Temperature (0.7)
- Controls randomness in token selection
- Higher = more creative/varied corrections
- Lower = more deterministic/conservative
- Model card recommends 0.7 for optimal quality

### Top-P / Nucleus Sampling (0.95)
- Considers tokens with cumulative probability up to P
- 0.95 = consider top 95% probability mass
- Balances quality and diversity

### Top-K (40)
- Limits sampling to top K most likely tokens
- Prevents extremely unlikely token selection
- Works with top-p for better results

### Min-P (0.01)
- Minimum probability threshold for token selection
- Tokens below this probability are excluded
- Helps filter out very unlikely options

### Frequency/Presence Penalty (0.0)
- Controls repetition in generated text
- 0.0 = no penalty (recommended for grammar correction)
- Higher values discourage repetition

---

## Chat Template Note

The model card specifies a **custom chat template** for the original Qwen3 transformers model:

**Official Template (Transformers):**
```jinja2
{%- for message in messages %}
{%- if message.role == "user" %}
{{- '<|text_start|>\n' + message.content + '<|text_end|>\n' }}
{%- elif message.role == "assistant" %}
{{- '<|corrected_start|>\n' + message.content + '<|corrected_end|>\n' }}
{%- endif %}
{%- endfor %}
{%- if add_generation_prompt %}
{{- '<|corrected_start|>\n' }}
{%- endif %}
```

**Example formatted input:**
```
<|text_start|>
i dont know weather to bring a umbrella today
<|text_end|>
<|corrected_start|>
```

**Current Implementation (GGUF):**
We use a simpler prompt template for the GGUF quantized version:
```
### Instruction
You are a copy editor. Fix grammar...

### Input
{text}

### Response
```

**Why the difference?**
- GGUF models are converted from the original transformers format
- The conversion process may not preserve custom chat templates
- Our template uses common instruction-following format (Alpaca-style)
- Has been extensively validated and works reliably

**Validation Results:**
- ✅ 100% test accuracy (31/31 tests)
- ✅ Grade A quality (95/100)
- ✅ Real-world validation (15,927 words)
- ✅ Character name preservation (100%)
- ✅ GPU performance validated (1,587 wpm)

**Recommendation:** Keep current prompt template. The GGUF conversion works differently than the original transformers model, and our template has been proven effective. If quality issues arise, we can test the custom template format.

---

## Backward Compatibility

Users can maintain previous behavior (more deterministic) by explicitly setting:
```python
filter = GRMRV3GrammarFilter(
    temperature=0.1,    # More deterministic
    top_p=0.15,         # More conservative
    # Other params use new defaults
)
```

---

## Testing Recommendations

### 1. Quick Comparison Test
Run quality benchmark with both parameter sets:
```bash
# Test with new defaults (temperature=0.7)
python benchmark_grmr_quality.py

# Test with old defaults (temperature=0.1)
python benchmark_grmr_quality.py --temperature 0.1 --top-p 0.15
```

### 2. Long Document Test
Compare output quality on real documents:
```bash
# New parameters
python test_long_document_gpu.py

# Save outputs and manually review differences
```

### 3. Expected Differences
With `temperature=0.7`:
- More varied corrections (less repetitive phrasing)
- Potentially more natural language
- Slightly less deterministic (same input may vary slightly)

With `temperature=0.1`:
- Highly deterministic (reproducible)
- More conservative corrections
- May be slightly more repetitive

---

## References

**Model Card:** https://huggingface.co/qingy2024/GRMR-V3-Q4B

**Key Quote from Model Card:**
> "IMPORTANT: Please ensure you are using the following sampler settings for optimal results:
> temperature = 0.7, frequency_penalty = 0.0, presence_penalty = 0.0,
> min_p = 0.01, top_p = 0.95, top_k = 40"

**Original Training:**
- Base model: unsloth/Qwen3-4B-Base
- Fine-tuned from: Qwen3 4B (4 billion parameters)
- Dataset: qingy2024/grmr-v4-60k (60,000 examples)
- Max sequence length: 16,384 tokens
- Training precision: Mixed precision (BF16/FP16)
- Architecture: Qwen3 (Transformer decoder)

---

## Implementation Status

✅ **All model card parameters now implemented**
✅ **Defaults updated to match recommendations**
✅ **Backward compatibility maintained via parameter overrides**
✅ **Documentation updated**

**Next Steps:**
1. Test with new parameters on quality benchmark
2. Compare output quality with temperature=0.7 vs 0.1
3. Update quality report if significant differences observed
4. Consider adding parameter presets (e.g., "conservative", "optimal", "creative")
