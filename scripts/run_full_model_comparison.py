"""
Run complete Q4 vs Q8 comparison on both CPU and GPU.

This script orchestrates running the comparison tests on both CPU and GPU,
then generates a combined report showing the impact of GPU acceleration
on both models.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_comparison(use_gpu: bool, long_doc: str = "corpus/large.md"):
    """Run the comparison test with specified device."""
    device_name = "GPU" if use_gpu else "CPU"
    print(f"\n{'='*80}")
    print(f"Running Q4 vs Q8 comparison on {device_name}")
    print(f"{'='*80}\n")

    cmd = ["python", "scripts/compare_q4_vs_q8.py", "--long-doc", long_doc]
    if use_gpu:
        cmd.append("--gpu")

    try:
        subprocess.run(cmd, check=True, capture_output=False, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {device_name} test failed with exit code {e.returncode}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️  {device_name} test interrupted by user")
        return False


def find_latest_results():
    """Find the two most recent result files."""
    results_dir = Path("results")
    if not results_dir.exists():
        return None, None

    result_files = sorted(
        results_dir.glob("q4_vs_q8_comparison_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if len(result_files) >= 2:
        return result_files[0], result_files[1]
    elif len(result_files) == 1:
        return result_files[0], None
    else:
        return None, None


def generate_combined_report(cpu_file: Path, gpu_file: Path):
    """Generate a combined CPU vs GPU comparison report."""
    print(f"\n{'='*80}")
    print("COMBINED CPU vs GPU REPORT")
    print(f"{'='*80}\n")

    with open(cpu_file, encoding="utf-8") as f:
        cpu_data = json.load(f)

    with open(gpu_file, encoding="utf-8") as f:
        gpu_data = json.load(f)

    print("📊 QUALITY COMPARISON (CPU vs GPU):")
    print("\nQ4 Model:")
    print(f"  CPU Pass Rate: {cpu_data['models']['q4']['quality_pass_rate']:.1%}")
    print(f"  GPU Pass Rate: {gpu_data['models']['q4']['quality_pass_rate']:.1%}")

    print("\nQ8 Model:")
    print(f"  CPU Pass Rate: {cpu_data['models']['q8']['quality_pass_rate']:.1%}")
    print(f"  GPU Pass Rate: {gpu_data['models']['q8']['quality_pass_rate']:.1%}")

    print("\n⚡ PERFORMANCE COMPARISON:")

    # Load times
    print("\nModel Load Times:")
    print(f"  Q4 CPU: {cpu_data['models']['q4']['load_time_s']:.2f}s")
    print(f"  Q4 GPU: {gpu_data['models']['q4']['load_time_s']:.2f}s")
    print(f"  Q8 CPU: {cpu_data['models']['q8']['load_time_s']:.2f}s")
    print(f"  Q8 GPU: {gpu_data['models']['q8']['load_time_s']:.2f}s")

    # Long document performance
    if "long_document" in cpu_data["models"]["q4"] and not cpu_data["models"]["q4"][
        "long_document"
    ].get("skipped"):
        print("\nLong Document Processing (952 words, 51 paragraphs):")

        cpu_q4_time = cpu_data["models"]["q4"]["long_document"]["total_time_s"]
        gpu_q4_time = gpu_data["models"]["q4"]["long_document"]["total_time_s"]
        cpu_q8_time = cpu_data["models"]["q8"]["long_document"]["total_time_s"]
        gpu_q8_time = gpu_data["models"]["q8"]["long_document"]["total_time_s"]

        print(
            f"  Q4 CPU: {cpu_q4_time:.2f}s ({cpu_data['models']['q4']['long_document']['words_per_second']:.0f} words/sec)"
        )
        print(
            f"  Q4 GPU: {gpu_q4_time:.2f}s ({gpu_data['models']['q4']['long_document']['words_per_second']:.0f} words/sec)"
        )
        print(f"  Q4 GPU Speedup: {cpu_q4_time / gpu_q4_time:.2f}x faster")

        print(
            f"\n  Q8 CPU: {cpu_q8_time:.2f}s ({cpu_data['models']['q8']['long_document']['words_per_second']:.0f} words/sec)"
        )
        print(
            f"  Q8 GPU: {gpu_q8_time:.2f}s ({gpu_data['models']['q8']['long_document']['words_per_second']:.0f} words/sec)"
        )
        print(f"  Q8 GPU Speedup: {cpu_q8_time / gpu_q8_time:.2f}x faster")

        print(f"\n  GPU: Q4 vs Q8 difference: {abs(gpu_q4_time - gpu_q8_time):.2f}s")
        if gpu_q4_time < gpu_q8_time:
            print(f"  Q4 is {gpu_q8_time / gpu_q4_time:.2f}x faster than Q8 on GPU")
        else:
            print(f"  Q8 is {gpu_q4_time / gpu_q8_time:.2f}x faster than Q4 on GPU")

    # Average processing times
    cpu_q4_avg = sum(
        r["processing_time_ms"] for r in cpu_data["models"]["q4"]["quality_tests"]
    ) / len(cpu_data["models"]["q4"]["quality_tests"])
    gpu_q4_avg = sum(
        r["processing_time_ms"] for r in gpu_data["models"]["q4"]["quality_tests"]
    ) / len(gpu_data["models"]["q4"]["quality_tests"])
    cpu_q8_avg = sum(
        r["processing_time_ms"] for r in cpu_data["models"]["q8"]["quality_tests"]
    ) / len(cpu_data["models"]["q8"]["quality_tests"])
    gpu_q8_avg = sum(
        r["processing_time_ms"] for r in gpu_data["models"]["q8"]["quality_tests"]
    ) / len(gpu_data["models"]["q8"]["quality_tests"])

    print("\nAverage Processing Time per Test:")
    print(f"  Q4 CPU: {cpu_q4_avg:.0f}ms")
    print(f"  Q4 GPU: {gpu_q4_avg:.0f}ms (speedup: {cpu_q4_avg / gpu_q4_avg:.2f}x)")
    print(f"  Q8 CPU: {cpu_q8_avg:.0f}ms")
    print(f"  Q8 GPU: {gpu_q8_avg:.0f}ms (speedup: {cpu_q8_avg / gpu_q8_avg:.2f}x)")

    print(f"\n{'='*80}")
    print("FINAL RECOMMENDATION")
    print(f"{'='*80}")

    # Determine best model
    q8_better_quality = (
        gpu_data["models"]["q8"]["quality_pass_rate"]
        > gpu_data["models"]["q4"]["quality_pass_rate"]
    )

    if q8_better_quality:
        quality_diff = (
            gpu_data["models"]["q8"]["quality_pass_rate"]
            - gpu_data["models"]["q4"]["quality_pass_rate"]
        )
        print(f"✓ Q8 has BETTER QUALITY (+{quality_diff:.1%} pass rate)")

        if "long_document" in gpu_data["models"]["q4"]:
            perf_diff = abs(gpu_q8_time - gpu_q4_time)
            if perf_diff < 5:  # Less than 5 seconds difference
                print(f"✓ Q8 performance is ACCEPTABLE ({perf_diff:.1f}s slower on test doc)")
                print("\n🎯 RECOMMENDATION: Switch to Q8 model")
                print("   - Better quality with minimal performance impact")
                print("   - GPU acceleration makes it practical")
            else:
                print(f"⚠️  Q8 is SLOWER ({perf_diff:.1f}s on test doc)")
                print("\n🎯 RECOMMENDATION: Offer both models as options")
                print("   - Q4: Default (faster, good quality)")
                print("   - Q8: Optional (slower, better quality)")
    else:
        print("✓ Q4 and Q8 have SIMILAR QUALITY")
        print("\n🎯 RECOMMENDATION: Keep Q4 as default")
        print("   - Faster model with equivalent quality")
        print("   - Smaller memory footprint (2.33GB vs 3.99GB)")

    print(f"{'='*80}\n")

    # Save combined report
    combined_report = {
        "timestamp": datetime.now().isoformat(),
        "cpu_results": cpu_file.name,
        "gpu_results": gpu_file.name,
        "summary": {
            "q4": {
                "cpu_pass_rate": cpu_data["models"]["q4"]["quality_pass_rate"],
                "gpu_pass_rate": gpu_data["models"]["q4"]["quality_pass_rate"],
                "cpu_avg_time_ms": cpu_q4_avg,
                "gpu_avg_time_ms": gpu_q4_avg,
                "gpu_speedup": cpu_q4_avg / gpu_q4_avg,
            },
            "q8": {
                "cpu_pass_rate": cpu_data["models"]["q8"]["quality_pass_rate"],
                "gpu_pass_rate": gpu_data["models"]["q8"]["quality_pass_rate"],
                "cpu_avg_time_ms": cpu_q8_avg,
                "gpu_avg_time_ms": gpu_q8_avg,
                "gpu_speedup": cpu_q8_avg / gpu_q8_avg,
            },
        },
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = Path("results") / f"cpu_vs_gpu_combined_{timestamp}.json"

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(combined_report, f, indent=2, ensure_ascii=False)

    print(f"📁 Combined report saved to: {report_file}\n")


def main():
    """Run full comparison suite."""
    print("=" * 80)
    print("COMPLETE Q4 vs Q8 MODEL COMPARISON (CPU + GPU)")
    print("=" * 80)
    print("\nThis will run:")
    print("1. Q4 vs Q8 comparison on CPU")
    print("2. Q4 vs Q8 comparison on GPU")
    print("3. Combined analysis of all results")
    print("\nEstimated time: 15-30 minutes (depending on GPU)")
    print("=" * 80)

    # Run CPU test
    cpu_success = run_comparison(use_gpu=False)

    if not cpu_success:
        print("\n❌ CPU test failed or was interrupted. Stopping.")
        return 1

    print("\n✓ CPU test completed successfully!")
    print("\nStarting GPU test in 5 seconds...")
    import time

    time.sleep(5)

    # Run GPU test
    gpu_success = run_comparison(use_gpu=True)

    if not gpu_success:
        print("\n❌ GPU test failed or was interrupted.")
        print("You can analyze CPU results separately if needed.")
        return 1

    print("\n✓ GPU test completed successfully!")
    print("\nGenerating combined report...")

    # Find latest results
    latest, second_latest = find_latest_results()

    if latest and second_latest:
        # Determine which is CPU and which is GPU
        with open(latest, encoding="utf-8") as f:
            latest_data = json.load(f)

        if latest_data["device"] == "cuda":
            gpu_file, cpu_file = latest, second_latest
        else:
            cpu_file, gpu_file = latest, second_latest

        generate_combined_report(cpu_file, gpu_file)
    else:
        print("⚠️  Could not find both result files for combined report.")

    print("\n✅ All tests completed!")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user.")
        sys.exit(1)
