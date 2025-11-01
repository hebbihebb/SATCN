"""Quick GPU verification test."""
import time
from pathlib import Path

from llama_cpp import Llama

model_path = Path(".GRMR-V3-Q4B-GGUF/GRMR-V3-Q4B.Q4_K_M.gguf")
print("=" * 80)
print("GPU VERIFICATION TEST")
print("=" * 80)
print(f"\nModel: {model_path.name}")
print("Loading with n_gpu_layers=-1 (all layers on GPU)...\n")

start = time.time()
llm = Llama(
    model_path=str(model_path),
    n_ctx=4096,
    n_gpu_layers=-1,
    verbose=True,  # Show llama.cpp backend logs
)
load_time = time.time() - start
print(f"\n✓ Model loaded in {load_time:.2f}s\n")

print("Testing inference speed...")
prompt = """### Instruction
You are a copy editor. Fix grammar, spelling, and punctuation while keeping character names, slang, and factual content unchanged. Respond with the corrected text only.

### Input
The dogs barks loudly.

### Response
"""

start = time.time()
output = llm(prompt, max_tokens=50, temperature=0.1, stop=["###"])
duration = time.time() - start

result = output["choices"][0]["text"].strip()
tokens = output["usage"]["completion_tokens"]
tok_per_sec = tokens / duration if duration > 0 else 0

print("\n✓ Inference complete!")
print(f"  Time: {duration:.2f}s")
print(f"  Tokens: {tokens}")
print(f"  Speed: {tok_per_sec:.1f} tokens/sec")
print(f"  Output: {result}")
print("\n" + "=" * 80)
