'''
File name: panel-scripts/metadata_pn.py

Description: contains the Panel code that generates the metadata webpage/dashboard
             of the website.

             Calls functions in module-scripts/metadata, and utils folders.
             
Author: Ana Uribe
'''

########################################## IMPORTS ##########################################
import holoviews as hv
import panel as pn

########################################## HELPER FUNCTIONS #################################


########################################## FUNCTIONS ########################################
# load bohek extension
hv.extension("bokeh")

# set the sizing mode
pn.extension(sizing_mode="stretch_width")
