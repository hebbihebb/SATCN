"""Show actual output differences between Q4 and Q8 models."""
import json
import sys
from pathlib import Path

# Find the latest results file
results_dir = Path("results")
result_files = sorted(results_dir.glob("q4_vs_q8_comparison_*.json"), reverse=True)

if not result_files:
    print("No comparison results found!")
    sys.exit(1)

results_file = result_files[0]
print(f"Reading: {results_file.name}\n")

with open(results_file) as f:
    data = json.load(f)

print("=" * 80)
print("Q4 vs Q8 MODEL OUTPUT COMPARISON")
print("=" * 80)

q4_tests = {t["name"]: t for t in data["models"]["q4"]["quality_tests"]}
q8_tests = {t["name"]: t for t in data["models"]["q8"]["quality_tests"]}

# First, show tests where outputs differ
print("\n### TESTS WITH DIFFERENT OUTPUTS ###\n")
different_count = 0

for test_name in sorted(q4_tests.keys()):
    q4 = q4_tests[test_name]
    q8 = q8_tests[test_name]

    if q4["output"] != q8["output"]:
        different_count += 1
        print(f"\n{different_count}. {test_name}")
        print(f"   Input:     {q4['input']}")
        print(f"   Q4 Output: {q4['output']} [{('PASS' if q4['passed'] else 'FAIL')}]")
        print(f"   Q8 Output: {q8['output']} [{('PASS' if q8['passed'] else 'FAIL')}]")

        if q4["passed"] != q8["passed"]:
            if q8["passed"]:
                print("   >>> Q8 FIXED THIS, Q4 FAILED <<<")
            else:
                print("   >>> Q4 FIXED THIS, Q8 FAILED <<<")

print(f"\n{different_count} tests produced different outputs")

# Show tests where pass/fail differs but output is same
print("\n\n### TESTS WITH SAME OUTPUT BUT DIFFERENT PASS/FAIL ###\n")
same_output_count = 0

for test_name in sorted(q4_tests.keys()):
    q4 = q4_tests[test_name]
    q8 = q8_tests[test_name]

    if q4["output"] == q8["output"] and q4["passed"] != q8["passed"]:
        same_output_count += 1
        print(f"\n{test_name}")
        print(f"   Input:  {q4['input']}")
        print(f"   Output: {q4['output']}")
        print(
            f"   Q4: {('PASS' if q4['passed'] else 'FAIL')}, Q8: {('PASS' if q8['passed'] else 'FAIL')}"
        )

if same_output_count == 0:
    print("(None)")

# Summary
print("\n\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

q4_passed = sum(1 for t in q4_tests.values() if t["passed"])
q8_passed = sum(1 for t in q8_tests.values() if t["passed"])
total = len(q4_tests)

print(f"\nQ4 Pass Rate: {q4_passed/total*100:.1f}% ({q4_passed}/{total})")
print(f"Q8 Pass Rate: {q8_passed/total*100:.1f}% ({q8_passed}/{total})")
print(f"\nTests with different outputs: {different_count}")
print(f"Tests with same output but different scoring: {same_output_count}")

# Long document comparison
if "long_document" in data["models"]["q4"] and "long_document" in data["models"]["q8"]:
    print("\n\n" + "=" * 80)
    print("LONG DOCUMENT TEST (952 words)")
    print("=" * 80)
    q4_long = data["models"]["q4"]["long_document"]
    q8_long = data["models"]["q8"]["long_document"]
    print(
        f"\nQ4 Time: {q4_long['total_time_s']:.2f}s ({q4_long['words_per_second']:.1f} words/sec)"
    )
    print(f"Q8 Time: {q8_long['total_time_s']:.2f}s ({q8_long['words_per_second']:.1f} words/sec)")
    print(f"\nQ4 Changes: {q4_long['paragraphs_changed']}/{q4_long['paragraph_count']} paragraphs")
    print(f"Q8 Changes: {q8_long['paragraphs_changed']}/{q8_long['paragraph_count']} paragraphs")
