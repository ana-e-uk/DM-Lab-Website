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
def add_metadata_widgets(column, row, c):
    global config
    config = c
    column[:] = [
        pn.pane.Markdown('''
            Draw a box on the map to explore the metadata in that region.
            
            Once you've selected the desired location on the map, click the 'Explore Region' button to visualize the road network.
            '''),
        drawing_button,
        pn.pane.Markdown(''' 
            Choose a road or intersection to explore:
            '''),
        node_select,
        edge_select,
    ]
    row[:] = [
        pn.pane.Markdown('''
            Road Network Metadata:
            '''),
        
    ]

##### -------------------- Drawing Button -------------------- #####
# Define function called when drawing button is clicked
def on_button_click(event):
    print(f'\nButton clicked! Getting Metadata...')
    get_metadata(config.map, config.bounding_box)

# Create the drawing button
drawing_button = pn.widgets.Button(name='Explore Region', description='If new trajectory was uploaded, wait a couple minutes')

# Attach the function to the button's click
drawing_button.on_click(on_button_click)

##### -------------------- Node and Edge Buttons -------------------- #####
# Define function called when a NODE is selected
def on_node_select(event):
    print(f'Button clicked! Displaying intersection {node_select.value}')
    # display_node_data(node_select.value)

# Create node button
node_select = pn.widgets.Select(options=['n1', 'n2'], width=200, height=40)
    
# Set a watch on it
node_select.param.watch(on_node_select, 'value')

# Define function called when a EDGE is selected
def on_edge_select(event):
    print(f'Button clicked! Displaying road {edge_select.value}')
    # display_node_data(node_select.value)

# Create node button
edge_select = pn.widgets.Select(options=['e1', 'e2'], width=200, height=40)
    
# Set a watch on it
edge_select.param.watch(on_edge_select, 'value')
    



