#!/usr/bin/env python3
"""
T5 Corrector Integration Test Script

This script demonstrates and tests the new T5Corrector module integration
into the SATCN pipeline. It provides comprehensive examples of:

1. Standalone T5Corrector usage
2. Batch processing
3. Pipeline integration (Markdown and EPUB)
4. Different T5 modes (replace, hybrid, supplement)
5. Performance benchmarking

Usage:
    # Basic test (standalone corrector)
    python test_t5_corrector_integration.py

    # Test with pipeline
    python test_t5_corrector_integration.py --pipeline

    # Test with sample file
    python test_t5_corrector_integration.py --file tests/samples/sample.md

    # Skip model loading (quick check)
    python test_t5_corrector_integration.py --skip-model
"""

import sys
import argparse
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def print_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_result(label, original, corrected):
    """Print a correction result."""
    print(f"{label}:")
    print(f"  Original:  {original}")
    print(f"  Corrected: {corrected}")
    if original != corrected:
        print(f"  ✓ Modified")
    else:
        print(f"  - No change")
    print()


def test_standalone_corrector():
    """Test T5Corrector standalone usage."""
    print_header("Test 1: Standalone T5Corrector")

    from satcn.correction import T5Corrector

    print("Initializing T5 corrector...")
    start_time = time.time()
    corrector = T5Corrector()
    init_time = time.time() - start_time

    print(f"✓ Model loaded in {init_time:.2f} seconds")
    print(f"  Model: {corrector.model_name}")
    print(f"  Device: {corrector.device}")
    print(f"  Max length: {corrector.max_length}")
    print()

    # Test various correction scenarios
    test_cases = [
        "Thiss sentance have many speling errrors.",
        "The team are working on they're project over their.",
        "I wants to goes to the store for buying some grocerys.",
        "Its a beautifull day, isnt it?",
        "He dont know nothing about this subject.",
    ]

    print("Testing corrections:")
    print("-" * 70)

    for i, text in enumerate(test_cases, 1):
        start = time.time()
        corrected = corrector.correct(text)
        duration = time.time() - start

        print_result(f"Test {i} ({duration:.2f}s)", text, corrected)

    # Show statistics
    stats = corrector.get_stats()
    print("-" * 70)
    print("Statistics:")
    print(f"  Texts processed: {stats['texts_processed']}")
    print(f"  Corrections made: {stats['corrections_made']}")
    print(f"  Errors: {stats['errors']}")
    print()


def test_batch_processing():
    """Test batch processing."""
    print_header("Test 2: Batch Processing")

    from satcn.correction import T5Corrector

    corrector = T5Corrector()

    texts = [
        "First sentance with eror.",
        "Second sentance also have mistake.",
        "Third one is perfekt.",
    ]

    print("Processing batch of texts...")
    start = time.time()
    corrected_texts = corrector.correct_batch(texts, show_progress=True)
    duration = time.time() - start

    print()
    for i, (original, corrected) in enumerate(zip(texts, corrected_texts), 1):
        print_result(f"Text {i}", original, corrected)

    print(f"Batch processed in {duration:.2f} seconds")
    print(f"Average: {duration/len(texts):.2f} seconds per text")
    print()


def test_pipeline_integration(test_file=None):
    """Test pipeline integration."""
    print_header("Test 3: Pipeline Integration")

    from pipeline.pipeline_runner import PipelineRunner
    import tempfile
    import os

    # Create or use test file
    if test_file is None:
        # Create temporary markdown file
        test_content = """# Test Document

This is a test docment with some speling erors.

## Section 1

The team are working on they're project. Its going very well.

## Section 2

We wants to make sure everything work correctly.
"""
        fd, test_file = tempfile.mkstemp(suffix='.md', text=True)
        with os.fdopen(fd, 'w') as f:
            f.write(test_content)
        temp_file = True
    else:
        temp_file = False

    print(f"Input file: {test_file}")
    print()

    # Test different T5 modes
    modes = ["replace", "hybrid", "supplement"]

    for mode in modes:
        print(f"Testing T5 mode: {mode}")
        print("-" * 70)

        try:
            pipeline = PipelineRunner(
                test_file,
                use_t5=True,
                t5_mode=mode
            )

            start = time.time()
            result = pipeline.run()
            duration = time.time() - start

            if result and 'output_filepath' in result:
                print(f"✓ Pipeline completed in {duration:.2f} seconds")
                print(f"  Output: {result['output_filepath']}")

                # Clean up output file
                if os.path.exists(result['output_filepath']):
                    os.remove(result['output_filepath'])
            else:
                print("✗ Pipeline failed")

        except Exception as e:
            print(f"✗ Error: {e}")

        print()

    # Clean up temp file
    if temp_file and os.path.exists(test_file):
        os.remove(test_file)


def test_model_alternatives():
    """Test alternative T5 models."""
    print_header("Test 4: Alternative Models")

    from satcn.correction import T5Corrector

    available_models = T5Corrector.list_models()

    print("Available models:")
    for name, model_id in available_models.items():
        print(f"  {name}: {model_id}")
    print()

    print("Note: To use an alternative model:")
    print("  corrector = T5Corrector(model_name='model-id-here')")
    print()


def test_confidence_scores():
    """Test confidence scoring (future feature)."""
    print_header("Test 5: Confidence Scores")

    from satcn.correction import T5Corrector

    corrector = T5Corrector()

    text = "This is a test sentance."
    corrected, confidence = corrector.correct(text, return_confidence=True)

    print(f"Text: {text}")
    print(f"Corrected: {corrected}")
    print(f"Confidence: {confidence}")
    print()
    print("Note: Confidence scoring is a placeholder for future enhancement.")
    print()


def benchmark_performance():
    """Benchmark T5 corrector performance."""
    print_header("Performance Benchmark")

    from satcn.correction import T5Corrector
    import statistics

    corrector = T5Corrector()

    test_text = "This sentance have some erors that need to be corrected by the model."

    print("Running 5 correction passes for benchmarking...")
    durations = []

    for i in range(5):
        start = time.time()
        corrector.correct(test_text)
        duration = time.time() - start
        durations.append(duration)
        print(f"  Pass {i+1}: {duration:.3f}s")

    print()
    print("Statistics:")
    print(f"  Mean: {statistics.mean(durations):.3f}s")
    print(f"  Median: {statistics.median(durations):.3f}s")
    print(f"  Min: {min(durations):.3f}s")
    print(f"  Max: {max(durations):.3f}s")
    print()


def check_environment():
    """Check system environment for T5 compatibility."""
    print_header("Environment Check")

    # Check Python version
    print(f"Python version: {sys.version}")

    # Check for torch
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA device: {torch.cuda.get_device_name(0)}")
            print(f"CUDA version: {torch.version.cuda}")
    except ImportError:
        print("✗ PyTorch not installed")
        return False

    # Check for transformers
    try:
        import transformers
        print(f"Transformers version: {transformers.__version__}")
    except ImportError:
        print("✗ Transformers not installed")
        return False

    # Check for satcn.correction
    try:
        from satcn.correction import T5Corrector
        print("✓ satcn.correction module found")
    except ImportError as e:
        print(f"✗ satcn.correction import failed: {e}")
        return False

    print()
    return True


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(
        description="Test T5Corrector integration",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--skip-model',
        action='store_true',
        help='Skip model loading (quick environment check only)'
    )
    parser.add_argument(
        '--pipeline',
        action='store_true',
        help='Include pipeline integration tests'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Test file for pipeline integration'
    )
    parser.add_argument(
        '--benchmark',
        action='store_true',
        help='Run performance benchmark'
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("  T5 Corrector Integration Test Suite")
    print("  SATCN - Experimental T5 Integration")
    print("=" * 70)

    # Environment check
    if not check_environment():
        print("\n✗ Environment check failed. Please install dependencies:")
        print("  pip install -r requirements-t5.txt")
        sys.exit(1)

    if args.skip_model:
        print("\n✓ Environment check passed (model loading skipped)")
        sys.exit(0)

    # Run tests
    try:
        # Test 1: Standalone corrector
        test_standalone_corrector()

        # Test 2: Batch processing
        test_batch_processing()

        # Test 3: Pipeline integration (optional)
        if args.pipeline:
            test_pipeline_integration(args.file)

        # Test 4: Alternative models
        test_model_alternatives()

        # Test 5: Confidence scores
        test_confidence_scores()

        # Benchmark (optional)
        if args.benchmark:
            benchmark_performance()

        # Summary
        print_header("Test Summary")
        print("✓ All tests completed successfully!")
        print()
        print("Next steps:")
        print("  1. Run with your own files:")
        print("     python -m pipeline.pipeline_runner --use-t5 your_file.md")
        print()
        print("  2. Try different T5 modes:")
        print("     python -m pipeline.pipeline_runner --use-t5 --t5-mode hybrid your_file.md")
        print()
        print("  3. Run unit tests:")
        print("     pytest tests/unit/test_t5_corrector.py -v")
        print()

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
