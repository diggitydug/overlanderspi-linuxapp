from PIL.Image import new
import gi
from matplotlib import pyplot
import matplotlib
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
import numpy as np
import maptiler
from gps_handler import get_coordinates
import config

glade_file = "gui.glade"
builder = Gtk.Builder()
builder.add_from_file(glade_file)

viewport = builder.get_object("view")

map_lat, map_lon = tuple(map(float, config.get_config('default loc').split(',')))
physical_lat, physical_lon = get_coordinates()
zoom = int(config.get_config('default zoom'))
resolution = [int(config.get_config('resolution_width')), int(config.get_config('resolution_height'))]
figure = FigureCanvas(maptiler.get_figure(map_lat, map_lon, zoom, resolution))

viewport.add(figure)

window = builder.get_object("main_window")
window.show_all()

def get_tiles():
    figure = None
    if (physical_lat is not None and physical_lon is not None):
        figure = FigureCanvas(maptiler.get_figure(physical_lat, physical_lon, zoom, resolution))
    else:
        figure = FigureCanvas(maptiler.get_figure(map_lat, map_lon, zoom, resolution))

    for mapimg in viewport.get_children():
        matplotlib.pyplot.close('all')
        viewport.remove(mapimg)
        
    
    viewport.add(figure)
    
    viewport.queue_draw()
    window.show_all()
    update_gui()

def zoom_in():
    global zoom
    if zoom < 19:
        zoom = zoom +1
        print("Zoomed to level: " + str(zoom))
        get_tiles()

def zoom_out():
    global zoom
    if zoom >2:
        zoom = zoom -1
        print("Zoomed to level: " + str(zoom))
        get_tiles()

def start_record():
    print("Starting track record")

def open_settings():
    print("Opening Settings")
        
def update_gui():
    while Gtk.events_pending():
        Gtk.main_iteration_do(True)

class Gui_Event_Handler:

    def exit(self, *args):
        Gtk.main_quit()
    
    def map_resolution(self, *args):
        global resolution
        global viewport
        res_check = [viewport.get_allocation().width, viewport.get_allocation().height]
        if (res_check !=  resolution):
            resolution = res_check
            get_tiles()

    def open_settings(self, *args):
        open_settings()

    def zoom_in(self, *args):
        zoom_in()

    def zoom_out(self, *args):
        zoom_out()

    def start_record(self, *args):
        start_record()

def start_gui():
    builder.connect_signals(Gui_Event_Handler())
    Gtk.main()

start_gui()