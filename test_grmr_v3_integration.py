#!/usr/bin/env python3
"""Manual integration harness for the GRMR-V3 GGUF grammar model.

This mirrors ``test_t5_integration.py`` but targets the local
`.GRMR-V3-Q4B-GGUF/GRMR-V3-Q4B.Q4_K_M.gguf` model via llama.cpp bindings.

Usage (after implementing ``GRMRV3GrammarFilter``):

    $ python test_grmr_v3_integration.py

The script:
    1. Verifies that the GGUF model file exists.
    2. Loads ``GRMRV3GrammarFilter``.
    3. Runs a standalone text correction demo.
    4. Exercises pipeline-style input data.
    5. Prints an integration checklist.

Until the filter is implemented, the script will exit early with guidance.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

MODEL_PATH = Path('.GRMR-V3-Q4B-GGUF/GRMR-V3-Q4B.Q4_K_M.gguf')

try:
    from pipeline.filters.grmr_v3_filter import GRMRV3GrammarFilter  # type: ignore
except ImportError:
    GRMRV3GrammarFilter = None  # type: ignore


def _print_header(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60 + "\n")


def _check_model_file() -> bool:
    if MODEL_PATH.exists():
        print(f"✓ Found model file at {MODEL_PATH}")
        return True

    print(f"❌ Model file not found at {MODEL_PATH}")
    print("   Expected a local GGUF model. Download or move the file before running tests.")
    return False


def _ensure_filter_available() -> Optional[GRMRV3GrammarFilter]:  # type: ignore[name-defined]
    if GRMRV3GrammarFilter is None:
        print("❌ GRMRV3GrammarFilter is not available yet.")
        print("   Implement pipeline.filters.grmr_v3_filter.GRMRV3GrammarFilter as outlined in docs/GRMR_V3_GGUF_TEST_PLAN.md")
        return None

    try:
        return GRMRV3GrammarFilter(model_path=str(MODEL_PATH))
    except FileNotFoundError:
        print("❌ Could not load the GGUF model. Double-check MODEL_PATH.")
    except Exception as exc:  # pragma: no cover - diagnostic output only
        print(f"❌ Failed to initialize GRMRV3GrammarFilter: {exc}")
        print("   Confirm llama-cpp-python is installed and compiled with the right backend.")
    return None


def _demo_sentences(filter_instance: GRMRV3GrammarFilter) -> None:  # type: ignore[name-defined]
    _print_header("Standalone grammar corrections")
    test_cases: List[str] = [
        "Thiss sentnce have two speling errrors.",
        "The crew was suppose to arrive yesteday evening.",
        "Irina said she dont wanna go to the market no more.",
        "Their going too fast for the narow bridge.",
        "I has forgotten where I put the keys."  # Keep simple for deterministic output
    ]

    for idx, text in enumerate(test_cases, start=1):
        print(f"Test {idx}:")
        print(f"  Original : {text}")
        corrected = filter_instance.correct_text(text)
        print(f"  Corrected: {corrected}\n")


def _demo_pipeline(filter_instance: GRMRV3GrammarFilter) -> None:  # type: ignore[name-defined]
    _print_header("Pipeline-style integration test")
    sample_data = {
        'text_blocks': [
            {
                'content': 'This block is mostly fine.',
                'metadata': {'type': 'paragraph'}
            },
            {
                'content': 'This block contain a grammar mistake.',
                'metadata': {'type': 'paragraph'}
            },
            {
                'content': 'Ther are multiple speling misteaks and punctuation problems here',
                'metadata': {'type': 'paragraph'}
            }
        ]
    }

    print("Input data:")
    for i, block in enumerate(sample_data['text_blocks']):
        print(f"  Block {i}: {block['content']}")

    result = filter_instance.process(sample_data)

    print("\nOutput data:")
    for i, block in enumerate(result['text_blocks']):
        print(f"  Block {i}: {block['content']}")


def _print_guide() -> None:
    _print_header("Integration Guide")
    guide = """
To integrate GRMRV3GrammarFilter into the SATCN pipeline:

1. Install dependencies
   ---------------------
   # CPU only
   pip install llama-cpp-python numpy

   # NVIDIA GPU (requires CUDA toolkit)
   CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python numpy

2. Implement the filter wrapper
   -----------------------------
   - File: pipeline/filters/grmr_v3_filter.py
   - Class: GRMRV3GrammarFilter
   - Follow docs/GRMR_V3_GGUF_TEST_PLAN.md for prompt + decoding settings

3. Wire into the pipeline
   ----------------------
   - Update pipeline/pipeline_runner.py
     * Add `--use-grmr` CLI switch mirroring `--use-t5`
     * Instantiate GRMRV3GrammarFilter with the desired mode (replace/hybrid/supplement)
   - Optionally expose via satcn/correction for programmatic use

4. Run automated tests
   --------------------
   pytest tests/unit/test_grmr_v3_filter.py -k "not benchmark"
   pytest tests/integration/test_grmr_v3_pipeline.py

5. Compare against T5 baseline
   ----------------------------
   - Run docs/T5_TESTING_SESSION_OCT2025.md scenarios using both filters
   - Capture latency + quality notes in docs/GRMR_V3_GGUF_TEST_PLAN.md
"""
    print(guide)


def main() -> int:
    _print_header("GRMR-V3 GGUF Grammar Model - Integration Test")

    if not _check_model_file():
        return 1

    filter_instance = _ensure_filter_available()
    if filter_instance is None:
        return 1

    _demo_sentences(filter_instance)
    _demo_pipeline(filter_instance)
    _print_guide()

    print("\n✓ GRMR-V3 integration smoke test completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
