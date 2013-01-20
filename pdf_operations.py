#!usr/bin/python

import os

from pyPdf import PdfFileWriter, PdfFileReader

def merge_pdf(new_filename, pdfs, encryp=False, user_pw="", owner_pw=None, lvl=128):
    """
    Merges pdfs into one pdf called new_filename.
    """
    output = PdfFileWriter()
        
    for p in pdfs:
        pdf = PdfFileReader(open(p, "rb"))
        for page_num in range(pdf.getNumPages()):
            page = pdf.getPage(page_num)
            output.addPage(page)
    
    with file(new_filename, "wb") as outputStream: 
        outputStream = open(new_filename, "wb")
        
        if encryp and lvl == 128:
            output.encrypt(user_pw, owner_pw, True)
        elif encryp:
            output.encrypt(user_pw, owner_pw, False)
        output.write(outputStream)

def get_pdfinfo(pdf_file):
    """
    Obtains information from pdf_file
    """
    pdf = PdfFileReader(open(pdf_file, "rb"))
    if not pdf.isEncrypted:
        info = {}
        info["numPages"] = pdf.numPages
        info["filepath"] = os.path.abspath(pdf_file)
        
        info.update(pdf.getDocumentInfo())
        return info
    else:
        return None
    
