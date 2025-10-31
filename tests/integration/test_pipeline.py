import pytest
import os
from satcn.core.pipeline_runner import PipelineRunner

@pytest.fixture
def markdown_sample():
    return 'tests/samples/sample_markdown_basic.md'

@pytest.fixture
def epub_sample():
    return 'tests/samples/sample_epub_basic.epub'

def test_markdown_pipeline_integration(markdown_sample):
    """
    Tests that the full pipeline runs successfully on a markdown file.
    """
    runner = PipelineRunner(markdown_sample)
    runner.run()
    output_filepath = markdown_sample.replace('.md', '_corrected.md')
    assert os.path.exists(output_filepath)
    with open(output_filepath, 'r') as f:
        content = f.read()
        assert '# Sample Markdown' in content
        assert '* List item 1' in content
    os.remove(output_filepath)

def test_epub_pipeline_integration(epub_sample):
    """
    Tests that the full pipeline runs successfully on an EPUB file.
    """
    runner = PipelineRunner(epub_sample)
    runner.run()
    output_filepath = epub_sample.replace('.epub', '_corrected.epub')
    assert os.path.exists(output_filepath)
    # For the epub, we'll just check that the file was created.
    # A more thorough check would require parsing the epub, which is complex.
    os.remove(output_filepath)
