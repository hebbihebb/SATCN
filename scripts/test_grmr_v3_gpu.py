"""
Test GRMR-V3 model with GPU acceleration
This is the actual GRMR-V3 model, not the T5 model
"""
import os
import time
from pathlib import Path

# Add CUDA to PATH before importing llama_cpp
cuda_path = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64"
if cuda_path not in os.environ["PATH"]:
    os.environ["PATH"] = cuda_path + ";" + os.environ["PATH"]
    print(f"✓ Added CUDA to PATH: {cuda_path}\n")

from llama_cpp import Llama


def test_grmr_v3_gpu():
    """Test GRMR-V3 on GPU."""
    print("=" * 70)
    print("Testing GRMR-V3 Grammar Correction with GPU Acceleration")
    print("=" * 70)

    model_path = Path(__file__).parent / ".GRMR-V3-Q4B-GGUF" / "GRMR-V3-Q4B.Q4_K_M.gguf"

    if not model_path.exists():
        print(f"❌ Model not found at: {model_path}")
        return False

    print(f"\nModel: {model_path.name}")
    print(f"Size: {model_path.stat().st_size / (1024*1024):.1f} MB")

    # Test cases
    test_cases = [
        "There going to the store their.",
        "I seen him yesterday and he dont want to come.",
        "The cats is sleeping on the couch.",
        "Me and him went to school together.",
        "She should of went to the party.",
    ]

    # Load model with GPU support
    print(f"\n{'='*70}")
    print("Loading model with GPU acceleration...")
    print("GPU Layers: 35 (offload most layers to GPU)")
    print(f"{'='*70}\n")

    load_start = time.time()

    try:
        model = Llama(
            model_path=str(model_path),
            n_ctx=4096,
            n_gpu_layers=35,  # Offload layers to GPU
            verbose=True,
        )

        load_time = time.time() - load_start
        print(f"\n✅ Model loaded successfully in {load_time:.2f}s with GPU support!")

    except Exception as e:
        print(f"\n❌ Failed to load model: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Run corrections
    print(f"\n{'='*70}")
    print("Running Grammar Corrections")
    print(f"{'='*70}\n")

    times = []
    total_words = 0

    for i, test_input in enumerate(test_cases, 1):
        print(f"Test {i}/{len(test_cases)}:")
        print(f"  Input:  {test_input}")

        # Count words
        words = len(test_input.split())
        total_words += words

        # Prepare prompt
        prompt = f"""### Instruction
You are a copy editor. Fix grammar, spelling, and punctuation while keeping character names, slang, and factual content unchanged. Respond with the corrected text only.

### Input
{test_input}

### Response
"""

        # Run correction
        start = time.time()
        try:
            result = model(
                prompt,
                max_tokens=256,
                temperature=0.1,
                top_p=0.15,
                repeat_penalty=1.05,
                stop=["###", "\n\n"],
            )

            elapsed = time.time() - start
            times.append(elapsed)

            corrected = result["choices"][0]["text"].strip()

            print(f"  Output: {corrected}")
            print(f"  Time:   {elapsed:.2f}s")
            print("  Status: ✅ Success")

        except Exception as e:
            print(f"  Status: ❌ Error: {e}")
            return False

        print()

    # Calculate statistics
    avg_time = sum(times) / len(times)
    total_time = sum(times)
    words_per_min = (total_words / total_time) * 60

    print(f"{'='*70}")
    print("GPU Performance Results")
    print(f"{'='*70}")
    print(f"Total tests:        {len(test_cases)}")
    print(f"Total words:        {total_words}")
    print(f"Total time:         {total_time:.2f}s")
    print(f"Average per test:   {avg_time:.2f}s")
    print(f"Throughput:         {words_per_min:.0f} words/minute")
    print(f"{'='*70}")

    print("\n✅ GPU test completed successfully!")
    print(f"   Achieved {words_per_min:.0f} words/minute with GPU acceleration")

    return True


if __name__ == "__main__":
    success = test_grmr_v3_gpu()
    exit(0 if success else 1)
