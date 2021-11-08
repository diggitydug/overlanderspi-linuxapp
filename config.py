#The purpose of this file is to handle
#parts of the application that are 
#related to configurations set as 
#both default and user configured

import configparser
from os import path, write
import os
import errno

config_parser = configparser.ConfigParser()
config_mode = 'DEFAULT'

record_path = path.expanduser('~') + '/Overlanders Pi/Path Recordings/'
cache_path = path.expanduser('~') + '/Overlanders Pi/Maps/'

#If you change these update the version number
#If you add a setting with a bool value update get_config()
default_config = {
        'version': '2',
        'window mode':'fullscreen',
        'resolution_width': '800',
        'resolution_height': '480',
        'caching':'True',
        'default zoom': '9',
        'default loc': '33.307161,-111.681168',
        'gps path': '/dev/ttyACM0',
        'poll frequency':'30',
        'recording path': record_path,
        'cache path': cache_path,
        'record dialog': 'False',
        'homing default': 'True',
    }

#Called when application detects no config 
#file and creates it with default settings
def new_config():
    #Add new default configs here
    config_parser['DEFAULT'] = default_config
    config_parser['USER'] = {}
    with open('config.txt', 'w') as configfile:
        config_parser.write(configfile)

if (path.exists('config.txt')):
    config_parser.read('config.txt')
    update_default = False
    if (config_parser['DEFAULT']['version'] != default_config['version']):
        print('Updating default config to latest version')
        for config in default_config:
            config_parser['DEFAULT'] = default_config
        
        with open('config.txt', 'w') as configfile:
            config_parser.write(configfile)

else:
    new_config()

if not path.exists(os.path.dirname(record_path)):
        try:
            os.makedirs(os.path.dirname(record_path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

if not path.exists(os.path.dirname(cache_path)):
        try:
            os.makedirs(os.path.dirname(cache_path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def get_user_attribute():
    attributes = []
    for config in config_parser['USER']:
        attributes.append(config)
    return attributes

def get_config(attribute):
    #This if statements checks for the elements that should be bools 
    if (attribute == 'caching' or 
    attribute == 'record dialog' or 
    attribute == 'homing default'):
        try:
            value = config_parser['USER'].getboolean(attribute)
            return value
        except:
            value = config_parser['DEFAULT'].getboolean(attribute)
            return value
    else:
        try:
            value = config_parser['USER'][attribute]
            return value
        except:
            try:
                value = config_parser['DEFAULT'][attribute]
                return value
            except:
                print("You put the wrong setting")

def set_config(values):
    try:
        config_parser['USER'] = values
        with open('config.txt', 'w') as configfile:
            config_parser.write(configfile)
    except:
        print('Could not update settings')