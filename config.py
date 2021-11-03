#The purpose of this file is to handle
#parts of the application that are 
#related to configurations set as 
#both default and user configured

import configparser
from os import path, write

config_parser = configparser.ConfigParser()
config_mode = 'DEFAULT'

default_config = {
        'window mode':'fullscreen',
        'resolution_width': '800',
        'resolution_height': '480',
        'caching':'True',
        'default zoom': '9',
        'default loc': '33.307161,-111.681168',
        'gps path': '/dev/ttyACM0'
    }

#Called when application detects no config 
#file and creates it with default settings
def new_config():
    #Add new default configs here
    config_parser['DEFAULT'] = default_config
    with open('config.txt', 'w') as configfile:
        config_parser.write(configfile)

if (path.exists('config.txt')):
    config_parser.read('config.txt')
    update_default = False
    for config in default_config:
        print(config)
    for config in config_parser['DEFAULT']:
        if not (config_parser['DEFAULT'][config] == default_config[config]):
            update_default = True
    
    if update_default:
        print('Updating defaults to match newest config')
        config_parser['DEFAULT'] = default_config
        with open('config.txt', 'w') as configfile:
            config_parser.write(configfile)
else:
    new_config()

def get_config(attribute):
    try:
        value = config_parser['USER'][attribute]
        return value
    except:
        try:
            value = config_parser['DEFAULT'][attribute]
            return value
        except:
            print("You put the wrong setting")