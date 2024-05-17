''' 
File name modules/metadata/functions.py

Description: contains functions used by __init__.py

TODO: Save osmid for edges so you don't have to query the u,v parts...

Author: Ana Uribe 
'''
########################################## IMPORTS ########################################## 

import numpy as np
import osmnx as ox
import os
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')

from .visualization import plot_map

########################################## DATA UPLOAD ########################################## 

# directory and file names
metadata_dir = '/Users/bean/Documents/DM-Lab-Website/data/output'
e_f_file = 'edge_f.csv'
e_s_file = 'edge_s.csv'
n_f_file = 'node_f.csv'
n_s_file = 'node_s.csv'

c_e_f_file = 'c_edge_f.csv'
c_e_s_file = 'c_edge_s.csv'
c_n_f_file = 'c_node_f.csv'
c_n_s_file = 'c_node_s.csv'

# create pandas df for each file
e_f = pd.read_csv(os.path.join(metadata_dir, e_f_file))
e_s = pd.read_csv(os.path.join(metadata_dir, e_s_file))
n_f = pd.read_csv(os.path.join(metadata_dir, n_f_file))
n_s = pd.read_csv(os.path.join(metadata_dir, n_s_file))
########################################## FUNCTIONS ########################################## 

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

    # print(osm_edges_list[0:2])
    # print(osm_nodes_list[0:5])

    # Convert tuples to strings
    osm_edges_list_str = [str(value) for value in osm_edges_list]

    # get computed metadata for the edges and nodes in the list
    c_e_f = e_f[e_f['Edge'].isin(osm_edges_list_str)]
    c_e_s = e_s[e_s['Edge'].isin(osm_edges_list_str)]
    c_n_f = n_f[n_f['Node'].isin(osm_nodes_list)]
    c_n_s = n_s[n_s['Node'].isin(osm_nodes_list)]

    # print(c_e_f.head(3))
    print(c_e_s.head(3))
    # print(c_n_f.head(3))
    # print(c_n_s.head(3))

    # save filtered dataframes
    c_e_f.to_csv(os.path.join(metadata_dir, c_e_f_file), index=None)
    c_e_s.to_csv(os.path.join(metadata_dir, c_e_s_file), index=None)
    c_n_f.to_csv(os.path.join(metadata_dir, c_n_f_file), index=None)
    c_n_s.to_csv(os.path.join(metadata_dir, c_n_s_file), index=None)

def display_node_data(filtered_df):
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2], [0, 1, 2])
    ax.set_title(f'First node:{filtered_df['Node'].tolist()[0]}')

    return fig

def display_edge_data(filtered_df):
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2], [2, 1, 0])
    ax.set_title(f'First edge:{filtered_df['Edge'].tolist()[0]}')

    return fig

