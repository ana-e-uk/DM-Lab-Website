'''
File name: panel-scripts/map_matching_pn.py

Description: contains the Panel code that generates the map-matching webpage/dashboard
             of the website.

             Calls functions in module-scripts/map-matching, and utils folders.
Author: Mohamed Hemdan
'''
import panel as pn
import numpy as np
import pandas as pd
import statistics as stat
import io

import ipywidgets as ipw
from ipywidgets import HTML
from ipyleaflet import Marker, Circle, Map, basemaps, FullScreenControl, basemap_to_tiles, DrawControl, Polyline, Popup


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

from visualization import (plot_graph_only, plot_matches_on_pyleaflet)

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

######## Choosing the trajectory to match ################
# Define a list of options
import os
options = os.listdir('../../data/examples')
options.insert(0, '')
chosen_traj_filename = ''

# Create the select widget
select_widget = pn.widgets.Select(options=options)

# Define a function to be called when an option is selected
def on_select(event):
    global chosen_traj_filename
    chosen_traj_filename = select_widget.value
    print(f"Selected: {select_widget.value}")

# Attach the function to the select widget
select_widget.param.watch(on_select, 'value')

# Define a function to be called when the button is clicked
def on_button_click(event):
    global chosen_traj_filename
    global map
    map_match(chosen_traj_filename, map)
    print("Button clicked!")

# Create the button
button = pn.widgets.Button(name='Match One Trajectory', description='Wait for 5 minutes')

# Attach the function to the button's click event
button.on_click(on_button_click)

##### layout #####
sidebar_elements = pn.Column(instructions_text, 
                             select_widget,
                             button
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

##### Plot a trajectory #####

def map_match(traj_filename, map):

    from mappymatch import package_root
    from mappymatch.constructs.trace import Trace
    from mappymatch.constructs.geofence import Geofence
    from mappymatch.maps.nx.nx_map import NxMap, NetworkType
    from mappymatch.matchers.lcss.lcss import LCSSMatcher
    import random

    # Step 1: Read the csv file
    # traj_filename = 'sample_full_traj_59-Scan-50%_edge_node_df.csv'
    print("Traj Filename: ", traj_filename)
    df = pd.read_csv('../../data/examples/'+traj_filename)  # Update 'your_data.csv' with your CSV file path

    # # Step 3: Add markers for each point
    # mean_lat, mean_long = df.lat.mean(), df.long.mean()
    # new_center = (mean_lat, mean_long)  # Coordinates of the new center
    # new_zoom = 14  # New zoom level

    # df.sort_values(by=["Vehicle ID", 'Position Date Time'], inplace=True)

    # df.reset_index(drop=True, inplace=True)
    print("Selecting one Trajectory!")
    vechile_ids = df["Vehicle ID"].unique()
    # one_id = vechile_ids[0]
    one_id = random.choice(vechile_ids)
    sub_df = df[df["Vehicle ID"] == one_id]
    sub_df.sort_values(by=['Position Date Time'], inplace=True)    

    # Do Map Matching
    print("Getting the trace!")
    trace = Trace.from_dataframe(dataframe=sub_df, xy=True, lat_column='lat', lon_column='long')
    print("Getting the geofence!")
    geofence = Geofence.from_trace(trace, padding=1e3)
    print("Getting the underlying road network!")
    nx_map = NxMap.from_geofence(geofence, network_type=NetworkType.DRIVE)
    print("Matching the trace to the road network!")
    matcher = LCSSMatcher(nx_map)
    match_result = matcher.match_trace(trace)

    # Plotting the match result
    print("Now Plotting the matches...!")
    plot_matches_on_pyleaflet(matches=match_result.matches, map=map)


# Set the new center and zoom level
    # map.center = new_center
    # map.zoom = new_zoom
    # for _, location in df.iterrows():
    #     marker = Circle(
    #         location=(location['lat'], location['long']), 
    #         radius = 50,  # Set the radius of the point circle
    #         color = "red",  # Set the color of the point circle
    #         fill_color = "red"  
    #         )
    #     map.add_layer(marker)

    # for i, c in enumerate(trace.coords):
    #     folium.PolyLine(
    #         [(p.y, p.x) for p in trace.coords], color=line_color
    #     ).add_to(m)

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
