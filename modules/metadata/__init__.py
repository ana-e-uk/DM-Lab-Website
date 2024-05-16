'''
File name: module-scripts/metadata/__init__.py

Description: contains the important functions that can generate the output
             of the metadata module

             Imports constants from metadata/constants.py
             import it like this 
             from modules.metadata import [function]

Author: Ana Uribe
'''
########################################## IMPORTS ########################################## 

import pandas as pd
import os
import panel as pn
from .functions import get_metadata
########################################## DATA UPLOAD ########################################## 

# directory and file names
metadata_dir = '/Users/bean/Documents/DM-Lab-Website/data/output'
c_e_f_file = 'c_edge_f.csv'
c_e_s_file = 'c_edge_s.csv'
c_n_f_file = 'c_node_f.csv'
c_n_s_file = 'c_node_s.csv'

# create pandas df for each file
c_e_f = pd.read_csv(os.path.join(metadata_dir, c_e_f_file))
c_e_s = pd.read_csv(os.path.join(metadata_dir, c_e_s_file))
c_n_f = pd.read_csv(os.path.join(metadata_dir, c_n_f_file))
c_n_s = pd.read_csv(os.path.join(metadata_dir, c_n_s_file))

########################################## CONSTANTS ########################################## 
# Instantiate global vars
config = None

########################################## FUNCTIONS ########################################## 

# Function that edits website column to add metadata functionality
def add_metadata_widgets(column, row, c):

    # read in config variable
    global config
    config = c

    # edit panel column object
    column[:] = [
        pn.pane.Markdown('''
            Draw a box on the map to explore the metadata in that region.
            
            Once you've selected the desired location on the map, click the 'Explore Region' button to visualize the road network.
            '''),
        drawing_button,
        # pn.pane.Markdown(''' 
        #     Choose a road or intersection to explore:
        #     '''),
    ]

    # edit panel row object
    row[:] = [
        pn.pane.Markdown('''
            Road Network Metadata:
            '''),
        node_select,
        edge_select,
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

node_select = pn.widgets.Select(options=['n1'], width=200, height=40)     # Create node button
node_select.param.watch(on_node_select, 'value')    # Set a watch on it

# Define function called when a EDGE is selected
def on_edge_select(event):
    print(f'Button clicked! Displaying road {edge_select.value}')
    # display_node_data(node_select.value)

edge_select = pn.widgets.Select(options=['e1'], width=200, height=40)     # Create edge button
edge_select.param.watch(on_edge_select, 'value')    # Set a watch on it
    



