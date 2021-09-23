import PySimpleGUIWx as sg
from layout import *

layout = menu()

window = sg.Window('Overlander\'s Pi', layout,no_titlebar=False,location=(0,10),size=(800,480))

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    
window.close()