from gi.repository import Gtk

class Handler:
    def on_main_window_delete_event(self, *args):
        Gtk.main_quit()
    
    def on_addbutton_clicked(self, button):
        print "add"
        
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

builder = Gtk.Builder()
builder.add_from_file("main_gui.glade")
builder.connect_signals(Handler())

window = builder.get_object("main_window")
window.show_all()

Gtk.main()