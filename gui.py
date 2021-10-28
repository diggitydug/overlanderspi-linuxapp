import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.figure import Figure
import numpy as np
from maptile_get import get_figure
from gps_handler import get_coordinates
from gui_event_handler import Gui_Event_Handler
import config

glade_file = "gui.glade"
builder = Gtk.Builder()
builder.add_from_file(glade_file)
builder.connect_signals(Gui_Event_Handler())

viewport = builder.get_object("view")

default_lat, default_lon = config.get_config('default loc')
current_lat, current_lon = get_coordinates()
zoom = int(config.get_config('default zoom'))
figure = get_figure(default_lat, default_lon, zoom)

viewport.add(FigureCanvas(figure))

window = builder.get_object("main_window")
window.show_all()
Gtk.main()

#def set
#def map_draw():
    