'''
File name: module-scripts/metadata/__init__.py

Description: contains all the functions that generate the output
             of the metadata module

             Imports constants from metadata/constants.py

Author: Ana Uribe
'''

import panel as pn
from .functions import *#(map_match)

chosen_traj_filename = ''
# map = None
config = None
def add_map_matching_widgets(column, c):
    # global chosen_traj_filename
    # chosen_traj_filename = traj_filename
    # global map
    global config
    config = c
    column[:] = [
        match_button
    ]


# Define a function to be called when the button is clicked
def on_button_click(event):
    map_match(config.chosen_traj_filename, config.map)
    print("Button clicked!")

# Create the button
match_button = pn.widgets.Button(name='Match One Trajectory', description='Wait for 5 minutes')

# Attach the function to the button's click event
match_button.on_click(on_button_click)