#!/usr/bin/env python3
"""
Quick benchmark comparing GRMR-V3 vs T5 grammar correction models.

Usage:
    python benchmark_grmr_vs_t5.py
"""

import time

# Test sentences with various grammar issues
TEST_SENTENCES = [
    "Thiss sentnce have two speling errrors.",
    "The crew was suppose to arrive yesteday evening.",
    "Irina said she dont wanna go to the market no more.",
    "Their going too fast for the narow bridge.",
    "I has forgotten where I put the keys.",
    "The woman which I met yesterday was vary nice.",
    "Me and him went to the store.",
    "She run to the park every morning.",
]


def benchmark_grmr_v3():
    """Benchmark GRMR-V3 GGUF model."""
    try:
        from pipeline.filters.grmr_v3_filter import GRMRV3GrammarFilter

        print("=" * 60)
        print("GRMR-V3 GGUF Model Benchmark")
        print("=" * 60)

        # Initialize model
        print("\nInitializing model...")
        start_time = time.time()
        filter_obj = GRMRV3GrammarFilter()
        init_time = time.time() - start_time
        print(f"✓ Model loaded in {init_time:.2f}s")

        # Run corrections
        print(f"\nProcessing {len(TEST_SENTENCES)} test sentences...")
        corrections = []
        total_time = 0

        for i, sentence in enumerate(TEST_SENTENCES, 1):
            start = time.time()
            corrected = filter_obj.correct_text(sentence)
            duration = time.time() - start
            total_time += duration
            corrections.append((sentence, corrected, duration))

            print(f"\n[{i}/{len(TEST_SENTENCES)}] {duration:.2f}s")
            print(f"  Original : {sentence}")
            print(f"  Corrected: {corrected}")

        # Summary
        avg_time = total_time / len(TEST_SENTENCES)
        stats = filter_obj.get_stats()

        print(f"\n{'─' * 60}")
        print("Summary:")
        print(f"  Model load time: {init_time:.2f}s")
        print(f"  Total inference: {total_time:.2f}s")
        print(f"  Average per sentence: {avg_time:.2f}s")
        print(f"  Total tokens generated: {stats['total_tokens_generated']}")
        print("  Device: CPU (RTX 4060 available but not using GPU)")
        print(f"{'─' * 60}")

        return {
            "model": "GRMR-V3",
            "init_time": init_time,
            "total_time": total_time,
            "avg_time": avg_time,
            "corrections": corrections,
            "stats": stats,
        }

    except ImportError as e:
        print(f"✗ GRMR-V3 not available: {e}")
        print("  Install with: pip install -r requirements-grmr.txt")
        return None
    except Exception as e:
        print(f"✗ Error running GRMR-V3 benchmark: {e}")
        return None


def benchmark_t5():
    """Benchmark T5 model."""
    try:
        from pipeline.filters.t5_correction_filter import T5CorrectionFilter

        print("\n" + "=" * 60)
        print("T5 Model Benchmark")
        print("=" * 60)

        # Initialize model
        print("\nInitializing model...")
        start_time = time.time()
        filter_obj = T5CorrectionFilter()
        init_time = time.time() - start_time
        print(f"✓ Model loaded in {init_time:.2f}s")

        # Run corrections
        print(f"\nProcessing {len(TEST_SENTENCES)} test sentences...")
        corrections = []
        total_time = 0

        for i, sentence in enumerate(TEST_SENTENCES, 1):
            start = time.time()
            corrected = filter_obj.correct_text(sentence)
            duration = time.time() - start
            total_time += duration
            corrections.append((sentence, corrected, duration))

            print(f"\n[{i}/{len(TEST_SENTENCES)}] {duration:.2f}s")
            print(f"  Original : {sentence}")
            print(f"  Corrected: {corrected}")

        # Summary
        avg_time = total_time / len(TEST_SENTENCES)

        print(f"\n{'─' * 60}")
        print("Summary:")
        print(f"  Model load time: {init_time:.2f}s")
        print(f"  Total inference: {total_time:.2f}s")
        print(f"  Average per sentence: {avg_time:.2f}s")
        print(f"{'─' * 60}")

        return {
            "model": "T5",
            "init_time": init_time,
            "total_time": total_time,
            "avg_time": avg_time,
            "corrections": corrections,
        }

    except ImportError as e:
        print(f"✗ T5 not available: {e}")
        print("  Install with: pip install transformers torch")
        return None
    except Exception as e:
        print(f"✗ Error running T5 benchmark: {e}")
        return None


def compare_results(grmr_results, t5_results):
    """Compare GRMR-V3 and T5 results."""
    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)

    if grmr_results and t5_results:
        print("\nSpeed Comparison:")
        print(f"  GRMR-V3: {grmr_results['avg_time']:.2f}s per sentence")
        print(f"  T5:      {t5_results['avg_time']:.2f}s per sentence")

        if grmr_results["avg_time"] < t5_results["avg_time"]:
            speedup = t5_results["avg_time"] / grmr_results["avg_time"]
            print(f"  ✓ GRMR-V3 is {speedup:.1f}x faster")
        else:
            slowdown = grmr_results["avg_time"] / t5_results["avg_time"]
            print(f"  ✓ T5 is {slowdown:.1f}x faster")

        print("\nCorrection Quality Comparison:")
        print("(Check for character name preservation, accuracy, etc.)")

        for i, (original, _, _) in enumerate(grmr_results["corrections"]):
            grmr_corrected = grmr_results["corrections"][i][1]
            t5_corrected = t5_results["corrections"][i][1]

            print(f"\n[{i+1}] {original}")
            print(f"  GRMR-V3: {grmr_corrected}")
            print(f"  T5:      {t5_corrected}")

            # Check if "Irina" is preserved
            if "Irina" in original:
                grmr_preserves = "Irina" in grmr_corrected
                t5_preserves = "Irina" in t5_corrected
                print(
                    f"  Name preservation: GRMR-V3={'✓' if grmr_preserves else '✗'}, T5={'✓' if t5_preserves else '✗'}"
                )

    elif grmr_results:
        print("\n✓ GRMR-V3 benchmark completed")
        print("✗ T5 benchmark not available for comparison")

    elif t5_results:
        print("\n✓ T5 benchmark completed")
        print("✗ GRMR-V3 benchmark not available for comparison")

    else:
        print("\n✗ No models available for benchmarking")
        print("  Install at least one model to run benchmarks")


def main():
    print("SATCN Grammar Model Benchmark")
    print("Testing GRMR-V3 vs T5 performance\n")

    # Run benchmarks
    grmr_results = benchmark_grmr_v3()
    t5_results = benchmark_t5()

    # Compare
    compare_results(grmr_results, t5_results)

    print("\n" + "=" * 60)
    print("Benchmark Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
