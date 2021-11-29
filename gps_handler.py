import serial
import pynmea2
import os

#This file should access the serial NMEA data stream from
#The USB dongle and return the current lat and lon with 
#the get_coordinates function

s_mode = os.path.exists('s.py')
if (s_mode):
    import s

def get_coordinates():
    if(s_mode):
       return s.s()
    else:
        return None, None

def get_devices():
    return ['/test/path']