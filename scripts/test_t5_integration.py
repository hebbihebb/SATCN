#!/usr/bin/env python3
"""
Test script to demonstrate FLAN-T5 integration for grammar/spelling correction.

This script demonstrates how the T5GrammarFilter works both standalone and
within the existing pipeline architecture.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.filters.t5_grammar_filter import T5GrammarFilter

def test_standalone():
    """Test the T5 filter with direct text input."""
    print("=" * 60)
    print("Testing T5GrammarFilter - Standalone Mode")
    print("=" * 60)

    # Initialize the filter
    print("\n1. Loading T5 model...")
    print("   (This may take a while on first run - downloading ~3GB model)")

    try:
        t5_filter = T5GrammarFilter(
            model_name="pszemraj/flan-t5-large-grammar-synthesis"
        )
    except Exception as e:
        print(f"\n❌ Failed to load model: {e}")
        print("\nNote: Make sure you have transformers and torch installed:")
        print("  pip install transformers torch")
        return False

    print("✓ Model loaded successfully!\n")

    # Test cases
    test_sentences = [
        "Thiss sentnce have many speling errrors.",
        "The cat are sleeping on the couch.",
        "I has three apples and two orange.",
        "She don't likes to running in the park.",
        "Their going to they're house over there."
    ]

    print("2. Testing grammar/spelling corrections:\n")

    for i, text in enumerate(test_sentences, 1):
        print(f"Test {i}:")
        print(f"  Original:  {text}")
        corrected = t5_filter.correct_text(text)
        print(f"  Corrected: {corrected}")
        print()

    return True

def test_pipeline_integration():
    """Test the T5 filter within the pipeline data structure."""
    print("\n" + "=" * 60)
    print("Testing T5GrammarFilter - Pipeline Integration")
    print("=" * 60)

    print("\n3. Testing with pipeline data structure...\n")

    try:
        t5_filter = T5GrammarFilter()
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return False

    # Simulate pipeline data structure
    test_data = {
        'text_blocks': [
            {
                'content': 'This is a test sentence with no errors.',
                'metadata': {'type': 'paragraph'}
            },
            {
                'content': 'This sentence have a grammar error.',
                'metadata': {'type': 'paragraph'}
            },
            {
                'content': 'Ther are many speling misteaks here.',
                'metadata': {'type': 'paragraph'}
            }
        ]
    }

    print("Input data:")
    for i, block in enumerate(test_data['text_blocks']):
        print(f"  Block {i}: {block['content']}")

    # Process through filter
    result = t5_filter.process(test_data)

    print("\nOutput data:")
    for i, block in enumerate(result['text_blocks']):
        print(f"  Block {i}: {block['content']}")

    return True

def show_integration_guide():
    """Display integration guide."""
    print("\n" + "=" * 60)
    print("Integration Guide")
    print("=" * 60)

    guide = """
To integrate T5GrammarFilter into your pipeline:

1. Update requirements.txt:
   Add these lines:
   ---
   transformers>=4.30.0
   torch>=2.0.0
   accelerate>=0.20.0
   ---

2. Modify pipeline/pipeline_runner.py:

   a) Import the filter (add to imports at top):
      from .filters.t5_grammar_filter import T5GrammarFilter

   b) Add to _get_filters() method (line ~30):

      Option A - Replace grammar filter:
      return [
          (parser_filter, False),
          (SpellingCorrectionFilter(), False),
          (T5GrammarFilter(), False),  # ← New T5 filter
          (TTSNormalizer(), False),
          (output_generator, False)
      ]

      Option B - Use both (T5 first, then rule-based cleanup):
      return [
          (parser_filter, False),
          (T5GrammarFilter(), False),  # ← Add this
          (SpellingCorrectionFilter(), False),
          (GrammarCorrectionFilterSafe(), True),
          (TTSNormalizer(), False),
          (output_generator, False)
      ]

3. Performance considerations:
   - First run: Downloads ~3GB model from Hugging Face
   - GPU recommended: ~10-50x faster than CPU
   - Memory: ~6-8GB GPU RAM or ~8-16GB system RAM
   - Speed: ~0.5-2 seconds per sentence (GPU), ~5-30 seconds (CPU)

4. Using local model:
   If you want to use the model in flan-t5-large-grammar-synthesis/:
   - Download full model files (not just GGUF)
   - Use: T5GrammarFilter(model_name="./flan-t5-large-grammar-synthesis")

5. Testing:
   Run unit tests:
   $ pytest tests/unit/test_t5_grammar_filter.py

   Run integration test:
   $ python test_t5_integration.py
"""
    print(guide)

def main():
    """Main test runner."""
    print("\n" + "=" * 60)
    print("FLAN-T5 Grammar Correction - Integration Test")
    print("=" * 60)

    # Run standalone test
    if not test_standalone():
        print("\n⚠️  Standalone test failed. Check error messages above.")
        return 1

    # Run pipeline integration test
    if not test_pipeline_integration():
        print("\n⚠️  Pipeline integration test failed.")
        return 1

    # Show integration guide
    show_integration_guide()

    print("\n✓ All tests completed successfully!")
    print("\nNext steps:")
    print("  1. Review the integration guide above")
    print("  2. Update requirements.txt with transformers dependencies")
    print("  3. Modify pipeline_runner.py to include T5GrammarFilter")
    print("  4. Test with real documents: python -m pipeline.pipeline_runner <file.md>")

    return 0

if __name__ == "__main__":
    sys.exit(main())
