#!usr/bin/python

import os

from pyPdf import PdfFileWriter, PdfFileReader

class PasswordError(Exception):
    """Error when invalid password is given"""

def merge_pdf(new_filename, pdfs, encryp=False, user_pw="", owner_pw=None, lvl=128):
    """
    Merges pdfs into one pdf called new_filename.
    
    pdf: list of tuples (path=string, password=string)
    """
    output = PdfFileWriter()
        
    for path, pw in pdfs:
        pdf = PdfFileReader(open(path, "rb"))
        
        if pdf.isEncrypted:
            decryption = pdf.decrypt(pw)
            if decryption == 0:
                raise PasswordError
        
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
        
def throw():
    raise PasswordError
    
if __name__ == "__main__":
    #merge_pdf("merge_encrypt")
    if throw() == PasswordError:
        print "huzzah"