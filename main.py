import gi
gi.require_version('Gtk', '3.0')
gi.require_version("Gdk", "3.0")
gi.require_version("OsmGpsMap", "1.0")
from gi.repository import (Gtk,
    Gdk,
    GdkPixbuf,
    GLib,
    Gtk,
    OsmGpsMap as osmgpsmap,
)
import gps_handler
import config
import os
import time

assert osmgpsmap._version == "1.0"

glade_file = "overlanderspi.glade"
builder = Gtk.Builder()
builder.add_from_file(glade_file)
recording = False
recording_file_path = None #This will hold the value of the entire path including file name
recording_file_name = None #This is just to hold the file name excluding the path
recording_file = None #This is to store the actual file being recorded to

viewport = builder.get_object("view")
record_dialog = builder.get_object('record_file_dialog')
download_dialog = builder.get_object('download_maps_dialog')
record_button = builder.get_object('record_button')
homing_button = builder.get_object('pin_button')

#Load configs from config.py
map_lat, map_lon = tuple(map(float, config.get_config('default loc').split(',')))
physical_lat, physical_lon = gps_handler.get_coordinates()
zoom = int(float(config.get_config('default zoom')))
resolution = [int(config.get_config('resolution_width')), int(config.get_config('resolution_height'))]
gps_functions = config.get_config('show gps')
homing_default = config.get_config('homing default')

osm = osmgpsmap.Map()
osm.set_property("map-source", osmgpsmap.MapSource_t.OPENSTREETMAP)
osm.set_center_and_zoom(map_lat,map_lon,zoom)
if (config.get_config('caching')):
    osm.props.tile_cache = config.get_config('cache path')
else:
    osm.props.tile_cache = osmgpsmap.MAP_CACHE_DISABLED

pin_image = GdkPixbuf.Pixbuf.new_from_file_at_size("icons/gps.png", 24, 24)
map_pin = None

viewport.add(osm)

window = builder.get_object("main_window")
window.connect("destroy", Gtk.main_quit)


def exit_settings():
    print("Exiting Settings")
    for child in window.get_children():
        window.remove(child)
    map_view = builder.get_object('map_view')

    window.add(map_view)
    update_gui()


def record_to_file():
    global recording, recording_file
    if not recording:
        return recording
    lat, lon = gps_handler.get_coordinates()
    if (lat is not None and lon is not None):
        lat = "%.5f" % lat
        lon = "%.5f" % lon
        recording_file.write(str(lat) + ', ' + str(lon) + '\n')
        return True    
    else:
        return False
      

def start_record_loop():
    refresh_setting = int(config.get_config('poll frequency'))
    refresh_rate = int(60/refresh_setting) * 1000
    record_to_file()
    GLib.timeout_add(refresh_rate, record_to_file)

def start_record():
    global recording, recording_file, recording_file_path, recording_file_name
    recording = True
    print("Starting track record")
    timestr = time.strftime("%Y%m%d-%H%M")
    file_timestr = time.strftime("%Y-%m-%d %H:%M")
    recording_file_name = 'GPSTrack-' + timestr
    file_path = config.get_config('recording path')
    recording_file_path = file_path + recording_file_name
    recording_file = open(str(recording_file_path), 'a')

    poll_frequency = config.get_config('poll frequency')
    file_open = "Overlander\'s Pi GPS Log\nStarted at " + file_timestr + "\nPosition Polled " + poll_frequency +' times per minute \n\n'

    
    recording_file.write(file_open)
    start_record_loop()


def end_record():
    global recording, recording_file_name, recording_file_path
    recording = False
    record_to_file()
    print("Ending track record")
   
    if (config.get_config('record dialog')):
        entry = builder.get_object('record_file_name')
        entry.set_text(recording_file_name)
        recording_file.close()

        record_dialog.run()
    else: 
        recording_file.close()
        print('Saving GPS record: ' + recording_file_path)
   

def update_gui():
    global record_button, homing_button
    if (not gps_functions and not homing_default):
        window.show_all()
        record_button.hide()
        homing_button.hide()
    elif (not gps_functions and homing_default):
        window.show_all()
        record_button.hide()
    else:
        window.show_all()
    
    while Gtk.events_pending():
        Gtk.main_iteration_do(True)


def no_dongle_error():
    pass

def print_tiles():
        if osm.props.tiles_queued != 0:
            print(osm.props.tiles_queued, "tiles queued")
        return True


class Gui_Event_Handler:

    def exit(self, *args):
        Gtk.main_quit()

    def open_settings(self, *args):
        for child in window.get_children():
            window.remove(child)

        settings = builder.get_object('settings_view')

        cache_toggle = builder.get_object('cache_toggle')
        cache_bool = config.get_config('caching')
        cache_toggle.set_active(cache_bool)

        zoom = builder.get_object('zoom_setting')
        zoom_val = config.get_config('default zoom')
        zoom.set_value(int(zoom_val))

        lat = builder.get_object('default_lat_value')
        lon = builder.get_object('default_lon_value')
        lat_val,lon_val = tuple(map(float, config.get_config('default loc').split(',')))
        lat.set_value(lat_val)
        lon.set_value(lon_val)

        gps_dongle_path = builder.get_object('gps_dongle_path')
        path_val = config.get_config('gps dongle path')
        gps_dongle_path.append_text(path_val)
        for devices in gps_handler.get_devices():
            gps_dongle_path.append_text(devices)
        gps_dongle_path.set_active(0)

        polling = builder.get_object('gps_poll_value')
        poll_val = config.get_config('poll frequency')
        polling.set_value(int(poll_val))

        record_path = builder.get_object('recording_folder')
        record_path_val = config.get_config('recording path')
        record_path.set_current_folder(record_path_val)

        cache_path = builder.get_object('cache_dir_val')
        cache_path_val = config.get_config('cache path')
        cache_path.set_current_folder(cache_path_val)

        record_dialog = builder.get_object('ask_record_toggle')
        record_dialog_bool = config.get_config('record dialog')
        record_dialog.set_active(record_dialog_bool)

        homing_default = builder.get_object('homing_default_toggle')
        homing_default_bool = config.get_config('homing default')
        homing_default.set_active(homing_default_bool)

        homing_zoom = builder.get_object('homing_zoom_setting')
        homing_zoom_val = config.get_config('homing zoom')
        homing_zoom.set_value(int(homing_zoom_val))

        show_gps = builder.get_object('show_gps_toggle')
        show_gps_val = config.get_config('show gps')
        show_gps.set_active(show_gps_val)

        window.add(settings)
        window.show_all()
        update_gui()

    def zoom_in(self, *args):
        global osm
        global zoom
        if zoom < 18:
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
        
        cache_bool = builder.get_object('cache_toggle').get_state()
        if(config.get_config('caching') != cache_bool):
            settings['caching'] = cache_bool
            if (cache_bool):
                osm.props.tile_cache = config.get_config('cache path')
            else:
                osm.props.tile_cache = osmgpsmap.MAP_CACHE_DISABLED
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

        device_path = builder.get_object('gps_dongle_path').get_active_text()

        if (device_path != config.get_config('gps dongle path')):
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

        recording_folder = builder.get_object('recording_folder').get_current_folder() + '/'
        
        if (recording_folder != config.get_config('recording path')):
            print('Updating default recording path')
            settings['recording path'] = recording_folder + '/'

        cache_path = builder.get_object('cache_dir_val').get_current_folder() + '/'

        if (cache_path != config.get_config('cache path')):
            print('Updating cache path')
            settings['cache path'] = cache_path + '/'

        record_dialog = builder.get_object('ask_record_toggle').get_active()

        if (record_dialog != config.get_config('record dialog')):
            print('Updating record dialog settings')
            settings['record dialog'] = record_dialog

        homing_default_val = builder.get_object('homing_default_toggle').get_active()
        global homing_default

        if (homing_default_val != config.get_config('homing default')):
            print("Updating homing default setting")
            homing_default = homing_default_val
            settings['homing default'] = homing_default_val

        homing_zoom = int(builder.get_object('homing_zoom_setting').get_value())

        if (homing_zoom != int(config.get_config('homing zoom'))):
            print('Updating homing zoom setting')
            settings['homing zoom'] = homing_zoom

        show_gps = builder.get_object('show_gps_toggle').get_active()
        global gps_functions

        if (show_gps != config.get_config('show gps')):
            gps_functions = show_gps
            print("Updating show gps setting")
            settings['show gps'] = show_gps
        
        if not error:
            config.set_config(settings)
            exit_settings()        

    def exit_settings(self, *args):
        exit_settings()

    def move_to_pin(self, *args):
        print('Moving map location')
        pin_default = config.get_config('homing default')
        global physical_lat, physical_lon, map_lat, map_lon, zoom, map_pin
        physical_lat, physical_lon = gps_handler.get_coordinates()
        pin_zoom = int(config.get_config('homing zoom'))
        zoom = pin_zoom
        if(map_pin is not None):
            osm.image_remove(map_pin)
        if (physical_lat is not None and physical_lon is not None):
            map_lat , map_lon = physical_lat, physical_lon
            osm.set_center_and_zoom(map_lat, map_lon, pin_zoom)

            map_pin = osm.image_add(map_lat, map_lon, pin_image)
        else:
            if(pin_default):
                map_lat, map_lon = tuple(map(float, config.get_config('default loc').split(',')))
                osm.set_center_and_zoom(map_lat, map_lon, pin_zoom)  
                map_pin = osm.image_add(map_lat, map_lon, pin_image)
            else:
                no_dongle_error()

    def save_recording(self, *args):
        global recording_file_path
        file_name = builder.get_object('record_file_name').get_text()
        file_path =  config.get_config('recording path')
        os.rename(recording_file_path, file_path + file_name)
        record_dialog.hide()
        print("Saving GPS recording: " + file_path + file_name)

    def discard_recording(self, *args):
        record_dialog.hide()
        print("Discarding recording")

    def restore_defaults(self, *args):
        config.restore_defaults()
        exit_settings()

    def download_dialog(self, *args):
        print("Opening map download dialog")
        download_dialog.run()  

    def current_zoom_download_toggled(self, switch, status):
        print("Current Zoom toggle flipped")
        lowest = builder.get_object('lowest_detail_entry')
        lowest.set_property('editable', not status)
        update_gui()

        if status:
            builder.get_object('lowest_detail_entry').set_value(zoom)

    def cancel_map_download(self, *args):
        print("Cancelling map download")
        builder.get_object('zoom_detail_error').set_text("")
        download_dialog.hide()

    def download_maps(self, *args):
        lowest = int(builder.get_object('lowest_detail_entry').get_value())
        highest = int(builder.get_object('highest_detail_entry').get_value())
        if(lowest <= highest):
            bbox = osm.get_bbox()
            download_dialog.hide()
            builder.get_object('zoom_detail_error').set_text("")
            print("Downloading map tiles")
            osm.download_maps(*bbox, lowest, highest)
            
        else:
            builder.get_object('zoom_detail_error').set_text("Highest detail must be a higher value than Lowest value")
        


def start_gui():
    update_gui()
    builder.connect_signals(Gui_Event_Handler())
    Gtk.main()

if __name__ == "__main__":
    start_gui()
