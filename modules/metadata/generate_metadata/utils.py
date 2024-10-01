'''
File name: utils

DESCRIPTION: Contains functions that generate map metadata.
             Functions called by get_map_metadata.py
             
Author: Ana Uribe
'''
########################################## IMPORTS ##########################################
import json
import numpy as np
import pandas as pd
import os

import ast
from scipy.stats import t
from collections import Counter

########################################## VARIABLES ##########################################
constants_path = '/Users/bean/Documents/masters-project/map-metadata/constants.json'

########################################## LOAD IN CONSTANTS ##########################################
# dictionary with constants
j_file = open(constants_path)
constants_dict = json.load(j_file)
j_file.close()


# get metadata column names
compass_dir = constants_dict['metadata cols']['compass directions']
day = constants_dict['metadata cols']['day']
day_type = constants_dict['metadata cols']['day type']
time_type = constants_dict['metadata cols']['time type']
time_bin = constants_dict['metadata cols']['time bin']
edge = constants_dict['metadata cols']['edge']
node = constants_dict['metadata cols']['node']
avg_speed = constants_dict['metadata cols']['avg speed']
max_speed = constants_dict['metadata cols']['max speed']
min_speed = constants_dict['metadata cols']['min speed']
travel_time = constants_dict['metadata cols']['travel time']
directions = constants_dict['metadata cols']['directions']
flow = constants_dict['metadata cols']['flow']
avg_speed_ci = constants_dict['metadata cols']['avg speed CI']
travel_time_ci = constants_dict['metadata cols']['travel time CI']
traj_count = constants_dict['metadata cols']['count']

########################################## HELPER FUNCTIONS ##########################################
def get_edges_of_node(n, e_df):
    ''' 
    Returns all the edges that correspond to a node
    '''
    unique_edges = list(np.unique(e_df[edge]))

    node_edges = []
    edge_dirs = []
    
    for s in unique_edges:

        u_e = ast.literal_eval(s)

        if n == u_e[0] or n == u_e[1]:
            node_edges.append(u_e)
            edge_dirs.append(list(e_df[e_df[edge] == s][compass_dir])[0])   # we want all instances of dirs
            # print(f'edge: {s} \t edge directions: {edge_dirs}')
    
    return node_edges, edge_dirs

def calc_confidence_interval(data, alpha=0.05):

    k = len(data)
    df = k - 1

    confidence_level = 1 - alpha

    X_bar = np.mean(data)
    s = np.std(data, ddof=1)  # TODO: check ddof


    t_score = t.ppf((1 + confidence_level) / 2, df)

    standard_error = s / np.sqrt(k)
    margin_of_error = t_score * standard_error

    lower_bound = round(X_bar - margin_of_error, 2)
    upper_bound = round(X_bar + margin_of_error, 2)

    c_i = (lower_bound, upper_bound)
    
    return c_i, X_bar

def get_edge_structural_metadata(df):

    # get all compass directions
    c_dir = list(np.unique(df[compass_dir]))
    if len(df) == 0:    # TODO: check that this doesn't happen
        return np.NAN, np.NAN
    elif len(df) == 1:
        one_way = np.NAN
    else:
        # var saving if edge is one-way (0=False, 1=True)
        one_way = 1.0

        # calculate road directions using compass directions
        directly_opposite_pairs =  [('N', 'S'), ('NE', 'SW'), ('E', 'W'), ('SE', 'NW')]  # opposite directions
        generally_opposite_pairs = [('N', 'SW'), ('N', 'SE'), ('NE', 'W'), ('NE', 'S'), ('E', 'NW'), ('E', 'SW'), ('SE', 'N'), ('SE', 'W'), ('S', 'NE'), ('S', 'NW'), ('SW', 'E'), ('SW', 'N'), ('W', 'NE'), ('W', 'SE'), ('NW', 'S'), ('NW', 'E')]

        # check if you have two opposite directions
        for pair in directly_opposite_pairs:
            if pair[0] in c_dir and pair[1] in c_dir:
                one_way= 0.0
                break
        
        # if you didn't find directly opposite directions,
        # try to find generally opposite directions
        if one_way == 1.0:
            for pair in generally_opposite_pairs:
                if pair[0] in c_dir and pair[1] in c_dir:
                    one_way = 0.5
                    break
    
    return c_dir, one_way

def get_edge_functional_metadata(df):

    if len(df) == 0:    # check that this doesn't happen
        return np.NAN, np.NAN, np.NAN, np.NAN, np.NAN, np.NAN
    
    # get average speed vales
    a_s_col = df[avg_speed]
    a_s_no_nan = a_s_col.dropna()
    if len(a_s_no_nan) == 0:
        avg_ci = np.NAN
        avg_s = np.NAN
    elif len(a_s_no_nan) == 1:
        avg_ci = np.NAN
        avg_s = a_s_no_nan.item()
    else:
        avg_ci, avg_s = calc_confidence_interval(a_s_no_nan)

    # get travel time values
    tt_col = df[travel_time]
    tt_no_nan = tt_col.dropna()
    if len(tt_no_nan) == 0:
        travel_t_ci = np.NAN
        travel_t = np.NAN
    elif len(tt_no_nan) == 1:
        travel_t_ci = np.NAN
        travel_t = tt_no_nan.item()
    else:
        travel_t_ci, travel_t = calc_confidence_interval(tt_no_nan)

    # get max speed values
    max_no_nan = df[max_speed].dropna()
    min_no_nan = df[min_speed].dropna()
    if len(max_no_nan) == 0:
        max_s = np.NAN
    elif len(max_no_nan) == 1:
        max_s = max_no_nan.item()
    else:
        max_s = max(max_no_nan)
    
    # get min speed values
    min_no_nan = df[min_speed].dropna()
    if len(min_no_nan) == 0:
        min_s = np.NAN
    elif len(min_no_nan) == 1:
        min_s = min_no_nan.item()
    else:
        min_s = min(min_no_nan)

    return int(round(avg_s)), avg_ci, int(round(max_s)), int(round(min_s)), round(travel_t, 4), travel_t_ci

def get_node_structural_metadata(n, e_df):

    # get all edges (and their directions) corresponding to current node
    node_edges, edge_dirs = get_edges_of_node(n, e_df)

    return node_edges, edge_dirs

def get_node_functional_metadata(df):

    avg_s, avg_ci, max_s, min_s, travel_t, travel_t_ci = get_edge_functional_metadata(df)

    if len(df) > 1:
        # calculate flow by getting proportion of trips that correspond to each edge
        counter = dict(Counter(df[compass_dir]))
    else:
        counter = {}
    
    return avg_s, avg_ci, max_s, min_s, travel_t, travel_t_ci, counter

def get_edge_metadata_df(df):

    # define columns for each df
    s_cols = [edge, compass_dir, directions, traj_count]
    f_cols = [edge, time_bin, avg_speed, avg_speed_ci, max_speed, min_speed, travel_time, travel_time_ci, traj_count]
    
    # create row list to append values
    structural_rows = []
    functional_rows = []

    # define time bins (for functional vals)
    unique_time_bins = [-1, 1, 0, 2]

    # get unique values
    unique_vals = np.unique(df[edge].dropna())

    # for every unique edge
    for v in unique_vals:

        # create subset df
        v_df = df[df[edge] == v]

        # get structural values
        c_dir, dir = get_edge_structural_metadata(v_df)

        new_s_row = [v, c_dir, dir, len(v_df)]
        structural_rows.append(new_s_row)

        # check size of df
        if len(v_df) < 5:
            avg_s, avg_ci, max_s, min_s, travel_t, travel_t_ci = get_edge_functional_metadata(v_df)
            new_f_row = [v, 3, avg_s, avg_ci, max_s, min_s, travel_t, travel_t_ci, len(v_df)]
            functional_rows.append(new_f_row)

        else:
            for b in unique_time_bins:  # make a row for each time bin
                
                # create subset df
                b_df = v_df[v_df[time_bin] == b]

                avg_s, avg_ci, max_s, min_s, travel_t, travel_t_ci = get_edge_functional_metadata(b_df)

                new_f_row = [v, b, avg_s, avg_ci, max_s, min_s, travel_t, travel_t_ci, len(b_df)]
                functional_rows.append(new_f_row)

    # generate final structural and functional dataframes 
    structural_df = pd.DataFrame(structural_rows, columns=s_cols)
    functional_df = pd.DataFrame(functional_rows, columns=f_cols)

    return structural_df, functional_df

def get_node_metadata_df(df, e_structural_df):

    # define columns for each df
    s_cols = [node, 'Edges', 'Edges_count', directions, traj_count]
    f_cols = [node, time_bin, avg_speed, avg_speed_ci, max_speed, min_speed, travel_time, travel_time_ci, flow, traj_count]

    # create row list to append values
    structural_rows = []
    functional_rows = []

    # define time bins (for functional vals)
    unique_time_bins = [-1, 1, 0, 2]

    # get unique values
    unique_vals = np.unique(df[node].dropna())

    # for every unique value (edge or node)
    for v in unique_vals:

        # create subset df
        v_df = df[df[node] == v]

        # get structural values
        e, dir = get_node_structural_metadata(n=v, e_df=e_structural_df)

        new_s_row = [v, e, len(e), dir, len(v_df)]
        structural_rows.append(new_s_row)

        # get functional values (vary with time)

        # check size of df
        if len(v_df) < 5:
            avg_s, avg_ci, max_s, min_s, travel_t, travel_t_ci, counter = get_node_functional_metadata(v_df)
            new_f_row = [v, 3, avg_s, avg_ci, max_s, min_s, travel_t, travel_t_ci, counter, len(v_df)]
            functional_rows.append(new_f_row)
        
        else:
            for b in unique_time_bins:

                # create subset df
                b_df = v_df[v_df[time_bin] == b]

                avg_s, avg_ci, max_s, min_s, travel_t, travel_t_ci, counter = get_node_functional_metadata(b_df)

                new_f_row = [v, b, avg_s, avg_ci, max_s, min_s, travel_t, travel_t_ci, counter, len(b_df)]
                functional_rows.append(new_f_row)

    # generate final structural and functional dataframes 
    structural_df = pd.DataFrame(structural_rows, columns=s_cols)
    functional_df = pd.DataFrame(functional_rows, columns=f_cols)

    return structural_df, functional_df

########################################## MAIN ##########################################
def get_map_metadata(e_df, n_df):

    # get edge and node df
    s_edge_df, f_edge_df = get_edge_metadata_df(e_df)
    s_node_df, f_node_df = get_node_metadata_df(n_df, e_structural_df=s_edge_df)

    return s_edge_df, f_edge_df, s_node_df, f_node_df
