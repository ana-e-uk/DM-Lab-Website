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
import config
pn.extension()

########################################## FUNCTIONS ########################################
##### instructions text #####
instructions_text = pn.pane.Markdown('''
                                     ## Instructions:
                                     Visualize current GPS trajectories and map metadata using the tools below.

                                     You can also upload GPS trajectories to contribute to the GPS trajectory-extracted metadata.
                                     
                                     ### Select GPS File to View:
                                    ''')

##### instructions text #####
upload_text = pn.pane.Markdown('''
                                ### Upload GPS File:
                               ''')

######## SELECTION  ################
options = os.listdir(TRAJ_DIR)
options.insert(0, '')
select_widget = pn.widgets.Select(options=options, width=200, height=40)
def on_select(event):
    config.chosen_traj_filename = select_widget.value
    print(f"Selected: {select_widget.value}")
select_widget.param.watch(on_select, 'value')

view_button = pn.widgets.Button(name='View', description='Wait..!', width=70, height=40)
def on_button_click(event):
    plot_traj_from_file(TRAJ_DIR + config.chosen_traj_filename, crs=LATLON_CRS, map=config.map) #TODO: To add the crs here
view_button.on_click(on_button_click)

######## UPLOAD  ################
file_input = pn.widgets.FileInput(accept=".csv,.txt", width=200, height=40) #, callback=upload_callback)

upload_button = pn.widgets.Button(name='Upload', description='Prepare your file', width=70, height=40)
def on_upload_button_click(event):
    global file_input
    global TRAJ_DIR
    print("Filename: ", file_input.filename)
    if file_input.value is not None:
        file_input.save(TRAJ_DIR + file_input.filename)
upload_button.on_click(on_upload_button_click)

######## POPUP (Not useful rn)  ################
w1 = pn.widgets.TextInput(name='Filename:')
w2 = pn.widgets.FloatSlider(name='Slider')
modal = Modal(pn.Column(
    w1, w2, sizing_mode="fixed"
))
modal.param.open.label = "file"
pn.extension('modal')

######## MODULE SELECTION  ################
module_select_text = pn.pane.Markdown('''
                                     ### Modules
                                     ''')

###############   MODULE SPECIFICATION Column ##########
module_spec = pn.Column(pn.pane.Markdown('''             
                        Choose the **Map Matching** module to visualize how a trajectory is matched to the OSM road network. Note you must choose a trajectory file above.
                        
                        Choose the **Trajectory Split** module to visualize how GPS trajectories are segmented into Origin-Destination trips.
                                         
                        Chose the **Metadata** Module to explore OSM and GPS trajectory-extracted road network information. 
                        '''))

###############   MODULE VISUALIZATION Column ##########
module_viz = pn.Row(pn.pane.Markdown('''
                                     ### Zoom in and out to change the granularity of the OSM map.
                                     '''))

#####################################################

options = ['Map Matching', 'Trajectory Split', 'Metadata']
module_select_radio = pn.widgets.RadioBoxGroup(name='Modules', options=options)
from modules.map_matching import add_map_matching_widgets
from modules.metadata import add_metadata_widgets
from modules.traj_split import add_traj_split_widgets

def radio_callback(event):
    global module_spec
    global module_viz
    selected_option = event.new
    if selected_option == 'Map Matching':
        add_map_matching_widgets(module_spec, config)
    elif selected_option == 'Trajectory Split':
        add_traj_split_widgets(module_spec)
    elif selected_option == 'Metadata':
        add_metadata_widgets(module_spec, module_viz, config)
    else:
        raise Exception("Error Found!")
module_select_radio.param.watch(radio_callback, 'value')

######## MODULE CONTROL AREA  ################
# module_select_text = pn.pane.Markdown('''
#                                      ### module instructions:
#                                      Choose which of the following to perform on the data as a module
#                                      ''')


########### Map View #################
# center = (42.5, -41)
# zoom = 2
# map = Map(basemap=basemaps.OpenStreetMap.Mapnik, center=center, zoom=zoom)

# ********** Start code below from Yousseff Hussein's 'visualization_iHARP_V01.py':
# ********** https://github.com/joHussien/iHARPVis/blob/main/VisualizationDemoV01/visualization_iHARP_V01.py

# Add full-screen control to the map
full_screen_control = FullScreenControl(exit_button=True)
config.map.add_control(full_screen_control)
osm_basemap = basemap_to_tiles(basemaps.OpenStreetMap.Mapnik)

# Add the baseconfig.maps to the map
config.map.add_layer(osm_basemap)

##### Bounding Box Tool #####
# Add draw controls to the map
draw_control = DrawControl()
draw_control.rectangle = {
    "shapeOptions": {
        "fillOpacity": 0.1
    }
}
config.map.add_control(draw_control)

##### Saving shape from draw control to config #####
def get_coordinates(drawing):

    shape = drawing['new']
    if shape:
        if 'coordinates' in shape['geometry']:  # Check if 'coordinates' key exists
            config.bounding_box = shape['geometry']['coordinates']
            # print(config.bounding_box)
        else:
            print("Invalid shape format")
            config.bounding_box = []
        drawing['new']=''
    
coordinates = draw_control.observe(get_coordinates, names='last_draw')
map_pane = pn.panel(config.map)

########################################## Layout ##########################################
sidebar_elements = pn.Column(instructions_text, 
                             pn.Row(select_widget, view_button),
                             upload_text,
                             pn.Row(file_input, upload_button),
                             pn.Column(module_select_text, module_select_radio),
                             module_spec,
                             # modal.param.open, modal # TODO: can be added later
                            )
main_elements = [pn.Column(map_pane, module_viz)]
template = pn.template.FastListTemplate(
    site='Open Metadata',
    title="Map Services For GPS Trajectories",
    sidebar=sidebar_elements,
    main=main_elements,
    font='Times New Roman'
).servable()