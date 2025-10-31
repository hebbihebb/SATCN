"""
Test GPU performance vs CPU performance for GRMR-V3 grammar correction.
"""
import time
from pathlib import Path

# Test text (50 words)
TEST_TEXT = """
theres alot of mistakes in this sentance that need fixing their our several errors with
word usage and grammer issues that the model should correct properly its going to test
weather the GPU is faster then CPU for processing text through the correction model
"""


def test_correction(use_gpu=False, n_gpu_layers=0):
    """Test correction with or without GPU."""
    from llama_cpp import Llama

    model_path = Path(__file__).parent / "flan-t5-large-grammar-synthesis" / "ggml-model-Q6_K.gguf"

    print(f"\n{'='*60}")
    print(f"Testing {'GPU' if use_gpu else 'CPU'} Mode")
    print(f"{'='*60}")

    # Load model
    print(f"Loading model{'with GPU support' if use_gpu else ''}...")
    load_start = time.time()

    model = Llama(
        model_path=str(model_path),
        n_ctx=4096,
        n_gpu_layers=n_gpu_layers if use_gpu else 0,
        verbose=False,
    )

    load_time = time.time() - load_start
    print(f"Model loaded in {load_time:.2f}s")

    # Warm-up run
    print("Warming up...")
    _ = model(f"Correct: {TEST_TEXT[:50]}", max_tokens=50, temperature=0.1)

    # Timed runs
    print("\nRunning 3 correction tests...")
    times = []

    for i in range(3):
        start = time.time()
        result = model(
            f"Correct the grammar and spelling:\n\n{TEST_TEXT}\n\nCorrected:",
            max_tokens=200,
            temperature=0.1,
            stop=["\n\n"],
        )
        elapsed = time.time() - start
        times.append(elapsed)

        corrected = result["choices"][0]["text"].strip()
        print(f"\nRun {i+1}: {elapsed:.2f}s")
        print(f"Output: {corrected[:100]}...")

    avg_time = sum(times) / len(times)
    words_per_min = (len(TEST_TEXT.split()) / avg_time) * 60

    print(f"\n{'='*60}")
    print(f"Results for {'GPU' if use_gpu else 'CPU'}:")
    print(f"  Average time: {avg_time:.2f}s")
    print(f"  Throughput: {words_per_min:.0f} words/minute")
    print(f"{'='*60}")

    return avg_time, words_per_min


def main():
    """Run performance comparison."""
    print("\n" + "=" * 60)
    print("GRMR-V3 GPU vs CPU Performance Test")
    print("=" * 60)

    # Test CPU
    cpu_time, cpu_wpm = test_correction(use_gpu=False)

    # Test GPU
    gpu_time, gpu_wpm = test_correction(use_gpu=True, n_gpu_layers=35)

    # Compare
    speedup = cpu_time / gpu_time
    print("\n" + "=" * 60)
    print("FINAL COMPARISON")
    print("=" * 60)
    print(f"CPU:  {cpu_time:.2f}s per test ({cpu_wpm:.0f} words/min)")
    print(f"GPU:  {gpu_time:.2f}s per test ({gpu_wpm:.0f} words/min)")
    print(f"\nSpeedup: {speedup:.2f}x faster on GPU")
    print("=" * 60)


if __name__ == "__main__":
    # Ensure CUDA is in PATH
    import os

    cuda_path = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64"
    if cuda_path not in os.environ["PATH"]:
        os.environ["PATH"] = cuda_path + ";" + os.environ["PATH"]
        print(f"Added CUDA to PATH: {cuda_path}")

    main()
