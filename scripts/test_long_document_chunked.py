#!/usr/bin/env python3
"""
Test GRMR-V3 with a long document using chunked processing.

Processes long documents by splitting into paragraph-sized chunks
that fit within the 4096 token context window.
"""

import re
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.filters.grmr_v3_filter import GRMRV3GrammarFilter


def split_into_paragraphs(text):
    """Split text into paragraphs (double newline separated)."""
    # Split on double newlines (paragraph breaks)
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if p.strip()]


def estimate_tokens(text):
    """Rough token estimate (1 token ≈ 4 characters)."""
    return len(text) // 4


def test_long_document_chunked():
    """Test with tools/test_long.md using paragraph-based chunking."""

    print("=" * 70)
    print("GRMR-V3 LONG DOCUMENT TEST (CHUNKED PROCESSING)")
    print("=" * 70)

    # Read the document
    input_file = Path("tools/test_long.md")
    if not input_file.exists():
        print(f"✗ File not found: {input_file}")
        return

    print(f"\nReading: {input_file}")
    with open(input_file, encoding="utf-8") as f:
        content = f.read()

    # Document stats
    file_size = len(content.encode("utf-8"))
    word_count = len(content.split())

    print("✓ Loaded document")
    print(f"  Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"  Words: {word_count:,}")

    # Split into paragraphs
    paragraphs = split_into_paragraphs(content)
    print(f"  Paragraphs: {len(paragraphs)}")

    # Filter out very short paragraphs (likely headers/metadata)
    # Only process paragraphs with at least 10 words
    text_paragraphs = [p for p in paragraphs if len(p.split()) >= 10]
    print(f"  Text paragraphs (10+ words): {len(text_paragraphs)}")

    # Initialize filter
    print("\nInitializing GRMR-V3 filter...")
    init_start = time.time()
    filter_obj = GRMRV3GrammarFilter()
    init_time = time.time() - init_start
    print(f"✓ Filter initialized in {init_time:.2f}s")

    # Process paragraphs
    print(f"\nProcessing {len(text_paragraphs)} text paragraphs...")
    print("Progress: ", end="", flush=True)

    corrected_paragraphs = []
    process_start = time.time()
    paragraphs_corrected = 0

    for i, paragraph in enumerate(text_paragraphs):
        # Show progress every 10 paragraphs
        if i % 10 == 0:
            print(f"{i}...", end="", flush=True)

        # Check token count
        estimated_tokens = estimate_tokens(paragraph)
        if estimated_tokens > 3500:  # Leave room for response
            # Skip very long paragraphs
            print(f"\n  ⚠️  Skipping paragraph {i+1} (too long: ~{estimated_tokens} tokens)")
            corrected_paragraphs.append(paragraph)
            continue

        # Correct the paragraph
        corrected = filter_obj.correct_text(paragraph)
        corrected_paragraphs.append(corrected)

        if corrected != paragraph:
            paragraphs_corrected += 1

    process_time = time.time() - process_start
    print(" Done!")

    # Reconstruct document (keep original structure, replace text paragraphs)
    # For simplicity, just join corrected paragraphs
    corrected_content = "\n\n".join(corrected_paragraphs)

    print(f"\n✓ Processing complete in {process_time:.2f}s ({process_time/60:.1f} minutes)")

    # Calculate performance metrics
    time_per_paragraph = process_time / len(text_paragraphs)
    words_in_text = sum(len(p.split()) for p in text_paragraphs)
    time_per_word = process_time / words_in_text if words_in_text > 0 else 0

    print(f"\n{'─' * 70}")
    print("PERFORMANCE METRICS")
    print(f"{'─' * 70}")
    print(f"  Total time: {process_time:.2f}s ({process_time/60:.1f} minutes)")
    print(f"  Paragraphs processed: {len(text_paragraphs)}")
    print(f"  Paragraphs corrected: {paragraphs_corrected}")
    print(f"  Time per paragraph: {time_per_paragraph:.2f}s")
    print(f"  Time per word: {time_per_word*1000:.1f}ms")
    print(f"  Words per second: {words_in_text/process_time:.1f}")

    # Get filter statistics
    stats = filter_obj.get_stats()
    print(f"\n  Tokens generated: {stats['total_tokens_generated']}")
    print(f"  Model duration: {stats['total_duration_ms']/1000:.2f}s")

    # Save output
    output_file = Path("tools/test_long_corrected.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(corrected_content)

    print(f"\n✓ Output saved to: {output_file}")

    # Character name preservation check
    print(f"\n{'─' * 70}")
    print("CHARACTER NAME PRESERVATION CHECK")
    print(f"{'─' * 70}")

    names_to_check = ["Irina", "Volin", "Seraphim", "Audra"]
    print(f"Checking: {', '.join(names_to_check)}")

    all_preserved = True
    for name in names_to_check:
        count_original = content.count(name)
        count_corrected = corrected_content.count(name)

        if count_original > 0:
            preserved = count_original == count_corrected
            status = "✓" if preserved else "✗"
            print(f"  {status} '{name}': {count_original} → {count_corrected}")
            if not preserved:
                all_preserved = False

    if all_preserved:
        print("\n✓ All character names preserved perfectly!")
    else:
        print("\n⚠️  Some character names were changed")

    # Scaling estimates
    print(f"\n{'─' * 70}")
    print("SCALING ESTIMATES (for similar content)")
    print(f"{'─' * 70}")

    # Based on actual performance
    words_per_minute = (words_in_text / process_time) * 60

    # Typical documents
    chapter_words = 3500
    chapter_time = (chapter_words / words_per_minute) * 60
    print(f"  Typical chapter ({chapter_words:,} words): ~{chapter_time/60:.1f} minutes")

    novel_words = 90000
    novel_time = (novel_words / words_per_minute) * 60
    print(
        f"  Full novel ({novel_words:,} words): ~{novel_time/60:.1f} minutes ({novel_time/3600:.1f} hours)"
    )

    story_words = 5000
    story_time = (story_words / words_per_minute) * 60
    print(f"  Short story ({story_words:,} words): ~{story_time/60:.1f} minutes")

    print(f"\n  Processing rate: ~{words_per_minute:.0f} words/minute")

    # Show sample corrections
    if paragraphs_corrected > 0:
        print(f"\n{'─' * 70}")
        print(f"CORRECTIONS MADE: {paragraphs_corrected} paragraphs")
        print(f"{'─' * 70}")

        # Find first corrected paragraph
        for i, (orig, corr) in enumerate(zip(text_paragraphs, corrected_paragraphs, strict=False)):
            if orig != corr:
                print(f"\nExample correction (paragraph {i+1}):")
                print(f"Original:  {orig[:200]}...")
                print(f"Corrected: {corr[:200]}...")
                break

    print(f"\n{'═' * 70}")
    print("TEST COMPLETE")
    print(f"{'═' * 70}")


if __name__ == "__main__":
    test_long_document_chunked()
