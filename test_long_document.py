#!/usr/bin/env python3
"""
Test GRMR-V3 with a long document to measure real-world performance.

Tests:
- Processing speed on full document
- Memory usage
- Correction quality on longer context
- Character name preservation throughout
"""

import sys
import time
import traceback
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.filters.grmr_v3_filter import GRMRV3GrammarFilter


def count_words(text):
    """Count words in text."""
    return len(text.split())


def count_sentences(text):
    """Rough estimate of sentences."""
    import re
    # Simple sentence count - periods, question marks, exclamation marks
    sentences = re.split(r'[.!?]+', text)
    return len([s for s in sentences if s.strip()])


def test_long_document():
    """Test with tools/test_long.md"""
    
    print("=" * 70)
    print("GRMR-V3 LONG DOCUMENT TEST")
    print("=" * 70)
    
    # Read the document
    input_file = Path("tools/test_long.md")
    if not input_file.exists():
        print(f"✗ File not found: {input_file}")
        return
    
    print(f"\nReading: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Document stats
    file_size = len(content.encode('utf-8'))
    line_count = content.count('\n') + 1
    word_count = count_words(content)
    sentence_count = count_sentences(content)
    
    print(f"✓ Loaded document")
    print(f"  Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"  Lines: {line_count:,}")
    print(f"  Words: {word_count:,}")
    print(f"  Sentences (est): {sentence_count:,}")
    
    # Initialize filter
    print(f"\nInitializing GRMR-V3 filter...")
    init_start = time.time()
    try:
        filter_obj = GRMRV3GrammarFilter()
        init_time = time.time() - init_start
        print(f"✓ Filter initialized in {init_time:.2f}s")
    except Exception as e:
        print(f"✗ Failed to initialize filter: {e}")
        traceback.print_exc()
        return
    
    # Process the document
    # For very long documents, we'll process in chunks to avoid context window issues
    print(f"\nProcessing document...")
    print(f"Note: Processing full text as-is (may include markdown metadata)")
    
    process_start = time.time()
    
    try:
        # Process the entire document
        corrected = filter_obj.correct_text(content)
        
        process_time = time.time() - process_start
        
        print(f"✓ Processing complete in {process_time:.2f}s")
        
        # Calculate performance metrics
        time_per_word = process_time / word_count if word_count > 0 else 0
        time_per_sentence = process_time / sentence_count if sentence_count > 0 else 0
        
        print(f"\n{'─' * 70}")
        print("PERFORMANCE METRICS")
        print(f"{'─' * 70}")
        print(f"  Total time: {process_time:.2f}s ({process_time/60:.1f} minutes)")
        print(f"  Time per word: {time_per_word*1000:.1f}ms")
        print(f"  Time per sentence: {time_per_sentence:.3f}s")
        print(f"  Words per second: {word_count/process_time:.1f}")
        
        # Get filter statistics
        stats = filter_obj.get_stats()
        print(f"\n  Tokens generated: {stats['total_tokens_generated']}")
        print(f"  Model duration: {stats['total_duration_ms']/1000:.2f}s")
        
        # Check for changes
        changes_made = content != corrected
        if changes_made:
            # Calculate rough change percentage
            diff_chars = sum(1 for a, b in zip(content, corrected) if a != b)
            change_pct = (diff_chars / len(content)) * 100 if len(content) > 0 else 0
            print(f"\n  Changes made: Yes (~{change_pct:.2f}% of characters)")
        else:
            print(f"\n  Changes made: No (document already perfect)")
        
        # Save output
        output_file = Path("tools/test_long_corrected.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(corrected)
        
        print(f"\n✓ Output saved to: {output_file}")
        
        # Character name preservation check
        print(f"\n{'─' * 70}")
        print("CHARACTER NAME PRESERVATION CHECK")
        print(f"{'─' * 70}")
        
        # Look for character names in the original
        names_to_check = ['Irina', 'Volin', 'Seraphim', 'Audra']
        print(f"Checking preservation of: {', '.join(names_to_check)}")
        
        all_preserved = True
        for name in names_to_check:
            count_original = content.count(name)
            count_corrected = corrected.count(name)
            
            if count_original > 0:
                preserved = count_original == count_corrected
                status = "✓" if preserved else "✗"
                print(f"  {status} '{name}': {count_original} → {count_corrected}")
                if not preserved:
                    all_preserved = False
        
        if all_preserved:
            print(f"\n✓ All character names preserved perfectly!")
        else:
            print(f"\n⚠️  Some character names were changed")
        
        # Show a sample correction (first few paragraphs)
        print(f"\n{'─' * 70}")
        print("SAMPLE OUTPUT (first 500 characters)")
        print(f"{'─' * 70}")
        print(corrected[:500] + "...")
        
        # Estimate cost for larger documents
        print(f"\n{'─' * 70}")
        print("SCALING ESTIMATES")
        print(f"{'─' * 70}")
        
        # Novel chapter (typical: 3000-5000 words)
        chapter_words = 3500
        chapter_time = chapter_words * time_per_word
        print(f"  Typical chapter ({chapter_words:,} words): ~{chapter_time/60:.1f} minutes")
        
        # Full novel (typical: 80,000-100,000 words)
        novel_words = 90000
        novel_time = novel_words * time_per_word
        print(f"  Full novel ({novel_words:,} words): ~{novel_time/60:.1f} minutes ({novel_time/3600:.1f} hours)")
        
        # Short story
        story_words = 5000
        story_time = story_words * time_per_word
        print(f"  Short story ({story_words:,} words): ~{story_time/60:.1f} minutes")
        
    except Exception as e:
        print(f"\n✗ Processing failed: {e}")
        traceback.print_exc()
        return
    
    print(f"\n{'═' * 70}")
    print("TEST COMPLETE")
    print(f"{'═' * 70}")


if __name__ == '__main__':
    test_long_document()
