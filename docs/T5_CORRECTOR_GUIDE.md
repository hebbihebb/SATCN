# T5 Corrector Integration Guide

## Overview

The **T5 Corrector** is an experimental text correction module for SATCN that uses transformer-based language models (specifically T5/FLAN-T5) to perform context-aware grammar and spelling correction.

This guide covers the new `satcn.correction` module architecture, integration strategies, and usage examples.

## What's New

### Module Structure

We've introduced a new modular architecture for correction components:

```
satcn/
├── __init__.py
└── correction/
    ├── __init__.py
    └── t5_corrector.py      # New T5 correction engine

pipeline/
└── filters/
    └── t5_correction_filter.py  # Pipeline integration wrapper
```

### Key Features

1. **Clean API**: Simple, intuitive interface for text correction
2. **Standalone or Pipeline**: Use independently or integrate into SATCN pipeline
3. **Multiple Integration Modes**: Replace, hybrid, or supplement existing filters
4. **GPU/CPU Support**: Automatic device detection with fallback
5. **Batch Processing**: Process multiple texts efficiently
6. **Statistics Tracking**: Monitor corrections and performance
7. **Error Handling**: Graceful degradation on failures

## Installation

### 1. Install Dependencies

```bash
# Install T5 requirements
pip install -r requirements-t5.txt

# Or install manually:
pip install torch>=2.0.0 transformers>=4.30.0 accelerate>=0.20.0
```

### 2. GPU Setup (Recommended)

For best performance, use a CUDA-capable GPU:

```bash
# Check CUDA availability
python check_cuda.py

# If CUDA is not detected, install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 3. Model Download

The model will be automatically downloaded on first use (~3GB). Alternatively:

```bash
python -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; \
           AutoTokenizer.from_pretrained('pszemraj/flan-t5-large-grammar-synthesis'); \
           AutoModelForSeq2SeqLM.from_pretrained('pszemraj/flan-t5-large-grammar-synthesis')"
```

## Usage

### Standalone Usage

#### Basic Correction

```python
from satcn.correction import T5Corrector

# Initialize corrector
corrector = T5Corrector()

# Correct text
original = "This sentance have many erors."
corrected = corrector.correct(original)
print(corrected)  # "This sentence has many errors."
```

#### Batch Processing

```python
from satcn.correction import T5Corrector

corrector = T5Corrector()

texts = [
    "First sentance with eror.",
    "Second sentance also have mistake.",
    "Third one is perfekt."
]

corrected_texts = corrector.correct_batch(texts, show_progress=True)

for original, corrected in zip(texts, corrected_texts):
    print(f"{original} → {corrected}")
```

#### Custom Configuration

```python
from satcn.correction import T5Corrector

corrector = T5Corrector(
    model_name="pszemraj/flan-t5-large-grammar-synthesis",  # Model to use
    device="cuda",           # Force CUDA (or "cpu", "mps", None for auto)
    max_length=512,          # Maximum sequence length
    num_beams=4,             # Beam search parameter (higher = better quality)
    use_half_precision=True  # Use float16 on GPU
)

corrected = corrector.correct("Your text here")
```

#### Statistics Tracking

```python
corrector = T5Corrector()

# Process some texts
corrector.correct("Text one with erors")
corrector.correct("Text two is perfect")

# Get statistics
stats = corrector.get_stats()
print(f"Processed: {stats['texts_processed']}")
print(f"Corrected: {stats['corrections_made']}")
print(f"Errors: {stats['errors']}")

# Reset statistics
corrector.reset_stats()
```

### Pipeline Integration

#### Mode 1: Replace (Recommended)

Replace spelling and grammar filters with T5 only:

```bash
python -m pipeline.pipeline_runner --use-t5 document.md
```

**Pipeline order:**
1. Parser (Markdown/EPUB)
2. **T5 Correction** ← Single correction stage
3. TTS Normalization
4. Output

**Pros:**
- Simplest pipeline
- Context-aware corrections
- Handles spelling + grammar together

**Cons:**
- Slower than rule-based (GPU recommended)
- Less predictable than rules

#### Mode 2: Hybrid

T5 first, then rule-based cleanup:

```bash
python -m pipeline.pipeline_runner --use-t5 --t5-mode hybrid document.md
```

**Pipeline order:**
1. Parser
2. **T5 Correction** ← Major corrections
3. Spelling Filter ← Catch remaining issues
4. Grammar Filter ← Rule-based cleanup
5. TTS Normalization
6. Output

**Pros:**
- Best of both worlds (AI + rules)
- Comprehensive corrections
- Deterministic fallback

**Cons:**
- Longest processing time
- Potential filter conflicts

#### Mode 3: Supplement

Add T5 after existing filters:

```bash
python -m pipeline.pipeline_runner --use-t5 --t5-mode supplement document.md
```

**Pipeline order:**
1. Parser
2. Spelling Filter
3. Grammar Filter
4. **T5 Correction** ← Final polish
5. TTS Normalization
6. Output

**Pros:**
- Conservative approach
- Keeps existing corrections
- Additional AI polish

**Cons:**
- May over-correct
- Longest pipeline

### Programmatic Pipeline Usage

```python
from pipeline.pipeline_runner import PipelineRunner

# Create pipeline with T5
pipeline = PipelineRunner(
    "document.md",
    use_t5=True,
    t5_mode="replace"
)

# Run pipeline
result = pipeline.run()

print(f"Output: {result['output_filepath']}")
```

## Advanced Usage

### Alternative Models

```python
from satcn.correction import T5Corrector

# List available models
models = T5Corrector.list_models()
print(models)

# Use alternative model
corrector = T5Corrector(model_name="vennify/t5-base-grammar-correction")
```

### Confidence Scores (Future Feature)

```python
corrector = T5Corrector()

corrected, confidence = corrector.correct(
    "Text to correct",
    return_confidence=True
)

print(f"Corrected: {corrected}")
print(f"Confidence: {confidence}")
```

*Note: Confidence scoring is currently a placeholder for future enhancement.*

### Custom Logger

```python
import logging
from satcn.correction import T5Corrector

logger = logging.getLogger("my_app")
corrector = T5Corrector(logger=logger)
```

## Testing

### Run Integration Tests

```bash
# Quick environment check
python test_t5_corrector_integration.py --skip-model

# Full integration tests
python test_t5_corrector_integration.py

# With pipeline tests
python test_t5_corrector_integration.py --pipeline

# With benchmarking
python test_t5_corrector_integration.py --benchmark
```

### Run Unit Tests

```bash
# Test T5Corrector module
pytest tests/unit/test_t5_corrector.py -v

# Run all tests
pytest tests/ -v
```

### Test with Real Documents

```bash
# Test Markdown
python -m pipeline.pipeline_runner --use-t5 tests/samples/sample.md

# Test EPUB
python -m pipeline.pipeline_runner --use-t5 tests/samples/sample.epub
```

## Performance

### Hardware Requirements

| Configuration | Speed per Sentence | Memory Required | Use Case |
|--------------|-------------------|-----------------|----------|
| **CPU only** | 5-30 seconds | 8-16 GB RAM | Testing, small batches |
| **GPU (NVIDIA)** | 0.5-2 seconds | 6-8 GB VRAM | Production, large documents |
| **Apple Silicon** | 2-5 seconds | 8 GB unified | Mac development |

### Optimization Tips

1. **Use GPU** - 10-50x faster than CPU
2. **Half Precision** - Use `use_half_precision=True` on GPU (default)
3. **Reduce Max Length** - Lower `max_length` for shorter texts
4. **Batch Processing** - Use `correct_batch()` for multiple texts

### Benchmarking

```bash
# Run performance benchmark
python test_t5_corrector_integration.py --benchmark

# Run full pipeline benchmark
python benchmark.py
```

## Troubleshooting

### Issue: "No module named 'torch'"

**Solution**: Install PyTorch:
```bash
pip install torch transformers accelerate
```

### Issue: "CUDA not available" (but you have GPU)

**Solution**: Install CUDA-enabled PyTorch:
```bash
./fix_cuda.sh
# OR manually:
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Issue: Very slow on CPU

**Solutions:**
1. Use GPU if available (10-50x faster)
2. Switch to smaller model: `T5Corrector(model_name="pszemraj/flan-t5-base-grammar-synthesis")`
3. Reduce `max_length` parameter
4. Use hybrid mode with T5 only for critical sections

### Issue: "CUDA out of memory"

**Solutions:**
1. Reduce `max_length`: `T5Corrector(max_length=256)`
2. Disable half precision: `T5Corrector(use_half_precision=False)`
3. Fall back to CPU: `T5Corrector(device="cpu")`

### Issue: Over-corrections or hallucinations

**Expected Behavior**: This is a known limitation in the experimental phase.

**Future Mitigations:**
- Edit constraints and guardrails
- Slang/informal language masking
- Domain-specific fine-tuning
- Confidence thresholds

## API Reference

### T5Corrector Class

```python
class T5Corrector:
    """T5-based text correction engine."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        max_length: int = 512,
        num_beams: int = 4,
        use_half_precision: bool = True,
        logger: Optional[logging.Logger] = None
    )

    def correct(
        self,
        text: str,
        return_confidence: bool = False
    ) -> Union[str, Tuple[str, float]]

    def correct_batch(
        self,
        texts: List[str],
        show_progress: bool = False
    ) -> List[str]

    def process(self, data: Dict) -> Dict

    def get_stats(self) -> Dict[str, int]

    def reset_stats(self) -> None

    @classmethod
    def list_models(cls) -> Dict[str, str]
```

### PipelineRunner Updates

```python
class PipelineRunner:
    """SATCN pipeline runner with T5 support."""

    def __init__(
        self,
        input_filepath: str,
        fail_fast: bool = False,
        use_t5: bool = False,           # Enable T5 correction
        t5_mode: str = "replace"        # "replace", "hybrid", or "supplement"
    )
```

## Examples

### Example 1: Simple Correction

```python
from satcn.correction import T5Corrector

corrector = T5Corrector()
result = corrector.correct("Thiss sentance have erors.")
print(result)  # "This sentence has errors."
```

### Example 2: Process Document

```python
from pipeline.pipeline_runner import PipelineRunner

pipeline = PipelineRunner("document.md", use_t5=True)
result = pipeline.run()
print(f"Corrected document: {result['output_filepath']}")
```

### Example 3: Custom Workflow

```python
from satcn.correction import T5Corrector

# Initialize once
corrector = T5Corrector()

# Process multiple documents
for doc_path in ["doc1.txt", "doc2.txt", "doc3.txt"]:
    with open(doc_path) as f:
        text = f.read()

    corrected = corrector.correct(text)

    with open(f"{doc_path}.corrected", "w") as f:
        f.write(corrected)

# Show statistics
stats = corrector.get_stats()
print(f"Total processed: {stats['texts_processed']}")
```

## Comparison: T5 vs Existing Filters

| Feature | pyspellchecker | LanguageTool | T5 Corrector |
|---------|---------------|--------------|--------------|
| **Context-aware** | ❌ No | ⚠️ Limited | ✅ Yes |
| **Handles complex grammar** | ❌ No | ⚠️ Some | ✅ Yes |
| **Speed (GPU)** | Fast | Medium | Fast |
| **Speed (CPU)** | Fast | Medium | Slow |
| **Predictable** | ✅ Yes | ✅ Yes | ⚠️ Mostly |
| **Resource usage** | Low | Medium | High |
| **Setup complexity** | Low | Medium | Medium-High |

## Roadmap

### Current Status (v0.2.0)

- ✅ Core T5Corrector module
- ✅ Pipeline integration (3 modes)
- ✅ Standalone API
- ✅ Batch processing
- ✅ GPU/CPU support
- ✅ Statistics tracking
- ✅ Comprehensive tests
- ✅ Documentation

### Future Enhancements

- [ ] Confidence scoring
- [ ] Edit constraints/guardrails
- [ ] Slang/informal language masking
- [ ] Domain-specific fine-tuning
- [ ] Model quantization (8-bit/4-bit)
- [ ] True batch inference
- [ ] Output caching
- [ ] A/B testing framework
- [ ] Multi-language support

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on contributing to the T5 integration.

## License

This project is licensed under the same terms as SATCN.

## References

- **Model**: [pszemraj/flan-t5-large-grammar-synthesis](https://huggingface.co/pszemraj/flan-t5-large-grammar-synthesis)
- **Base Model**: [google/flan-t5-large](https://huggingface.co/google/flan-t5-large)
- **Transformers**: [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- **SATCN**: [Main README](../README.md)

## Support

For issues or questions:
- Check [T5_INTEGRATION_GUIDE.md](../T5_INTEGRATION_GUIDE.md) for troubleshooting
- Run diagnostic: `python check_cuda.py`
- Open an issue on GitHub
