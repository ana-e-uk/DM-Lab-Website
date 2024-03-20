'''
File name: 2_metadata_pn.py

DESCRIPTION: Generates metadata dashboard webpage. 
             This page has instructions on the sidebar and the map on the main area.

CURRENT DESCRIPTION: Prints description text in sidebar, plots ipyleaflet map on the main part of dashboard. 
                     Select tool and metadata visualization NOT coded yet.

             Imports functions from main.py

Author: Ana Uribe
'''
########################################## IMPORTS ##########################################
import panel as pn
import numpy as np
import pandas as pd
import io

import ipywidgets as ipw
import folium
from ipyleaflet import Map, basemaps

# import bokeh
from bokeh.plotting import figure, save
import geopandas as gpd


from main import (get_speed_stats, 
                  get_points_for_e_n, 
                  get_turn_driving_directions)

# pn.extension("ipywidgets")
pn.extension()

########################################## HELPER FUNCTIONS ##########################################
'''
FUNCTION: get_metadata_from_b_box_or_point

DESCRIPTION: Query the existing metadata file and return all the metadata that lies within the bounding box,
             or the metadata closest to the point. This data will be visualized using other functions.

IN: bounding box () or point (coordinate - (float, float))
OUT: metadata_df (pandas DataFrame) - datataframe of the metadata of the roads/intersections within the bounding box 
                                      or corresp. to the road/intersection closest to the point input.
'''

'''
FUNCTION: visualize_metadata

DESCRIPTION: Visualize the desired metadata on the dashboard map.
             When a road or intersection is hovered over/clicked on, you can see: speed statistics, turn/driving directions,
             length of road(?) etc.

IN: df (pandas DataFrame) - dataframe of the metadata
OUT: --
'''

########################################## SIDEBAR ELEMENTS ########################################## 
# instructions text
instructions_text = pn.pane.Markdown('''
                                     ## Instructions:
                                     
                                     Use the map tools to draw a bounding box on the map. The available road segments for this region will be displayed.

                                     Hover over or click on the road segments or intersections to see the current statistics and metadata for that road segment or intersection.
                                     ''')

# layout
sidebar_elements = pn.Column(instructions_text
                            )

########################################## MAIN ELEMENTS ##########################################
##### Map #####
# folium map
# map_pane = pn.pane.plot.Folium(folium.Map(location=[13.406, 80.110], tiles="OpenStreetMap", zoom_start=2.5), height = 700)

# ipyleaflet map (from https://ipyleaflet.readthedocs.io/en/latest/map_and_basemaps/basemaps.html)
center = [38.128, 2.588]
zoom = 5
map = Map(basemap=basemaps.OpenStreetMap.Mapnik, center=center, zoom=zoom)
map_pane = pn.panel(map)

##### Code below from Yousseff Hussein https://github.com/joHussien/iHARPVis/blob/main/VisualizationDemoV01/visualization_iHARP_V01.py
# Add full-screen control to the map
# full_screen_control = FullScreenControl(exit_button=True)
# m.add_control(full_screen_control)

##### End code from Y.H.

##### Bounding Box Tool #####




main_elements = [map_pane]


########################################## TEMPLATE ##########################################
template = pn.template.FastListTemplate(
    site='Metadata',
    title="Map Metadata From GPS Trajectories",
    sidebar=sidebar_elements,
    main=main_elements,
    font='Times New Roman'
).servable()
