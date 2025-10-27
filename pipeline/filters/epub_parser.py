# pipeline/filters/epub_parser.py
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import uuid
import logging

class EpubParserFilter:
    """
    A filter that parses an EPUB file, extracts the text, and prepares a
    data structure for subsequent processing.
    """
    def process(self, filepath):
        """
        Processes an EPUB file and returns a dictionary containing the
        extracted text blocks and the parsed book.
        """
        try:
            book = epub.read_epub(filepath)
            text_blocks = []
            html_docs = {}

            for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                html_docs[item.get_name()] = soup
                for p in soup.find_all('p'):
                    if p.string and p.string.strip():
                        text_blocks.append({
                            'content': p.string.strip(),
                            'metadata': {'element': p, 'item_name': item.get_name()}
                        })

            return {
                'text_blocks': text_blocks,
                'book': book,
                'html_docs': html_docs,
                'format': 'epub',
                'filepath': filepath
            }
        except Exception as e:
            logging.error(f"Error parsing EPUB file {filepath}: {e}", exc_info=True)
            raise

class EpubOutputGenerator:
    """
    A filter that takes the modified data structure and book,
    and generates a corrected EPUB file.
    """
    def process(self, data):
        """
        Takes the data structure with modified text blocks and the Ebook,
        updates the book, and writes it to a file.
        """
        try:
            for block in data['text_blocks']:
                # The 'element' in metadata is the BeautifulSoup tag
                block['metadata']['element'].string = block['content']

            for item_name, soup in data['html_docs'].items():
                # Find the corresponding item in the book and update its content
                for item in data['book'].get_items_of_type(ebooklib.ITEM_DOCUMENT):
                    if item.get_name() == item_name:
                        item.set_content(str(soup).encode('utf-8'))
                        break

            # Ensure all TOC items have a UID
            for item in data['book'].toc:
                if not item.uid:
                    item.uid = str(uuid.uuid4())

            output_filepath = data['filepath'].replace('.epub', '_corrected.epub')
            epub.write_epub(output_filepath, data['book'], {})

            return {**data, 'output_filepath': output_filepath}
        except Exception as e:
            logging.error(f"Error generating EPUB file for {data.get('filepath', 'Unknown')}: {e}", exc_info=True)
            raise
