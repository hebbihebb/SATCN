from ebooklib import epub

def create_minimal_epub(filepath):
    """
    Creates a minimal EPUB file for testing.
    """
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier('id123456')
    book.set_title('Sample Ebook')
    book.set_language('en')

    # Create chapter
    c1 = epub.EpubHtml(title='Intro', file_name='chap_01.xhtml', lang='en')
    c1.content=u'<h1>Introduction</h1><p>This is a sample ebook for integration testing.</p>'

    # Add chapter to book
    book.add_item(c1)

    # Define Table of Contents
    book.toc = (epub.Link('chap_01.xhtml', 'Introduction', 'intro'),)

    # Add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define spine
    book.spine = ['nav', c1]

    # Write to file
    epub.write_epub(filepath, book, {})

if __name__ == '__main__':
    create_minimal_epub('tests/samples/sample_epub_basic.epub')
