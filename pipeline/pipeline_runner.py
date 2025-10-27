import argparse
import os
import logging
import time
from .filters.markdown_parser import MarkdownParserFilter, MarkdownOutputGenerator
from .filters.epub_parser import EpubParserFilter, EpubOutputGenerator
from .filters.grammar_filter_safe import GrammarCorrectionFilterSafe
from .filters.spelling_filter import SpellingCorrectionFilter
from .filters.tts_normalizer import TTSNormalizer
from .utils.logging_setup import setup_logging

class PipelineRunner:
    def __init__(self, input_filepath, fail_fast=False):
        self.input_filepath = input_filepath
        self.fail_fast = fail_fast
        self.logger = setup_logging()
        self.filters = self._get_filters()

    def _get_filters(self):
        _, file_extension = os.path.splitext(self.input_filepath)
        if file_extension.lower() == '.md':
            parser_filter = MarkdownParserFilter()
            output_generator = MarkdownOutputGenerator()
        elif file_extension.lower() == '.epub':
            parser_filter = EpubParserFilter()
            output_generator = EpubOutputGenerator()
        else:
            raise ValueError(f"Unsupported file type '{file_extension}'. Please provide a .md or .epub file.")

        return [
            (parser_filter, False),
            (SpellingCorrectionFilter(), False),
            (GrammarCorrectionFilterSafe(), True),
            (TTSNormalizer(), False),
            (output_generator, False)
        ]

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
    parser = argparse.ArgumentParser(description='Corrects grammar in a Markdown or EPUB file.')
    parser.add_argument('input_file', help='The path to the input file.')
    parser.add_argument('--fail-fast', action='store_true', help='Stop pipeline on first filter failure.')
    args = parser.parse_args()

    try:
        pipeline = PipelineRunner(args.input_file, args.fail_fast)
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
