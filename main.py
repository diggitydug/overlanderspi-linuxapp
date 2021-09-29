import PySimpleGUI as sg
from layout import *
import constant

layout = [layout_header()]

for element in menu():
    layout.append(element)



window = sg.Window('Overlander\'s Pi', layout ,no_titlebar=False,location=(0,10),size=(800,480))

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit': # if user closes window or clicks exit
        break
    
window.close()