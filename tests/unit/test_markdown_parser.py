import pytest
import os
from satcn.core.filters.markdown_parser import MarkdownParserFilter, MarkdownOutputGenerator

@pytest.fixture
def markdown_file(tmp_path):
    """Create a dummy markdown file for testing."""
    content = """# Header 1
## Header 2
This is a paragraph with some *italic* and **bold** text.

- List item 1
- List item 2
"""
    file_path = tmp_path / "test.md"
    file_path.write_text(content)
    return str(file_path)

@pytest.mark.xfail(reason="Nested inline formatting currently causes duplicated text during serialization")
def test_markdown_round_trip(markdown_file):
    """
    Tests that parsing a markdown file and then immediately generating it
    results in the same content, ignoring whitespace differences.
    """
    parser = MarkdownParserFilter()
    generator = MarkdownOutputGenerator()

    # Parse the markdown file
    parsed_data = parser.process(markdown_file)

    # Immediately generate the markdown file from the parsed data
    generated_data = generator.process(parsed_data)

    # Read the content of the original and generated files
    with open(markdown_file, 'r', encoding='utf-8') as f:
        original_content = f.read()

    with open(generated_data['output_filepath'], 'r', encoding='utf-8') as f:
        generated_content = f.read()

    # Compare the files line by line, ignoring leading/trailing whitespace and blank lines.
    original_lines = [line.strip() for line in original_content.strip().splitlines() if line.strip()]
    generated_lines = [line.strip() for line in generated_content.strip().splitlines() if line.strip()]
    assert original_lines == generated_lines
