'''
File name: panel-scripts/metadata_pn.py

Description: contains the Panel code that generates the metadata webpage/dashboard
             of the website.

             Calls functions in module-scripts/metadata, and utils folders.
             
Author: Ana Uribe
'''

########################################## IMPORTS ##########################################
# import holoviews as hv
import panel as pn
import numpy as np
import pandas as pd

import bokeh
from bokeh.plotting import figure

from main import (get_speed_stats, 
                  get_points_for_e_n, 
                  get_turn_driving_directions)

pn.extension()
########################################## HELPER FUNCTIONS #################################

def return_chosen_data(select_widget):
    if select_widget == 'All Trajectories':
        # TODO: maybe cache data?
        data_path = '/Users/bean/Documents/masters-project/data/trajectory_datasets/full_traj_59-Scan-50%_edge_node_df.csv'
    else:
        data_path = '/Users/bean/Documents/masters-project/data/trajectory_datasets/sample_full_traj_59-Scan-50%_edge_node_df.csv'
    
    data = pd.read_csv(data_path)
    return data

def return_e_n_choices(select_widget, data):
    if select_widget == 'Edge':
        choices = sorted(edge for edge in data["edge_idx"].unique() if edge)
    else:
        choices = sorted(int(node) for node in data["node"].unique() if node)

    return choices

########################################## FUNCTIONS ########################################
# load bohek extension
# hv.extension("bokeh")

# set the sizing mode
# pn.extension(sizing_mode="stretch_width")

########################################### sidebar elements ##########################################
trajectory_descr = pn.pane.Markdown("**Trajectories to Use**")
trajectory_choices_widget = pn.widgets.Select(name='Choices', options=['All Trajectories', 'My Uploaded Trajectories Only'])

trajectory_data = pn.bind(return_chosen_data,
                          select_widget=trajectory_choices_widget)

edge_node_choice_descr = pn.pane.Markdown("**Choose an Edge or Node to display metadata for:**")
select_edge_or_node_widget = pn.widgets.Select(name='', options=['Edge', 'Node'])

select_e_n_bind = pn.bind(return_e_n_choices,
                          select_widget=select_edge_or_node_widget,
                          data=trajectory_data)

e_n_choices_widget = pn.widgets.Select(name='Choices', options=select_e_n_bind)

metadata_descr = pn.pane.Markdown("**Metadata**")

e_n_df = pn.bind(get_points_for_e_n,
                 df=trajectory_data,
                 e=select_edge_or_node_widget,
                 idx=e_n_choices_widget
                 )

speed_stats_bokeh_plot = pn.bind(get_speed_stats,
                                 e_n_df, 
                                 bokeh=True
                                )

metadata_speed_text = pn.pane.Markdown('**Speed Statistics:**')
metadata_plot_pane = pn.pane.Bokeh(speed_stats_bokeh_plot, theme="dark_minimal", max_height=300, max_width=300) #, sizing_mode='stretch_width')#, max_height=300, max_width=300) #, sizing_mode='scale_width')

turn_driving_directions_dict_str = pn.bind(get_turn_driving_directions,
                                           df=e_n_df,
                                           e=select_edge_or_node_widget)

metadata_dir_text = pn.pane.Markdown('**Directions:**')

metadata_str = pn.pane.Str(turn_driving_directions_dict_str)
 
sidebar_elements = pn.Column(trajectory_descr, 
                             trajectory_choices_widget, 
                             edge_node_choice_descr, 
                             select_edge_or_node_widget, 
                             e_n_choices_widget, 
                             metadata_descr,
                             metadata_speed_text,
                             metadata_plot_pane,
                             metadata_dir_text,
                             metadata_str
                            )

########################################### main elements ##########################################

# graph_plot =

main_elements = []

########################################## template bringing all pieces together ##########################################
template = pn.template.FastListTemplate(
    site='Metadata',
    title="Map Metadata From GPS Trajectories",
    sidebar=sidebar_elements,
    main=main_elements,
    font='Times New Roman'
).servable()

########################################## Other code ##########################################

###### this layout has the speed plot and driving directions side by side (using pn.Column and pn.Row)
# sidebar_elements = pn.Column(trajectory_descr, 
#                              trajectory_choices, 
#                              edge_node_choice_descr, 
#                              select_edge_or_node_widget, 
#                              e_n_choices_widget, 
#                              metadata_descr,
#                              pn.Row(pn.Column(metadata_plot),
#                                     pn.Column(metadata_text))
#                             )

##### This code helps check what type the value of a widget returns when you're trying to figure it out
# def check_type(select_widget):
#     try:
#         print('1', select_widget.value)
#         print('1', select_widget.value.__class__)
#         return select_widget.value
#     except: 
#         try:
#             print('2', select_widget.__class__)
#             return select_widget.__class___
#         except:
#             print('3', select_widget)
#             return select_widget
# e_n_df = check_type(e_n_choices_widget)
