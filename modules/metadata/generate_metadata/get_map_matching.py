'''
File name: get_map_matching

DESCRIPTION: For each point of a trajectory with the following info:
                < trajectory_id, timestamp, latitude, longitude >
             
             Perform map matching for the points using the Python package OSMnx s.t. each point 
             is associated with an edge (road) and node (intersection). 
             
Author: Ana Uribe
'''
########################################## IMPORTS ##########################################
import json
import os
import pandas as pd
import numpy as np
import ast
from mappymatch.utils.crs import LATLON_CRS

import osmnx as ox

########################################## VARIABLES ##########################################
constants_path = '/Users/bean/Documents/masters-project/map-metadata/constants.json'

########################################## LOAD IN DATA ##########################################
# dictionary with constants
j_file = open(constants_path)
constants_dict = json.load(j_file)
j_file.close()

# get dir paths
processed_dir = constants_dict['processed directory']
trajectory_w_metadata_file_name = constants_dict['trajectory metadata out']
out_file_name = constants_dict['map matching out']
osm_node_info_file = constants_dict['OSM node info file']
osm_edge_info_file = constants_dict['OSM edge info file']

# get trajectory df column names
latitude = constants_dict['trajectory cols']['latitude col name']
longitude = constants_dict['trajectory cols']['longitude col name']

# get metadata column names
edge = constants_dict['metadata cols']['edge']
node = constants_dict['metadata cols']['node']

osm_edge_cols = constants_dict['metadata cols']['OSM edge col names']
osm_edge_new_cols = constants_dict['metadata cols']['OSM edge new col names']

osm_node_cols = constants_dict['metadata cols']['OSM node col names']
osm_node_new_cols = constants_dict['metadata cols']['OSM node new col names']

# get map matching values
network_type = constants_dict['map matching vals']['network type']

# load in trajectory df
df = pd.read_csv(os.path.join(processed_dir, trajectory_w_metadata_file_name))

########################################## HELPER FUNCTIONS ########################################## 
def get_vector(x1, y1, x2, y2):
    # Calculate the vector components
    vector_x = x2 - x1
    vector_y = y2 - y1
    
    vector = [vector_x, vector_y]
    return vector

def get_graph_from_bb(latitude, longitude, network_type, verbose=False):
    
    n = max(latitude)
    s = min(latitude)

    e = max(longitude)
    w = min(longitude)

    G = ox.graph_from_bbox(n, s, e, w, network_type=network_type, simplify=True, retain_all=True, truncate_by_edge=True)
    # G = ox.project_graph(G=G, to_crs= LATLON_CRS)

    if verbose:
        print(f'Number of edges in graph: {len(G.edges)}')
        print(f'Number of nodes in graph: {len(G.nodes)}')
    
    return G

def exclude_edges_nodes(l, d):
    idx = l[0]
    dist = l[1]

    new_list = []

    # create new list of indexes, replace vals that have a dist > d
    for i, cur_d in zip(idx, dist):
        if cur_d > d:
            new_list.append(None)
        else:
            new_list.append(i)
    
    return new_list

def assign_edges_nodes(G, latitude, longitude):
    ''' 
    IN: G (ox graph)
        latitude (list) - latitude values of each point in the dataset (trajectory)
        longitude (list) - longitude values of each point in the dataset
    
    OUT: new_edge_list (list) - edges corresponding to each point in the dataset (if point is >10 meters away, returns None for that point)
         new_node_list (list) - nodes corresponding to each point in the dataset (if point is >40 meters away, returns None for that point)
         edges_and_vectors (dict) - contains two keys with ordered values that correspond to eachother: 
                                        Edge that has a list of all the unique edges
                                        Vector that has a list of the vector for each unique edge
         unique_n (list) - unique nodes in new_nodes_list
         unique_n_dict (dict) - key values are individual nodes, with the edges that correspond to this node as the values
        
    '''
    # use OSMNx to get the nearest graph edges for each lat/long point in the trajectory
    edge_list = ox.distance.nearest_edges(G, 
                                          longitude, 
                                          latitude, 
                                          interpolate=None, 
                                          return_dist=True
                                         )
    
    node_list = ox.distance.nearest_nodes(G, 
                                          longitude,
                                          latitude, 
                                          return_dist=True
                                         )
    
    # filter out edges and nodes that are too far away for a specific point
    new_edge_list = exclude_edges_nodes(edge_list, 10)
    new_node_list = exclude_edges_nodes(node_list, 40)

    # get unique edge and node lists
    unique_e = set(new_edge_list)
    unique_n = set(new_node_list)

    # get the vector of each edge
    edges_and_vectors = {'Edge': [],
                         'Vector': []}

    # get a list of all the edges for each node
    unique_n_dict = {value: [] for value in unique_n}

    for e in unique_e:
        # grab nodes for this edge
        u = e[0]
        v = e[1]

        # get the location of each node
        try:
            node_data = G.nodes[u]
            u_x = node_data['x']
            u_y = node_data['y']
        except:
            node_data = ox.geocoder.geocode_to_gdf(query=[f"N{u}"], by_osmid=True)
            u_x = node_data.geometry.x.iloc[0]
            u_y = node_data.geometry.y.iloc[0]
        try:
            node_data = G.nodes[v]
            v_x = node_data['x']
            v_y = node_data['y']
        except:
            node_data = ox.geocoder.geocode_to_gdf(query=[f"N{v}"], by_osmid=True)
            v_x = node_data.geometry.x.iloc[0]
            v_y = node_data.geometry.y.iloc[0]
        
        # get the edge vector for this vector
        vector = get_vector(x1=u_x, y1=u_y, x2=v_x, y2=v_y)

        edges_and_vectors['Edge'].append(e)
        edges_and_vectors['Vector'].append(vector)

        # add edge to the corresponding nodes
        try:
            unique_n_dict[u].append(e)
            unique_n_dict[v].append(e)
        except:
            # print(f'passed for node {u} or {v}')
            pass

    return new_edge_list, new_node_list, edges_and_vectors, unique_n, unique_n_dict

def compute_OSM_node_vals(x, vals_list):
    if x is np.nan or str(x) == 'nan':
        return None, None
    else:
        val_1 = nodes.loc[int(x)][vals_list[0]]
        val_2 = nodes.loc[int(x)][vals_list[1]]
        val_3 = unique_n_dict[x]

        return val_1, val_2, val_3
   
def compute_OSM_edge_vals(x, vals_list):
    vals = edges.loc[x][vals_list]
    return vals

########################################## MAIN ##########################################
# grab latitude/longitude columns
lat_col = df[latitude]
long_col = df[longitude]

# get osmnx graph segment that corresponds
print('Getting Graph from bounding box')
G = get_graph_from_bb(lat_col, long_col, network_type=network_type, verbose=True)

# get edges, nodes for each point
e, n, edges_vectors, unique_n, unique_n_dict = assign_edges_nodes(G, lat_col, long_col)
print('Finished getting edge and node information')

# get the OSM node and edge features you want for each edge
nodes, edges = ox.graph_to_gdfs(G)

unique_n_df = pd.DataFrame(unique_n, columns=['Node']).dropna(subset=['Node'])
unique_e_df = pd.DataFrame(edges_vectors, columns=['Edge', 'Vector']).dropna(subset=['Edge'])

print('Starting to get the OSM node values for each edge and node')
unique_n_df[osm_node_new_cols] = unique_n_df['Node'].apply(lambda x: pd.Series(compute_OSM_node_vals(x, osm_node_cols)))
unique_e_df[osm_edge_new_cols] = unique_e_df['Edge'].apply(lambda x: pd.Series(compute_OSM_edge_vals(x, osm_edge_cols)))

unique_n_df['Node'] = unique_n_df['Node'].astype(int)

# add edges, nodes to df
df[edge] = e
df[node] = n

# save df to processed data
df.to_csv(os.path.join(processed_dir, out_file_name), index=False)

unique_n_df.to_csv(os.path.join(processed_dir, osm_node_info_file), index=False)
unique_e_df.to_csv(os.path.join(processed_dir, osm_edge_info_file), index=False)
