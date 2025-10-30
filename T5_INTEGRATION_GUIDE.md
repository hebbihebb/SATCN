# FLAN-T5 Grammar Correction Integration Guide

## Overview

This guide explains how to integrate the FLAN-T5 model for context-aware grammar and spelling correction into the SATCN text processing pipeline.

## What Was Added

### New Files

1. **`pipeline/filters/t5_grammar_filter.py`**
   - Complete implementation of T5-based grammar correction filter
   - Follows the existing filter interface
   - Handles model loading, text correction, and error handling

2. **`test_t5_integration.py`**
   - Standalone test script to verify T5 integration
   - Demonstrates both standalone and pipeline usage
   - Run with: `python test_t5_integration.py`

3. **`tests/unit/test_t5_grammar_filter.py`**
   - Unit tests for the T5 filter
   - Run with: `pytest tests/unit/test_t5_grammar_filter.py`

4. **`requirements-t5.txt`**
   - Additional dependencies needed for T5 integration

## Integration Approaches

### Option 1: Replace Existing Grammar Filter (Recommended for Testing)

**Use Case**: You want to test T5's performance as the primary grammar correction method.

**Modify** `pipeline/pipeline_runner.py`:

```python
# Add import at top
from .filters.t5_grammar_filter import T5GrammarFilter

# Modify _get_filters() method (around line 30):
def _get_filters(self):
    # ... existing parser code ...

    return [
        (parser_filter, False),
        (SpellingCorrectionFilter(), False),
        (T5GrammarFilter(), False),  # ← Replace grammar filter with T5
        (TTSNormalizer(), False),
        (output_generator, False)
    ]
```

**Pros**:
- Simpler pipeline
- Context-aware corrections (much better than pyspellchecker)
- Handles both spelling and grammar in one pass

**Cons**:
- Slower than rule-based (especially on CPU)
- Less predictable outputs
- Requires GPU for reasonable performance

### Option 2: Hybrid Approach

**Use Case**: Combine T5's contextual understanding with rule-based determinism.

```python
return [
    (parser_filter, False),
    (T5GrammarFilter(), False),  # ← First pass: T5 for major corrections
    (SpellingCorrectionFilter(), False),  # ← Catch remaining spelling
    (GrammarCorrectionFilterSafe(), True),  # ← Rule-based cleanup
    (TTSNormalizer(), False),
    (output_generator, False)
]
```

**Pros**:
- Best of both worlds: AI + rules
- T5 handles context, LanguageTool handles deterministic rules
- More comprehensive corrections

**Cons**:
- Longer processing time
- Potential conflicts between filters

### Option 3: Replace Spelling + Grammar with T5 Only

**Use Case**: Simplify the pipeline and rely entirely on T5.

```python
return [
    (parser_filter, False),
    (T5GrammarFilter(), False),  # ← Single filter for all corrections
    (TTSNormalizer(), False),
    (output_generator, False)
]
```

**Pros**:
- Simplest pipeline
- T5 handles spelling + grammar + context together
- Potentially more coherent corrections

**Cons**:
- Slowest option
- No deterministic fallback

## Installation

### 1. Install Dependencies

```bash
# Install T5 requirements
pip install transformers>=4.30.0 torch>=2.0.0 accelerate>=0.20.0 sentencepiece protobuf

# OR install from the requirements file
pip install -r requirements-t5.txt
```

### 2. Download the Model

On first run, the model will be automatically downloaded from Hugging Face (~3GB).

**Option A: Automatic download (recommended)**
```python
# In your code or tests
filter = T5GrammarFilter()  # Downloads automatically
```

**Option B: Pre-download manually**
```bash
python -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; \
           AutoTokenizer.from_pretrained('pszemraj/flan-t5-large-grammar-synthesis'); \
           AutoModelForSeq2SeqLM.from_pretrained('pszemraj/flan-t5-large-grammar-synthesis')"
```

**Option C: Use local model folder**

If you want to use the model from `flan-t5-large-grammar-synthesis/`:

1. Download the full model files (not just GGUF):
   ```bash
   git lfs install
   git clone https://huggingface.co/pszemraj/flan-t5-large-grammar-synthesis
   ```

2. Use local path:
   ```python
   filter = T5GrammarFilter(model_name="./flan-t5-large-grammar-synthesis")
   ```

   **Note**: Your current folder only contains GGUF files (for llama.cpp), not the full PyTorch model needed for Transformers.

## Testing

### Quick Test

```bash
# Run integration test
python test_t5_integration.py
```

This will:
1. Load the T5 model
2. Test several example sentences
3. Show corrections
4. Display integration guide

### Unit Tests

```bash
# Run T5 filter tests
pytest tests/unit/test_t5_grammar_filter.py -v

# Run all tests
pytest tests/
```

### Test with Real Documents

```bash
# Process a Markdown file
python -m pipeline.pipeline_runner test.md

# Process an EPUB file
python -m pipeline.pipeline_runner book.epub
```

## Performance Considerations

### Hardware Requirements

| Configuration | Speed per Sentence | Memory Required | Recommended For |
|--------------|-------------------|-----------------|-----------------|
| **CPU only** | 5-30 seconds | 8-16 GB RAM | Testing, small batches |
| **GPU (NVIDIA)** | 0.5-2 seconds | 6-8 GB VRAM | Production, large documents |
| **Apple M1/M2** | 2-5 seconds | 8 GB unified | Mac development |

### Optimization Tips

1. **Use GPU if available**
   ```python
   # Automatic device selection (recommended)
   filter = T5GrammarFilter()  # Auto-detects CUDA

   # Force CPU (for testing)
   filter = T5GrammarFilter(device="cpu")
   ```

2. **Batch processing**
   - The filter processes blocks sequentially
   - For large documents, consider adding batch processing to the filter

3. **Model quantization** (future improvement)
   - Use 8-bit or 4-bit quantization with `bitsandbytes`
   - Reduces memory by 50-75% with minimal quality loss

4. **Caching** (future improvement)
   - Cache model outputs for identical text blocks
   - Useful for documents with repeated text

## Configuration Options

### T5GrammarFilter Parameters

```python
T5GrammarFilter(
    model_name="pszemraj/flan-t5-large-grammar-synthesis",  # Model to use
    max_length=512,        # Max tokens per text block
    device=None           # 'cuda', 'cpu', or None for auto
)
```

### Model Alternatives

You can try other T5-based grammar models:

```python
# Smaller, faster model (if available)
filter = T5GrammarFilter(model_name="pszemraj/flan-t5-base-grammar-synthesis")

# Other grammar correction models
filter = T5GrammarFilter(model_name="vennify/t5-base-grammar-correction")
```

## Troubleshooting

### Issue: "CUDA out of memory"

**Solution**: Reduce max_length or use CPU
```python
filter = T5GrammarFilter(max_length=256)  # Smaller chunks
# OR
filter = T5GrammarFilter(device="cpu")
```

### Issue: "Model not found"

**Solution**: Check internet connection, or use local path
```bash
# Verify model exists
huggingface-cli download pszemraj/flan-t5-large-grammar-synthesis
```

### Issue: "Too slow on CPU"

**Solutions**:
1. Use GPU if available
2. Switch to smaller model (t5-base instead of t5-large)
3. Process only critical sections
4. Use hybrid approach (T5 for some blocks, rules for others)

### Issue: "Import error: transformers not found"

**Solution**: Install dependencies
```bash
pip install transformers torch accelerate
```

## Comparison: T5 vs Current Filters

| Feature | pyspellchecker | LanguageTool | T5 Grammar Filter |
|---------|---------------|--------------|-------------------|
| **Accuracy** | Low | Medium-High | High |
| **Context-aware** | ❌ No | ⚠️ Limited | ✅ Yes |
| **Speed** | Fast | Medium | Slow (CPU) / Fast (GPU) |
| **Predictable** | ✅ Yes | ✅ Yes | ⚠️ Mostly |
| **Resource usage** | Low | Medium | High |
| **Setup complexity** | Low | Medium | Medium-High |
| **Works offline** | ✅ Yes | ✅ Yes* | ✅ Yes* |

*After initial model download

## Examples

### Before and After

```python
# Input
"Thiss sentnce have many speling errrors."

# Current (pyspellchecker + LanguageTool)
"This sentence have many spelling errors."  # Still has "have" error

# With T5
"This sentence has many spelling errors."  # Fully corrected
```

```python
# Input
"The team are working on they're project over their."

# Current
"The team are working on they're project over their."  # No change

# With T5
"The team is working on their project over there."  # All fixed
```

## Next Steps

1. **Test the integration**
   ```bash
   python test_t5_integration.py
   ```

2. **Choose integration approach** (see Options above)

3. **Update `pipeline_runner.py`** with your chosen approach

4. **Update `requirements.txt`**
   ```bash
   cat requirements-t5.txt >> requirements.txt
   ```

5. **Run regression tests**
   ```bash
   pytest tests/test_regression.py
   ```

6. **Benchmark performance**
   ```bash
   python benchmark.py
   ```

7. **Update README.md** to reflect T5 integration

## Future Enhancements

- [ ] Fine-tune T5 on domain-specific text (e.g., technical writing)
- [ ] Add batch processing for better GPU utilization
- [ ] Implement output caching
- [ ] Add confidence scores to corrections
- [ ] Support for other languages
- [ ] Model quantization (8-bit/4-bit) for efficiency
- [ ] A/B testing framework to compare correction quality

## References

- Model: https://huggingface.co/pszemraj/flan-t5-large-grammar-synthesis
- Base model: https://huggingface.co/google/flan-t5-large
- Transformers docs: https://huggingface.co/docs/transformers
- Project README: See line 31 for T5 in roadmap
