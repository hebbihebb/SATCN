"""
Simple GPU test - just check if GPU layers parameter works
"""
import os
from pathlib import Path

from llama_cpp import Llama

# Add CUDA to PATH
cuda_path = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64"
if cuda_path not in os.environ["PATH"]:
    os.environ["PATH"] = cuda_path + ";" + os.environ["PATH"]

model_path = Path(__file__).parent / "flan-t5-large-grammar-synthesis" / "ggml-model-Q6_K.gguf"

print("Testing GPU support...")
print(f"Model: {model_path.name}")

try:
    # Try loading with GPU layers
    print("\nAttempting to load with GPU support (n_gpu_layers=10)...")
    model = Llama(
        model_path=str(model_path),
        n_ctx=512,  # Use model's training context size
        n_gpu_layers=10,
        verbose=True,
    )
    print("✅ Model loaded successfully with GPU support!")

    # Try a simple generation
    print("\nTesting inference...")
    result = model("Hello", max_tokens=5)
    print("✅ Inference successful!")
    print(f"Output: {result['choices'][0]['text']}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
