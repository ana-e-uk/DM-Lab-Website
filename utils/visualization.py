'''
File name: utils/visualization.py

Description: contains functions that generate the visualization for the Panel dashboards.
             These functions are used by several modules, while module-specific visualization
             functions are in the corresponding visualization.py module script.

Authors: 
    Ana Uribe
'''

########################################## IMPORTS ##########################################
import folium

from utils.constants import (
                             COLORS
                            )

########################################## FUNCTIONS ########################################

def get_folium_map(lat, long, zoom_start=11):
    '''
    Given latitude and longitude values and zoom start, returns a folium map object, m
    '''
    m = folium.Map(location=[lat, long], zoom_start=zoom_start)
    
    return m

def get_polyline(trip, num_trip=1, w=4, o=1, c=COLORS):
    '''
    Given a trip (trajectory) of [x, y] coordinates, returns 
    '''
    poly_line = folium.PolyLine(trip,
                        weight = w,
                        color = c[num_trip],
                        opacity= o)
    
    return poly_line