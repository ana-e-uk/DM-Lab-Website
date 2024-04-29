'''
File name: 3_metadata_pn.py

DESCRIPTION: Generates metadata dashboard webpage. 
             This page has instructions on the sidebar and plots ipyleaflet map on the main part of the dashboard.
             You can draw a bounding box region and a point with a select tool.
             Select tool returns subset of metadata that falls within the drawn bounding box or point.
             This metadata is visualized and is interactable.

CURRENT DESCRIPTION: Visualization and interactability of metadata is NOT coded yet.
                     
             Imports functions from main.py, constants.py, visualization.py

Author: Ana Uribe
'''
########################################## IMPORTS ##########################################
import panel as pn
import numpy as np
import pandas as pd
import statistics as stat
import io

import ipywidgets as ipw
from ipywidgets import HTML
from ipyleaflet import Map, basemaps, FullScreenControl, basemap_to_tiles, DrawControl, Polyline, Popup

from shapely.geometry import Polygon


import bokeh
from bokeh.plotting import figure, save
import geopandas as gpd

from constants import(METADATA_DIR,
                      POINT_RANGE
                      )

from main import (get_graph,
                  get_speed_stats, 
                  get_points_for_e_n, 
                  get_turn_driving_directions
                  )

from visualization import (plot_graph_only)

# pn.extension("ipywidgets")
pn.extension()
########################################## ##########################################

########################################## HELPER FUNCTIONS ##########################################
def get_metadata_from_point(coordinates):
    '''
    FUNCTION: get_metadata_from_point

    DESCRIPTION: Query the existing metadata file and return all the metadata that lies around the point.
                 This data will be visualized using other functions.

    IN: coordinates - [float, float]

    OUT: metadata_df_slice (pandas DataFrame) - datataframe of the metadata of the roads/intersections within the point.
    '''
    ##### Get coordninates #####
    lat_coord = coordinates[1]
    long_coord = coordinates[0]
    
    min_lat = min(lat_coord - POINT_RANGE, lat_coord + POINT_RANGE)
    max_lat = max(lat_coord - POINT_RANGE, lat_coord + POINT_RANGE)

    min_long = min(long_coord - POINT_RANGE, long_coord + POINT_RANGE)
    max_long = max(long_coord - POINT_RANGE, long_coord + POINT_RANGE)

    # print(f'Coordinate values chosen:\n\tlatitude: {lat_coord} \n\tlongitude: {long_coord}')
    # print(f'Coordinate values chosen:\n\tlatitude: ({min_lat}, \t {max_lat})\n\tlongitude: ({min_long}, \t {max_long})')
    
    #### Query metadata file #####
    # read in all of the metadata
    metadata_df = pd.read_csv(METADATA_DIR)

    # grab only the data that fall within lat/long ranges
    metadata_df_slice = metadata_df[(metadata_df['lat'] >= min_lat) & (metadata_df['lat'] <= max_lat) & (metadata_df['long'] >= min_long) & (metadata_df['long'] <= max_long)]
    
    return metadata_df_slice

def get_metadata_from_b_box(coordinates):
    '''
    FUNCTION: get_metadata_from_b_box

    DESCRIPTION: Query the existing metadata file and return all the metadata that lies within the bounding box.
                 This data will be visualized using other functions.

    IN: coordinates (list) - contains corner coordinates of the bounding box

    OUT: metadata_df_slice (pandas DataFrame) - datataframe of the metadata of the roads/intersections within the bounding box.
    '''
    ##### Get coordninates as bounding box #####
    # ********** Code adapted from Yousseff Hussein's 'calculate daily stats' function:
    # ********** https://github.com/joHussien/iHARPVis/blob/main/VisualizationDemoV01/visualization_iHARP_V01.py#L200

    min_lat, max_lat, min_long, max_long = [], [], [], []

    min_lat, min_long = min(coordinates, key=lambda x: x[1])[1], min(coordinates, key=lambda x: x[0])[0]
    max_lat, max_long = max(coordinates, key=lambda x: x[1])[1], max(coordinates, key=lambda x: x[0])[0]

    # ********** End code from Y.H.
        
    # print(f'Coordinate values chosen:\n\tlatitude: ({min_lat}, \t {max_lat})\n\tlongitude: ({min_long}, \t {max_long})')
    
    #### Query metadata file #####
    # read in all of the metadata
    metadata_df = pd.read_csv(METADATA_DIR)

    # grab only the data that fall within lat/long ranges
    metadata_df_slice = metadata_df[(metadata_df['lat'] >= min_lat) & (metadata_df['lat'] <= max_lat) & (metadata_df['long'] >= min_long) & (metadata_df['long'] <= max_long)]

    return metadata_df_slice

def create_map_with_multiple_polylines(df, m, colors):
    
    # Initialize a placeholder for the popup outside the loop
    # This ensures we're working with only one popup at a time
    popup = Popup(max_width=200)
    
    for index, row in df.iterrows():
        polyline = Polyline(
            locations=row['Coordinates'],
            color=colors[index],
            fill=False,
            weight=5,
            opacity=0.9
        )
        m.add_layer(polyline)

        def on_polyline_click(event=None, feature=None, id=row['ID'], **kwargs):
            # Configure the popup for the current polyline
            coords = list(df[df['ID'] == id]['Coordinates'])[0][0]
            print(f'event:{event}\nid: {id}\nfeature:{feature}\ncoords:{coords}')

            # Update popup location and content
            popup.location = coords

            popup.child = HTML(value=f"<b>{row['Speed']}</b>: {row['Heading']}")
            
            # Check if the popup is already on the map
            if popup not in m.layers:
                m.add_layer(popup)
            else:
                # Popup is already on the map, so we just updated its content and location
                popup.open = True

        polyline.on_click(on_polyline_click)
    
    return m

def visualize_metadata(bool, df, map):
    '''
    FUNCTION: visualize_metadata

    DESCRIPTION: Visualize the desired metadata on the dashboard map.
                When a road or intersection is hovered over/clicked on, you can see: speed statistics, turn/driving directions,
                length of road(?) etc.

    IN: df (pandas DataFrame) - dataframe of the metadata
    OUT: --
    '''
    if bool:
        print('reached visualize metadata function')
        colors = ['#BD44E8', '#2075DE', '#970E02', '#06FD6A']
        m = create_map_with_multiple_polylines(df,map,colors=colors)

        return m
    else:
        pass

def get_metadata(drawing):
    '''
    FUNCTION: get_metadata

    DESCRIPTION: Calls functions to get the metadata from the given bounding box or point coordinates drawn by the user,
                 and visualizes it on the map.

    IN: drawing (dict) - dictionary with information about the drawing from ipyleaflet's DrawControl
                         The information of interest is the coordinates of the geometry.

    OUT: None
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
            
            else:   # handle bounding box shape
                coordinates = coordinates[0]
                metadata = get_metadata_from_b_box(coordinates)

            # visualize metadata
            print('First three rows of metadata dataframe:')
            print(metadata.head(3))
            print(f'Metadata dataframe size: {metadata.shape}')

        else:
            print("Invalid shape format")
        drawing['new']=''
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
center = (42.5, -41)
zoom = 2
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
draw_control.observe(get_metadata, names='last_draw')

# ********** End code from Y.H.

#TODO: have the get_metadata function save the metadata df slice or the new df we want
# (with the coordinates for one trajectory combined in a list) and then on click or something
# add the polylines to the map/call a function to add them to the map, as well as add the popup for them

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
