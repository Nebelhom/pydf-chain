#!usr/bin/python

"""
up method still problematic. mostly to do with types

Current finding:
    
    Gtk.TreeModel has a get_previous and get_next iter method
    That way could insert elements etc.
    
    Gtk.TreeModel should be self.merge_model but that is shown as
    Gtk.ListStore. In the doc this is the same concept.
    
    => explanation. I called it wrongly ;) ...didn't help so far 
    
    Traceback (most recent call last):
  File "/home/nebelhom/SpyderWorkspace/pydf-chain/main_gui.py", line 146, in on_upbutton_clicked
    self.merge_model.insert(row, prev_iter)
  File "/usr/lib/python2.7/dist-packages/gi/overrides/Gtk.py", line 989, in insert
    return self._do_insert(position, row)
  File "/usr/lib/python2.7/dist-packages/gi/overrides/Gtk.py", line 970, in _do_insert
    row, columns = self._convert_row(row)
  File "/usr/lib/python2.7/dist-packages/gi/overrides/Gtk.py", line 822, in _convert_row
    if len(row) != n_columns:
TypeError: object of type 'TreeIter' has no len()

New approach with Gtk.TreePath has a method called up and down.

If that does what it should, then I am happy but it has strange
behaviour. - it doesn't

http://www.gtk.org/api/2.6/gtk/GtkTreeModel.html#gtk-tree-path-up
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

        # Make sure that not none or the first element is selected
        if sel_rows != []:
            # store the treeiters from paths
            iters = []
            for row in sel_rows:
                iters.append(self.merge_model.get_iter(row))
            
            for i in iters:
                prev_iter = self.merge_model.iter_previous(i)
                if i is not None and prev_iter is not None:
                    self.merge_model.swap(i, prev_iter)
                    
    def on_downbutton_clicked(self, button):
        """
        Moves each selection one position down.
        """
        # get the selected rows as paths
        sel_model, sel_rows = self.merge_view.get_selection().get_selected_rows()

        # Make sure that something is selected
        if sel_rows != []: 

            # store the treeiters from paths
            iters = []
            for row in sel_rows:
                iters.append(self.merge_model.get_iter(row))
            iters.reverse()     # Avoid strange behaviour that way      
            
            for i in iters:
                next_iter = self.merge_model.iter_next(i)
                if i is not None and next_iter is not None:
                    self.merge_model.swap(i, next_iter)
        
    def on_savebutton_clicked(self, button):
        if len(self.merge_model) == 0:
            dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.WARNING,
            Gtk.ButtonsType.OK, "Please add pdf files to your list")
            dialog.format_secondary_text(
                "There are no valid pdf files to be merged.")
            response = dialog.run()
    
            dialog.destroy()
                
        else:
            dialog = Gtk.FileChooserDialog("Please choose a file", self.window, #builder.get_object("main_window"),
                Gtk.FileChooserAction.SAVE,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    
            self.add_pdf_filters(dialog)
            response = dialog.run()
            
            # Still add test if file already exists
            # and for if pdf not mentionend
            if response == Gtk.ResponseType.OK:
                if os.path.exists(dialog.get_filename()):
                    dlg = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.WARNING,
                    Gtk.ButtonsType.OK_CANCEL, ("The file " + dialog.get_filename() + " already exists!"))
                    dlg.format_secondary_text("Are you sure you want to overwrite?")
                    yes_no = dlg.run()
                    if yes_no == Gtk.ResponseType.CANCEL:
                        pass
                    else:
                        self.merge_pdfs(dialog.get_filename())
                    dlg.destroy()             
                else:
                    self.merge_pdfs(dialog.get_filename())
                    
            dialog.destroy()
            
    def merge_pdfs(self, save_path):
        if not save_path.endswith(".pdf"):
            save_path = save_path + ".pdf"               
        pdfs = []
        for row in self.merge_model:
            pdfs.append(row[0])
        pdf_ops.merge_pdf(save_path, pdfs)
        

    def error_message(self, message):
        raise IOError(message)
        
    def run(self):
        self.window.show_all()
        Gtk.main()   

if __name__ == "__main__":
    pydf_chain = PyDF_Chain()
    pydf_chain.run()