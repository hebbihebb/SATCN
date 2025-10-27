import argparse
import os
import shutil
from pipeline.pipeline_runner import PipelineRunner

def add_to_regression(input_filepath):
    """
    Runs the pipeline on an input file and adds the input and output to the
    regression corpus.
    """
    # Get the slug from the input filepath
    slug = os.path.splitext(os.path.basename(input_filepath))[0]

    # Run the pipeline
    runner = PipelineRunner(input_filepath)
    result = runner.run()
    output_filepath = result['output_filepath']

    # Copy the input and output files to the regression corpus
    regression_corpus_dir = 'tests/regression_corpus'
    new_input_filepath = os.path.join(regression_corpus_dir, f'input_{slug}.md')
    new_golden_filepath = os.path.join(regression_corpus_dir, f'golden_{slug}.md')
    shutil.copyfile(input_filepath, new_input_filepath)
    shutil.copyfile(output_filepath, new_golden_filepath)

    print(f"Added {new_input_filepath} and {new_golden_filepath} to the regression corpus.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add a file to the regression corpus.')
    parser.add_argument('input_file', help='The path to the input file.')
    args = parser.parse_args()
    add_to_regression(args.input_file)
