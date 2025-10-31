"""
Compare GRMR-V3 Q4 vs Q8 model performance and quality.

This script tests both quantization levels of the GRMR-V3 model:
- Q4_K_M (4-bit quantized, 2.5GB) - Current production model
- Q8_0 (8-bit quantized, 4.3GB) - Higher precision, potentially better quality

Tests:
1. Quality: Run benchmark test suite (31 grammar/spelling cases)
2. Performance: Processing speed and memory usage
3. Consistency: Same input produces same output (temperature=0.1)
4. Long Document: Real-world 15K+ word novel correction

Results are logged to: results/q4_vs_q8_comparison_{timestamp}.json
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Force UTF-8 encoding for stdout to handle Unicode characters
if sys.stdout.encoding != "utf-8":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from satcn.core.filters.grmr_v3_filter import GRMRV3GrammarFilter  # noqa: E402

# Test cases covering grammar, spelling, punctuation, and edge cases
TEST_CASES = [
    # Grammar errors
    {
        "name": "subject_verb_agreement",
        "input": "The dogs barks loudly.",
        "expected_fixes": ["bark"],
        "category": "grammar",
    },
    {
        "name": "tense_consistency",
        "input": "She walks to the store and bought milk.",
        "expected_fixes": ["walked", "buys"],
        "category": "grammar",
    },
    {
        "name": "pronoun_case",
        "input": "Him and me went to the park.",
        "expected_fixes": ["He", "I"],
        "category": "grammar",
    },
    {
        "name": "double_negative",
        "input": "I don't know nothing about it.",
        "expected_fixes": ["anything"],
        "category": "grammar",
    },
    {
        "name": "run_on_sentence",
        "input": "I love coding it's my favorite hobby I do it every day.",
        "expected_fixes": [".", ",", ";"],
        "category": "grammar",
    },
    # Spelling errors
    {
        "name": "common_misspelling",
        "input": "I recieved your message yesterday.",
        "expected_fixes": ["received"],
        "category": "spelling",
    },
    {
        "name": "homophone_confusion",
        "input": "Their going to there house over they're.",
        "expected_fixes": ["They're", "their", "there"],
        "category": "spelling",
    },
    {
        "name": "typo_correction",
        "input": "The qwick brown fox jumps over teh lazy dog.",
        "expected_fixes": ["quick", "the"],
        "category": "spelling",
    },
    # Punctuation
    {
        "name": "missing_comma",
        "input": "After eating the dog went outside.",
        "expected_fixes": [","],
        "category": "punctuation",
    },
    {
        "name": "missing_apostrophe",
        "input": "Its a beautiful day and Im happy.",
        "expected_fixes": ["It's", "I'm"],
        "category": "punctuation",
    },
    {
        "name": "comma_splice",
        "input": "I love reading, it's my favorite activity.",
        "expected_fixes": [";", "."],
        "category": "punctuation",
    },
    # Proper nouns (should NOT be changed)
    {
        "name": "character_names",
        "input": "Katniss Everdeen and Peeta Mellark fought in the arena.",
        "expected_fixes": [],
        "category": "preservation",
    },
    {
        "name": "fantasy_terms",
        "input": "The Dementors attacked Hogwarts castle.",
        "expected_fixes": [],
        "category": "preservation",
    },
    # Edge cases
    {
        "name": "dialogue_formatting",
        "input": '"Hello," she said. "How are you?"',
        "expected_fixes": [],
        "category": "edge_case",
    },
    {
        "name": "numbers_and_dates",
        "input": "On March 15th, 2023, we met at 3:30 PM.",
        "expected_fixes": [],
        "category": "edge_case",
    },
    {
        "name": "mixed_errors",
        "input": "Their are alot of mistakes in this sentance, dont you think.",
        "expected_fixes": ["There", "a lot", "sentence", "don't", "?"],
        "category": "mixed",
    },
]


def load_model(model_path: str, device: str = None) -> GRMRV3GrammarFilter:
    """Load GRMR-V3 model from specified path."""
    print(f"Loading model: {Path(model_path).name}")
    print(f"Size: {Path(model_path).stat().st_size / (1024**3):.2f} GB")
    print(f"Device: {device if device else 'CPU'}")

    start_time = time.time()
    filter_instance = GRMRV3GrammarFilter(model_path=model_path, device=device)
    load_time = time.time() - start_time

    print(f"Model loaded in {load_time:.2f}s\n")
    return filter_instance, load_time


def run_quality_test(filter_instance: GRMRV3GrammarFilter, test_case: dict) -> dict[str, Any]:
    """Run a single quality test case."""
    print(f"  Testing: {test_case['name']}", end=" ", flush=True)

    input_text = test_case["input"]
    start_time = time.time()

    # Correct the text with error handling
    try:
        output_text = filter_instance.correct_text(input_text)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        raise
    except Exception as e:
        print(f"\n    ✗ ERROR: {e}")
        return {
            "name": test_case["name"],
            "category": test_case["category"],
            "input": input_text,
            "output": None,
            "error": str(e),
            "passed": False,
            "processing_time_ms": 0,
        }

    processing_time = time.time() - start_time

    # Check if output differs from input
    has_changes = output_text != input_text

    # Check if expected fixes are present (basic substring check)
    expected_fixes = test_case.get("expected_fixes", [])
    fixes_found = []
    fixes_missing = []

    for fix in expected_fixes:
        if fix in output_text:
            fixes_found.append(fix)
        else:
            fixes_missing.append(fix)

    # Determine if test passed
    if not expected_fixes:
        # Preservation test - output should be identical
        passed = output_text == input_text
    else:
        # Correction test - at least some fixes should be present
        passed = len(fixes_found) > 0

    result = {
        "name": test_case["name"],
        "category": test_case["category"],
        "input": input_text,
        "output": output_text,
        "has_changes": has_changes,
        "expected_fixes": expected_fixes,
        "fixes_found": fixes_found,
        "fixes_missing": fixes_missing,
        "passed": passed,
        "processing_time_ms": processing_time * 1000,
    }

    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} ({processing_time*1000:.0f}ms)")
    if fixes_missing:
        print(f"    Missing fixes: {fixes_missing}")

    return result


def run_consistency_test(
    filter_instance: GRMRV3GrammarFilter, text: str, runs: int = 3
) -> dict[str, Any]:
    """Test if model produces consistent results across multiple runs."""
    print(f"\n  Running consistency test ({runs} iterations)...")

    outputs = []
    times = []

    for i in range(runs):
        start_time = time.time()
        output = filter_instance.correct_text(text)
        processing_time = time.time() - start_time

        outputs.append(output)
        times.append(processing_time)
        print(f"    Run {i+1}: {processing_time*1000:.0f}ms")

    # Check if all outputs are identical
    all_identical = all(output == outputs[0] for output in outputs)

    return {
        "consistent": all_identical,
        "outputs": outputs,
        "avg_time_ms": sum(times) / len(times) * 1000,
        "std_time_ms": (sum((t - sum(times) / len(times)) ** 2 for t in times) / len(times)) ** 0.5
        * 1000,
    }


def run_long_document_test(filter_instance: GRMRV3GrammarFilter, doc_path: str) -> dict[str, Any]:
    """Test performance on a long document."""
    print(f"\n  Testing with long document: {Path(doc_path).name}")

    if not os.path.exists(doc_path):
        print("    ⚠ Document not found, skipping")
        return {"skipped": True, "reason": "Document not found"}

    # Read document
    with open(doc_path, encoding="utf-8") as f:
        content = f.read()

    word_count = len(content.split())
    char_count = len(content)

    print(f"    Words: {word_count:,}, Characters: {char_count:,}")

    # Process document (paragraph by paragraph like the real pipeline)
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

    start_time = time.time()
    corrected_paragraphs = []

    for i, para in enumerate(paragraphs):
        if i % 10 == 0:
            print(f"    Processing paragraph {i+1}/{len(paragraphs)}...")
        corrected_paragraphs.append(filter_instance.correct_text(para))

    total_time = time.time() - start_time
    corrected_content = "\n\n".join(corrected_paragraphs)

    # Count changes
    changes = sum(
        1 for orig, corr in zip(paragraphs, corrected_paragraphs, strict=False) if orig != corr
    )

    print(f"    ✓ Completed in {total_time:.2f}s")
    print(f"    Changes: {changes}/{len(paragraphs)} paragraphs")

    return {
        "word_count": word_count,
        "char_count": char_count,
        "paragraph_count": len(paragraphs),
        "paragraphs_changed": changes,
        "total_time_s": total_time,
        "words_per_second": word_count / total_time,
        "output": corrected_content,
    }


def compare_models(q4_path: str, q8_path: str, device: str = None, long_doc_path: str = None):
    """Main comparison function."""
    print("=" * 80)
    print("GRMR-V3 Q4 vs Q8 Model Comparison")
    print("=" * 80)
    print()

    results = {
        "timestamp": datetime.now().isoformat(),
        "device": device if device else "cpu",
        "models": {"q4": {"path": q4_path}, "q8": {"path": q8_path}},
        "tests": {},
    }

    # Test Q4 model
    print("=" * 80)
    print("TESTING Q4 MODEL (4-bit quantization)")
    print("=" * 80)
    print()

    q4_filter, q4_load_time = load_model(q4_path, device)
    results["models"]["q4"]["load_time_s"] = q4_load_time

    print("Running quality tests...")
    q4_quality_results = []
    for test_case in TEST_CASES:
        q4_quality_results.append(run_quality_test(q4_filter, test_case))

    results["models"]["q4"]["quality_tests"] = q4_quality_results
    results["models"]["q4"]["quality_pass_rate"] = sum(
        1 for r in q4_quality_results if r["passed"]
    ) / len(q4_quality_results)

    print("\nRunning consistency test...")
    q4_consistency = run_consistency_test(
        q4_filter, "The dog barks loudly at the mailman every morning."
    )
    results["models"]["q4"]["consistency"] = q4_consistency

    if long_doc_path:
        print("\nRunning long document test...")
        q4_long_doc = run_long_document_test(q4_filter, long_doc_path)
        results["models"]["q4"]["long_document"] = q4_long_doc

    # Clean up Q4 model
    del q4_filter

    print("\n" + "=" * 80)
    print("TESTING Q8 MODEL (8-bit quantization)")
    print("=" * 80)
    print()

    q8_filter, q8_load_time = load_model(q8_path, device)
    results["models"]["q8"]["load_time_s"] = q8_load_time

    print("Running quality tests...")
    q8_quality_results = []
    for test_case in TEST_CASES:
        q8_quality_results.append(run_quality_test(q8_filter, test_case))

    results["models"]["q8"]["quality_tests"] = q8_quality_results
    results["models"]["q8"]["quality_pass_rate"] = sum(
        1 for r in q8_quality_results if r["passed"]
    ) / len(q8_quality_results)

    print("\nRunning consistency test...")
    q8_consistency = run_consistency_test(
        q8_filter, "The dog barks loudly at the mailman every morning."
    )
    results["models"]["q8"]["consistency"] = q8_consistency

    if long_doc_path:
        print("\nRunning long document test...")
        q8_long_doc = run_long_document_test(q8_filter, long_doc_path)
        results["models"]["q8"]["long_document"] = q8_long_doc

    # Clean up Q8 model
    del q8_filter

    # Generate comparison summary
    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    print()

    print("📊 QUALITY COMPARISON:")
    print(f"  Q4 Pass Rate: {results['models']['q4']['quality_pass_rate']:.1%}")
    print(f"  Q8 Pass Rate: {results['models']['q8']['quality_pass_rate']:.1%}")

    q4_passed = sum(1 for r in q4_quality_results if r["passed"])
    q8_passed = sum(1 for r in q8_quality_results if r["passed"])
    print(f"  Q4: {q4_passed}/{len(TEST_CASES)} tests passed")
    print(f"  Q8: {q8_passed}/{len(TEST_CASES)} tests passed")

    if q8_passed > q4_passed:
        print(f"  ✓ Q8 is MORE ACCURATE (+{q8_passed - q4_passed} tests)")
    elif q8_passed < q4_passed:
        print(f"  ✓ Q4 is MORE ACCURATE (+{q4_passed - q8_passed} tests)")
    else:
        print("  = EQUAL ACCURACY")

    print()
    print("⚡ PERFORMANCE COMPARISON:")
    print(f"  Q4 Load Time: {q4_load_time:.2f}s")
    print(f"  Q8 Load Time: {q8_load_time:.2f}s")

    q4_avg_time = sum(r["processing_time_ms"] for r in q4_quality_results) / len(q4_quality_results)
    q8_avg_time = sum(r["processing_time_ms"] for r in q8_quality_results) / len(q8_quality_results)

    print(f"  Q4 Avg Processing: {q4_avg_time:.0f}ms per test")
    print(f"  Q8 Avg Processing: {q8_avg_time:.0f}ms per test")

    if q4_avg_time < q8_avg_time:
        speedup = q8_avg_time / q4_avg_time
        print(f"  ✓ Q4 is FASTER ({speedup:.2f}x speedup)")
    else:
        speedup = q4_avg_time / q8_avg_time
        print(f"  ✓ Q8 is FASTER ({speedup:.2f}x speedup)")

    print()
    print("🔄 CONSISTENCY:")
    print(f"  Q4: {'✓ Consistent' if q4_consistency['consistent'] else '✗ Inconsistent'}")
    print(f"  Q8: {'✓ Consistent' if q8_consistency['consistent'] else '✗ Inconsistent'}")

    if long_doc_path and not q4_long_doc.get("skipped") and not q8_long_doc.get("skipped"):
        print()
        print("📄 LONG DOCUMENT PERFORMANCE:")
        print(
            f"  Q4: {q4_long_doc['total_time_s']:.2f}s ({q4_long_doc['words_per_second']:.0f} words/sec)"
        )
        print(
            f"  Q8: {q8_long_doc['total_time_s']:.2f}s ({q8_long_doc['words_per_second']:.0f} words/sec)"
        )

        if q4_long_doc["total_time_s"] < q8_long_doc["total_time_s"]:
            speedup = q8_long_doc["total_time_s"] / q4_long_doc["total_time_s"]
            print(f"  ✓ Q4 is FASTER ({speedup:.2f}x speedup on long documents)")
        else:
            speedup = q4_long_doc["total_time_s"] / q8_long_doc["total_time_s"]
            print(f"  ✓ Q8 is FASTER ({speedup:.2f}x speedup on long documents)")

    # Save results
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = results_dir / f"q4_vs_q8_comparison_{timestamp}.json"

    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print()
    print(f"📁 Results saved to: {results_file}")
    print()

    # Print recommendation
    print("=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)

    if q8_passed > q4_passed and q8_avg_time < q4_avg_time * 1.5:
        print("✓ Q8 MODEL RECOMMENDED: Better accuracy with acceptable performance")
    elif q8_passed > q4_passed:
        print("⚖ Q8 MODEL RECOMMENDED: Better accuracy, but slower performance")
        print("   Consider Q8 if quality is more important than speed")
    elif q4_avg_time < q8_avg_time * 0.8:
        print("✓ Q4 MODEL RECOMMENDED: Similar accuracy with better performance")
    else:
        print("⚖ MODELS ARE EQUIVALENT: Use Q4 for speed, Q8 for potential quality edge")

    print("=" * 80)

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compare GRMR-V3 Q4 vs Q8 models")
    parser.add_argument("--gpu", action="store_true", help="Use GPU acceleration")
    parser.add_argument(
        "--long-doc", type=str, help="Path to long document for testing", default="corpus/large.md"
    )

    args = parser.parse_args()

    # Model paths
    q4_path = ".GRMR-V3-Q4B-GGUF/GRMR-V3-Q4B.Q4_K_M.gguf"
    q8_path = ".GRMR-V3-Q4B-GGUF/GRMR-V3-Q4B.Q8_0.gguf"

    # Device selection
    device = "cuda" if args.gpu else None

    # Run comparison
    compare_models(q4_path, q8_path, device=device, long_doc_path=args.long_doc)
