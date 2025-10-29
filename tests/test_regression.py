import pytest
import os
import difflib
from pipeline.pipeline_runner import PipelineRunner
from pipeline.utils.language_tool_utils import get_language_tool

REGRESSION_CORPUS_DIR = 'tests/regression_corpus'

def find_regression_files():
    """Finds all input files in the regression corpus."""
    input_files = []
    for filename in os.listdir(REGRESSION_CORPUS_DIR):
        if filename.startswith('input_') and filename.endswith('.md') and not filename.endswith('_corrected.md'):
            input_files.append(os.path.join(REGRESSION_CORPUS_DIR, filename))
    return input_files

@pytest.mark.parametrize("input_filepath", find_regression_files())
def test_regression(input_filepath):
    """
    Runs the pipeline on an input file and compares the output to the golden file.
    """
    tool, _ = get_language_tool()
    if tool is None:
        pytest.skip("LanguageTool backend unavailable; skipping golden diff checks")

    golden_filepath = input_filepath.replace('input_', 'golden_')

    # Run the pipeline
    runner = PipelineRunner(input_filepath)
    result = runner.run()
    output_filepath = result['output_filepath']

    # Compare the output to the golden file
    assert os.path.exists(output_filepath), f"Output file not created for {input_filepath}"

    # To provide a useful diff, we read the contents of both files
    with open(output_filepath, 'r', encoding='utf-8') as f:
        output_content = f.readlines()
    with open(golden_filepath, 'r', encoding='utf-8') as f:
        golden_content = f.readlines()

    # Strip trailing newlines to avoid comparison issues
    output_content = [line.rstrip('\n') for line in output_content]
    golden_content = [line.rstrip('\n') for line in golden_content]

    diff = list(difflib.unified_diff(golden_content, output_content, fromfile='golden', tofile='output'))

    assert not diff, f"Output differs from golden file for {input_filepath}:\n{''.join(diff)}"

    # Clean up the output file
    os.remove(output_filepath)
