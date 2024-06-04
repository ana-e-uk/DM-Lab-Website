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
import matplotlib 
matplotlib.use('agg')

import pandas as pd
import os
import panel as pn
import time

import matplotlib.pyplot as plt
import threading
import param

pn.extension()

from .functions import get_metadata, display_data #display_node_data, display_edge_data
from .visualization import generate_markdown
########################################## DATA CONSTANTS ########################################## 
# Get Data Directory
# Get the directory of the current file
current_file_dir = os.path.dirname(os.path.abspath(__file__))

# Generalize the target directory path
# Assuming the target path is ../../data/output relative to the current file
generalized_path = os.path.join(current_file_dir, '..', '..', 'data', 'output')

# Normalize the path to ensure it's in the correct format
metadata_dir  = os.path.normpath(generalized_path)

# File names
c_e_f_file = 'c_edge_f.csv'
c_e_s_file = 'c_edge_s.csv'
c_n_f_file = 'c_node_f.csv'
c_n_s_file = 'c_node_s.csv'

########################################## CONSTANTS ########################################## 
# Instantiate global vars
config = None

########################################## MAIN FUNCTION ########################################## 

# Function that edits website column to add metadata functionality
def add_metadata_widgets(column, row, c):

    # read in config variable
    global config
    config = c

    # edit panel column object
    column[:] = [
        # pn.pane.Markdown('''
        #     ### How to Explore the Metadata
        #     1. Draw a box on the map and click the **Explore Region** button. The OSM road network within that region will be plotted on the map.

        #     2. Use the **Roads** or **Intersections** drop-down menus to choose which road or intersection metadata will appear under the map.
        #     '''),
        drawing_button,
        # pn.pane.Markdown(''' 
        #     Choose a road or intersection to explore:
        #     '''),
    ]

    # edit panel row object
    row[:] = [
        pn.Column(
            pn.Row(
                    pn.pane.Markdown('''
                        Choose a road or intersection:
                        '''),
                    node_select,
                    edge_select
                  ),
            pn.Row( plot_updater.metadata_markdown_pane,
                    plot_updater.plot_pane,
                  )
        )
    ]

########################################## HELPER FUNCTIONS ########################################## 

##### -------------------- Create Drawing Button and Link to Event -------------------- #####
# Define function called when drawing button is clicked
def on_button_click(event):
    print(f'\nButton clicked! Getting Metadata...')
    get_metadata(config.map, config.bounding_box)

# Create the drawing button
drawing_button = pn.widgets.Button(name='Explore Region', description='Draw a box on the map')

# Attach the function to the button's click
drawing_button.on_click(on_button_click)

##### -------------------- Parameterized Class for Select Widgets and Plots -------------------- #####
class PlotUpdater(param.Parameterized):
    # chosen intersection (n) and road (e) from select widget
    selected_option_n = param.Integer(default=None)
    selected_option_e = param.String(default=None)
    # current (soon to be past) intersection (n) and road (e)
    cur_n = param.Integer(default=0)
    cur_e = param.String(default=None)
    # select widget options
    options_n = param.List()
    options_e = param.List()
    # matplotlib plot
    plot_pane = param.ClassSelector(class_=pn.pane.Matplotlib)
    # markdown pane
    metadata_markdown_pane = param.ClassSelector(class_=pn.pane.Markdown)
    # pandas dataframe that will be updated
    df_n = pd.DataFrame()
    df_e = pd.DataFrame()
    df_n_f = pd.DataFrame()
    df_e_f = pd.DataFrame()

    def __init__(self, file_path_n, file_path_e, file_path_n_f, file_path_e_f, **params):
        super().__init__(**params)
        # file paths
        self.file_path_n = file_path_n
        self.file_path_e = file_path_e
        self.file_path_n_f = file_path_n_f
        self.file_path_e_f = file_path_e_f
        # plot pane
        self.plot_pane = pn.pane.Matplotlib(self.create_placeholder_plot(), width=900, height=300)
        # markdown pane
        self.metadata_markdown_pane = pn.pane.Markdown('''
                                                        Metadata:
                                                       ''', width=200)
        # update functions
        self.update_options_n()
        self.update_options_e()
        self.update_options_n_f()
        self.update_options_e_f()
        # function to update pandas dfs and select widget options
        self.watch_file(self.file_path_n, self.update_options_n)
        self.watch_file(self.file_path_e, self.update_options_e)
        self.watch_file(self.file_path_n_f, self.update_options_n_f)
        self.watch_file(self.file_path_e_f, self.update_options_e_f)

    def create_placeholder_plot(self):
        # placeholder needed to avoid Attribute error
        fig, ax = plt.subplots(1, 3, figsize=(15, 5))
        ax[0].text(0.1, 0.5, 'Select an option above')
        return fig
    
    def update_options_n(self, options=None):
        # Update node options in select widget given dataframe file
        if options is not None:
            self.options_n = options
        else:
            try:
                self.df_n = pd.read_csv(self.file_path_n)
                self.options_n = self.df_n['Node'].unique().tolist()
            except Exception as e:
                print(f'Error reading Structural Node CSV file: {e}')
    
    def update_options_n_f(self):
        # Update dataframe
        try:
            self.df_n_f = pd.read_csv(self.file_path_n_f)
        except Exception as e:
            print(f'Error reading Functional Node CSV file: {e}')

    def update_options_e(self, options=None):
        # Update edge options in select widget given dataframe file
        if options is not None:
            self.options_e = options
        else:
            try:
                self.df_e = pd.read_csv(self.file_path_e)
                self.df_e_f = pd.read_csv(self.file_path_e_f)
                self.options_e = self.df_e['Edge'].unique().tolist()
            except Exception as e:
                print(f'Error reading Edge CSV file: {e}')
    
    def update_options_e_f(self):
        # Update dataframe
        try:
            self.df_e_f = pd.read_csv(self.file_path_e_f)
        except Exception as e:
            print(f'Error reading Functional Edge CSV file: {e}')

    # Update plot when the selected options changes
    @param.depends('selected_option_n', 'selected_option_e', watch=True)
    def update_plot(self):

        # Plots chosen node info
        if self.selected_option_n and not self.df_n_f.empty and self.selected_option_n != self.cur_n:
            
            # get plots
            filtered_df_n = self.df_n_f[self.df_n_f['Node'] ==  int(self.selected_option_n)]
            fig = display_data(filtered_df_n)
            
            # get markdown
            filtered_df_n_s = self.df_n[self.df_n['Node'] == int(self.selected_option_n)]
            markdown_pane = generate_markdown(row=filtered_df_n_s, node=True)

            # update cur_n so if/elif works when you update the node selected option
            self.cur_n = int(self.selected_option_n)

        # Plots chosen edge info
        elif self.selected_option_e and not self.df_e_f.empty:

            # get plots
            filtered_df_e = self.df_e_f[self.df_e_f['Edge'] == self.selected_option_e]
            fig = display_data(filtered_df_e)

            # get markdown
            filtered_df_e_s = self.df_e[self.df_e['Edge'] == self.selected_option_e]
            markdown_pane = generate_markdown(row=filtered_df_e_s, node=False)

        # update self objects
        self.plot_pane.object = fig
        self.metadata_markdown_pane.object = markdown_pane

    def watch_file(self, file_path, update_func):
        # Reload file to update node/edge options if files are modified
        def _watch():
            last_modified = 0
            while True:
                try:
                    current_modified = os.path.getmtime(file_path)
                    if current_modified != last_modified:
                        last_modified = current_modified
                        update_func()
                    time.sleep(5)   # check every five seconds
                except KeyboardInterrupt:
                    print('Stopped watching file.')
                    break
        watcher_thread = threading.Thread(target=_watch, daemon=True)
        watcher_thread.start()

##### -------------------- Initialize plot updater with CSV files -------------------- #####
plot_updater = PlotUpdater(file_path_n=os.path.join(metadata_dir, c_n_s_file),  # structural node metadata
                           file_path_e=os.path.join(metadata_dir, c_e_s_file),  # structural edge metadata
                           file_path_n_f=os.path.join(metadata_dir, c_n_f_file),    # functional node metadata
                           file_path_e_f=os.path.join(metadata_dir, c_e_f_file)     # functional edge metadata
                           )

##### -------------------- Create Select Widgets and Link to Events -------------------- #####
# Create the Select widgets
node_select = pn.widgets.Select(name='Intersections', options=plot_updater.options_n)
edge_select = pn.widgets.Select(name='Roads', options=plot_updater.options_e)

# Link Select widgets to the parameters
node_select.param.watch(lambda event: setattr(plot_updater, 'selected_option_n', event.new), 'value')
edge_select.param.watch(lambda event: setattr(plot_updater, 'selected_option_e', event.new), 'value')

# Link the select widgets to the options parameters
def update_select_options(event):
    node_select.options = plot_updater.options_n
    edge_select.options = plot_updater.options_e

# Update select options
plot_updater.param.watch(update_select_options, ['options_n', 'options_e'])



######################## ######################## ######################## 
########################       GRAVEYARD          ########################
######################## ######################## ########################
# ##### -------------------- Node and Edge Select Widgets -------------------- #####
# ##### --------------------Function to update NODE options
# def update_n_options():
#     try:
#         # Read the CSV file containing chosen nodes or edges
#         df = pd.read_csv(os.path.join(metadata_dir, c_n_s_file))
#         # Assume the options are in a column named 'Node'
#         options = df['Node'].tolist()
#         # Update the select widget options
#         node_select.options = options
#     except Exception as e:
#         print(f"Error reading CSV: {e}")

# # Create node select widget
# node_select = pn.widgets.Select(name='Intersections', options=[], width=200, height=40)

# # Watch the CSV file for changes
# def watch_n_file():
#     last_modified = 0
#     while True:
#         try:
#             current_modified = os.path.getmtime(os.path.join(metadata_dir, c_n_s_file))
#             if current_modified != last_modified:
#                 last_modified = current_modified
#                 update_n_options()
#             time.sleep(5)  # Check every 5 seconds
#         except KeyboardInterrupt:
#             print("Stopped watching the file.")
#             break

# watcher_thread = threading.Thread(target=watch_n_file, daemon=True)
# watcher_thread.start()

# ###### -------------------- Function to update EDGE options
# def update_e_options():
#     try:
#         # Read the CSV file containing chosen nodes or edges
#         df = pd.read_csv(os.path.join(metadata_dir, c_e_s_file))
#         # Assume the options are in a column named 'Edge'
#         options = df['Edge'].tolist()
#         # Update the select widget options
#         edge_select.options = options
#     except Exception as e:
#         print(f"Error reading CSV: {e}")

# # Create edge select widget
# edge_select = pn.widgets.Select(name='Roads', options=[], width=200, height=40)

# # Watch the CSV file for changes
# def watch_e_file():
#     last_modified = 0
#     while True:
#         try:
#             current_modified = os.path.getmtime(os.path.join(metadata_dir, c_e_s_file))
#             if current_modified != last_modified:
#                 last_modified = current_modified
#                 update_e_options()
#             time.sleep(5)  # Check every 5 seconds
#         except KeyboardInterrupt:
#             print("Stopped watching the file.")
#             break

# watcher_thread = threading.Thread(target=watch_e_file, daemon=True)
# watcher_thread.start()

# ##### -------------------- Visualizing Node and Edge Data -------------------- #####

# # Define function called when a EDGE is selected
# def on_edge_select(event):
#     print(f'Button clicked! Displaying road {edge_select.value}')
#     # display_node_data(node_select.value)

# edge_select.param.watch(on_edge_select, 'value')    # Set a watch on it
    


# # Define function called when a NODE is selected
# def on_node_select(event):
#     print(f'Button clicked! Displaying intersection {node_select.value}')
#     # display_node_data(node_select.value)

# node_select.param.watch(on_node_select, 'value')    # Set a watch on it
