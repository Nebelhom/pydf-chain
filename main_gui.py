#!usr/bin/python

"""
up method still problematic. mostly to do with types
"""

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
        self.merge_model = builder.get_object("merge_pdf_liststore")
        self.merge_view = builder.get_object("merge_pdf_treeview")
        # columns
        self.source_col = self.merge_view.get_column(0)
        self.pw_col = self.merge_view.get_column(1)
        self.numPage_col = self.merge_view.get_column(2)
        
        # connect the signals
        builder.connect_signals(self)
        
    def on_main_window_delete_event(self, *args):
        Gtk.main_quit()
        
    def refresh_treeview(self, pdfs):

        # clear the treeview - CRUCIAL - Otherwise duplication in a row        
        self.source_col.clear()
        self.pw_col.clear()
        self.numPage_col.clear()
        
        # Renderer
        source_render = Gtk.CellRendererText()
        pw_render = Gtk.CellRendererText()
        pw_render.set_property("editable", True)
        numPage_render = Gtk.CellRendererText()
        
        # I have no idea how that works
        # see harishankar.org/blog/entry.php/python-gtk-howto-cell-rendering-a-treeview-created-in-glade
        self.source_col.pack_start(source_render, False)
        self.pw_col.pack_start(pw_render, False)
        self.numPage_col.pack_start(numPage_render, False)
        
        self.source_col.add_attribute(source_render, "text", 0)
        self.pw_col.add_attribute(pw_render, "text", 1)
        self.numPage_col.add_attribute(numPage_render, "text", 2)
    
    def on_addbutton_clicked(self, button):
        """
        Add one or many pdf files to the treeview.
        """
        dialog = Gtk.FileChooserDialog("Please choose a file", self.window, #builder.get_object("main_window"),
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_pdf_filters(dialog)
        dialog.set_select_multiple(True)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            
            pdfs = dialog.get_filenames()
        
            for pdf in pdfs:
                # add to the list store
                info = pdf_ops.get_pdfinfo(pdf)
                self.merge_model.append([info["filepath"]," ",info["numPages"]])
            self.refresh_treeview(pdfs)
                
        dialog.destroy()
        
    def add_pdf_filters(self, dialog):
        """
        Apply filter to only allow pdf files to be chosen.
        """
        filter_pdf = Gtk.FileFilter()
        filter_pdf.set_name("PDF files")
        filter_pdf.add_mime_type("application/pdf")
        dialog.add_filter(filter_pdf)
        
    def on_removebutton_clicked(self, button):
        """
        Remove one or many pdf files to the treeview.
        """
        # see http://harishankar.org/blog/entry.php/python-gtk-howto-deleting-multiple-selected-items-from-a-gtk-treeview     
        
        # get the selected rows as paths
        sel_model, sel_rows = self.merge_view.get_selection().get_selected_rows()

        # store the treeiters from paths
        iters = []
        for row in sel_rows:
            iters.append(self.merge_model.get_iter(row))
        
        # remove the rows (treeiters)
        for i in iters:
            if i is not None:
                self.merge_model.remove(i)
        
    def on_copybutton_clicked(self, button):
        print "copy"
        
    def on_upbutton_clicked(self, button):
        """
        Moves each selection one position up.
        """
        # get the selected rows as paths
        sel_model, sel_rows = self.merge_view.get_selection().get_selected_rows()
        print type(sel_rows[0])
        if sel_rows[0] == 0 or len(self.merge_model) == 0:
            pass
        else:
            for pos in sel_rows:
                self.merge_model.swap(self.merge_model.get_iter(pos),
                                      self.merge_model.get_iter(pos).prev())
        
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