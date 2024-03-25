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
from ipyleaflet import Map, basemaps, FullScreenControl, basemap_to_tiles, DrawControl
from shapely.geometry import Polygon

import bokeh
from bokeh.plotting import figure, save
import geopandas as gpd

from constants import(METADATA_DIR,
                      POINT_RANGE
                      )

from main import (get_speed_stats, 
                  get_points_for_e_n, 
                  get_turn_driving_directions
                  )

# pn.extension("ipywidgets")
pn.extension()

########################################## HELPER FUNCTIONS ##########################################
def get_b_box_p_coordinates(drawing):
    '''
    FUNCTION: get_b_box_p_coordinates

    DESCRIPTION: Returns the bounding box or point coordinates of the bounding box or point drawn with draw_control

    IN: drawing ()
    OUT: bounding box () or point (coordinate - (float, float))
    '''
    # ********** Code adapted from Yousseff Hussein's 'calculate statistics' function:
    # ********** https://github.com/joHussien/iHARPVis/blob/main/VisualizationDemoV01/visualization_iHARP_V01.py#L439

    shape = drawing['new']
    if shape:
        
        if 'coordinates' in shape['geometry']:  # Check if 'coordinates' key exists
            coordinates = None
            coordinates = shape['geometry']['coordinates']

            if isinstance(coordinates[0], float):  # Handle single point shape
                metadata = get_metadata_from_point(coordinates)
            
            else:
                # get metadata from bounding box
                coordinates = coordinates[0]
                metadata = get_metadata_from_b_box(coordinates)

            # visualize metadata


        else:
            print("Invalid shape format")
        drawing['new']=''

def get_metadata_from_point(coordinates):
    '''
    FUNCTION: get_metadata_from_point

    DESCRIPTION: Query the existing metadata file and return all the metadata that lies within the bounding box,
                or the metadata closest to the point. This data will be visualized using other functions.

    IN: coordinates - [(float, float)]
    OUT: metadata_df_slice (pandas DataFrame) - datataframe of the metadata of the roads/intersections within the bounding box 
                                                or corresp. to the road/intersection closest to the point input.
    '''
    ##### Get coordninates #####
    lat_coord = coordinates[1]
    long_coord = coordinates[0]
    # print(f'Coordinate values chosen:\n\tlatitude: {lat_coord} \n\tlongitude: {long_coord}')
    
    min_lat = min(lat_coord - POINT_RANGE, lat_coord + POINT_RANGE)
    max_lat = max(lat_coord - POINT_RANGE, lat_coord + POINT_RANGE)

    min_long = min(long_coord - POINT_RANGE, long_coord + POINT_RANGE)
    max_long = max(long_coord - POINT_RANGE, long_coord + POINT_RANGE)

    # print(f'Coordinate values chosen:\n\tlatitude: ({min_lat}, \t {max_lat})\n\tlongitude: ({min_long}, \t {max_long})')
    
    #### Query metadata file #####
    # read in all of the metadata
    metadata_df = pd.read_csv(METADATA_DIR)

    # grab only the data that fall within lat/long ranges
    metadata_df_slice = metadata_df[(metadata_df['lat'] >= min_lat) & (metadata_df['lat'] <= max_lat) & (metadata_df['long'] >= min_long) & (metadata_df['long'] <= max_long)]

    print(metadata_df_slice)
    
    return metadata_df_slice

def get_metadata_from_b_box(coordinates):
    '''
    FUNCTION: get_metadata_from_b_box

    DESCRIPTION: Query the existing metadata file and return all the metadata that lies within the bounding box,
                or the metadata closest to the point. This data will be visualized using other functions.

    IN: coordinates ()
    OUT: metadata_df_slice (pandas DataFrame) - datataframe of the metadata of the roads/intersections within the bounding box 
                                                or corresp. to the road/intersection closest to the point input.
    '''
    ##### Get coordninates as bounding box #####
    # ********** Code adapted from Yousseff Hussein's 'calculate daily stats' function:
    # ********** https://github.com/joHussien/iHARPVis/blob/main/VisualizationDemoV01/visualization_iHARP_V01.py#L200

    min_lat, max_lat, min_long, max_long = [], [], [], []

    polygon = Polygon(coordinates)

    min_lat, min_long = min(coordinates, key=lambda x: x[1])[1], min(coordinates, key=lambda x: x[0])[0]
    max_lat, max_long = max(coordinates, key=lambda x: x[1])[1], max(coordinates, key=lambda x: x[0])[0]

    # ********** End code from Y.H.
        
    # print(f'Coordinate values chosen:\n\tlatitude: ({min_lat}, \t {max_lat})\n\tlongitude: ({min_long}, \t {max_long})')
    
    #### Query metadata file #####
    # read in all of the metadata
    metadata_df = pd.read_csv(METADATA_DIR)

    # grab only the data that fall within lat/long ranges
    metadata_df_slice = metadata_df[(metadata_df['lat'] >= min_lat) & (metadata_df['lat'] <= max_lat) & (metadata_df['long'] >= min_long) & (metadata_df['long'] <= max_long)]

    print(metadata_df_slice)
    
    return metadata_df_slice

def visualize_metadata():
    '''
    FUNCTION: visualize_metadata

    DESCRIPTION: Visualize the desired metadata on the dashboard map.
                When a road or intersection is hovered over/clicked on, you can see: speed statistics, turn/driving directions,
                length of road(?) etc.

    IN: df (pandas DataFrame) - dataframe of the metadata
    OUT: --
    '''
    pass

########################################## SIDEBAR ELEMENTS ########################################## 
##### instructions text #####
instructions_text = pn.pane.Markdown('''
                                     ## Instructions:
                                     
                                     Use the map tools to draw a bounding box on the map. The available road segments for this region will be displayed.

                                     Hover over or click on the road segments or intersections to see the current statistics and metadata for that road segment or intersection.
                                     ''')

##### layout #####
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

# ********** Start code below from Yousseff Hussein's 'visualization_iHARP_V01.py':
# ********** https://github.com/joHussien/iHARPVis/blob/main/VisualizationDemoV01/visualization_iHARP_V01.py

# Add full-screen control to the map
full_screen_control = FullScreenControl(exit_button=True)
map.add_control(full_screen_control)
osm_basemap = basemap_to_tiles(basemaps.OpenStreetMap.Mapnik)

# Add the basemaps to the map
map.add_layer(osm_basemap)

##### Bounding Box Tool #####
# Add draw controls to the map
draw_control = DrawControl()
draw_control.rectangle = {
    "shapeOptions": {
        "fillOpacity": 0.1
    }
}
# Configure the DrawControl to only allow rectangle shapes
draw_control.polyline = {}
draw_control.circle = {}
draw_control.polygon = {}
draw_control.marker = {}
draw_control.CircleMarker = {}

map.add_control(draw_control)

#Do something when sleecting a new area on the map
draw_control.observe(get_b_box_p_coordinates, names='last_draw')

# ********** End code from Y.H.

# declare map panel object
map_pane = pn.panel(map)


##### layout #####
main_elements = [map_pane]


########################################## TEMPLATE ##########################################
template = pn.template.FastListTemplate(
    site='Metadata',
    title="Map Metadata From GPS Trajectories",
    sidebar=sidebar_elements,
    main=main_elements,
    font='Times New Roman'
).servable()
