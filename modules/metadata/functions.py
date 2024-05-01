''' 
File name modules/metadata/functions.py

Description: contains functions used by __init__.py

Author: Ana Uribe
'''

import osmnx as ox

POINT_RANGE = 0.05
network_type = 'drive'

def get_metadata(m, bb):
    '''
    IN: m (ipyleaflet map)
        bb (boundig box)

    DESCRIPTION: get the OSMnx road network within the bounding box,
                 and return the road network and all the related metadata

    OUT: m_plus (ipyleaflet map) map with OSMnx road network 
         metadata_df (pandas df) OSM and computed metadata
    '''

    # Determine if bounding box or point
    if isinstance(bb[0], float):  # Handle single point shape
        lat_coord = bb[1]
        long_coord = bb[0]
        
        min_lat = min(lat_coord - POINT_RANGE, lat_coord + POINT_RANGE)
        max_lat = max(lat_coord - POINT_RANGE, lat_coord + POINT_RANGE)

        min_long = min(long_coord - POINT_RANGE, long_coord + POINT_RANGE)
        max_long = max(long_coord - POINT_RANGE, long_coord + POINT_RANGE)


    else:   # Handle bounding box shape
        coordinates = bb[0]
        min_lat, max_lat, min_long, max_long = [], [], [], []

        min_lat, min_long = min(coordinates, key=lambda x: x[1])[1], min(coordinates, key=lambda x: x[0])[0]
        max_lat, max_long = max(coordinates, key=lambda x: x[1])[1], max(coordinates, key=lambda x: x[0])[0]

    # print(min_lat, min_long, max_lat, max_long)

    # get OSMnx graph from bounding box
    G = ox.graph_from_bbox(north=max_lat, 
                           south=min_lat,
                           east=max_long,
                           west=min_long,
                           network_type=network_type)

    # save edge/node information from OSMnx graph

    
    # get list of edges/nodes from OSMnx graph to query metadata output


    # add OSMnx graph to map and return it 


    # return OSM and computed metadata for all the edges and nodes

    return