'''
File name: panel-scripts/main.py

Description: contains the Panel code that generates the main and data upload webpage/dashboard
             of the website.

             Calls functions in module-scripts, panel-scripts, and utils folders.

             Imports constants from utils/constants.py

Authors:
    Mohamed Hemdan
'''

########################################## IMPORTS ##########################################
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

# from constants import(METADATA_DIR,
#                       POINT_RANGE
#                       )
from constants import (TRAJ_DIR)


from visualization import (plot_graph_only, plot_matches_on_pyleaflet, plot_traj_from_file)

# pn.extension("ipywidgets")
pn.extension()


########################################## HELPER FUNCTIONS #################################



########################################## FUNCTIONS ########################################
##### instructions text #####
instructions_text = pn.pane.Markdown('''
                                     ## Instructions:
                                     
                                     This is the main page of our Open Meta Data Map System. The system contains three main services for which you can upload trajectories. Please select what you want to do here
                                     Use the map tools to draw a bounding box on the map. The available road segments for this region will be displayed.

                                     Hover over or click on the road segments or intersections to see the current statistics and metadata for that road segment or intersection.
                                     ''')

######## Choosing the trajectory to match ################
# Define a list of options
import os
from mappymatch.utils.crs import LATLON_CRS, XY_CRS

options = os.listdir(TRAJ_DIR)
options.insert(0, '')
chosen_traj_filename = ''

# Create the select widget
select_widget = pn.widgets.Select(options=options, width=200, height=30)
# Define a function to be called when an option is selected
def on_select(event):
    global chosen_traj_filename
    chosen_traj_filename = select_widget.value
    print(f"Selected: {select_widget.value}")
    # chosen_traj_filename = TRAJ_DIR + chosen_traj_filename

# Attach the function to the select widget
select_widget.param.watch(on_select, 'value')

# Define a function to be called when the button is clicked
def on_button_click(event):
    global chosen_traj_filename
    global map
    # map_match(chosen_traj_filename, map)
    plot_traj_from_file(TRAJ_DIR + chosen_traj_filename, crs=LATLON_CRS, map=map) #TODO: To add the crs here
    print("Button clicked!")

from userdefined_components import Modal

w1 = pn.widgets.TextInput(name='Filename:')
w2 = pn.widgets.FloatSlider(name='Slider')

modal = Modal(pn.Column(
    w1, w2, sizing_mode="fixed"
))

# Create a function to define the content of the popup
def create_popup():
    modal_dialog = modal# pn.modal(popup_content, header="Popup Window", button_type="primary", closable=True)
    # modal_dialog.content = pn.panel("This is a popup window!")
    return modal_dialog

# Define a function to be called when the button is clicked
counter = 0
def on_upload_button_click(event):
    global file_input
    global TRAJ_DIR
    print("Filename: ", file_input.filename)
    if file_input.value is not None:
        file_input.save(TRAJ_DIR + file_input.filename)

# Define a function to handle file uploads
def upload_callback(event):
    uploaded_file = event.new
    if uploaded_file:
        print(f"Uploaded file: {uploaded_file}")
        # Do something with the uploaded file

# Create a FileInput widget
file_input = pn.widgets.FileInput(accept=".csv,.txt", width=200, height=30) #, callback=upload_callback)
upload_button = pn.widgets.Button(name='Upload', description='Prepare your file')
upload_set = pn.Row(file_input, upload_button)

# Create the button
view_button = pn.widgets.Button(name='View', description='Wait..!')
traj_select_set = pn.Row(select_widget, view_button)

# Attach the function to the button's click event
view_button.on_click(on_button_click)
upload_button.on_click(on_upload_button_click)


##### layout #####
pn.extension('modal')

sidebar_elements = pn.Column(instructions_text, 
                             traj_select_set, 
                             upload_set,
                             modal.param.open, modal,
                            #  buttons_set
                            )


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
# draw_control.polyline = {}
# draw_control.circle = {}
# draw_control.polygon = {}
# draw_control.marker = {}
# draw_control.CircleMarker = {}

map.add_control(draw_control)

#Do something when sleecting a new area on the map
# draw_control.observe(get_metadata, names='last_draw')

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