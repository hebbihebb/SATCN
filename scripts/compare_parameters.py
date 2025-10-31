"""
Compare GRMR-V3 output quality with old vs new parameters.
Tests both deterministic (temp=0.1) and optimal (temp=0.7) settings.
"""

import time

from pipeline.filters.grmr_v3_filter import GRMRV3GrammarFilter

# Test cases covering different grammar issues
TEST_CASES = [
    # Case 1: Basic grammar
    "She dont like the movie.",
    # Case 2: Subject-verb agreement
    "The dogs was barking loudly.",
    # Case 3: Complex sentence
    "Me and him went to the store yesterday and we buyed some milk.",
    # Case 4: Punctuation and capitalization
    "what time is it i need to know",
    # Case 5: Character name preservation
    "Xander and Buffy was fighting the vampires in Sunnydale.",
    # Case 6: Long sentence with multiple errors
    "The scientific community have been researching this phenomena for many years but they hasnt found no conclusive evidence yet.",
    # Case 7: Contextual correction
    "Their going too the store to buy there groceries.",
]


def test_with_parameters(temperature: float, top_p: float, top_k: int, min_p: float, label: str):
    """Test GRMR-V3 with specific parameters."""
    print(f"\n{'='*80}")
    print(f"Testing: {label}")
    print(f"Parameters: temperature={temperature}, top_p={top_p}, top_k={top_k}, min_p={min_p}")
    print(f"{'='*80}\n")

    # Initialize filter with specific parameters
    filter = GRMRV3GrammarFilter(
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        min_p=min_p,
        device="cuda",  # Use GPU
    )

    results = []
    total_time = 0

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\nTest {i}:")
        print(f"Input:  {test_case}")

        start = time.time()
        corrected = filter.correct_text(test_case)
        elapsed = time.time() - start
        total_time += elapsed

        print(f"Output: {corrected}")
        print(f"Time:   {elapsed:.2f}s")

        results.append({"input": test_case, "output": corrected, "time": elapsed})

    avg_time = total_time / len(TEST_CASES)
    print(f"\n{'='*80}")
    print(f"Average time per correction: {avg_time:.2f}s")
    print(f"Total time: {total_time:.2f}s")
    print(f"{'='*80}\n")

    return results


def compare_results(old_results, new_results):
    """Compare outputs between old and new parameters."""
    print(f"\n{'='*80}")
    print("COMPARISON ANALYSIS")
    print(f"{'='*80}\n")

    differences = 0
    character_preservation_old = 0
    character_preservation_new = 0

    for i, (old, new) in enumerate(zip(old_results, new_results, strict=False), 1):
        print(f"\nTest {i}:")
        print(f"Input:     {old['input']}")
        print(f"Old (0.1): {old['output']}")
        print(f"New (0.7): {new['output']}")

        if old["output"] != new["output"]:
            differences += 1
            print("  ⚠️  DIFFERENT")
        else:
            print("  ✓ IDENTICAL")

        # Check character name preservation (Test 5: Xander, Buffy, Sunnydale)
        if i == 5:
            old_preserved = all(name in old["output"] for name in ["Xander", "Buffy", "Sunnydale"])
            new_preserved = all(name in new["output"] for name in ["Xander", "Buffy", "Sunnydale"])
            character_preservation_old = 1 if old_preserved else 0
            character_preservation_new = 1 if new_preserved else 0

            if old_preserved:
                print("  ✓ Old: Character names preserved")
            else:
                print("  ✗ Old: Character names NOT preserved")

            if new_preserved:
                print("  ✓ New: Character names preserved")
            else:
                print("  ✗ New: Character names NOT preserved")

    # Summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total test cases: {len(TEST_CASES)}")
    print(
        f"Different outputs: {differences}/{len(TEST_CASES)} ({differences/len(TEST_CASES)*100:.1f}%)"
    )
    print(
        f"Identical outputs: {len(TEST_CASES)-differences}/{len(TEST_CASES)} ({(len(TEST_CASES)-differences)/len(TEST_CASES)*100:.1f}%)"
    )
    print("\nCharacter preservation:")
    print(f"  Old parameters: {'✓ PASS' if character_preservation_old else '✗ FAIL'}")
    print(f"  New parameters: {'✓ PASS' if character_preservation_new else '✗ FAIL'}")

    # Performance comparison
    old_avg = sum(r["time"] for r in old_results) / len(old_results)
    new_avg = sum(r["time"] for r in new_results) / len(new_results)
    print("\nAverage correction time:")
    print(f"  Old parameters: {old_avg:.2f}s")
    print(f"  New parameters: {new_avg:.2f}s")
    print(
        f"  Difference: {abs(new_avg - old_avg):.2f}s ({((new_avg - old_avg) / old_avg * 100):+.1f}%)"
    )
    print(f"{'='*80}\n")


def main():
    print("\n" + "=" * 80)
    print("GRMR-V3 PARAMETER COMPARISON TEST")
    print("=" * 80)
    print("\nThis test compares GRMR-V3 output quality with:")
    print("  Old: temperature=0.1, top_p=0.15 (deterministic)")
    print("  New: temperature=0.7, top_p=0.95 (optimal, per model card)")
    print("\nBoth configurations use:")
    print("  top_k=40, min_p=0.01")
    print("  GPU acceleration (35/37 layers)")
    print("\n" + "=" * 80)

    # Test with old parameters (deterministic)
    old_results = test_with_parameters(
        temperature=0.1, top_p=0.15, top_k=40, min_p=0.01, label="OLD PARAMETERS (Deterministic)"
    )

    # Test with new parameters (optimal)
    new_results = test_with_parameters(
        temperature=0.7, top_p=0.95, top_k=40, min_p=0.01, label="NEW PARAMETERS (Optimal)"
    )

    # Compare results
    compare_results(old_results, new_results)

    print("\n✓ Comparison complete!")
    print("\nNext steps:")
    print("1. Review outputs for quality differences")
    print("2. Verify character name preservation")
    print("3. Check if new parameters maintain Grade A quality")
    print("4. Decide whether to commit parameter updates\n")


if __name__ == "__main__":
    main()
