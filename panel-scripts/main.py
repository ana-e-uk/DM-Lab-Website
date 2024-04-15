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
import os
from mappymatch.utils.crs import LATLON_CRS, XY_CRS
from ipyleaflet import Map, basemaps, FullScreenControl, basemap_to_tiles, DrawControl
from constants import (TRAJ_DIR)
from visualization import (plot_traj_from_file)
from userdefined_components import Modal
pn.extension()

########################################## ON ACTION FUNCTIONS #################################



########################################## FUNCTIONS ########################################
##### instructions text #####
instructions_text = pn.pane.Markdown('''
                                     ## Instructions:
                                     This is the OpenSource MetaData Project. You can upload trajectories and use them. You can also perform certain operations like map matching on the map. Also, you can upload trajectories. 
                                     ''')

######## Widgets  ################
options = os.listdir(TRAJ_DIR)
options.insert(0, '')
chosen_traj_filename = ''
select_widget = pn.widgets.Select(options=options, width=200, height=40)
def on_select(event):
    global chosen_traj_filename
    chosen_traj_filename = select_widget.value
    print(f"Selected: {select_widget.value}")
select_widget.param.watch(on_select, 'value')

view_button = pn.widgets.Button(name='View', description='Wait..!', width=70, height=40)
def on_button_click(event):
    global chosen_traj_filename
    global map
    plot_traj_from_file(TRAJ_DIR + chosen_traj_filename, crs=LATLON_CRS, map=map) #TODO: To add the crs here
view_button.on_click(on_button_click)

file_input = pn.widgets.FileInput(accept=".csv,.txt", width=200, height=40) #, callback=upload_callback)

upload_button = pn.widgets.Button(name='Upload', description='Prepare your file', width=70, height=40)
def on_upload_button_click(event):
    global file_input
    global TRAJ_DIR
    print("Filename: ", file_input.filename)
    if file_input.value is not None:
        file_input.save(TRAJ_DIR + file_input.filename)
upload_button.on_click(on_upload_button_click)

w1 = pn.widgets.TextInput(name='Filename:')
w2 = pn.widgets.FloatSlider(name='Slider')
modal = Modal(pn.Column(
    w1, w2, sizing_mode="fixed"
))
pn.extension('modal')


########### MAP #################
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
map.add_control(draw_control)
map_pane = pn.panel(map)

########################################## TEMPLATE ##########################################
######## Layout ################
main_elements = [map_pane]
sidebar_elements = pn.Column(instructions_text, 
                             pn.Row(select_widget, view_button), 
                             pn.Row(file_input, upload_button),
                             modal.param.open, modal
                            )
####### tempelate ###########
template = pn.template.FastListTemplate(
    site='Metadata',
    title="Map Metadata From GPS Trajectories",
    sidebar=sidebar_elements,
    main=main_elements,
    font='Times New Roman'
).servable()