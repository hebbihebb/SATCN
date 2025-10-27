import argparse
from .filters.markdown_parser import MarkdownParserFilter, MarkdownOutputGenerator
from .filters.grammar_filter import GrammarCorrectionFilter
from .filters.spelling_filter import SpellingCorrectionFilter
from .filters.tts_normalizer import TTSNormalizer

class PipelineRunner:
    def __init__(self, filters):
        self.filters = filters

    def run(self, data):
        for f in self.filters:
            data = f.process(data)
        return data

def main():
    """Main function to run the pipeline from the command line."""
    parser = argparse.ArgumentParser(description='Corrects grammar in a Markdown file.')
    parser.add_argument('input_file', help='The path to the input Markdown file.')
    args = parser.parse_args()

    # Define the pipeline
    pipeline = PipelineRunner([
        MarkdownParserFilter(),
        SpellingCorrectionFilter(),
        GrammarCorrectionFilter(),
        TTSNormalizer(),
        MarkdownOutputGenerator()
    ])

    # Run the pipeline
    result = pipeline.run(args.input_file)
    print(f"File processed. Corrected content written to: {result['output_filepath']}")

if __name__ == '__main__':
    main()
