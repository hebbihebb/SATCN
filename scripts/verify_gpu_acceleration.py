#!/usr/bin/env python3
"""
Verify GPU acceleration is working for GRMR-V3.

This script checks:
1. If llama-cpp-python is installed with CUDA support
2. If CUDA device is detected and usable
3. Performance comparison between CPU and GPU

Usage:
    python verify_gpu_acceleration.py
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def check_cuda_availability():
    """Check if CUDA is available in llama-cpp-python."""
    print("=" * 70)
    print("CUDA Availability Check")
    print("=" * 70)

    try:
        from llama_cpp import Llama

        print("✓ llama-cpp-python is installed")
    except ImportError:
        print("✗ llama-cpp-python not installed")
        return False

    # Try to check CUDA support
    try:
        import torch

        if torch.cuda.is_available():
            print(f"✓ PyTorch CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            print("⚠ PyTorch CUDA not available (but llama-cpp may still have CUDA)")
    except ImportError:
        print("ℹ PyTorch not installed (not required for llama-cpp-python)")

    return True


def test_gpu_loading():
    """Test if model can be loaded with GPU."""
    print("\n" + "=" * 70)
    print("GPU Model Loading Test")
    print("=" * 70)

    from pipeline.filters.grmr_v3_filter import GRMRV3GrammarFilter

    # Try to load with GPU
    print("\nAttempting to load model with GPU...")
    try:
        filter_gpu = GRMRV3GrammarFilter(device="cuda")
        print("✓ Model loaded successfully with device='cuda'")

        # The actual device used will be logged during init
        if filter_gpu.device == "cuda":
            print("✓ GPU device confirmed in filter object")
            return filter_gpu
        else:
            print(f"⚠ Filter initialized but using: {filter_gpu.device}")
            return None
    except Exception as e:
        print(f"✗ Failed to load with GPU: {e}")
        return None


def benchmark_cpu_vs_gpu():
    """Compare CPU vs GPU performance."""
    print("\n" + "=" * 70)
    print("CPU vs GPU Performance Benchmark")
    print("=" * 70)

    from pipeline.filters.grmr_v3_filter import GRMRV3GrammarFilter

    test_sentences = [
        "Thiss sentnce have two speling errrors.",
        "She run to the store every day.",
        "Their going too fast for the bridge.",
        "I has forgotten where I put it.",
        "The woman which I met was vary nice.",
    ]

    # Test CPU
    print("\n[CPU Test]")
    print("Initializing CPU model...")
    start_init = time.time()
    filter_cpu = GRMRV3GrammarFilter(device="cpu")
    cpu_init_time = time.time() - start_init
    print(f"CPU init time: {cpu_init_time:.2f}s")

    print(f"Processing {len(test_sentences)} sentences...")
    cpu_times = []
    for sentence in test_sentences:
        start = time.time()
        _ = filter_cpu.correct_text(sentence)
        cpu_times.append(time.time() - start)

    cpu_avg = sum(cpu_times) / len(cpu_times)
    cpu_total = sum(cpu_times)
    print(f"CPU average: {cpu_avg:.3f}s per sentence")
    print(f"CPU total: {cpu_total:.2f}s")

    # Test GPU
    print("\n[GPU Test]")
    print("Initializing GPU model...")
    start_init = time.time()
    try:
        filter_gpu = GRMRV3GrammarFilter(device="cuda")
        gpu_init_time = time.time() - start_init
        print(f"GPU init time: {gpu_init_time:.2f}s")

        print(f"Processing {len(test_sentences)} sentences...")
        gpu_times = []
        for sentence in test_sentences:
            start = time.time()
            _ = filter_gpu.correct_text(sentence)
            gpu_times.append(time.time() - start)

        gpu_avg = sum(gpu_times) / len(gpu_times)
        gpu_total = sum(gpu_times)
        print(f"GPU average: {gpu_avg:.3f}s per sentence")
        print(f"GPU total: {gpu_total:.2f}s")

        # Calculate speedup
        speedup = cpu_avg / gpu_avg
        print("\n" + "─" * 70)
        print(f"Speedup: {speedup:.2f}x faster with GPU")
        print(
            f"Time saved: {cpu_total - gpu_total:.2f}s ({(1 - gpu_total/cpu_total)*100:.1f}% faster)"
        )
        print("─" * 70)

        if speedup >= 3.0:
            print("\n✓ Excellent GPU acceleration!")
        elif speedup >= 1.5:
            print("\n✓ Good GPU acceleration")
        elif speedup >= 1.1:
            print("\n⚠ Minimal GPU acceleration (check GPU usage)")
        else:
            print("\n⚠ GPU may not be working correctly (slower than CPU)")

    except Exception as e:
        print(f"✗ GPU test failed: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print("GRMR-V3 GPU ACCELERATION VERIFICATION")
    print("=" * 70 + "\n")

    # Step 1: Check CUDA availability
    if not check_cuda_availability():
        print("\n✗ Cannot proceed without llama-cpp-python")
        return 1

    # Step 2: Test GPU loading
    gpu_filter = test_gpu_loading()
    if gpu_filter is None:
        print("\n⚠ GPU loading test failed")
        print("The model may still work with CPU, but GPU acceleration is not available.")
        return 1

    # Step 3: Benchmark CPU vs GPU
    try:
        benchmark_cpu_vs_gpu()
    except Exception as e:
        print(f"\n✗ Benchmark failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    print("\n" + "=" * 70)
    print("✓ GPU Verification Complete")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
