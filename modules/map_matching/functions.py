'''
File name: panel-scripts/map_matching_pn.py

Description: contains the Panel code that generates the map-matching webpage/dashboard
             of the website.

             Calls functions in module-scripts/map-matching, and utils folders.
Author: Mohamed Hemdan
'''
import pandas as pd
from visualization import (plot_matches_on_pyleaflet)

from mappymatch.constructs.trace import Trace
from mappymatch.constructs.geofence import Geofence
from mappymatch.maps.nx.nx_map import NxMap, NetworkType
from mappymatch.matchers.lcss.lcss import LCSSMatcher
import random

########################################## SIDEBAR ELEMENTS ########################################## 


def map_match(traj_filename, map):
    # Step 1: Read the csv file
    import os
    print("Traj Filename: ", traj_filename)
    print('current folder: ', os.getcwd())
    df = pd.read_csv('./data/examples/'+traj_filename)  # Update 'your_data.csv' with your CSV file path

    print("Selecting one Trajectory!")
    vechile_ids = df["Vehicle ID"].unique()
    # one_id = vechile_ids[0]
    one_id = random.choice(vechile_ids)
    sub_df = df[df["Vehicle ID"] == one_id]
    sub_df.sort_values(by=['Position Date Time'], inplace=True)    

    # Do Map Matching
    print("Getting the trace!")
    trace = Trace.from_dataframe(dataframe=sub_df, xy=True, lat_column='lat', lon_column='long')
    print("Getting the geofence!")
    geofence = Geofence.from_trace(trace, padding=1e3)
    print("Getting the underlying road network!")
    nx_map = NxMap.from_geofence(geofence, network_type=NetworkType.DRIVE)
    print("Matching the trace to the road network!")
    matcher = LCSSMatcher(nx_map)
    match_result = matcher.match_trace(trace)

    # Plotting the match result
    print("Now Plotting the matches...!")
    plot_matches_on_pyleaflet(matches=match_result.matches, map=map)