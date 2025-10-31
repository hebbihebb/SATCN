"""
Test script to reproduce and debug markdown formatting issues with GRMR-V3.

Issue: Bold/italic markdown (***text***) sometimes gets duplicated in output.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.filters.grmr_v3_filter import GRMRV3GrammarFilter


def test_markdown_patterns():
    """Test various markdown patterns to see which ones get duplicated."""
    
    print("Initializing GRMR-V3 filter...")
    filter_obj = GRMRV3GrammarFilter()
    
    test_cases = [
        # Bold/Italic combinations
        "This is ***bold and italic*** text.",
        "The word ***important*** should not be duplicated.",
        "Multiple ***first*** and ***second*** instances.",
        
        # Just bold
        "This is **bold** text.",
        "The word **important** should stay bold.",
        
        # Just italic
        "This is *italic* text.",
        "The word *emphasis* should stay italic.",
        
        # Mixed formatting in sentence
        "She said, ***'Wait!'*** and ran **quickly** down the *path*.",
        
        # Inline code
        "The function `correct_text()` is called here.",
        
        # Multiple markdown patterns
        "***Bold italic*** followed by **just bold** and *just italic*.",
        
        # Edge case: nested
        "Text with ***nested **bold** inside*** markdown.",
    ]
    
    print("\n" + "="*70)
    print("MARKDOWN FORMATTING TEST RESULTS")
    print("="*70)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}]")
        print(f"Input:  {test}")
        
        result = filter_obj.correct_text(test)
        
        print(f"Output: {result}")
        
        # Check for duplication markers
        if "******" in result or "****" in result:
            print("⚠️  ISSUE DETECTED: Markdown duplication found!")
        elif test != result and ("***" in test):
            print("ℹ️  Markdown content changed")
        else:
            print("✓ OK")
    
    print("\n" + "="*70)
    print("STATISTICS")
    print("="*70)
    stats = filter_obj.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == '__main__':
    test_markdown_patterns()
