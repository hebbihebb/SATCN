"""CLI interface for SATCN pipeline."""

import argparse
import sys
from pathlib import Path

from satcn.core.pipeline_runner import PipelineRunner


def main():
    """Main CLI entrypoint for SATCN."""
    parser = argparse.ArgumentParser(
        description="SATCN - Spelling and Text Correction Normalizer for TTS preprocessing"
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Input file (.md or .epub) to process",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop processing on first filter error",
    )
    parser.add_argument(
        "--use-grmr",
        action="store_true",
        help="Use GRMR-V3 GGUF model for grammar correction (recommended)",
    )
    parser.add_argument(
        "--grmr-mode",
        choices=["replace", "hybrid", "supplement"],
        default="replace",
        help="GRMR-V3 integration mode",
    )
    parser.add_argument(
        "--use-t5",
        action="store_true",
        help="Use T5 transformer for grammar correction (experimental)",
    )
    parser.add_argument(
        "--t5-mode",
        choices=["replace", "hybrid", "supplement"],
        default="replace",
        help="T5 integration mode",
    )

    args = parser.parse_args()

    # Validate input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1

    # Run pipeline
    try:
        runner = PipelineRunner(
            input_filepath=str(input_path),
            fail_fast=args.fail_fast,
            use_t5=args.use_t5,
            t5_mode=args.t5_mode,
            use_grmr=args.use_grmr,
            grmr_mode=args.grmr_mode,
        )
        runner.run()
        print(f"\n✅ Processing complete! Check output file: {input_path.stem}_corrected{input_path.suffix}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
