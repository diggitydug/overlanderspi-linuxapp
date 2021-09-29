import PySimpleGUI as sg
import constant

def menu():
    layout = [[sg.FileBrowse("Open Map",size=(30,1))]]

    return layout

def layout_header():
    header = [sg.Text('Overlander\'s Pi'), sg.Button('', image_data=constant.EXIT_ICON,border_width=0, key='Exit')]
    return header