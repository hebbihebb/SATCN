"""
Quick parameter comparison test - CPU only version.
Can run immediately while GPU installation completes.
"""

import time

from pipeline.filters.grmr_v3_filter import GRMRV3GrammarFilter

# Small set of test cases for quick comparison
TEST_CASES = [
    "She dont like the movie.",
    "The dogs was barking loudly.",
    "Xander and Buffy was fighting the vampires in Sunnydale.",
]


def test_config(label, **params):
    """Test with specific parameters."""
    print(f"\n{'='*70}")
    print(f"{label}")
    print(f"Parameters: {params}")
    print(f"{'='*70}")

    filter = GRMRV3GrammarFilter(
        n_gpu_layers=0,  # CPU only for quick test
        verbose=False,
        **params,
    )

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{i}. Input:  {test_case}")
        start = time.time()
        corrected = filter.correct_text(test_case)
        elapsed = time.time() - start
        print(f"   Output: {corrected}")
        print(f"   Time:   {elapsed:.1f}s")

    return filter


print("\n" + "=" * 70)
print("QUICK PARAMETER COMPARISON - CPU MODE")
print("=" * 70)
print("\nComparing old (deterministic) vs new (optimal) parameters...")

# Test with OLD parameters (deterministic)
print("\n" + "=" * 70)
print("PHASE 1: OLD PARAMETERS (temperature=0.1, top_p=0.15)")
print("=" * 70)
old_filter = test_config(
    "OLD PARAMETERS (Deterministic)", temperature=0.1, top_p=0.15, top_k=40, min_p=0.01
)

# Test with NEW parameters (optimal per model card)
print("\n" + "=" * 70)
print("PHASE 2: NEW PARAMETERS (temperature=0.7, top_p=0.95)")
print("=" * 70)
new_filter = test_config(
    "NEW PARAMETERS (Model Card Optimal)", temperature=0.7, top_p=0.95, top_k=40, min_p=0.01
)

print("\n" + "=" * 70)
print("ANALYSIS")
print("=" * 70)
print("\nOld parameters (temp=0.1, top_p=0.15):")
print("  - More deterministic (same input → same output)")
print("  - Narrower sampling (only top 15% of tokens)")
print("  - More conservative corrections")
print("\nNew parameters (temp=0.7, top_p=0.95):")
print("  - More varied (same input → potentially different outputs)")
print("  - Wider sampling (top 95% of tokens)")
print("  - May produce more natural/varied corrections")
print("\nNote: Running on CPU for speed. GPU test will run when installation completes.")
print("=" * 70 + "\n")
