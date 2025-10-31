#!/usr/bin/env python3
"""
Quick test on first 50 paragraphs of test_long.md to get accurate metrics.
"""

import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pipeline.filters.grmr_v3_filter import GRMRV3GrammarFilter


def split_paragraphs(text):
    """Split into paragraphs."""
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip() and len(p.split()) >= 10]


def main():
    print("=" * 70)
    print("GRMR-V3 SAMPLE TEST (First 50 paragraphs)")
    print("=" * 70)

    # Read document
    with open("tools/test_long.md", encoding="utf-8") as f:
        content = f.read()

    paragraphs = split_paragraphs(content)
    sample_size = min(50, len(paragraphs))
    sample_paragraphs = paragraphs[:sample_size]

    print(f"\nProcessing first {sample_size} paragraphs...")
    print(f"Total words in sample: {sum(len(p.split()) for p in sample_paragraphs):,}")

    # Initialize
    print("\nInitializing...")
    start = time.time()
    filter_obj = GRMRV3GrammarFilter()
    init_time = time.time() - start
    print(f"✓ Initialized in {init_time:.2f}s")

    # Process
    print("\nProcessing...")
    process_start = time.time()
    corrected = []
    corrections_made = 0

    for i, para in enumerate(sample_paragraphs):
        if i % 10 == 0:
            print(f"  {i}/{sample_size}...", end="", flush=True)
        result = filter_obj.correct_text(para)
        corrected.append(result)
        if result != para:
            corrections_made += 1

    process_time = time.time() - process_start
    print(" Done!")

    # Stats
    stats = filter_obj.get_stats()
    words_processed = sum(len(p.split()) for p in sample_paragraphs)

    print(f"\n{'─'*70}")
    print("RESULTS")
    print(f"{'─'*70}")
    print(f"  Paragraphs processed: {sample_size}")
    print(f"  Corrections made: {corrections_made}")
    print(f"  Total time: {process_time:.1f}s ({process_time/60:.1f} min)")
    print(f"  Time per paragraph: {process_time/sample_size:.2f}s")
    print(f"  Words processed: {words_processed:,}")
    print(f"  Processing rate: {words_processed/process_time:.0f} words/sec")
    print(f"  Tokens generated: {stats['total_tokens_generated']}")

    # Character name check
    original_text = "\n\n".join(sample_paragraphs)
    corrected_text = "\n\n".join(corrected)

    print(f"\n{'─'*70}")
    print("CHARACTER PRESERVATION")
    print(f"{'─'*70}")
    for name in ["Irina", "Volin", "Seraphim", "Audra"]:
        orig_count = original_text.count(name)
        corr_count = corrected_text.count(name)
        if orig_count > 0:
            status = "✓" if orig_count == corr_count else "✗"
            print(f"  {status} {name}: {orig_count} → {corr_count}")

    # Scaling estimates
    words_per_min = (words_processed / process_time) * 60
    print(f"\n{'─'*70}")
    print("SCALING ESTIMATES")
    print(f"{'─'*70}")
    print(f"  Processing rate: {words_per_min:.0f} words/minute")

    chapter_words = 3500
    print(f"  Chapter ({chapter_words:,} words): {(chapter_words/words_per_min):.1f} minutes")

    novel_words = 90000
    print(
        f"  Novel ({novel_words:,} words): {(novel_words/words_per_min):.1f} minutes ({(novel_words/words_per_min)/60:.1f} hours)"
    )

    print(f"\n{'═'*70}")
    print("TEST COMPLETE")
    print(f"{'═'*70}")


if __name__ == "__main__":
    main()
