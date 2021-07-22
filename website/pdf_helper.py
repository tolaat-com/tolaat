import PyPDF2
import tempfile

from os.path import join, dirname

import logging


def censor_pages(pdf_stream, censored_pages):
    if not censored_pages:
        return pdf_stream

    d = dirname(__file__)
    censorship = join(d, 'resources', 'censorship-message-red.pdf')
    censorship_f = open(censorship, 'rb')
    reader = PyPDF2.PdfFileReader(censorship_f)
    censorship_page = reader.getPage(0)

    reader = PyPDF2.PdfFileReader(pdf_stream)
    writer = PyPDF2.PdfFileWriter()
    pages = reader.getNumPages()
    for i in range(pages):
        page = reader.getPage(i)

        if str(i+1) in censored_pages:
            writer.addPage(censorship_page)
        else:
            writer.addPage(page)

    f = tempfile.SpooledTemporaryFile()
    writer.write(f)
    f.seek(0)

    censorship_f.close()

    return f


def count_pages(file):
    try:
        with open(file, 'rb') as f:
            reader = PyPDF2.PdfFileReader(f)
            return reader.getNumPages()
    except:
        logging.warning('Exception counting pages', exc_info=True)
        return -1