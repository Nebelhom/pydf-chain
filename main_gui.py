#!usr/bin/python

import sys
import os

from gi.repository import Gtk

import pdf_operations as pdf_ops

class PyDF_Chain:
    
    def __init__(self):
        try:
            builder = Gtk.Builder()
            builder.add_from_file("main_gui.glade")
        except:
            self.error_message("Failed to load UI XML file: main_gui.glade")
            sys.exit(1)        

        self.window = builder.get_object("main_window")
        
        # Merge PDF Tab
        self.merge_store = builder.get_object("merge_pdf_liststore")
        self.merge_treeview = builder.get_object("merge_pdf_treeview")
        # columns
        self.merge_columns = [
            builder.get_object("treeviewsource"),
            builder.get_object("treeviewpassword"),
            builder.get_object("treeviewpages")
            ]
        
        # connect the signals
        builder.connect_signals(self)
        
    def on_main_window_delete_event(self, *args):
        Gtk.main_quit()
    
    def on_addbutton_clicked(self, button):
        dialog = Gtk.FileChooserDialog("Please choose a file", self.window, #builder.get_object("main_window"),
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filters(dialog)
        dialog.set_select_multiple(True)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            pdfs = dialog.get_filenames()
            for pdf in pdfs:
                # add to the list store
                info = pdf_ops.get_pdfinfo(pdf)
                pdf_iter = self.merge_store.append([info["filepath"]," ",info["numPages"]])
                
                # display on the list
                column = Gtk.TreeViewColumn()
                
                # Renderer
                #source_file = Gtk.CellRendererText()
                #password = Gtk.CellRendererText() # Change later to entry widget
                #numPages = Gtk.CellRendererText() # Should render an int
                                
                
                #column0 = Gtk.TreeViewColumn("treeviewsource", source_file, text=0)
                #column1 = Gtk.TreeViewColumn("treeviewpassword", password, text=0)
                #column2 = Gtk.TreeViewColumn("treeviewpages", numPages, text=0)
        
        dialog.destroy()
        
    def add_filters(self, dialog):
        filter_pdf = Gtk.FileFilter()
        filter_pdf.set_name("PDF files")
        filter_pdf.add_mime_type("application/pdf")
        dialog.add_filter(filter_pdf)
        
    def on_removebutton_clicked(self, button):
        print "remove"
        
    def on_copybutton_clicked(self, button):
        print "copy"
        
    def on_upbutton_clicked(self, button):
        print "up"
        
    def on_downbutton_clicked(self, button):
        print "down"
        
    def on_savebutton_clicked(self, button):
        print "save"

    def error_message(self, message):
        raise IOError(message)
        
    def run(self):
        self.window.show_all()
        Gtk.main()   

if __name__ == "__main__":
    pydf_chain = PyDF_Chain()
    pydf_chain.run()