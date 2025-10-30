import argparse
import os
import logging
import time
from .filters.markdown_parser import MarkdownParserFilter, MarkdownOutputGenerator
from .filters.epub_parser import EpubParserFilter, EpubOutputGenerator
from .filters.grammar_filter_safe import GrammarCorrectionFilterSafe
from .filters.spelling_filter import SpellingCorrectionFilter
from .filters.tts_normalizer import TTSNormalizer
from .filters.t5_correction_filter import T5CorrectionFilter
from .utils.logging_setup import setup_logging

class PipelineRunner:
    def __init__(self, input_filepath, fail_fast=False, use_t5=False, t5_mode="replace"):
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
        """
        self.input_filepath = input_filepath
        self.fail_fast = fail_fast
        self.use_t5 = use_t5
        self.t5_mode = t5_mode
        self.logger = setup_logging()
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

        # Build filter pipeline based on T5 configuration
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

        else:
            # Default pipeline (no T5)
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
T5 Integration Modes:
  replace     - Replace spelling+grammar with T5 only (simplest, recommended)
  hybrid      - T5 first, then rule-based cleanup (most comprehensive)
  supplement  - Keep existing filters, add T5 at the end (experimental)

Examples:
  # Standard pipeline (no T5)
  python -m pipeline.pipeline_runner document.md

  # T5 replacement mode (experimental)
  python -m pipeline.pipeline_runner --use-t5 document.md

  # T5 hybrid mode
  python -m pipeline.pipeline_runner --use-t5 --t5-mode hybrid document.md
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
    args = parser.parse_args()

    try:
        pipeline = PipelineRunner(
            args.input_file,
            fail_fast=args.fail_fast,
            use_t5=args.use_t5,
            t5_mode=args.t5_mode
        )
        result = pipeline.run()
        if result and 'output_filepath' in result:
            logging.info(f"File processed successfully. Corrected content written to: {result['output_filepath']}")
        else:
            logging.error("Pipeline execution failed.")
    except ValueError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
