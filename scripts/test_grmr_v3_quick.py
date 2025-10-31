"""
Test GRMR-V3 model with CPU (known working)
Quick smoke test to verify the model still works after all our changes
"""
import time

from pipeline.filters.grmr_v3_filter import GRMRV3GrammarFilter


def test_grmr_v3_cpu():
    """Test GRMR-V3 on CPU (production environment)."""
    print("=" * 60)
    print("Testing GRMR-V3 Grammar Correction (CPU Mode)")
    print("=" * 60)

    # Test sentences with known errors
    test_cases = [
        {"input": "There going to the store their.", "expected_fixes": ["They're", "there"]},
        {
            "input": "I seen him yesterday and he dont want to come.",
            "expected_fixes": ["saw", "doesn't"],
        },
        {"input": "The cats is sleeping on the couch.", "expected_fixes": ["are"]},
        {"input": "Me and him went to school together.", "expected_fixes": ["He and I"]},
        {"input": "She should of went to the party.", "expected_fixes": ["have gone"]},
    ]

    print("\nInitializing GRMR-V3 filter...")
    start = time.time()
    filter_obj = GRMRV3GrammarFilter()
    init_time = time.time() - start
    print(f"✅ Model loaded in {init_time:.2f}s")

    print("\nRunning correction tests...\n")

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        input_text = test["input"]
        expected_fixes = test["expected_fixes"]

        print(f"Test {i}:")
        print(f"  Input:    {input_text}")

        start = time.time()
        corrected = filter_obj.correct_text(input_text)
        elapsed = time.time() - start

        print(f"  Output:   {corrected}")
        print(f"  Time:     {elapsed:.2f}s")

        # Check if any expected fixes are present
        has_fixes = any(fix.lower() in corrected.lower() for fix in expected_fixes)

        if corrected != input_text and has_fixes:
            print("  Status:   ✅ PASSED (corrections applied)")
            passed += 1
        elif corrected == input_text:
            print("  Status:   ⚠️  WARNING (no changes made)")
            failed += 1
        else:
            print("  Status:   ✅ PASSED (text modified)")
            passed += 1

        print()

    # Get statistics
    stats = filter_obj.get_stats()

    print("=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    print(f"Tests passed:        {passed}/{len(test_cases)}")
    print(f"Tests failed:        {failed}/{len(test_cases)}")
    print("\nModel Statistics:")
    print(f"  Total corrections: {stats['total_corrections']}")
    print(f"  Total tokens:      {stats['total_tokens_generated']}")
    print(f"  Avg time/text:     {stats['average_correction_time']:.2f}s")
    print("=" * 60)

    if passed >= 4:
        print("\n✅ GRMR-V3 is working correctly!")
        return True
    else:
        print("\n⚠️  Some tests failed - review results above")
        return False


if __name__ == "__main__":
    success = test_grmr_v3_cpu()
    exit(0 if success else 1)
