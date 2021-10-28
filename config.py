#The purpose of this file is to handle
#parts of the application that are 
#related to configurations set as 
#both default and user configured

import configparser
from os import path

config_parser = configparser.ConfigParser()
config_mode = 'DEFAULT'

#Called when application detects no config 
#file and creates it with default settings
def new_config():
    #Add new default configs here
    config_parser['DEFAULT'] = {
        'window mode':'fullscreen',
        'resolution': {
            'width': 800,
            'height':480
        },
        'caching':'True',
        'default zoom': 5,
        'default loc': (20,-135)
    }
    with open('config.txt', 'w') as configfile:
        config_parser.write(configfile)

if (path.exists('config.txt')):
    config_parser.read('config.txt')
else:
    new_config()

def get_config(attribute):
    try:
        value = config_parser["USER"][attribute]
        return value
    except:
        try:
            value = config_parser['DEFAULT'][attribute]
            return value
        except:
            print("You put the wrong setting")