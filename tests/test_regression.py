import pytest
import os
import glob
from pipeline.pipeline_runner import PipelineRunner
from pipeline.filters.markdown_parser import MarkdownParserFilter, MarkdownOutputGenerator
from pipeline.filters.grammar_filter import GrammarCorrectionFilter
from pipeline.filters.spelling_filter import SpellingCorrectionFilter
from pipeline.filters.tts_normalizer import TTSNormalizer

def find_test_files():
    """Finds all input files in the regression corpus."""
    return [f for f in glob.glob('tests/regression_corpus/input*.md') if '_corrected' not in f]

@pytest.fixture(scope="session")
def regression_pipeline():
    """Initializes the pipeline with all the filters for regression testing."""
    return PipelineRunner([
        MarkdownParserFilter(),
        SpellingCorrectionFilter(),
        GrammarCorrectionFilter(),
        TTSNormalizer(),
        MarkdownOutputGenerator()
    ])

@pytest.mark.parametrize("input_filepath", find_test_files())
def test_regression_corpus(regression_pipeline, input_filepath):
    """
    Tests the full pipeline with a regression test corpus.
    """
    print(f"Running test for {input_filepath}")
    golden_filepath = input_filepath.replace('input', 'golden')

    result = regression_pipeline.run(input_filepath)
    output_filepath = result['output_filepath']

    assert os.path.exists(output_filepath)

    with open(output_filepath, 'r', encoding='utf-8') as f:
        corrected_content = f.read()

    with open(golden_filepath, 'r', encoding='utf-8') as f:
        golden_content = f.read()

    assert corrected_content == golden_content

    # Clean up the generated file
    os.remove(output_filepath)
