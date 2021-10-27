import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.figure import Figure
import numpy as np
from maptile_get import get_figure
from gps_handler import get_coordinates

class Handler:
    def onDestroy(self, *args):
        print("window destroyed")
        Gtk.main_quit()

    def close_butt(self, button):
        print("Time to close")
        Gtk.main_quit()

builder = Gtk.Builder()
builder.add_from_file("gui.glade")
builder.connect_signals(Handler())

window = builder.get_object("main_window")

scroll_window = builder.get_object("scroll")
viewport = builder.get_object("view")

lat, lon = get_coordinates()

figure = get_figure(lat, lon, 4)

viewport.add(FigureCanvas(figure))

window.show_all()
Gtk.main()