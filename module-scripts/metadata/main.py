'''
File name: module-scripts/metadata/main.py

Description: contains all the functions that generate the output
             of the metadata module

             Imports constants from metadata/constants.py

Author: Ana Uribe
'''

########################################## IMPORTS ##########################################
import osmnx as ox
import statistics
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import bokeh
from bokeh.plotting import figure
from bokeh.layouts import column, row

from constants import ( DIST,
                             NETWORK_TYPE,

                             HEADING_DICT,
                             DIRECT_OPPOSITE_HEADING,
                             OPPOSITE_HEADING,
                             TURN_RANGES

                           )


########################################## HELPER FUNCTIONS #################################


########################################## FUNCTIONS ########################################

########################################## GETTING DF WITH EDGE, NODE INFO HELPER FUNCTIONS #################################
def get_lat_col(df):
    lat_col = df.lat
    return lat_col

def get_long_col(df):
    long_col = df.long
    return long_col

def get_center_point(lat_col, long_col):
    '''
    INPUT: lat_col (pandas DataFrame column (series)) - latitude values of the trajectories
           long_col (pandas DataFrame column (series)) - longitude values of the trajectories

    OUTPUT: (lat, long) (tuple of floats) - median of the latitude and longitude values in lat_col and long_col 
    '''
    lat =  statistics.median(lat_col)
    long = statistics.median(long_col)

    return (lat, long)

def index_edges(edges):
    '''
    INPUT: edges (osmnx graph edges) - edges in the graph

    OUTPUT: d (dictionary) - dict with key/value pairs where
                                key = each edge tuple (as a string)
                                value = edge index (int) (makes the edge index be one value rather than a tuple)
    '''
    d = {}
    idx = 0

    for e in edges:
        u = e[0]
        v = e[1]
        edge = [u, v]

        if str(edge) in d.keys():
            pass
        else:
            d[str(edge)] = idx
            idx += 1
    
    return d

def get_graph_from_bb(lat_col, long_col, network_type=NETWORK_TYPE, verbose=False):
    '''
    INPUT: lat_col (pandas DataFrame column (series)) - latitude values of the trajectories
           long_col (pandas DataFrame column (series)) - longitude values of the trajectories
           network_type (str) - type of network we want for the graph. Default: 'drive'
           verbose (boolean) -  True if you want print statements, else False

    OUTPUT: G (osmnx MultiDiGraph) - graph within bounds of N = max(lat_col), 
                                                            S = min(lat_col),
                                                            E = max(long_col),
                                                            W = min(long_col)
    '''
    # calculate bounds
    N = max(lat_col) 
    S = min(lat_col)

    E = max(long_col)
    W = min(long_col)

    # get graph from bounding box
    G = ox.graph_from_bbox(north=N, 
                           south=S,
                           east=E,
                           west=W,
                           network_type=network_type)
    
    if verbose:
        print(f'Number of edges in graph: {len(G.edges)}')
        print(f'Number of nodes in graph: {len(G.nodes)}')
    
    return G

def get_graph_from_point(lat_col, long_col, dist=DIST, network_type=NETWORK_TYPE, verbose=False):
    '''
    INPUT: lat_col (pandas DataFrame column (series)) - latitude values of the trajectories
           long_col (pandas DataFrame column (series)) - longitude values of the trajectories
           dist (int) - graph nodes and edges will be this far from the center point. Default: 8,000
           network_type (str) - type of network we want for the graph. Default: 'drive'
           verbose (boolean) -  True if you want print statements, else False
    
    OUTPUT: G (osmnx MultiDiGraph) - graph with center point calculated from lat/long values
                                     and distance from center point dist
    '''
    center_point = get_center_point(lat_col, long_col)

    G = ox.graph_from_point(center_point, dist=dist, network_type=network_type)

    if verbose:
        print(f'Number of edges in graph: {len(G.edges)}')
        print(f'Number of nodes in graph: {len(G.nodes)}')

    return G

def assign_edges_nodes(G, lat_col, long_col):
    '''
    INPUT: G (osmnx MultiDiGraph) - graph whose edges and nodes will be used
           lat_col (pandas DataFrame column (series)) - latitude values of the trajectories
           long_col (pandas DataFrame column (series)) - longitude values of the trajectories
    
    OUTPUT: edge_list (list) - nearest edge for each point in the trajectory as (u, v, key),
                               and distance from the point to corresponding edge. I.e., for each point, 
                               you have ((u, v, key), dist)
            e_idx_list (list) - corresponding edge index (from e_idx_dict) for the nearest edges in edge_list
            node_list (list) - nearest node for each point in the trajectory and the distance from the point to the node
                               i.e., for each point, you have (nearest node integer index, dist) 
    '''
    # get dictionary of edge indexes
    e_idx_dict = index_edges(G.edges)

    # use OSMNx to get the nearest graph edges for each lat/long point in the trajectory
    edge_list = ox.distance.nearest_edges(G, 
                                          long_col, 
                                          lat_col, 
                                          interpolate=None, 
                                          return_dist=True
                                         )

    e_idx_list = []
    edge_list_0 = edge_list[0]

    # get edge index from dict
    for i in range(len(edge_list_0)):
        e = edge_list_0[i]

        u = e[0]
        v = e[1]
        u_v = [u, v]

        e_idx_list.append(e_idx_dict[str(u_v)])

    # use OSMNx to get the nearest graph node for each lat/long point in the trajectory
    node_list = ox.distance.nearest_nodes(G, 
                                          long_col,
                                          lat_col, 
                                          return_dist=True
                                         )
    
    return edge_list, e_idx_list, node_list

########################################## GETTING DF WITH EDGE, NODE INFO FUNCTION ########################################

def get_final_df_and_graph(df, point=False, dist=DIST):
    '''
    INPUT: df (pandas DataFrame) - current dataframe with lat/long, and other trajectory info
                                   assuming latitude info in col 'lat', longitude info in column 'long'
           point (boolean) - True if want graph to be made from the center point of the lat/long col vals,
                             False (default) if want graph to be made from a bounding box made from the lat/long col vals
                             WARNING: if the dist value is not right, then the graph will not fit the traejctories.
                             It is best to let the graph be derived from the bounding box of the trajectories.
           dist (int) - graph nodes and edges will be this far from the center point. Default: 8,000

    OUTPUT: new_df (pandas DataFrame) - df with new columns: 'edge', 'edge_idx' and 'node'
                                    corresponding to the graph derrived from the bounding box created by
                                    the lat/long of the trajectories, or the center point (median) of the 
                                    lat/long values.
            G (OSMNx multidigraph) - graph that corresponds to the trajectories
    '''
    lat_col = df.lat
    long_col = df.long

    if point == False:
        G = get_graph_from_bb(lat_col, long_col)
    else:
        G = get_graph_from_point(df.lat, df.long, dist)

    edge_list, e_idx_list, node_list = assign_edges_nodes(G, lat_col, long_col)

    df_cols = df.columns
    additional_cols = ['edge', 'edge_idx', 'node']
    new_cols = []

    for c in df_cols:
        new_cols.append(c)
    
    for a in additional_cols:
        new_cols.append(a)

    edge_list_0 = edge_list[0]
    
    node_list_0 = node_list[0]

    # create new df
    new_df = pd.DataFrame(columns=df_cols, index=df.index)

    # copy columns we don't want to change
    for col in df_cols:
        new_df[col] = df[col]

    # add new cols
    for i in range(len(new_df)):
        new_df.loc[i, ('edge', 'edge_idx', 'node')] = str(edge_list_0[i]),int(e_idx_list[i]), str(node_list_0[i])

    return new_df, G

def get_graph(df, point=False, dist=DIST):
    '''
    INPUT: df (pandas DataFrame) - current dataframe with lat/long, and other trajectory info
                                   assuming latitude info in col 'lat', longitude info in column 'long'
           point (boolean) - True if want graph to be made from the center point of the lat/long col vals,
                             False (default) if want graph to be made from a bounding box made from the lat/long col vals
                             WARNING: if the dist value is not right, then the graph will not fit the traejctories.
                             It is best to let the graph be derived from the bounding box of the trajectories.
           dist (int) - graph nodes and edges will be this far from the center point. Default: 8,000

    OUTPUT: new_df (pandas DataFrame) - df with new columns: 'edge', 'edge_idx' and 'node'
                                    corresponding to the graph derrived from the bounding box created by
                                    the lat/long of the trajectories, or the center point (median) of the 
                                    lat/long values.
            G (OSMNx multidigraph) - graph that corresponds to the trajectories
    '''
    lat_col = df.lat
    long_col = df.long

    if point == False:
        G = get_graph_from_bb(lat_col, long_col)
    else:
        G = get_graph_from_point(df.lat, df.long, dist)

    return G

def get_final_df(df, point=False, dist=DIST):
    '''
    INPUT: df (pandas DataFrame) - current dataframe with lat/long, and other trajectory info
                                   assuming latitude info in col 'lat', longitude info in column 'long'
           point (boolean) - True if want graph to be made from the center point of the lat/long col vals,
                             False (default) if want graph to be made from a bounding box made from the lat/long col vals
                             WARNING: if the dist value is not right, then the graph will not fit the traejctories.
                             It is best to let the graph be derived from the bounding box of the trajectories.
           dist (int) - graph nodes and edges will be this far from the center point. Default: 8,000

    OUTPUT: new_df (pandas DataFrame) - df with new columns: 'edge', 'edge_idx' and 'node'
                                    corresponding to the graph derrived from the bounding box created by
                                    the lat/long of the trajectories, or the center point (median) of the 
                                    lat/long values.
    '''
    lat_col = df.lat
    long_col = df.long

    if point == False:
        G = get_graph_from_bb(lat_col, long_col)
    else:
        G = get_graph_from_point(df.lat, df.long, dist)

    edge_list, e_idx_list, node_list = assign_edges_nodes(G, lat_col, long_col)

    df_cols = df.columns
    additional_cols = ['edge', 'edge_idx', 'node']
    new_cols = []

    for c in df_cols:
        new_cols.append(c)
    
    for a in additional_cols:
        new_cols.append(a)

    edge_list_0 = edge_list[0]
    
    node_list_0 = node_list[0]

    # create new df
    new_df = pd.DataFrame(columns=df_cols, index=df.index)

    # copy columns we don't want to change
    for col in df_cols:
        new_df[col] = df[col]

    # add new cols
    for i in range(len(new_df)):
        new_df.loc[i, ('edge', 'edge_idx', 'node')] = str(edge_list_0[i]), int(e_idx_list[i]), str(node_list_0[i])

    return new_df


########################################## FUNCTIONS USING FINAL DF ########################################

def get_points_for_edge(df, e, verbose=False):
    '''
    INPUT: df (pandas DataFrame) - dataframe with trajectory info as well as corresponding graph nearest edge index for each point
           e (int) - index of one edge
           verbose (boolean) - True if you want print statements, else False
    
    OUTPUT: new_df (pandas DataFrame) - points in trajectory corresponding to edge e
    '''

    new_df = df[df.edge_idx == e]

    if verbose:
        print(f'For edge {e} there are \n\t{len(new_df)} points')

    return new_df

def get_points_for_node(df, n, verbose=False):
    '''
    INPUT: df (pandas DataFrame) - dataframe with trajectory info as well as corresponding graph nearest edge index for each point
           n (int) - index of one node
           verbose (boolean) - True if you want print statements, else False
    
    OUTPUT: new_df (pandas DataFrame) - points in trajectory corresponding to edge e
    '''

    new_df = df[df.node == n]

    if verbose:
        print(f'For node {n} there are \n\t{len(new_df)} points')

    return new_df

def get_points_for_e_n(df, e, idx, verbose=False):
    if e == 'Edge':
        new_df = get_points_for_edge(df, idx, verbose)
    else:
        new_df = get_points_for_node(df, idx, verbose)

    return new_df

def get_one_trip(df, id_idx_col, id, verbose=False):
    '''
    INPUT: df (pandas DataFrame) - dataframe with trajectory info as well as corresponding graph nearest edge index for each point
           id_idx_col (str) - name of column that has the ids
           id (int) - one trip/trajectory ID
           verbose (boolean) - True if you want print statements, else False
    
    OUTPUT: new_df (pandas DataFrame) - points in trajectory corresponding to edge e
    '''

    new_df = df[df[id_idx_col] == id]
    
    if verbose:
        print(f'For trip ID {id} there are \n\t{len(new_df)} points')

    return new_df

########################################## METADATA FUNCTIONS ########################################

def get_driving_directions(e_df, verbose=False):
    '''
    INPUT: e_df (pandas DataFrame) - dataframe with trajectory information for one edge. 
                                   Assuming heading information is in col 'heading'
           verbose (boolean) - True if you want print statements, else False
    
    OUTPUT: driving_directions (dict) -  dictionary with a boolean for two-way (False if one-way, True if two-way),
                                   and a list of the heading directions 
    '''
    # grab all unique headings for trajectories from headings col
    unique_headings = np.unique(e_df.heading)

    cardinal_directions = []

    # get all cardinal directions for the unique headings (binning headings into N,S,E,W,NE,NW, etc)
    for h in unique_headings:
        for k in HEADING_DICT.keys():
            if h >= HEADING_DICT[k][0] and h <= HEADING_DICT[k][1]:
                cardinal_directions.append(k)

    two_way_headings_list = []
    general_two_way_heading_list = []

    # check if there are any directly opposite cardinal directions in the set of cardinal directions
    # if there is, the road is probably two-way,
    # if there is not, the road is probably one-way
    for d in np.unique(cardinal_directions):
        if DIRECT_OPPOSITE_HEADING[d] in cardinal_directions:
            two_way_headings_list.append((d, DIRECT_OPPOSITE_HEADING[d]))

        # check if the cardinal directions are generally in opposite directions (eg. N and SW, SE)
        cur_opposite_dir = OPPOSITE_HEADING[d]
        for cur_dir in cur_opposite_dir:
            if cur_dir in cardinal_directions:
                general_two_way_heading_list.append((d, cur_dir))

    # create the driving directions dict and print results if needed
    driving_directions = {'two-way': True,
                          'cardinal directions': []}
 
    if two_way_headings_list != []:
        driving_directions['cardinal directions'] = np.unique(two_way_headings_list)   # TODO: make sure this works
        if verbose: print(f'This road is a two-way, with trajectories heading: {two_way_headings_list}')

    elif general_two_way_heading_list != []:
        driving_directions['cardinal directions'] = np.unique(general_two_way_heading_list) # TODO: make sure this works
        if verbose: print(f'This road may be a two-way, with trajectories heading: {general_two_way_heading_list}')

    else:
        driving_directions['two-way'] = False
        driving_directions['cardinal directions'] = np.unique(cardinal_directions)
        if verbose: print(f'This road is a one-way, with trajectories heading: {np.unique(cardinal_directions)}')
            
    return driving_directions

def get_turn_directions(n_df, verbose=False):
    '''
    INPUT: n_df (pandas DataFrame) - dataframe with trajectory information for one node. 
                                     Assuming heading information is in col 'heading'
           verbose (boolean) - True if you want print statements, else False
    
    OUTPUT: turn_directions (dict) - dictionary with a boolean for each direction: Right, Left, Ahead, U-turn
                                     False if no trajectory headings go that direction,
                                     True if one or more trajectory headings go that direction
            headings_lists (dict) - dictionary of lists of all the heading pairs for right, left, ahead, and u-turns
    '''
    # grab all unique headings for trajectories from headings col
    unique_headings = np.unique(n_df.heading)

    r_headings_list = []
    l_headings_list = []
    a_headings_list = []
    u_headings_list = []

    right = False
    left = False
    ahead = False
    u_turn = False

    # get turn direction ranges for each unique heading
    for h in unique_headings:

        r_range = TURN_RANGES['right']
        l_range = TURN_RANGES['left']
        a_range_one = TURN_RANGES['ahead'][0]
        a_range_two = TURN_RANGES['ahead'][1]
        u_range = TURN_RANGES['u-turn']

        # check if any heading is within a turn range with respect to h 
        # if any heading is within the r, l, a, u range w.r.t. h, 
        # add it to the corresponding headings list
        for h_2 in unique_headings:
            if h_2 != h:

                # change h_2 to be w.r.t. h
                h_2_wrt_h = (h_2 - h)%360
                
                # check right
                if h_2_wrt_h in range(r_range[0], r_range[1]):
                    right = True
                    r_headings_list.append((h, h_2))

                # check left
                if h_2_wrt_h in range(l_range[0], l_range[1]):
                    left = True
                    l_headings_list.append((h, h_2))

                # check ahead
                if (h_2_wrt_h in range(a_range_one[0], a_range_one[1])) or (h_2_wrt_h in range(a_range_two[0], a_range_two[1])):
                    ahead = True
                    a_headings_list.append((h, h_2))

                # check u-turn
                if h_2_wrt_h in range(u_range[0], u_range[1]):
                    u_turn = True
                    u_headings_list.append((h, h_2))

    # create dictionaries
    turn_directions = {'right': right,
                       'left': left,
                       'ahead': ahead,
                       'u-turn': u_turn}
    
    heading_lists = {'right': r_headings_list,
                     'left': l_headings_list,
                     'ahead': a_headings_list,
                     'u-turn': u_headings_list}
    
    # print statements
    if verbose:
        print(f'From this intersection, you can turn:\n\tRight:{right} \n\tLeft:{left} \n\tAhead:{ahead} \n\tU-turn:{u_turn}')

        print(f'\nThe following heading pairs helped determine turn directions:')
        if right:
            print(f'\tRight: {r_headings_list}')
        
        if left:
            print(f'\tLeft: {l_headings_list}')

        if ahead:
            print(f'\tAhead: {a_headings_list}')
        
        if u_turn:
            print(f'\tU-turn: {u_headings_list}')

    return turn_directions
    return turn_directions, heading_lists

def get_turn_driving_directions(df, e, verbose=False):
    if e == 'Edge':
        d = get_driving_directions(df, verbose)
    else:
        d = get_turn_directions(df, verbose)

    return str(d)

def get_speed_stats(e_n_df, bokeh, verbose=False):
    '''
    INPUT: e_n_df (pandas DataFrame) - dataframe with trajectory information for one edge or node. 
                                   Assuming average speed information is in col 'average_speed'
                                   and that speed is in miles per hour
           bokeh (boolean) - uses bokeh for plotting if True, else uses matplotlib
           verbose (boolean) - True if you want print statements, else False
    
    OUTPUT: fig, ax - matplotlib OR bokeh figure and axis with the graphs of the average speed distributions
                      with and without zero values
            speed_stats (dict) - dictonary with different speed statistic calculations
    '''
    # avg/median speed
    avg_speed = statistics.mean(e_n_df.average_speed)
    med_speed = statistics.median(e_n_df.average_speed)

    # max/min speed
    max_speed = max(e_n_df.average_speed)
    min_speed = min(e_n_df.average_speed)

    # speed without zeros
    col_no_zeros = e_n_df.average_speed[e_n_df.average_speed != 0]
    avg_speed_no_zeros = statistics.mean(col_no_zeros)
    med_speed_no_zeros = statistics.median(col_no_zeros)

    # save info in dictionary
    speed_stats = {'average': avg_speed,
                   'median': med_speed,
                   'maximum': max_speed,
                   'minimum': min_speed,
                   'average no zeros': avg_speed_no_zeros,
                   'median no zeros': med_speed_no_zeros}
    
    # generate histogram of distribution of avg speeds with and without zero vals
    if bokeh:
        f_1 = figure(toolbar_location=None,
                     title="Distribution of All Average Speeds")
        hist, edges = np.histogram(e_n_df.average_speed, density=False, bins=20)
        f_1.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color="skyblue", line_color="white")
        # f_1.xaxis.axis_label = "Speed: Miles per Hour"
        f_1.yaxis.axis_label = "Count"

        f_2 = figure(toolbar_location=None,
                     title="Distribution of Non-Zero Average Speeds")
        hist, edges = np.histogram(col_no_zeros, density=False, bins=20)
        f_2.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color="skyblue", line_color="white")
        f_2.xaxis.axis_label = "Speed: Miles per Hour"
        f_2.yaxis.axis_label = "Count"

        # fig = column(f_1, f_2, sizing_mode='stretch_both')
        fig = row(f_1, f_2, sizing_mode='stretch_both')

    else:
        fig, ax = plt.subplots(2, 1, sharex=True)

        ax[0].hist(e_n_df.average_speed, color='orangered')
        ax[0].set_title('Distribution of All Average Speeds')
        ax[0].set_ylabel('Count')

        ax[1].hist(col_no_zeros, color='teal')
        ax[1].set_title('Distribution of Non-Zero Average Speeds')
        ax[1].set_xlabel('Speed: Miles per Hour')
        ax[1].set_ylabel('Count')

        fig.tight_layout()

        # print speed stats
        if verbose:
            print(f'Speed statistics:\n\tAverage: {avg_speed} \n\tMedian: {med_speed}, \n\tMaximum: {max_speed} \n\tMinimum: {min_speed}')
            print(f'\nSpeed statistics without zeros: \n\tAverage: {avg_speed_no_zeros} \n\tMedian: {med_speed_no_zeros}')

        plt.close(fig)
    
    return fig
    # return (fig, speed_stats)
