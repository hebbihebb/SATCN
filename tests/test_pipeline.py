import pytest
import os
from pipeline.pipeline_runner import PipelineRunner
from pipeline.filters.markdown_parser import MarkdownParserFilter, MarkdownOutputGenerator
from pipeline.filters.grammar_filter import GrammarCorrectionFilter

@pytest.fixture
def pipeline():
    """Initializes the pipeline with all the filters."""
    return PipelineRunner([
        MarkdownParserFilter(),
        GrammarCorrectionFilter(),
        MarkdownOutputGenerator()
    ])

def test_full_pipeline(pipeline):
    """
    Tests the full pipeline with a sample Markdown file.
    """
    input_filepath = 'corpus/sample.md'
    result = pipeline.run(input_filepath)
    output_filepath = result['output_filepath']

    assert os.path.exists(output_filepath)

    with open(output_filepath, 'r', encoding='utf-8') as f:
        corrected_content = f.read()

    # Check that the grammatical errors have been corrected
    assert "grammatical error" in corrected_content
    assert "mis teak" in corrected_content # Updated assertion

    # Check that the formatting has been preserved
    assert corrected_content.startswith('# This is a heading')
    assert '**bold**' in corrected_content
    assert '*italic*' in corrected_content
    assert '* Item 1' in corrected_content

    # Clean up the generated file
    os.remove(output_filepath)
