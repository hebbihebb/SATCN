# pipeline/filters/markdown_parser.py

import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension

class _TextExtractorTreeprocessor(Treeprocessor):
    """
    A treeprocessor that extracts all text content from a markdown tree
    and stores it in a list of dictionaries.
    """
    def run(self, root):
        self.md.text_blocks = []
        self._extract_text(root)
        return root

    def _extract_text(self, element):
        # Extract text from the current element
        if element.text and element.text.strip():
            self.md.text_blocks.append({
                'content': element.text.strip(),
                'metadata': {'element': element, 'is_tail': False}
            })

        # Recursively process child elements
        for child in element:
            self._extract_text(child)
            # After processing a child, extract its tail text
            if child.tail and child.tail.strip():
                self.md.text_blocks.append({
                    'content': child.tail.strip(),
                    'metadata': {'element': child, 'is_tail': True}
                })

class _MarkdownExtractionExtension(Extension):
    """
    A markdown extension to enable text extraction.
    """
    def extendMarkdown(self, md):
        # The priority is set to a high number to ensure it runs after other treeprocessors
        extractor = _TextExtractorTreeprocessor(md)
        md.treeprocessors.register(extractor, 'text_extractor', 100)

        # After the tree is processed, we store the root element in the markdown instance
        class RootStoringTreeprocessor(Treeprocessor):
            def run(self, root):
                md.root = root
                return root
        md.treeprocessors.register(RootStoringTreeprocessor(md), 'root_storer', 0)

class MarkdownParserFilter:
    """
    A filter that parses a Markdown file, extracts the text, and prepares a
    data structure for subsequent processing.
    """
    def __init__(self):
        self.md_ext = _MarkdownExtractionExtension()
        self.md = markdown.Markdown(extensions=[self.md_ext])

    def process(self, filepath):
        """
        Processes a Markdown file and returns a dictionary containing the
        extracted text blocks and the parsed tree.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Reset the markdown instance to clear state from previous runs
        self.md.reset()

        # The convert method will parse the text and run our treeprocessor
        self.md.convert(content)

        # The treeprocessor stored the extracted text in the markdown instance
        text_blocks = getattr(self.md, 'text_blocks', [])

        # The root of the parsed tree is also available
        tree = self.md.root

        return {
            'text_blocks': text_blocks,
            'tree': tree,
            'format': 'markdown',
            'filepath': filepath
        }

class MarkdownOutputGenerator:
    """
    A filter that takes the modified data structure and tree,
    and generates a corrected Markdown file.
    """
    def process(self, data):
        """
        Takes the data structure with modified text blocks and the ElementTree,
        updates the tree, serializes it back to Markdown, and writes it to a file.
        """
        # 1. Update the tree with corrected text
        for block in data['text_blocks']:
            element = block['metadata']['element']
            is_tail = block['metadata']['is_tail']
            if is_tail:
                element.tail = ' ' + block['content'] if block['content'] else ''
            else:
                element.text = block['content']

        # 2. Serialize the tree back to Markdown
        markdown_content = self._serialize_children(data['tree'])

        # 3. Write to a new file
        output_filepath = data['filepath'].replace('.md', '_corrected.md')
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return {**data, 'output_filepath': output_filepath}

    def _get_markdown_syntax(self, tag):
        """Returns the prefix and suffix for a given Markdown tag."""
        return {
            'h1': ('# ', ''), 'h2': ('## ', ''), 'h3': ('### ', ''),
            'h4': ('#### ', ''), 'h5': ('##### ', ''), 'h6': ('###### ', ''),
            'li': ('* ', ''),
            'strong': ('**', '**'), 'em': ('*', '*'), 'code': ('`', '`')
        }.get(tag, ('', ''))

    def _is_block_element(self, tag):
        """Checks if a tag is a block-level element."""
        return tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li']

    def _serialize_element(self, element):
        """Recursively serializes an element and its children to Markdown."""
        parts = []

        prefix, suffix = self._get_markdown_syntax(element.tag)
        parts.append(prefix)

        if element.text:
            parts.append(element.text)

        for child in element:
            parts.append(self._serialize_element(child))

        parts.append(suffix)

        if self._is_block_element(element.tag):
             parts.append('\n\n')

        if element.tail:
            parts.append(element.tail)

        return "".join(parts)

    def _serialize_children(self, element):
        """Serializes the children of a given element."""
        return "".join(self._serialize_element(child) for child in element)
