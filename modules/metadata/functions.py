''' 
File name modules/metadata/functions.py

Description: contains functions used by __init__.py

TODO: Save osmid for edges so you don't have to query the u,v parts...

Author: Ana Uribe 
'''
import numpy as np
import osmnx as ox

from .visualization import plot_map

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
    if bb == None:
        return
    else:
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
    
    # add OSMnx graph to map and return it 
    plot_map(ox_map=G, m=m)

    # save edge/node information from OSMnx graph
    osm_nodes, osm_edges = ox.graph_to_gdfs(G)

    # get list of edges/nodes from OSMnx graph
    osm_nodes_list = list(osm_nodes.index)
    osm_edges['Edge'] = list(zip(osm_edges.index.get_level_values('u'), osm_edges.index.get_level_values('v'), osm_edges.index.get_level_values('key')))
    osm_edges_list = list(osm_edges['Edge'])

    # print(osm_edges_list[0:5])
    # print(osm_nodes_list[0:5])

    # get computed metadata for the edges and nodes in the list

    # combine metadata into one (or more?) dataframes to return and visualize


    # return