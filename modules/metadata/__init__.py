'''
File name: module-scripts/metadata/__init__.py

Description: contains the important functions that can generate the output
             of the metadata module

             Imports constants from metadata/constants.py
             import it like this 
             from modules.metadata import [function]

Author: Ana Uribe
'''


import panel as pn
from .functions import get_metadata

# Instantiate global vars
# chosen_traj_filename = ''
config = None

# Function that edits website column to add metadata functionality
def add_metadata_widgets(column, c):
    global config
    config = c
    column[:] = [
        pn.pane.Markdown('''
            Draw a box on the map to explore
            the metadata in that region. 
            '''),
        drawing_button
        
    ]

# Define function called when button is clicked
def on_button_click(event):
    print(f'\nButton clicked!')
    get_metadata(config.map, config.bounding_box)

# Create the button
drawing_button = pn.widgets.Button(name='Explore Region', description='If new trajectory was uploaded, wait a couple minutes')

# Attach the function to the button's click
drawing_button.on_click(on_button_click)