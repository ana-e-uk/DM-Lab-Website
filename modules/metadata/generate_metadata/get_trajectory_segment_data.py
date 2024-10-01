'''
File name: get_trajectory_segment_data

DESCRIPTION: For a dataset with the following info at each point:
                < trajectory_id, timestamp, latitude, longitude, edge, node, speed, compass direction, day type, time type >
             
             Split the dataset by trajectory_id, then by edge or node. The points in each of these groups is a trajectory segment
             corresponding to an edge or node. 
             
             Calculate the speed statistics (avg, max, min), compass direction, travel time, and day and time type of that trajectory segment.
             Then, for each trajectory segment, you have:
                < trajectory_id, edge, speed stats, compass direction, day type, time type, travel time > 
            and
                < trajectory_id, node, speed stats, compass direction, day type, time type, travel time >

Author: Ana Uribe
'''
########################################## IMPORTS ##########################################
import json
import os
import pandas as pd
import numpy as np

from collections import Counter
import ast

from get_trajectory_metadata import time_difference, distance_difference
########################################## VARIABLES ##########################################
constants_path = '/Users/bean/Documents/masters-project/map-metadata/constants.json'

########################################## LOAD IN DATA ##########################################
# dictionary with constants
j_file = open(constants_path)
constants_dict = json.load(j_file)
j_file.close()

# get dir paths
processed_dir = constants_dict['processed directory']
trajectory_w_metadata_map_matching_file = constants_dict['map matching out']
edge_info_file = constants_dict['OSM edge info file']

out_file_name_edge = constants_dict['trajectory segment out']['edge df']
out_file_name_node = constants_dict['trajectory segment out']['node df']

# get trajectory df column names
latitude = constants_dict['trajectory cols']['latitude col name']
longitude = constants_dict['trajectory cols']['longitude col name']
trip_id = constants_dict['trajectory cols']['trip id']
speed = constants_dict['trajectory cols']['speed col name']
timestamp = constants_dict['trajectory cols']['timestamp col name']

# get metadata column names
compass_dir = constants_dict['metadata cols']['compass directions']
day_type = constants_dict['metadata cols']['day type']
time_type = constants_dict['metadata cols']['time type']
time_bin = constants_dict['metadata cols']['time bin']
edge = constants_dict['metadata cols']['edge']
node = constants_dict['metadata cols']['node']
avg_speed = constants_dict['metadata cols']['avg speed']
max_speed = constants_dict['metadata cols']['max speed']
min_speed = constants_dict['metadata cols']['min speed']
travel_time = constants_dict['metadata cols']['travel time']

# load in trajectory df
df = pd.read_csv(os.path.join(processed_dir, trajectory_w_metadata_map_matching_file))

# load in edge file
edge_vector_df = pd.read_csv(os.path.join(processed_dir, edge_info_file))

########################################## HELPER FUNCTIONS ##########################################
def get_vector(x1, y1, x2, y2):
    # Calculate the vector components
    vector_x = x2 - x1
    vector_y = y2 - y1

    vector = [vector_x, vector_y]
    return vector

def get_trip_segment_metadata(df):

    # get unique trip_ids
    unique_trip_ids = np.unique(df[trip_id])

    # define df cols
    e_cols = [trip_id, edge, avg_speed, max_speed, min_speed, compass_dir, day_type, time_type, travel_time]
    n_cols = [trip_id, node, avg_speed, max_speed, min_speed, compass_dir, day_type, time_type, travel_time]

    # get edge and node df
    edge_df = get_e_n_df(df, unique_trip_ids=unique_trip_ids, cols=e_cols, val = edge)
    node_df = get_e_n_df(df, unique_trip_ids=unique_trip_ids, cols=n_cols, val = node)

    return edge_df, node_df

def get_e_n_df(df, unique_trip_ids, cols, val):

    # create row list to append values
    rows = []

    # for every unique trip id
    for trip in unique_trip_ids:

        # create subset df
        t_df = df[df[trip_id] == trip]

        # get unique edges/nodes
        unique_e_n = np.unique(t_df[val].dropna())
        # print(f't_df: {t_df.head(3)}')
        # print(f'length of d_df: {len(t_df)}')
        # for every unique edge/node
        for v in unique_e_n:
            # print(f'current v: {v}')

            if val == node:
                v_vector = None
            else:
                v_vector = edge_vector_df[edge_vector_df['Edge'] == v]['Vector'].item()

            v_df = t_df[t_df[val] == v]     # create subset df

            avg_speed, max_speed, min_speed, c_dir, d_type, t_type, travel_t = get_e_n_segment_metadata(v_df, v_vector)     # get metadata

            if val == node:
                v = int(v)
            else:
                v = ast.literal_eval(v)

            new_row = trip, v, avg_speed, max_speed, min_speed, c_dir, d_type, t_type, travel_t
            rows.append(new_row)

    new_df = pd.DataFrame(rows, columns=cols)

    # calculate time_bin col
    new_df[time_bin] = new_df[day_type] + new_df[time_type]

    return new_df

def get_travel_time(df, h_d=False):
    ''' 
    Returns travel time in minutes
    h_d (bool) - False if you just want the time difference between the first and last point,
                 True if you want the time difference divided by the length of the intersection/road
    '''
    # get first and last points of that trajectory segment
    first_point = df.loc[df[timestamp] == min(df[timestamp])]
    last_point = df.loc[df[timestamp] == max(df[timestamp])]

    f_lat = list(first_point[latitude])[0]
    f_long = list(first_point[longitude])[0]
    f_timestamp = list(first_point[timestamp])[0]

    l_lat = list(last_point[latitude])[0]
    l_long = list(last_point[longitude])[0]
    l_timestamp = list(last_point[timestamp])[0]

    # get the time difference between the first and last point
    time_dif = time_difference(p_1=f_timestamp, p_2=l_timestamp, units='minutes')

    if h_d:
        # get the distance between the first and last point
        distance = distance_difference(lat_1=f_lat, lat_2=l_lat, long_1=f_long, long_2=l_long)
        # compute travel time
        tt = np.divide(time_dif, distance)   # if want minutes/miles
        travel_time = round(tt, 4)
    else:
        # compute travel time
        travel_time = round(time_dif, 4)
    
    return travel_time

def get_e_n_segment_metadata(df, v_vector):
    if len(df) == 1:
        one_speed = int(round(df[speed].item()))
        d_type = df[day_type].item()
        t_type = df[time_type].item()
        return one_speed, one_speed, one_speed, np.NaN, d_type, t_type, np.NaN
    
    else:
        ### get speed statistics
        # check if nan value:
        try:
            avg_speed = int(round(np.mean(df[speed])))
            max_speed = int(round(max(df[speed])))
            min_speed = int(round(min(df[speed])))
        except Exception as e:
            avg_speed, max_speed, min_speed = np.NaN, np.NaN, np.NaN
            print(e)

        ### get compass directions (vector or edge name)

        # get first and last points of that trajectory segment
        first_point = df.loc[df[timestamp] == min(df[timestamp])]
        last_point = df.loc[df[timestamp] == max(df[timestamp])]
        if v_vector == None:
            # node case:
            c_dir = last_point['Edge'].item()
            
        else:
            # edge case:
            # get location of first and last points
            f_lat = list(first_point[latitude])[0]
            f_long = list(first_point[longitude])[0]
            l_lat = list(last_point[latitude])[0]
            l_long = list(last_point[longitude])[0]

            # get vector of trajectory segment
            segment_vector = get_vector(f_long, f_lat, l_long, l_lat)

            # compute dot product
            dot_product = np.vdot(ast.literal_eval(v_vector), segment_vector)

            if dot_product > 0:
                c_dir = '+'
            elif dot_product < 0:
                c_dir = '-'
            else:
                c_dir = 'p'

        ### day type
        d_type = get_most_frequent_value(df[day_type])
        ### time type
        t_type = get_most_frequent_value(df[time_type])

        ### travel time
        travel_t = get_travel_time(df)
    
    return avg_speed, max_speed, min_speed, c_dir, d_type, t_type, travel_t


def get_most_frequent_value(col):
    
    counter = Counter(col)
    categories = list(counter.keys())
    counts = list(counter.values())

    max_idx = counts.index(max(counts))

    most_frequent_val = categories[max_idx]

    return most_frequent_val

########################################## MAIN ##########################################
# get edge/node dataframes with trip segment metadata
e_df, n_df = get_trip_segment_metadata(df)

# save edge and node dataframes to csv
e_df.to_csv(os.path.join(processed_dir, out_file_name_edge,), index=False)
n_df.to_csv(os.path.join(processed_dir, out_file_name_node), index=False)
