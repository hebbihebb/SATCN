"""
Test GRMR-V3 on long document with GPU acceleration
This tests the full 50-paragraph sample that we previously tested on CPU
"""
import os
import time
from pathlib import Path

# Add CUDA to PATH before importing
cuda_path = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64"
if cuda_path not in os.environ["PATH"]:
    os.environ["PATH"] = cuda_path + ";" + os.environ["PATH"]

from llama_cpp import Llama


def load_test_document():
    """Load the test document."""
    test_file = Path(__file__).parent / "tools" / "test_long.md"

    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return None

    with open(test_file, encoding="utf-8") as f:
        content = f.read()

    return content


def split_into_paragraphs(text):
    """Split text into paragraphs."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paragraphs


def correct_paragraph(model, paragraph):
    """Correct a single paragraph."""
    prompt = f"""### Instruction
You are a copy editor. Fix grammar, spelling, and punctuation while keeping character names, slang, and factual content unchanged. Respond with the corrected text only.

### Input
{paragraph}

### Response
"""

    result = model(
        prompt,
        max_tokens=512,
        temperature=0.1,
        top_p=0.15,
        repeat_penalty=1.05,
        stop=["###", "\n\n"],
    )

    return result["choices"][0]["text"].strip()


def main():
    print("=" * 70)
    print("GRMR-V3 Long Document Test with GPU Acceleration")
    print("=" * 70)

    # Load test document
    print("\n1. Loading test document...")
    content = load_test_document()
    if not content:
        return False

    paragraphs = split_into_paragraphs(content)
    word_count = len(content.split())

    print("   ✓ Loaded document")
    print(f"   ✓ Paragraphs: {len(paragraphs)}")
    print(f"   ✓ Words: {word_count:,}")
    print(f"   ✓ Characters: {len(content):,}")

    # Load model with GPU
    print("\n2. Loading GRMR-V3 model with GPU acceleration...")
    model_path = Path(__file__).parent / ".GRMR-V3-Q4B-GGUF" / "GRMR-V3-Q4B.Q4_K_M.gguf"

    load_start = time.time()
    model = Llama(
        model_path=str(model_path),
        n_ctx=4096,
        n_gpu_layers=35,  # Offload to GPU
        verbose=False,
    )
    load_time = time.time() - load_start

    print(f"   ✓ Model loaded in {load_time:.2f}s")
    print("   ✓ GPU layers: 35/37")

    # Process paragraphs
    print(f"\n3. Processing {len(paragraphs)} paragraphs with GPU...")
    print("   " + "-" * 66)

    corrected_paragraphs = []
    paragraph_times = []

    overall_start = time.time()

    for i, paragraph in enumerate(paragraphs, 1):
        para_words = len(paragraph.split())

        # Show progress every 10 paragraphs
        if i % 10 == 0 or i == 1:
            print(f"   [{i:2d}/{len(paragraphs)}] Processing paragraph {i} ({para_words} words)...")

        start = time.time()
        corrected = correct_paragraph(model, paragraph)
        elapsed = time.time() - start

        corrected_paragraphs.append(corrected)
        paragraph_times.append(elapsed)

    overall_time = time.time() - overall_start

    print("   " + "-" * 66)
    print(f"   ✓ All {len(paragraphs)} paragraphs processed!")

    # Calculate statistics
    avg_time_per_para = sum(paragraph_times) / len(paragraph_times)
    words_per_minute = (word_count / overall_time) * 60

    # Save output
    output_file = Path(__file__).parent / "tools" / "test_long_gpu_corrected.md"
    output_content = "\n\n".join(corrected_paragraphs)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output_content)

    print(f"\n4. Results saved to: {output_file.name}")

    # Print performance summary
    print("\n" + "=" * 70)
    print("GPU Performance Summary")
    print("=" * 70)
    print("Input document:")
    print(f"  Paragraphs:           {len(paragraphs)}")
    print(f"  Words:                {word_count:,}")
    print(f"  Characters:           {len(content):,}")
    print()
    print("Processing time:")
    print(f"  Total time:           {overall_time/60:.2f} minutes ({overall_time:.1f}s)")
    print(f"  Model load time:      {load_time:.2f}s")
    print(f"  Avg time/paragraph:   {avg_time_per_para:.2f}s")
    print(f"  Min time/paragraph:   {min(paragraph_times):.2f}s")
    print(f"  Max time/paragraph:   {max(paragraph_times):.2f}s")
    print()
    print("Throughput:")
    print(f"  Words per minute:     {words_per_minute:.0f} wpm")
    print(f"  Paragraphs per min:   {(len(paragraphs)/overall_time)*60:.1f}")
    print()
    print("Output:")
    print(f"  File size:            {len(output_content):,} characters")
    print(f"  Saved to:             {output_file.name}")
    print("=" * 70)

    # Compare with CPU baseline (438 wpm)
    cpu_wpm = 438
    speedup = words_per_minute / cpu_wpm
    cpu_time_estimate = (word_count / cpu_wpm) * 60
    time_saved = cpu_time_estimate - overall_time

    print("\nGPU vs CPU Comparison:")
    print(f"  CPU baseline:         {cpu_wpm} wpm (~{cpu_time_estimate/60:.1f} minutes)")
    print(f"  GPU achieved:         {words_per_minute:.0f} wpm ({overall_time/60:.1f} minutes)")
    print(f"  Speedup:              {speedup:.2f}x faster")
    print(f"  Time saved:           {time_saved:.0f} seconds ({time_saved/60:.1f} minutes)")
    print("=" * 70)

    print("\n✅ Long document test completed successfully!")
    print(f"   GPU acceleration achieved {speedup:.2f}x speedup over CPU baseline")

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
