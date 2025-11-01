"""
GPU Performance Diagnostic Tool for GRMR-V3 Models

This script systematically tests different llama.cpp GPU configurations to identify
why GPU performance is slower than CPU. Based on llama.cpp best practices:

Key Variables to Test:
1. Kernel selection: MMQ (int8 Tensor Core) vs cuBLAS (FP16)
2. Batch sizes: n_batch and n_ubatch
3. KV cache type: f16 (default) vs q8_0 (quantized)
4. GPU layers: Ensure all layers offloaded (-1 = all)
5. Context size: Match model's training context

Reference: https://github.com/ggerganov/llama.cpp/issues/3479
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def get_ggml_type_id(type_name: str) -> int:
    """Convert KV cache type name to GGML type ID."""
    # From ggml.h enum ggml_type
    types = {
        "f16": 1,  # GGML_TYPE_F16
        "q8_0": 8,  # GGML_TYPE_Q8_0
        "q4_0": 2,  # GGML_TYPE_Q4_0
    }
    return types.get(type_name, 1)  # Default to f16


def test_configuration(
    model_path: Path,
    config_name: str,
    n_gpu_layers: int = -1,
    n_batch: int = 512,
    n_ubatch: int = 512,
    n_ctx: int = 4096,
    kv_cache_type: str = "f16",
    env_vars: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Test a specific GPU configuration.

    Args:
        model_path: Path to GGUF model file
        config_name: Human-readable name for this configuration
        n_gpu_layers: Number of layers to offload (-1 = all)
        n_batch: Prompt processing batch size (larger = better GPU utilization)
        n_ubatch: Physical batch size (tune to avoid OOM)
        n_ctx: Context window size
        kv_cache_type: KV cache quantization ('f16' or 'q8_0')
        env_vars: Environment variables to set (e.g., GGML_CUDA_FORCE_CUBLAS=1)

    Returns:
        dict with timing and configuration details
    """
    print(f"\n{'='*80}")
    print(f"Testing Configuration: {config_name}")
    print(f"{'='*80}")
    print(f"Model: {model_path.name}")
    print(f"GPU Layers: {n_gpu_layers} (-1 = all layers)")
    print(f"Batch Size: {n_batch}")
    print(f"Micro Batch: {n_ubatch}")
    print(f"Context: {n_ctx}")
    print(f"KV Cache: {kv_cache_type}")
    if env_vars:
        print("Environment Variables:")
        for k, v in env_vars.items():
            print(f"  {k}={v}")
    print(f"{'='*80}\n")

    # Set environment variables
    original_env = {}
    if env_vars:
        for k, v in env_vars.items():
            original_env[k] = os.environ.get(k)
            os.environ[k] = v

    try:
        # Test paragraphs of increasing size
        test_texts = [
            "The dogs barks loudly.",  # Short (4 words)
            "She walks to the store and bought milk. The weather was nice today.",  # Medium (13 words)
            "After eating the dog went outside. It was a beautiful sunny day and the birds were singing in the trees. The dog ran around the yard chasing squirrels.",  # Long (30 words)
        ]

        results = {
            "config_name": config_name,
            "model": str(model_path.name),
            "parameters": {
                "n_gpu_layers": n_gpu_layers,
                "n_batch": n_batch,
                "n_ubatch": n_ubatch,
                "n_ctx": n_ctx,
                "kv_cache_type": kv_cache_type,
            },
            "env_vars": env_vars or {},
            "tests": [],
            "load_time_sec": 0,
            "total_time_sec": 0,
        }

        # Load model with configuration
        print("Loading model...")
        load_start = time.time()

        # Create custom Llama instance with all parameters
        from llama_cpp import Llama

        type_k = get_ggml_type_id(kv_cache_type)
        type_v = get_ggml_type_id(kv_cache_type)

        llm = Llama(
            model_path=str(model_path),
            n_ctx=n_ctx,
            n_batch=n_batch,
            n_ubatch=n_ubatch,
            n_gpu_layers=n_gpu_layers,
            type_k=type_k,
            type_v=type_v,
            use_mlock=True,
            use_mmap=True,
            verbose=True,  # Enable verbose to see backend info
        )

        load_time = time.time() - load_start
        results["load_time_sec"] = load_time
        print(f"✓ Model loaded in {load_time:.2f}s\n")

        # Run tests
        total_start = time.time()
        for i, text in enumerate(test_texts, 1):
            word_count = len(text.split())
            print(f"Test {i}/3: {word_count} words...")

            # Format prompt
            prompt = f"""### Instruction
You are a copy editor. Fix grammar, spelling, and punctuation while keeping character names, slang, and factual content unchanged. Respond with the corrected text only.

### Input
{text}

### Response
"""

            # Run inference
            test_start = time.time()
            output = llm(
                prompt,
                max_tokens=256,
                temperature=0.1,
                top_p=0.15,
                top_k=40,
                stop=["###"],
                echo=False,
            )
            test_time = time.time() - test_start

            # Extract corrected text
            corrected = output["choices"][0]["text"].strip()
            tokens_generated = output["usage"]["completion_tokens"]
            tokens_per_sec = tokens_generated / test_time if test_time > 0 else 0

            print(
                f"  Time: {test_time:.2f}s | Tokens: {tokens_generated} | Speed: {tokens_per_sec:.1f} tok/s"
            )
            print(
                f"  Output: {corrected[:60]}..."
                if len(corrected) > 60
                else f"  Output: {corrected}"
            )

            results["tests"].append(
                {
                    "words": word_count,
                    "time_sec": test_time,
                    "tokens_generated": tokens_generated,
                    "tokens_per_sec": tokens_per_sec,
                    "corrected_text": corrected,
                }
            )

        results["total_time_sec"] = time.time() - total_start

        # Summary
        avg_tok_per_sec = sum(t["tokens_per_sec"] for t in results["tests"]) / len(results["tests"])
        print("\n✓ Configuration complete!")
        print(f"  Average speed: {avg_tok_per_sec:.1f} tokens/sec")
        print(f"  Total time: {results['total_time_sec']:.2f}s\n")

        return results

    except Exception as e:
        print(f"✗ Configuration failed: {e}\n")
        return {
            "config_name": config_name,
            "error": str(e),
            "parameters": {
                "n_gpu_layers": n_gpu_layers,
                "n_batch": n_batch,
                "n_ubatch": n_ubatch,
                "n_ctx": n_ctx,
                "kv_cache_type": kv_cache_type,
            },
        }

    finally:
        # Restore original environment
        for k, v in original_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def main():
    """Run comprehensive GPU performance diagnostics."""
    print("\n" + "=" * 80)
    print("GRMR-V3 GPU Performance Diagnostic Tool")
    print("=" * 80)
    print("\nThis script will test different llama.cpp configurations to identify")
    print("optimal GPU settings for your RTX 2070.")
    print("\nBased on llama.cpp best practices:")
    print("  - Test MMQ vs cuBLAS kernels")
    print("  - Test different batch sizes")
    print("  - Test KV cache quantization")
    print("  - Verify all layers are on GPU")
    print("\nEach configuration will process 3 test sentences.")
    print("Estimated time: 5-10 minutes")
    print("=" * 80 + "\n")

    # Use Q4 model for testing (faster to iterate)
    model_path = Path(".GRMR-V3-Q4B-GGUF/GRMR-V3-Q4B.Q4_K_M.gguf")

    if not model_path.exists():
        print(f"✗ Model not found: {model_path}")
        print("Please ensure the model file exists.")
        sys.exit(1)

    # Test configurations
    configurations = []

    # 1. Baseline: Default settings
    print("\n>>> Configuration 1: Baseline (Default Settings)")
    configurations.append(
        test_configuration(
            model_path,
            config_name="1_baseline_default",
            n_gpu_layers=-1,
            n_batch=512,  # llama.cpp default
            n_ubatch=512,  # llama.cpp default
            n_ctx=4096,
            kv_cache_type="f16",
        )
    )

    # 2. Force cuBLAS (FP16 GEMM)
    print("\n>>> Configuration 2: Force cuBLAS (FP16)")
    configurations.append(
        test_configuration(
            model_path,
            config_name="2_force_cublas",
            n_gpu_layers=-1,
            n_batch=512,
            n_ubatch=512,
            n_ctx=4096,
            kv_cache_type="f16",
            env_vars={"GGML_CUDA_FORCE_CUBLAS": "1"},
        )
    )

    # 3. Force MMQ (int8 Tensor Core)
    print("\n>>> Configuration 3: Force MMQ (int8 Tensor Core)")
    configurations.append(
        test_configuration(
            model_path,
            config_name="3_force_mmq",
            n_gpu_layers=-1,
            n_batch=512,
            n_ubatch=512,
            n_ctx=4096,
            kv_cache_type="f16",
            env_vars={"GGML_CUDA_FORCE_MMQ": "1"},
        )
    )

    # 4. Larger batch size (better GPU utilization)
    print("\n>>> Configuration 4: Larger Batch Size (1024)")
    configurations.append(
        test_configuration(
            model_path,
            config_name="4_large_batch",
            n_gpu_layers=-1,
            n_batch=1024,
            n_ubatch=256,
            n_ctx=4096,
            kv_cache_type="f16",
        )
    )

    # 5. Quantized KV cache (q8_0)
    print("\n>>> Configuration 5: Quantized KV Cache (q8_0)")
    configurations.append(
        test_configuration(
            model_path,
            config_name="5_kv_q8_0",
            n_gpu_layers=-1,
            n_batch=512,
            n_ubatch=512,
            n_ctx=4096,
            kv_cache_type="q8_0",
        )
    )

    # 6. Combined optimization: cuBLAS + large batch + q8_0 KV
    print("\n>>> Configuration 6: Combined Optimization")
    configurations.append(
        test_configuration(
            model_path,
            config_name="6_combined_cublas_batch_kv",
            n_gpu_layers=-1,
            n_batch=1024,
            n_ubatch=256,
            n_ctx=4096,
            kv_cache_type="q8_0",
            env_vars={"GGML_CUDA_FORCE_CUBLAS": "1"},
        )
    )

    # 7. Combined optimization: MMQ + large batch + q8_0 KV
    print("\n>>> Configuration 7: Combined MMQ Optimization")
    configurations.append(
        test_configuration(
            model_path,
            config_name="7_combined_mmq_batch_kv",
            n_gpu_layers=-1,
            n_batch=1024,
            n_ubatch=256,
            n_ctx=4096,
            kv_cache_type="q8_0",
            env_vars={"GGML_CUDA_FORCE_MMQ": "1"},
        )
    )

    # 8. Extreme batch size (max GPU utilization)
    print("\n>>> Configuration 8: Extreme Batch Size (2048)")
    configurations.append(
        test_configuration(
            model_path,
            config_name="8_extreme_batch",
            n_gpu_layers=-1,
            n_batch=2048,
            n_ubatch=512,
            n_ctx=4096,
            kv_cache_type="q8_0",
            env_vars={"GGML_CUDA_FORCE_CUBLAS": "1"},
        )
    )

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    output_file = results_dir / f"gpu_diagnostics_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "model": str(model_path),
                "configurations": configurations,
            },
            f,
            indent=2,
        )

    # Print summary
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80 + "\n")

    print(f"{'Configuration':<40} {'Avg Speed (tok/s)':<20} {'Status':<10}")
    print("-" * 80)

    for config in configurations:
        name = config["config_name"]
        if "error" in config:
            print(f"{name:<40} {'ERROR':<20} {'Failed':<10}")
        else:
            avg_speed = sum(t["tokens_per_sec"] for t in config["tests"]) / len(config["tests"])
            print(f"{name:<40} {avg_speed:<20.1f} {'OK':<10}")

    # Find best configuration
    valid_configs = [c for c in configurations if "error" not in c]
    if valid_configs:
        best = max(
            valid_configs,
            key=lambda c: sum(t["tokens_per_sec"] for t in c["tests"]) / len(c["tests"]),
        )
        best_speed = sum(t["tokens_per_sec"] for t in best["tests"]) / len(best["tests"])

        print("\n" + "=" * 80)
        print(f"✓ BEST CONFIGURATION: {best['config_name']}")
        print(f"  Average Speed: {best_speed:.1f} tokens/sec")
        print("  Parameters:")
        for k, v in best["parameters"].items():
            print(f"    {k}: {v}")
        if best["env_vars"]:
            print("  Environment Variables:")
            for k, v in best["env_vars"].items():
                print(f"    {k}={v}")
        print("=" * 80)

    print(f"\n✓ Results saved to: {output_file}")
    print("\nNext steps:")
    print("  1. Review results to identify fastest configuration")
    print("  2. Update GRMRV3GrammarFilter with optimal parameters")
    print("  3. Test with full Q4 vs Q8 comparison")
    print("  4. If GPU still slower than CPU, investigate PCIe bottleneck")


if __name__ == "__main__":
    main()
