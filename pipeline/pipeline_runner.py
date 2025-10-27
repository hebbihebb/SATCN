import argparse
import os
import logging
from .filters.markdown_parser import MarkdownParserFilter, MarkdownOutputGenerator
from .filters.epub_parser import EpubParserFilter, EpubOutputGenerator
from .filters.grammar_filter import GrammarCorrectionFilter
# from .filters.spelling_filter import SpellingCorrectionFilter
from .filters.tts_normalizer import TTSNormalizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PipelineRunner:
    def __init__(self, filters):
        self.filters = filters

    def run(self, data):
        try:
            for f in self.filters:
                logging.info(f"Executing filter: {f.__class__.__name__}")
                data = f.process(data)
            return data
        except Exception as e:
            logging.error(f"An error occurred during pipeline execution: {e}", exc_info=True)
            return None

def main():
    """Main function to run the pipeline from the command line."""
    parser = argparse.ArgumentParser(description='Corrects grammar in a Markdown or EPUB file.')
    parser.add_argument('input_file', help='The path to the input file.')
    args = parser.parse_args()

    input_filepath = args.input_file
    logging.info(f"Processing file: {input_filepath}")

    _, file_extension = os.path.splitext(input_filepath)

    if file_extension.lower() == '.md':
        parser_filter = MarkdownParserFilter()
        output_generator = MarkdownOutputGenerator()
    elif file_extension.lower() == '.epub':
        parser_filter = EpubParserFilter()
        output_generator = EpubOutputGenerator()
    else:
        logging.error(f"Unsupported file type '{file_extension}'. Please provide a .md or .epub file.")
        return

    # Define the pipeline
    pipeline = PipelineRunner([
        parser_filter,
        # SpellingCorrectionFilter(),
        GrammarCorrectionFilter(),
        TTSNormalizer(),
        output_generator
    ])

    # Run the pipeline
    result = pipeline.run(input_filepath)
    if result and 'output_filepath' in result:
        logging.info(f"File processed successfully. Corrected content written to: {result['output_filepath']}")
    else:
        logging.error("Pipeline execution failed.")

if __name__ == '__main__':
    main()
