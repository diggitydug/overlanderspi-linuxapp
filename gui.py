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
import os.path

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
figure = FigureCanvas(maptiler.get_figure(map_lat, map_lon, zoom, resolution))

viewport.add(figure)

window = builder.get_object("main_window")
window.show_all()

def Min(a, b):
    if  b < a:
        return b
    return a

def Max(a, b):
    if b > a:
        return b
    return a

def RoundDownToMultiple(i, m):
    return i/m*m

def RoundToNearestMultiple(i, m):
    if i % m > m / 2:
        return (i/m+1)*m
    return i/m*m

def exit_settings():
    print("Exiting Settings")
    for child in window.get_children():
        window.remove(child)

    settings = builder.get_object('map_view')
    window.add(settings)
    window.show_all()
    update_gui()

def get_tiles():
    figure = FigureCanvas(maptiler.get_figure(map_lat, map_lon, zoom, resolution))

    for mapimg in viewport.get_children():
        matplotlib.pyplot.close('all')
        viewport.remove(mapimg)
        
    viewport.add(figure)
    
    viewport.queue_draw()
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
    
    def map_resolution(self, *args):
        global resolution
        global viewport
        res_check = [viewport.get_allocation().width, viewport.get_allocation().height]
        if (res_check !=  resolution):
            resolution = res_check
            get_tiles()

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

        path = builder.get_object('default_path')
        path_val = config.get_config('gps path')
        path.set_text(path_val)

        window.add(settings)
        window.show_all()
        update_gui()

    def zoom_in(self, *args):
        global zoom
        if zoom < 19:
            zoom = zoom +1
            print("Zoomed to level: " + str(zoom))
            get_tiles()

    def zoom_out(self, *args):
        global zoom
        if zoom >4:
            zoom = zoom -1
            print("Zoomed to level: " + str(zoom))
            get_tiles()

    def toggle_record(self, *args):
        global recording
        record_button = builder.get_object('record_button')
        
        if  not recording:
            start_record()
            record_button.set_property('image', builder.get_object('stop_record_img'))
        else:
            end_record()
            record_button.set_property('image', builder.get_object('record_image'))

    def drag_start(self,w, event):
        
        if event.button == 1:
            p = w.get_parent()
            # offset == distance of parent widget from edge of screen ...
            global offsetx, offsety
            offsetx, offsety =  p.get_window().get_position()
            # plus distance from pointer to edge of widget
            offsetx += event.x
            offsety += event.y
            # maxx, maxy both relative to the parent
            # note that we're rounding down now so that these max values don't get
            # rounded upward later and push the widget off the edge of its parent.
            global maxx, maxy
            maxx = RoundDownToMultiple(p.get_allocation().width - w.get_allocation().width, SENSITIVITY)
            maxy = RoundDownToMultiple(p.get_allocation().height - w.get_allocation().height, SENSITIVITY)
            print(maxx,maxy)

    def drag_move(self, w, event):
        # x_root,x_root relative to screen
        # x,y relative to parent (fixed widget)
        # px,py stores previous values of x,y

        global px, py
        global offsetx, offsety

        # get starting values for x,y
        x = event.x_root - offsetx
        y = event.y_root - offsety
        print(x,y)
        # make sure the potential coordinates x,y:
        #   1) will not push any part of the widget outside of its parent container
        #   2) is a multiple of SENSITIVITY
        x = RoundToNearestMultiple(Max(Min(x, maxx), 0), SENSITIVITY)
        y = RoundToNearestMultiple(Max(Min(y, maxy), 0), SENSITIVITY)
        if x != px or y != py:
            px = x
            py = y
            print(px,py)

    def drag_test(self, *args):
        print(args)

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
        
        if not error:
            config.set_config(settings)
            exit_settings()        

    def exit_settings(self, *args):
        exit_settings()

    def move_to_pin(self, *args):
        print('Moving map location')
        global physical_lat
        global physical_lon
        physical_lat, physical_lon = get_coordinates()
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

def start_gui():
    builder.connect_signals(Gui_Event_Handler())
    Gtk.main()

start_gui()