#!usr/bin/python

"""
Get Progress bar working.

then figure out why special chars
like ( or ) are not working in adding files to the list...

=> This is a problem with pyPDF

"""

import sys
import os
import threading
from functools import partial

from gi.repository import Gtk, Gdk, GObject

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
        
        # Password related Gtk.Text entries
        self.owner_pw = builder.get_object("owner_pw_entry")
        self.owner_pw.set_visibility(False)
        self.user_pw = builder.get_object("user_pw_entry")
        self.user_pw.set_visibility(False)
        
        # Encryption radio buttons
        self.radio_none = builder.get_object("encrypt_radio_none")
        #self.radio_none.set_label("None")
        self.radio_128 = builder.get_object("encrypt_radio_128")
        #self.radio_128.set_label("128")
        self.radio_40 = builder.get_object("encrypt_radio_40")
        #self.radio_40.set_label("40")
        
        self.radio_group = self.radio_128.get_group()
        
        self.radio_none.set_active(True)
        
        # Progress
        self.progressbar = builder.get_object("progressbar")
        
        # connect the signals
        builder.connect_signals(self)
        
    def on_timeout(self, user_data):
        """
        Update value on the progress bar
        """

        # As this is a timeout function, return True so that it
        # continues to get called
        return True        
        
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
        pw_render.connect("edited", self.update_pw_entry)
        
       
        
        numPage_render = Gtk.CellRendererText()
        
        # I have no idea how that works
        # see harishankar.org/blog/entry.php/python-gtk-howto-cell-rendering-a-treeview-created-in-glade
        self.source_col.pack_start(source_render, False)
        self.pw_col.pack_start(pw_render, False)
        self.numPage_col.pack_start(numPage_render, False)
        
        self.source_col.add_attribute(source_render, "text", 0)
        self.pw_col.add_attribute(pw_render, "text", 1)
        self.numPage_col.add_attribute(numPage_render, "text", 2)
        
    def update_pw_entry(self, widget, path, new_pw):
        """
        Updates the password entry
        """
        self.merge_model[path][1] = new_pw

    def get_selected_iters(self):
        """
        Get selected items and return respective iters
        """
        # see http://harishankar.org/blog/entry.php/python-gtk-howto-deleting-multiple-selected-items-from-a-gtk-treeview     
        
        # get the selected rows as paths
        sel_model, sel_rows = self.merge_view.get_selection().get_selected_rows()

        # store the treeiters from paths
        iters = []
        for row in sel_rows:
            iters.append(self.merge_model.get_iter(row))
            
        return iters
        
    def get_active_radio(self, radio_group):
        """
        Returns the active radio_button's label.
        """
        for radio in radio_group:
            if radio.get_active():
                return radio.get_label()
                
    def get_encryption_details(self):
        """
        Checks if the user wants an encryption level.
        
        Returns parameters for either case.
        
        Factors:
        - Radio button not None.
        - Owner or user pw != ''
        """
        o_pw = self.owner_pw.get_text()
        u_pw = self.user_pw.get_text()
        radio_label = self.get_active_radio(self.radio_group)
        
        if (o_pw != '' or u_pw != '') and radio_label != 'None':
            # from merge_pdf params            
            # encryp=False, user_pw="", owner_pw=None, lvl=128
            if o_pw == '':
                return True, u_pw, None, int(radio_label)
            if u_pw == '':
                return True, o_pw, None, int(radio_label)
            else:
                return True, u_pw, o_pw, int(radio_label)
        else:
            return True, '', None, 128
            
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
                if info != None:
                    self.merge_model.append([info["filepath"],"",
                                             info["numPages"]])
                else:
                    self.merge_model.append([pdf,"", 0])
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
        iters = self.get_selected_iters()
        
        # remove the rows (treeiters)
        for i in iters:
            if i is not None:
                self.merge_model.remove(i)
        
    def on_copybutton_clicked(self, button):
        """
        Creates a copy right behind each selection.
        """
        iters = self.get_selected_iters()
        
        for i in iters:
            if i is not None:
                # Need to supply list not Gtk.Treeiter
                self.merge_model.append(self.merge_model[i][:]) 
        
    def on_upbutton_clicked(self, button):
        """
        Moves each selection one position up.
        """      
        iters = self.get_selected_iters()

        # Make sure that not none or the first element is selected
        if iters != []:
            for i in iters:
                prev_iter = self.merge_model.iter_previous(i)
                if i is not None and prev_iter is not None:
                    self.merge_model.swap(i, prev_iter)
                    
    def on_downbutton_clicked(self, button):
        """
        Moves each selection one position down.
        """
        
        iters = self.get_selected_iters()

        # Make sure that something is selected
        if iters != []:      
            for i in iters:
                next_iter = self.merge_model.iter_next(i)
                if i is not None and next_iter is not None:
                    self.merge_model.swap(i, next_iter)
        
    def on_savebutton_clicked(self, button):
        """
        Saves the merged pdf file.
        """
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
            
            # Check if file exists and if .pdf suffix
            if response == Gtk.ResponseType.OK:
                if os.path.exists(dialog.get_filename()):
                    dlg = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.WARNING,
                    Gtk.ButtonsType.OK_CANCEL, ("The file " + dialog.get_filename() + " already exists!"))
                    dlg.format_secondary_text("Are you sure you want to overwrite?")
                    yes_no = dlg.run()
                    
                    if yes_no == Gtk.ResponseType.CANCEL:
                        pass
                    else:
                        try:
                            self.merge_pdfs(dialog.get_filename())
                            #WT = WorkerThread(self, dialog.get_filename())
                            #WT.start()
                        except:
                            self.raise_error_dlg()
                    dlg.destroy()             
                else:
                    try:
                        self.merge_pdfs(dialog.get_filename())
                        #WT = WorkerThread(self, dialog.get_filename())
                        #WT.start()
                    except:
                        self.raise_error_dlg()
                    
            dialog.destroy()
            
    def raise_error_dlg(self):
        """
        Raises an error dialog.
        """
        error_dlg = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.WARNING,
        Gtk.ButtonsType.OK, ("An error has occurred. Process is aborted."))
        error_dlg.format_secondary_text("Have you used an invalid password?")
        just_run = error_dlg.run()
        error_dlg.destroy()
            
    #def merge_pdfs(self, save_path):
        """
        Merges the pdfs given in self.merge_model
        
        Utilises pdf_operations.merge_pdf function to achieve its goal.
        
        if not save_path.endswith(".pdf"):
            save_path = save_path + ".pdf"               
        pdfs = []
        for row in self.merge_model:
            pdfs.append((row[0], row[1])) # path and pw
            
        encryp, user_pw, owner_pw, lvl = self.get_encryption_details()
        pdf_ops.merge_pdf(save_path, pdfs, encryp, user_pw, owner_pw, lvl)
        """ 
        
    def pulse(self):
        self.progressbar.pulse()
        return self.still_working # 1 = repeat, 0 = stop

    def error_message(self, message):
        raise IOError(message)
        
    def run(self):
        self.window.show_all()
        Gtk.main()   

    
class WorkerThread(threading.Thread):

    def __init__ (self, parent, argument, running=True):
        threading.Thread.__init__(self)
        
        self.argument = argument
        self.parent = parent
        self.running = running
 
    def run(self):
        print "entering the thread"
        while self.running:
            self.merge_pdfs(self.argument)
        print "finishing the thread"
 
    def stop(self):
        self = None
        
    def merge_pdfs(self, save_path):
        """
        Merges the pdfs given in self.merge_model
        
        Utilises pdf_operations.merge_pdf function to achieve its goal.
        """
        if not save_path.endswith(".pdf"):
            save_path = save_path + ".pdf"               
        pdfs = []
        for row in self.parent.merge_model:
            pdfs.append((row[0], row[1])) # path and pw
            
        encryp, user_pw, owner_pw, lvl = self.parent.get_encryption_details()
        pdf_ops.merge_pdf(save_path, pdfs, encryp, user_pw, owner_pw, lvl)
        
        # ending the loop
        self.running = False

if __name__ == "__main__":
    #GObject.threads_init()
    pydf_chain = PyDF_Chain()
    pydf_chain.run()