'''
File name: module-scripts/traj-split/__init__.py

Description: contains all the functions that generate the output
             of the traj-split module

             This how you import it
             from modules.traj_split import [function]

Author:
'''

import panel as pn
from .functions import *#(Traj_split)

chosen_traj_filename = ''
config = None


# Create the button
split_button = pn.widgets.Button(name='Match One Trajectory', description='Wait for 5 minutes')

# Define a function to be called when the button is clicked
def on_button_click(event):
    trajSplit(config.chosen_traj_filename, config.map)
    print("Button clicked!")

# Attach the function to the button's click event
split_button.on_click(on_button_click)


def add_traj_split_widgets(column, c):
    global config
    config = c
    column[:] = [
        pn.pane.Markdown('''
            This part is for TrajSplit
            '''), split_button
    ]
    return