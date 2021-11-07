# overlanderspi-linuxapp
Repository for the linux app of the Overlanders Pi Project

# Configuring the Dev Environment
Note: Development has been set up in Ubuntu 20.04 with Python 3.8
Linux environment recommended for development due to requirements

To install dev dependencies run the command 
`sudo apt install libgirepository1.0-dev python3-gi pipenv python3-tk libosmgpsmap-1.0-1 gir1.2-osmgpsmap-1.0 libosmgpsmap-1.0-dev`

Install the pipenv package to handle the rest of the dependencies:
`pip install pycairo PyGObject`

Next navigate to the directory that this project was cloned to and from the terminal run:
`pipenv install`

This will should install necessary dependencies.

You can run main.py or gui.py to start the app
