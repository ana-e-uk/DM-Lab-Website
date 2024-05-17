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

from .functions import get_metadata, display_node_data, display_edge_data
########################################## DATA CONSTANTS ########################################## 
# directory and file names
metadata_dir = '/Users/bean/Documents/DM-Lab-Website/data/output'
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
        pn.Column(
            pn.Row(
                pn.pane.Markdown('''
                    Road Network Metadata:
                    '''),
                node_select,
                edge_select),
            plot_updater.plot_pane)
    ]

########################################## HELPER FUNCTIONS ########################################## 

##### -------------------- Drawing Button -------------------- #####
# Define function called when drawing button is clicked
def on_button_click(event):
    print(f'\nButton clicked! Getting Metadata...')
    get_metadata(config.map, config.bounding_box)

# Create the drawing button
drawing_button = pn.widgets.Button(name='Explore Region', description='If new trajectory was uploaded, wait a couple minutes')

# Attach the function to the button's click
drawing_button.on_click(on_button_click)

##### -------------------- Parameterized class for Select widgets and Plots -------------------- #####
class PlotUpdater(param.Parameterized):
    selected_option_n = param.Integer(default=None)
    selected_option_e = param.String(default=None)
    options_n = param.List()
    options_e = param.List()
    plot_pane = param.ClassSelector(class_=pn.pane.Matplotlib)
    df_n = pd.DataFrame()
    df_e = pd.DataFrame()

    def __init__(self, file_path_n, file_path_e, **params):
        super().__init__(**params)
        self.file_path_n = file_path_n
        self.file_path_e = file_path_e
        self.plot_pane = pn.pane.Matplotlib(self.create_placeholder_plot(), width=800, height=600)
        self.update_options_n()
        self.update_options_e()
        self.watch_file(self.file_path_n, self.update_options_n)
        self.watch_file(self.file_path_e, self.update_options_e)

    def create_placeholder_plot(self):
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, 'Select options to update plot')
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    def update_options(self, file_path, col_name, update_func):
        try:
            df = pd.read_csv(file_path)
            options = df[col_name].unique().tolist()
            update_func(options)
        except Exception as e:
            print(f'Error reading Csv file {file_path}: {e}')

    def update_options_n(self, options=None):
        if options is not None:
            self.options_n = options
        else:
            try:
                self.df_n = pd.read_csv(self.file_path_n)
                self.options_n = self.df_n['Node'].unique().tolist()
            except Exception as e:
                print(f'Error reading Node CSV file: {e}')

    def update_options_e(self, options=None):
        if options is not None:
            self.options_e = options
        else:
            try:
                self.df_e = pd.read_csv(self.file_path_e)
                self.options_e = self.df_e['Edge'].unique().tolist()
            except Exception as e:
                print(f'Error reading Edge CSV file: {e}')

    @param.depends('selected_option_n', 'selected_option_e', watch=True)
    def update_plot(self):
        fig, ax = plt.subplots()
        if self.selected_option_n and not self.df_n.empty:
            filtered_df_n = self.df_n[self.df_n['Node'] ==  self.selected_option_n]
            # fig = display_node_data(filtered_df_n)
            ax.scatter(filtered_df_n['Count'].tolist(), filtered_df_n['Count'].tolist())
        if self.selected_option_e and not self.df_e.empty:
            filtered_df_e = self.df_e[self.df_e['Edge'] == self.selected_option_e]
            ax.plot(filtered_df_e['Count'].tolist(), filtered_df_e['Count'].tolist())
            # fig = display_edge_data(filtered_df_e)
        # ax.set_title(f'Metadata plot:')
        ax.legend()
        self.plot_pane.object = fig

    def watch_file(self, file_path, update_func):
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

# Initialize plot updater with two CSV files
plot_updater = PlotUpdater(file_path_n=os.path.join(metadata_dir, c_n_s_file),
                           file_path_e=os.path.join(metadata_dir, c_e_s_file),
                           )

# Create the Select widgets and link them to the parameters
node_select = pn.widgets.Select(name='Intersections', options=plot_updater.options_n)
edge_select = pn.widgets.Select(name='Roads', options=plot_updater.options_e)

node_select.param.watch(lambda event: setattr(plot_updater, 'selected_option_n', event.new), 'value')
edge_select.param.watch(lambda event: setattr(plot_updater, 'selected_option_e', event.new), 'value')

# Link the select widgets to the options parameters
def update_select_options(event):
    node_select.options = plot_updater.options_n
    edge_select.options = plot_updater.options_e

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
