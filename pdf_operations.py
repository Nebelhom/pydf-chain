#!usr/bin/python

import os

from pyPdf import PdfFileWriter, PdfFileReader

def merge_pdf(new_filename, pdfs):
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
        output.write(outputStream)

def get_pdfinfo(pdf_file):
    """
    Obtains information from pdf_file
    """
    pdf = PdfFileReader(open(pdf_file, "rb"))
    info = {}
    info["numPages"] = pdf.numPages
    info["filepath"] = os.path.abspath(pdf_file)
    
    info.update(pdf.getDocumentInfo())
    
    return info
    
    
#print get_pdfinfo("JVogelLebenslauf.pdf")

#merge_pdf("test_name","JVogelLebenslauf.pdf","JVogelZeugnisse.pdf")
