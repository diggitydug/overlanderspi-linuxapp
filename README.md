# overlanderspi-linuxapp
Repository for the linux app of the Overlanders Pi Project

# Configuring the Dev Environment
Note: The environment requires python 3.8

To install dev dependencies run the command 
`sudo apt install libgirepository1.0-dev python3-gi`

Install the pipenv package to handle the rest of the dependencies:
`pip install pipenv pycairo PyGObject`

Next navigate to the directory that this project was cloned to and from the terminal run:
`python -m pipenv install`
or
`python3 -m pipenv install`

Which snippet to use depends on how python is installed on your system
