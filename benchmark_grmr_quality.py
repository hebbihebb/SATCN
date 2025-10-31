#!/usr/bin/env python3
"""
Comprehensive quality benchmark for GRMR-V3 grammar correction.

Tests model performance on:
- Grammar errors (subject-verb agreement, tense, etc.)
- Spelling errors
- Punctuation errors
- Character name preservation
- Contextual corrections
- Edge cases

Usage:
    python benchmark_grmr_quality.py [--output report.md]
"""

import argparse
import time
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, field

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class TestCase:
    """A single test case with input, expected correction categories."""
    input_text: str
    expected_corrections: List[str]  # What should be fixed
    preserve_elements: List[str] = field(default_factory=list)  # What should NOT change
    category: str = "general"
    
    
# Comprehensive test corpus
TEST_CORPUS = [
    # Grammar: Subject-verb agreement
    TestCase(
        "She run to the store every day.",
        ["subject-verb agreement"],
        category="grammar:sv-agreement"
    ),
    TestCase(
        "The dogs was barking loudly.",
        ["subject-verb agreement"],
        category="grammar:sv-agreement"
    ),
    TestCase(
        "He don't like vegetables.",
        ["subject-verb agreement"],
        category="grammar:sv-agreement"
    ),
    
    # Grammar: Tense consistency
    TestCase(
        "Yesterday I go to the market.",
        ["tense"],
        category="grammar:tense"
    ),
    TestCase(
        "She will went to the party tomorrow.",
        ["tense"],
        category="grammar:tense"
    ),
    
    # Grammar: Common errors
    TestCase(
        "Their going too fast.",
        ["they're vs their"],
        category="grammar:homophones"
    ),
    TestCase(
        "Its a beautiful day.",
        ["it's vs its"],
        category="grammar:homophones"
    ),
    TestCase(
        "Your going to love this.",
        ["you're vs your"],
        category="grammar:homophones"
    ),
    
    # Spelling errors
    TestCase(
        "Thiss sentnce have two speling errrors.",
        ["spelling"],
        category="spelling"
    ),
    TestCase(
        "I recieved the package yesteday.",
        ["spelling"],
        category="spelling"
    ),
    TestCase(
        "The resturant has excellant food.",
        ["spelling"],
        category="spelling"
    ),
    
    # Common word confusions
    TestCase(
        "The crew was suppose to arrive yesterday.",
        ["supposed to"],
        category="grammar:common-errors"
    ),
    TestCase(
        "I could of done better.",
        ["could have"],
        category="grammar:common-errors"
    ),
    TestCase(
        "She should of known better.",
        ["should have"],
        category="grammar:common-errors"
    ),
    
    # Character name preservation (critical for fiction)
    TestCase(
        "Irina said she dont wanna go to the market.",
        ["grammar"],
        preserve_elements=["Irina"],
        category="character-names"
    ),
    TestCase(
        "Kael has went to the mountains.",
        ["tense"],
        preserve_elements=["Kael"],
        category="character-names"
    ),
    TestCase(
        "Zara and Thorne was walking together.",
        ["subject-verb agreement"],
        preserve_elements=["Zara", "Thorne"],
        category="character-names"
    ),
    
    # Multiple errors in one sentence
    TestCase(
        "Me and him went too the store and buyed some milk.",
        ["pronoun", "homophone", "tense"],
        category="multiple-errors"
    ),
    TestCase(
        "She dont never want too go their anymore.",
        ["double negative", "grammar", "homophone"],
        category="multiple-errors"
    ),
    
    # Punctuation
    TestCase(
        "Where are you going",
        ["missing punctuation"],
        category="punctuation"
    ),
    TestCase(
        "Hello how are you doing today",
        ["missing punctuation"],
        category="punctuation"
    ),
    
    # Contextual corrections
    TestCase(
        "The woman which I met was nice.",
        ["who vs which"],
        category="grammar:relative-pronouns"
    ),
    TestCase(
        "The car who I bought is red.",
        ["which vs who"],
        category="grammar:relative-pronouns"
    ),
    
    # Articles
    TestCase(
        "I saw a elephant at the zoo.",
        ["a vs an"],
        category="grammar:articles"
    ),
    TestCase(
        "She is an honest woman.",
        [],  # Already correct
        category="grammar:articles"
    ),
    
    # Already correct sentences (should be unchanged)
    TestCase(
        "The quick brown fox jumps over the lazy dog.",
        [],  # No corrections needed
        category="correct-baseline"
    ),
    TestCase(
        "She walked carefully down the stairs.",
        [],  # No corrections needed
        category="correct-baseline"
    ),
    TestCase(
        "The children played happily in the park.",
        [],  # No corrections needed
        category="correct-baseline"
    ),
    
    # Slang and informal language (should preserve intent)
    TestCase(
        "I dont wanna go there.",
        ["grammar"],
        preserve_elements=["wanna"],  # Slang should be preserved
        category="slang-preservation"
    ),
    TestCase(
        "Shes gonna arrive soon.",
        ["grammar"],
        preserve_elements=["gonna"],  # Slang should be preserved
        category="slang-preservation"
    ),
    
    # Complex sentences
    TestCase(
        "The manager, who I met yesterday, said that the project which we was working on need more time.",
        ["subject-verb agreement"],
        category="complex"
    ),
]


def analyze_correction(
    original: str,
    corrected: str,
    expected_corrections: List[str],
    preserve_elements: List[str]
) -> Dict:
    """
    Analyze the quality of a correction.
    
    Returns:
        Dict with analysis results
    """
    analysis = {
        'changed': original != corrected,
        'preserved_elements': True,
        'likely_correct': None,  # None, True, or False
        'notes': []
    }
    
    # Check if elements that should be preserved are still there
    for element in preserve_elements:
        if element in original and element not in corrected:
            analysis['preserved_elements'] = False
            analysis['notes'].append(f"Lost preserved element: '{element}'")
    
    # If it changed and was supposed to, that's good
    if analysis['changed'] and expected_corrections:
        analysis['likely_correct'] = True
        analysis['notes'].append("Made correction as expected")
    
    # If it didn't change and wasn't supposed to, that's good
    elif not analysis['changed'] and not expected_corrections:
        analysis['likely_correct'] = True
        analysis['notes'].append("Correctly left unchanged")
    
    # If it changed but wasn't supposed to (over-correction)
    elif analysis['changed'] and not expected_corrections:
        analysis['likely_correct'] = False
        analysis['notes'].append("Over-correction: changed already-correct text")
    
    # If it didn't change but should have (under-correction)
    elif not analysis['changed'] and expected_corrections:
        analysis['likely_correct'] = False
        analysis['notes'].append(f"Under-correction: missed {', '.join(expected_corrections)}")
    
    return analysis


def run_benchmark(verbose: bool = True) -> Dict:
    """
    Run comprehensive GRMR-V3 quality benchmark.
    
    Args:
        verbose: Print detailed results
        
    Returns:
        Dict with benchmark results
    """
    from pipeline.filters.grmr_v3_filter import GRMRV3GrammarFilter
    
    if verbose:
        print("=" * 70)
        print("GRMR-V3 COMPREHENSIVE QUALITY BENCHMARK")
        print("=" * 70)
    
    # Initialize model
    if verbose:
        print("\nInitializing model...")
    start_time = time.time()
    filter_obj = GRMRV3GrammarFilter()
    init_time = time.time() - start_time
    if verbose:
        print(f"✓ Model loaded in {init_time:.2f}s\n")
    
    # Run all test cases
    results = []
    category_stats = {}
    
    for i, test_case in enumerate(TEST_CORPUS, 1):
        if verbose:
            print(f"[{i}/{len(TEST_CORPUS)}] Testing: {test_case.category}")
            print(f"  Input:  {test_case.input_text}")
        
        # Run correction
        start = time.time()
        corrected = filter_obj.correct_text(test_case.input_text)
        duration = time.time() - start
        
        # Analyze
        analysis = analyze_correction(
            test_case.input_text,
            corrected,
            test_case.expected_corrections,
            test_case.preserve_elements
        )
        
        result = {
            'test_case': test_case,
            'corrected': corrected,
            'duration': duration,
            'analysis': analysis
        }
        results.append(result)
        
        # Update category stats
        if test_case.category not in category_stats:
            category_stats[test_case.category] = {
                'total': 0,
                'correct': 0,
                'changed': 0,
                'preserved': 0
            }
        
        category_stats[test_case.category]['total'] += 1
        if analysis['likely_correct']:
            category_stats[test_case.category]['correct'] += 1
        if analysis['changed']:
            category_stats[test_case.category]['changed'] += 1
        if analysis['preserved_elements']:
            category_stats[test_case.category]['preserved'] += 1
        
        if verbose:
            print(f"  Output: {corrected}")
            if analysis['changed']:
                print(f"  ✓ Changed" if analysis['likely_correct'] else f"  ⚠️  Changed (unexpected)")
            else:
                print(f"  ✓ Unchanged" if analysis['likely_correct'] else f"  ⚠️  Unchanged (should have corrected)")
            if not analysis['preserved_elements']:
                print(f"  ✗ FAILED TO PRESERVE ELEMENTS")
            print(f"  Time: {duration:.2f}s\n")
    
    # Calculate overall statistics
    total_tests = len(results)
    correct_count = sum(1 for r in results if r['analysis']['likely_correct'])
    changed_count = sum(1 for r in results if r['analysis']['changed'])
    preservation_failures = sum(1 for r in results if not r['analysis']['preserved_elements'])
    
    total_time = sum(r['duration'] for r in results)
    avg_time = total_time / total_tests
    
    model_stats = filter_obj.get_stats()
    
    summary = {
        'init_time': init_time,
        'total_tests': total_tests,
        'correct_count': correct_count,
        'accuracy': correct_count / total_tests,
        'changed_count': changed_count,
        'preservation_failures': preservation_failures,
        'total_time': total_time,
        'avg_time': avg_time,
        'model_stats': model_stats,
        'category_stats': category_stats,
        'results': results
    }
    
    return summary


def print_summary(summary: Dict):
    """Print benchmark summary."""
    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    
    print(f"\n📊 Overall Statistics:")
    print(f"  Total test cases: {summary['total_tests']}")
    print(f"  Correct behavior: {summary['correct_count']}/{summary['total_tests']} ({summary['accuracy']*100:.1f}%)")
    print(f"  Changes made: {summary['changed_count']}")
    print(f"  Preservation failures: {summary['preservation_failures']}")
    
    print(f"\n⏱️  Performance:")
    print(f"  Model initialization: {summary['init_time']:.2f}s")
    print(f"  Total inference time: {summary['total_time']:.2f}s")
    print(f"  Average per test: {summary['avg_time']:.2f}s")
    print(f"  Tokens generated: {summary['model_stats']['total_tokens_generated']}")
    
    print(f"\n📈 Performance by Category:")
    for category, stats in sorted(summary['category_stats'].items()):
        accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  {category:30s}: {stats['correct']}/{stats['total']} ({accuracy:.0f}%)")
    
    # Highlight any failures
    failures = [r for r in summary['results'] if not r['analysis']['likely_correct']]
    if failures:
        print(f"\n⚠️  Issues Found ({len(failures)} cases):")
        for result in failures[:5]:  # Show first 5
            tc = result['test_case']
            print(f"\n  Category: {tc.category}")
            print(f"  Input:    {tc.input_text}")
            print(f"  Output:   {result['corrected']}")
            print(f"  Issue:    {', '.join(result['analysis']['notes'])}")
        
        if len(failures) > 5:
            print(f"\n  ... and {len(failures) - 5} more issues")
    else:
        print(f"\n✅ No issues found! All tests passed.")


def save_report(summary: Dict, output_path: str):
    """Save detailed report to markdown file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# GRMR-V3 Quality Benchmark Report\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- **Total tests:** {summary['total_tests']}\n")
        f.write(f"- **Accuracy:** {summary['accuracy']*100:.1f}%\n")
        f.write(f"- **Preservation failures:** {summary['preservation_failures']}\n")
        f.write(f"- **Average time:** {summary['avg_time']:.2f}s per test\n\n")
        
        f.write("## Performance by Category\n\n")
        f.write("| Category | Correct | Total | Accuracy |\n")
        f.write("|----------|---------|-------|----------|\n")
        for category, stats in sorted(summary['category_stats'].items()):
            accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            f.write(f"| {category} | {stats['correct']} | {stats['total']} | {accuracy:.0f}% |\n")
        
        f.write("\n## Detailed Results\n\n")
        for i, result in enumerate(summary['results'], 1):
            tc = result['test_case']
            analysis = result['analysis']
            
            status = "✅" if analysis['likely_correct'] else "⚠️"
            f.write(f"### {i}. {status} {tc.category}\n\n")
            f.write(f"**Input:** {tc.input_text}\n\n")
            f.write(f"**Output:** {result['corrected']}\n\n")
            f.write(f"**Changed:** {'Yes' if analysis['changed'] else 'No'}\n\n")
            f.write(f"**Preserved elements:** {'Yes' if analysis['preserved_elements'] else 'No'}\n\n")
            if analysis['notes']:
                f.write(f"**Notes:** {', '.join(analysis['notes'])}\n\n")
            f.write(f"**Duration:** {result['duration']:.2f}s\n\n")
            f.write("---\n\n")
    
    print(f"\n💾 Detailed report saved to: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive quality benchmark for GRMR-V3"
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Save detailed report to markdown file',
        default=None
    )
    parser.add_argument(
        '--quiet',
        '-q',
        action='store_true',
        help='Only print summary'
    )
    
    args = parser.parse_args()
    
    try:
        summary = run_benchmark(verbose=not args.quiet)
        print_summary(summary)
        
        if args.output:
            save_report(summary, args.output)
    
    except ImportError as e:
        print(f"✗ Error: {e}")
        print("Install dependencies with: pip install -r requirements-grmr.txt")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
