'''
File name: get_map_metadata

DESCRIPTION: Given datasets with the following information:
                < trajectory_id, edge, avg speed, max speed, min speed, compass direction, day type, time type >
             and
                < trajectory_id, node, avg speed, max speed, min speed, compass direction, day type, time type >
             
             Compute metadata (speed statistics, driving (oneways) and turn directions, road and intersection flows)
             for each of the edges and nodes.

             Imports functions from utils.py

Author: Ana Uribe
'''
########################################## IMPORTS ##########################################
import json
import numpy as np
import pandas as pd
import os
import ast

from collections import Counter
from scipy.stats import t

########################################## VARIABLES ##########################################
constants_path = '/Users/bean/Documents/masters-project/map-metadata/constants.json'

########################################## LOAD IN DATA ##########################################
# dictionary with constants
j_file = open(constants_path)
constants_dict = json.load(j_file)
j_file.close()

# get dir paths
in_dir = constants_dict['input directory']
processed_dir = constants_dict['processed directory']
out_dir = constants_dict['output directory']

# get file names
# in
n_file_name = constants_dict['trajectory segment out']['node df']
e_file_name = constants_dict['trajectory segment out']['edge df']

osm_n_file = constants_dict['OSM node info file']
osm_e_file = constants_dict['OSM edge info file']

# out
n_s = constants_dict['map metadata out']['node structural']
n_f = constants_dict['map metadata out']['node functional']
e_s = constants_dict['map metadata out']['edge structural']
e_f = constants_dict['map metadata out']['edge functional']

# metadata column names
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


# load files as pandas dataframes
n_df = pd.read_csv(os.path.join(processed_dir, n_file_name))
e_df = pd.read_csv(os.path.join(processed_dir, e_file_name))

osm_n_df = pd.read_csv(os.path.join(processed_dir, osm_n_file))
osm_e_df = pd.read_csv(os.path.join(processed_dir, osm_e_file))
osm_e_df = osm_e_df[['Edge','OSM_oneway','OSM_lanes','OSM_name','OSM_highway','OSM_maxspeed','OSM_length']]# don't need to save vector
########################################## HELPER FUNCTIONS ##########################################
def compute_oneway(x):
   set_x = set(x)
   if set_x == {np.NaN}:
      return None
   elif '-' in set_x and '+' in set_x:
      return False
   else:
      return True
   
def compute_street_count(x):
   set_x = set(x)
   return len(set_x)
   
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

def get_functional_row(s):
   # get flow
   fl = Counter(s['Compass_dir'])
   key_to_delete = np.NaN
   try:
      del fl[key_to_delete]
   except:
      pass

   # get box plot for speed
   # Convert to pandas Series
   data_series = pd.Series(s[avg_speed].dropna())

   # Calculate summary statistics
   if data_series.empty or len(data_series) < 4:  # at least 4 data points needed to calculate quartiles:
      summary_stats = {'points': list(s[avg_speed].dropna())}
   else:
      summary_stats = {
         'whislo': data_series.min(),
         'q1': data_series.quantile(0.25),
         'med': data_series.median(),
         'q3': data_series.quantile(0.75),
         'whishi': data_series.max(),
         'fliers': list(data_series[(data_series < data_series.quantile(0.25) - 1.5 * (data_series.quantile(0.75) - data_series.quantile(0.25))) | 
                                 (data_series > data_series.quantile(0.75) + 1.5 * (data_series.quantile(0.75) - data_series.quantile(0.25)))])
      }
   
   # get box plot for time
   # Convert to pandas Series
   data_series = pd.Series(s[travel_time].dropna())
   # print(data_series)
   # Calculate summary statistics
   if data_series.empty or len(data_series) < 4:  # at least 4 data points needed to calculate quartiles:
      summary_stats_t = {'points': list(s[travel_time].dropna())}
   else:
      summary_stats_t = {
         'whislo': data_series.min(),
         'q1': data_series.quantile(0.25),
         'med': data_series.median(),
         'q3': data_series.quantile(0.75),
         'whishi': data_series.max(),
         'fliers': list(data_series[(data_series < data_series.quantile(0.25) - 1.5 * (data_series.quantile(0.75) - data_series.quantile(0.25))) | 
                                 (data_series > data_series.quantile(0.75) + 1.5 * (data_series.quantile(0.75) - data_series.quantile(0.25)))])
      }

   # get average speed vales
   a_s_col = s[avg_speed]
   a_s_no_nan = a_s_col.dropna()
   if len(a_s_no_nan) == 0:
      avg_ci = np.NAN
      avg_s = np.NAN
   elif len(a_s_no_nan) == 1:
      avg_ci = np.NAN
      avg_s = int(round(a_s_no_nan.item()))
   else:
      avg_ci, avg_s = calc_confidence_interval(a_s_no_nan)
      avg_s = int(round(avg_s))

   # get travel time values
   tt_col = s[travel_time]
   tt_no_nan = tt_col.dropna()
   if len(tt_no_nan) == 0:
      travel_t_ci = np.NAN
      travel_t = np.NAN
   elif len(tt_no_nan) == 1:
      travel_t_ci = np.NAN
      travel_t = round(tt_no_nan.item(), 4)
   else:
      travel_t_ci, travel_t = calc_confidence_interval(tt_no_nan)
      round(travel_t, 4)

   # get max speed values
   max_no_nan = s[max_speed].dropna()
   min_no_nan = s[min_speed].dropna()
   if len(max_no_nan) == 0:
      max_s = np.NAN
   elif len(max_no_nan) == 1:
      max_s = max_no_nan.item()
   else:
      max_s = int(round(max(max_no_nan)))
    
   # get min speed values
   min_no_nan = s[min_speed].dropna()
   if len(min_no_nan) == 0:
      min_s = np.NAN
   elif len(min_no_nan) == 1:
      min_s = min_no_nan.item()
   else:
      min_s = int(round(min(min_no_nan)))

   return avg_s, avg_ci, max_s, min_s, travel_t, travel_t_ci, dict(fl), summary_stats, summary_stats_t

def get_functional_metadata(df, val):

   # define columns
   cols = [val, time_bin, avg_speed, avg_speed_ci, max_speed, min_speed, travel_time, travel_time_ci, flow, 'Boxplot_speed', 'Boxplot_time', traj_count]
   # list to append new rows
   rows = []
   # define time bins (for functional vals)
   unique_time_bins = [-1, 1, 0, 2]
   # get unique values
   unique_vals = np.unique(df[val].dropna())

   # for every unique val (edge/node)
   for v in unique_vals:
      # create subset df
      v_df = df[df[val] == v]
      # check size of df
      if len(v_df) < 7:
         # compute all trajectories together regardless of time bin
         avg_s, avg_ci, max_s, min_s, travel_t, travel_t_ci, fl, boxplot_stats, boxplot_stats_t = get_functional_row(v_df)
         new_row = [v, 3, avg_s, avg_ci, max_s, min_s, travel_t, travel_t_ci, fl, boxplot_stats, boxplot_stats_t, len(v_df)]
         rows.append(new_row)
      else:
         # make a row for each time bin
         for b in unique_time_bins:
            # create subset df
            b_df = v_df[v_df[time_bin] == b]
            avg_s, avg_ci, max_s, min_s, travel_t, travel_t_ci, fl, boxplot_stats, boxplot_stats_t = get_functional_row(b_df)
            new_row = [v, b, avg_s, avg_ci, max_s, min_s, travel_t, travel_t_ci, fl, boxplot_stats, boxplot_stats_t, len(b_df)]
            rows.append(new_row)

   functional_df = pd.DataFrame(rows, columns=cols)
   return functional_df

def get_edge_metadata(df, val):
   '''
   Using the saved osm information as well as the trajectory segment information, 
   return the edge structural and functional data:
      structural - Edge,Vector,     Oneway,Trajectory_count,      OSM_oneway,OSM_lanes,OSM_name,OSM_highway,OSM_maxspeed,OSM_length,
      functional - Edge, speed, speed CI, box_plots info, travel_time, CIs, trajectory_count
   '''
   ### Compute functional metadata
   e_f_df = get_functional_metadata(df, val)

   ### Compute structural metadata
   # compute oneway and total num of trajectories columns
   oneway_col = df.groupby(val).agg({'Compass_dir': [compute_oneway]})
   num_traj_col = e_f_df.groupby(val).agg({traj_count: ['sum']})
   
   def grab_s_data(x):
      oneway = oneway_col.xs(x).item()
      t_count = num_traj_col.xs(x).item()

      return oneway, t_count
   
   osm_e_df[['Oneway', traj_count]] = osm_e_df[val].apply(lambda x: pd.Series(grab_s_data(x)))
   
   return osm_e_df, e_f_df

def get_node_metadata(df, val):
   ### Compute functional metadata
   n_f_df = get_functional_metadata(df, val)

   ### Compute structural metadata
   # compute street count and total num of trajectories columns
   street_count_col = df.groupby(val).agg({'Compass_dir': [compute_street_count]})
   num_traj_col = n_f_df.groupby(val).agg({traj_count: ['sum']})

   def grab_s_data(x):
      try:
         st_count = street_count_col.xs(x).item()
         t_count = num_traj_col.xs(x).item()
      except Exception as e:
         st_count = 0
         t_count = 0
         print('Exception: x: ', x) #TODO: figure out why there's one nan value being passed
      return st_count, t_count

   osm_n_df[val].dropna()
   osm_n_df[['Street_count', traj_count]] = osm_n_df[val].apply(lambda x: pd.Series(grab_s_data(x)))

   return osm_n_df, n_f_df


########################################## MAIN ##########################################
# get the edge/node functional and structural metadata 
e_s_df, e_f_df = get_edge_metadata(e_df, val=edge)
n_s_df, n_f_df = get_node_metadata(n_df, val=node)

# # save all four dataframes to csv
e_s_df.to_csv(os.path.join(out_dir, e_s), index=False)
e_f_df.to_csv(os.path.join(out_dir, e_f), index=False)
n_s_df.to_csv(os.path.join(out_dir, n_s), index=False)
n_f_df.to_csv(os.path.join(out_dir, n_f), index=False)