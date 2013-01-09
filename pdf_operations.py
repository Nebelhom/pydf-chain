#!usr/bin/python

from pyPdf import PdfFileWriter, PdfFileReader

def merge_pdf(new_filename, *path2pdf):
    output = PdfFileWriter()
    pdfs = []
    
    for pdf in path2pdf:
        pdfs.append(PdfFileReader(file(pdf, "rb")))
        
    for pdf in pdfs:
        for page_num in range(pdf.getNumPages()):
            page = pdf.getPage(page_num)
            output.addPage(page)
    
    with file(new_filename, "wb") as outputStream: 
        outputStream = file(new_filename, "wb")
        output.write(outputStream)
        
merge_pdf("test_name","JVogelLebenslauf.pdf","JVogelZeugnisse.pdf")

# PdfFileReader(file("JVogelLebenslauf.pdf", "rb"))
#input2 = PdfFileReader(file("JVogelZeugnisse.pdf", "rb"))
