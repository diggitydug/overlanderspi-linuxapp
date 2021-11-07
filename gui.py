from PIL.Image import new
import gi
from matplotlib import pyplot
import matplotlib
gi.require_version('Gtk', '3.0')
gi.require_version("Gdk", "3.0")
gi.require_version("OsmGpsMap", "1.0")
from gi.repository import (Gtk,
    Gdk,
    GdkPixbuf,
    GLib,
    GObject,
    Gtk,
    OsmGpsMap as osmgpsmap,
)
from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
import numpy as np
import maptiler
from gps_handler import get_coordinates
import config
import os.path
import random

print(f"using library: {osmgpsmap.__file__} (version {osmgpsmap._version})")

assert osmgpsmap._version == "1.0"

glade_file = "gui.glade"
builder = Gtk.Builder()
builder.add_from_file(glade_file)
recording = False
offsetx = 0
offsety = 0
px = 0
py = 0
maxx = 0
maxy = 0

# higher values make movement more performant
# lower values make movement smoother
SENSITIVITY = 1

viewport = builder.get_object("view")

map_lat, map_lon = tuple(map(float, config.get_config('default loc').split(',')))
physical_lat, physical_lon = get_coordinates()
zoom = int(float(config.get_config('default zoom')))
resolution = [int(config.get_config('resolution_width')), int(config.get_config('resolution_height'))]

osm = osmgpsmap.Map()
osm.set_property("map-source", osmgpsmap.MapSource_t.OPENSTREETMAP)
osm.set_center_and_zoom(map_lat,map_lon,zoom)

viewport.add(osm)

window = builder.get_object("main_window")
window.show_all()

def exit_settings():
    print("Exiting Settings")
    for child in window.get_children():
        window.remove(child)

    settings = builder.get_object('map_view')
    window.add(settings)
    window.show_all()
    update_gui()

def start_record():
    global recording
    recording = True
    print("Starting track record")

def end_record():
    global recording
    recording = False
    print("Ending track record")
        
def update_gui():
    while Gtk.events_pending():
        Gtk.main_iteration_do(True)

class Gui_Event_Handler:

    def exit(self, *args):
        Gtk.main_quit()

    def open_settings(self, *args):
        for child in window.get_children():
            window.remove(child)

        settings = builder.get_object('settings_view')

        toggle = builder.get_object('cache_toggle')
        cache_bool = config.get_config('caching')
        toggle.set_active(cache_bool)

        zoom = builder.get_object('zoom_setting')
        zoom_val = config.get_config('default zoom')
        zoom.set_value(int(zoom_val))

        lat = builder.get_object('default_lat_value')
        lon = builder.get_object('default_lon_value')
        lat_val,lon_val = tuple(map(float, config.get_config('default loc').split(',')))
        lat.set_value(lat_val)
        lon.set_value(lon_val)

        gps_path = builder.get_object('default_path')
        path_val = config.get_config('gps path')
        gps_path.set_text(path_val)

        polling = builder.get_object('gps_poll_value')
        poll_val = config.get_config('poll frequency')
        polling.set_value(int(poll_val))

        record_path = builder.get_object('recording_folder')
        record_path_val = config.get_config('recording path')
        record_path.set_current_folder(record_path_val)

        window.add(settings)
        window.show_all()
        update_gui()

    def zoom_in(self, *args):
        global osm
        global zoom
        if zoom < 19:
            zoom = zoom +1
            osm.set_zoom(zoom)
            print("Zoomed to level: " + str(zoom))

    def zoom_out(self, *args):
        global osm
        global zoom
        if zoom > 4:
            zoom = zoom -1
            osm.set_zoom(zoom)
            print("Zoomed to level: " + str(zoom))

    def toggle_record(self, *args):
        global recording
        record_button = builder.get_object('record_button')
        
        if  not recording:
            start_record()
            record_button.set_property('image', builder.get_object('stop_record_img'))
        else:
            end_record()
            record_button.set_property('image', builder.get_object('record_image'))

    def save_settings(self, *args):
        print("Saving settings")

        error = False
        setting_view = builder.get_object('settings_view')
        error_obj = builder.get_object('setting_error_message')

        settings = {}
        user_attributes = config.get_user_attribute()
        for attribute in user_attributes:
            settings[attribute] = config.get_config(attribute)
        
        toggle_bool = builder.get_object('cache_toggle').get_state()
        if(config.get_config('caching') != toggle_bool):
            settings['caching'] = builder.get_object('cache_toggle').get_state()
            print('Caching setting updated')
        
        zoom_val = int(builder.get_object('zoom_setting').get_value())
        if (int(float(config.get_config('default zoom'))) != zoom_val):
            settings['default zoom'] = int(builder.get_object('zoom_setting').get_value())
            print('Default zoom setting updated')

        lat_val,lon_val = tuple(map(float, config.get_config('default loc').split(',')))
        new_lat = builder.get_object('default_lat_value').get_value()
        new_lon = builder.get_object('default_lon_value').get_value()
        if (new_lat != lat_val and new_lon != lon_val) :
            print('Updating default lat and lon')
            settings['default loc'] = str(new_lat)+','+str(new_lon)
        elif(new_lat != lat_val and new_lon == lon_val):
            print('Updating default lat')
            settings['default loc'] = str(new_lat)+','+str(new_lon)
        elif(new_lat == lat_val and new_lon != lon_val):
            print('Updating default lon')
            settings['default loc'] = str(new_lat)+','+str(new_lon)

        device_path = builder.get_object('default_path').get_text()

        if (device_path != config.get_config('gps path')):
            if os.path.exists(device_path):
                print('Updating default path to GPS Device')
                settings['gps path'] = device_path
            else:
                error = True
                error_obj.set_label('Invalid path to GPS Device')
                setting_view.add(error_obj)

        polling_val = int(builder.get_object('gps_poll_value').get_value())

        if (polling_val != int(config.get_config('poll frequency'))):
            print('Updating polling frequency')
            settings['poll frequency'] = polling_val

        recording_folder = builder.get_object('recording_folder').get_current_folder()
        
        if (recording_folder != config.get_config('recording path')):
            print('Updating default recording path')
            settings['recording path'] = recording_folder

        
        if not error:
            config.set_config(settings)
            exit_settings()        

    def exit_settings(self, *args):
        exit_settings()

    def move_to_pin(self, *args):
        print('Moving map location')
        global physical_lat, physical_lon, map_lat, map_lon, zoom
        physical_lat, physical_lon = get_coordinates()
        if (physical_lat is not None and physical_lon is not None):
            map_lat , map_lon = physical_lat, physical_lon
            osm.set_center_and_zoom(map_lat, map_lon, zoom)
        else:
            osm.set_center_and_zoom(map_lat, map_lon, zoom)        

def start_gui():
    builder.connect_signals(Gui_Event_Handler())
    Gtk.main()

start_gui()