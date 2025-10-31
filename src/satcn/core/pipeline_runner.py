import argparse
import os
import logging
import time
from satcn.core.filters.markdown_parser import (
    MarkdownParserFilter,
    MarkdownOutputGenerator,
)
from satcn.core.filters.epub_parser import EpubParserFilter, EpubOutputGenerator
from satcn.core.filters.grammar_filter_safe import GrammarCorrectionFilterSafe
from satcn.core.filters.spelling_filter import SpellingCorrectionFilter
from satcn.core.filters.tts_normalizer import TTSNormalizer
from satcn.core.filters.t5_correction_filter import T5CorrectionFilter
from satcn.core.filters import GRMR_V3_AVAILABLE
from satcn.core.utils.logging_setup import setup_logging

# Conditional import for GRMR-V3
if GRMR_V3_AVAILABLE:
    from satcn.core.filters.grmr_v3_filter import GRMRV3GrammarFilter

class PipelineRunner:
    def __init__(self, input_filepath, fail_fast=False, use_t5=False, t5_mode="replace", 
                 use_grmr=False, grmr_mode="replace"):
        """
        Initialize the SATCN pipeline runner.

        Args:
            input_filepath: Path to input file (.md or .epub)
            fail_fast: Stop on first filter failure
            use_t5: Enable T5-based correction (experimental)
            t5_mode: T5 integration mode:
                     - "replace": Replace spelling+grammar with T5 only
                     - "hybrid": T5 first, then rule-based cleanup
                     - "supplement": Keep existing filters, add T5
            use_grmr: Enable GRMR-V3 GGUF-based correction (experimental)
            grmr_mode: GRMR-V3 integration mode (same options as T5)
        """
        self.input_filepath = input_filepath
        self.fail_fast = fail_fast
        self.use_t5 = use_t5
        self.t5_mode = t5_mode
        self.use_grmr = use_grmr
        self.grmr_mode = grmr_mode
        self.logger = setup_logging()
        
        # Validate GRMR-V3 availability
        if self.use_grmr and not GRMR_V3_AVAILABLE:
            raise RuntimeError(
                "GRMR-V3 filter requested but llama-cpp-python is not installed.\n"
                "Install dependencies: pip install -r requirements-grmr.txt\n"
                "See docs/GRMR_V3_INSTALLATION_NOTES.md for details."
            )
        
        # Don't allow both T5 and GRMR-V3 at the same time (for now)
        if self.use_t5 and self.use_grmr:
            raise ValueError(
                "Cannot use both --use-t5 and --use-grmr simultaneously. "
                "Please choose one grammar correction model."
            )
        
        self.filters = self._get_filters()

    def _get_filters(self):
        """
        Build the filter pipeline based on configuration.

        Returns:
            List of (filter, returns_stats) tuples
        """
        _, file_extension = os.path.splitext(self.input_filepath)
        if file_extension.lower() == '.md':
            parser_filter = MarkdownParserFilter()
            output_generator = MarkdownOutputGenerator()
        elif file_extension.lower() == '.epub':
            parser_filter = EpubParserFilter()
            output_generator = EpubOutputGenerator()
        else:
            raise ValueError(f"Unsupported file type '{file_extension}'. Please provide a .md or .epub file.")

        # Build filter pipeline based on configuration
        filters = [(parser_filter, False)]

        if self.use_t5:
            self.logger.info(f"T5 correction enabled (mode: {self.t5_mode})")

            if self.t5_mode == "replace":
                # Replace spelling+grammar with T5 only (simplest)
                filters.append((T5CorrectionFilter(), True))

            elif self.t5_mode == "hybrid":
                # T5 first, then rule-based cleanup
                filters.append((T5CorrectionFilter(), True))
                filters.append((SpellingCorrectionFilter(), False))
                filters.append((GrammarCorrectionFilterSafe(), True))

            elif self.t5_mode == "supplement":
                # Keep existing filters, add T5 at the end
                filters.append((SpellingCorrectionFilter(), False))
                filters.append((GrammarCorrectionFilterSafe(), True))
                filters.append((T5CorrectionFilter(), True))

            else:
                raise ValueError(f"Unknown T5 mode: {self.t5_mode}")

        elif self.use_grmr:
            self.logger.info(f"GRMR-V3 correction enabled (mode: {self.grmr_mode})")

            if self.grmr_mode == "replace":
                # Replace spelling+grammar with GRMR-V3 only (simplest)
                filters.append((GRMRV3GrammarFilter(), False))  # GRMR-V3 doesn't return stats tuple

            elif self.grmr_mode == "hybrid":
                # GRMR-V3 first, then rule-based cleanup
                filters.append((GRMRV3GrammarFilter(), False))  # GRMR-V3 doesn't return stats tuple
                filters.append((SpellingCorrectionFilter(), False))
                filters.append((GrammarCorrectionFilterSafe(), True))

            elif self.grmr_mode == "supplement":
                # Keep existing filters, add GRMR-V3 at the end
                filters.append((SpellingCorrectionFilter(), False))
                filters.append((GrammarCorrectionFilterSafe(), True))
                filters.append((GRMRV3GrammarFilter(), False))  # GRMR-V3 doesn't return stats tuple

            else:
                raise ValueError(f"Unknown GRMR-V3 mode: {self.grmr_mode}")

        else:
            # Default pipeline (no ML models)
            filters.extend([
                (SpellingCorrectionFilter(), False),
                (GrammarCorrectionFilterSafe(), True),
            ])

        # TTS normalization and output generation always at the end
        filters.extend([
            (TTSNormalizer(), False),
            (output_generator, False)
        ])

        return filters

    def run(self):
        data = self.input_filepath
        for f, returns_stats in self.filters:
            start_time = time.time()
            log_extra = {
                "filter": f.__class__.__name__,
                "file": os.path.basename(self.input_filepath),
                "changes": 0,
                "duration_ms": None,
                "status": "ok",
                "error": None
            }
            try:
                original_text_blocks = [block['content'] for block in data.get('text_blocks', [])] if 'text_blocks' in data else []

                if returns_stats:
                    data, stats = f.process(data)
                    log_extra.update(stats)
                else:
                    data = f.process(data)

                end_time = time.time()
                log_extra['duration_ms'] = int((end_time - start_time) * 1000)

                if 'text_blocks' in data:
                    changes = sum(1 for i, block in enumerate(data['text_blocks'])
                                  if i < len(original_text_blocks) and block['content'] != original_text_blocks[i])
                    log_extra['changes'] = changes

                self.logger.info(f"Filter {f.__class__.__name__} executed successfully.", extra={'extra_data': log_extra})

            except Exception as e:
                end_time = time.time()
                log_extra['status'] = "failed"
                log_extra['error'] = str(e)
                log_extra['duration_ms'] = int((end_time - start_time) * 1000)
                self.logger.error(f"Filter {f.__class__.__name__} failed.", extra={'extra_data': log_extra})
                if self.fail_fast:
                    raise
        return data

def main():
    """Main function to run the pipeline from the command line."""
    parser = argparse.ArgumentParser(
        description='Corrects grammar in a Markdown or EPUB file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Grammar Model Integration Modes:
  replace     - Replace spelling+grammar with ML model only (simplest, recommended)
  hybrid      - ML model first, then rule-based cleanup (most comprehensive)
  supplement  - Keep existing filters, add ML model at the end (experimental)

Examples:
  # Standard pipeline (rule-based only)
  python -m pipeline.pipeline_runner document.md

  # T5 replacement mode (experimental, requires PyTorch)
  python -m pipeline.pipeline_runner --use-t5 document.md

  # GRMR-V3 replacement mode (experimental, requires llama-cpp-python)
  python -m pipeline.pipeline_runner --use-grmr document.md

  # GRMR-V3 hybrid mode (most thorough)
  python -m pipeline.pipeline_runner --use-grmr --grmr-mode hybrid document.md

Note: Cannot use --use-t5 and --use-grmr simultaneously.
        """
    )
    parser.add_argument('input_file', help='The path to the input file.')
    parser.add_argument('--fail-fast', action='store_true',
                       help='Stop pipeline on first filter failure.')
    parser.add_argument('--use-t5', action='store_true',
                       help='Enable T5-based correction (experimental, requires GPU for good performance)')
    parser.add_argument('--t5-mode', choices=['replace', 'hybrid', 'supplement'],
                       default='replace',
                       help='T5 integration mode (default: replace)')
    parser.add_argument('--use-grmr', action='store_true',
                       help='Enable GRMR-V3 GGUF-based correction (experimental, CPU or GPU)')
    parser.add_argument('--grmr-mode', choices=['replace', 'hybrid', 'supplement'],
                       default='replace',
                       help='GRMR-V3 integration mode (default: replace)')
    args = parser.parse_args()

    try:
        pipeline = PipelineRunner(
            args.input_file,
            fail_fast=args.fail_fast,
            use_t5=args.use_t5,
            t5_mode=args.t5_mode,
            use_grmr=args.use_grmr,
            grmr_mode=args.grmr_mode
        )
        result = pipeline.run()
        if result and 'output_filepath' in result:
            logging.info(f"File processed successfully. Corrected content written to: {result['output_filepath']}")
        else:
            logging.error("Pipeline execution failed.")
    except ValueError as e:
        logging.error(e)
    except RuntimeError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
