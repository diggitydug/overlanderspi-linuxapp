import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import gui

class Gui_Event_Handler:
    def exit(self, *args):
        Gtk.main_quit()
    
    def drawmap(self, viewport, args):
        print(viewport.get_allocation().width)

    