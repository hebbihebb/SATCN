import ebooklib
from ebooklib import epub

def create_epub(title, author, content, file_path):
    book = epub.EpubBook()
    book.set_identifier('id123456')
    book.set_title(title)
    book.set_language('en')
    book.add_author(author)

    c1 = epub.EpubHtml(title='Chapter 1', file_name='chap_1.xhtml', lang='en')
    c1.content = u'<html><body><h1>Chapter 1</h1><p>%s</p></body></html>' % content
    book.add_item(c1)
    book.toc = (epub.Link('chap_1.xhtml', 'Chapter 1', 'chap_1'),)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav', c1]
    epub.write_epub(file_path, book, {})

if __name__ == '__main__':
    create_epub(
        'Small Epub',
        'Jules',
        'This is a small EPUB document.',
        'corpus/small.epub'
    )
    create_epub(
        'Medium Epub',
        'Jules',
        'This is a medium-sized EPUB document. It has more content than the small document, but not as much as the large document.',
        'corpus/medium.epub'
    )
    create_epub(
        'Large Epub',
        'Jules',
        'This is a large EPUB document. It has a lot of content to test the performance of the pipeline.' * 50,
        'corpus/large.epub'
    )
