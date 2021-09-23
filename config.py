#The purpose of this file is to handle
#parts of the application that are 
#related to configurations set as 
#both default and user configured

import configparser
import os.path
from os import path

from wx.core import Width

#Called when application detects no config 
#file and creates it with default settings
def new_config():
    config = configparser.ConfigParser()
    #Add new default configs here
    config['DEFAULT'] = {
        'WindowMode':'fullscreen',
        'Resolution': {
            'width': 800,
            'height':480
        }
    }
    with open('config.txt', 'w') as configfile:
        config.write(configfile)


if (path.exists('config.txt')):
    pass
else:
    new_config()