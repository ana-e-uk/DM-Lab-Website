'''
File name: modules/metadata/visualization.py

Description: contains all the functions that generate the visualization for the
             metadata module webpage/dashboard

             Imports constants from metadata/constants.py

Author: Ana Uribe
'''

########################################## IMPORTS ##########################################
import matplotlib.pyplot as plt

import osmnx as ox
import numpy as np
import random
import pandas as pd
import ast

import geopandas as gpd
from mappymatch.utils.crs import LATLON_CRS
import folium
import networkx as nx


from ipyleaflet import Marker, Polyline, Circle, Map, basemaps, FullScreenControl, basemap_to_tiles, DrawControl, Polyline, Popup
from ipywidgets import HTML

from constants import (
                        FIG_SIZE,
                        GRAPH_BG_COLOR,
                        NODE_COLOR,
                        NODE_SIZE, 
                        EDGE_COLOR,

                        TRAJ_POINT_MARKER,
                        TRAJ_POINT_MARKER_SIZE,
                        PLOT_TYPES,
                      )

########################################## FUNCTIONS ########################################
def plot_map(ox_map, m=None):
    """
    Plot the roads on an NxMap.

    Args:
        tmap: The Nxmap to plot.
        m: the folium map to add to

    Returns:
        The folium map with the roads plotted.
    """
    tmap = nx.MultiDiGraph(ox_map)

    # TODO make this generic to all map types, not just NxMap
    roads = list(tmap.edges(data=True))
    road_df = pd.DataFrame([r[2] for r in roads])

    # print(road_df.head(3))

    gdf = gpd.GeoDataFrame(
        road_df, geometry=road_df['geometry'], crs=LATLON_CRS
    )
    if gdf.crs != LATLON_CRS:
        gdf = gdf.to_crs(LATLON_CRS)
    
    # m.center = gdf.iloc[int(len(gdf) / 2)].geometry.centroid.coords[0]
    # m.zoom = 14

    for t in gdf.itertuples():
        # print(t.geometry.coords)
        if t.geometry is None:
            pass
        else:
            l = [(lat, lon) for lon, lat in t.geometry.coords]
            c = l[0]
            # polyline = folium.PolyLine(
            polyline = Polyline(
                locations=l,
                color="red",
                # tooltip=[t.maxspeed, t.oneway]
            )#.add_to(m)
            polyline.popup = HTML("Hello World")
            m.add_layer(polyline)

            # message = HTML()
            # # message = f"<b>Oneway:</b> {t.oneway}"
            # message.value = "Hi"
            # popup = Popup(
            #     location=c,
            #     child=message,
            #     close_button=True,
            #     auto_close=False,
            #     close_on_escape_key=False
            #     )   
            # m.add(popup)
            # polyline.popup(message)
            
    return m

def no_info_plot(ax, min_max):
    # Adding labels and title
    ax.set_xlabel('Time Bins')
    ax.set_xticks([-1, 0, 1, 2, 3],['Weekend-Night', 'Weekday-Night', 'Weekend-Day', 'Weekday-Day', 'All'], rotation=20)
    ax.set_xlim([-1.5, 3.5])
    if min_max:
        ax.set_ylabel('Speed (miles per hour)')
        ax.set_title('Speed Variation Over Time Bins')
    else:
        ax.set_ylabel('Travel Time (minutes)')
        ax.set_title('Travel Time Variation Over Time Bins')

    ax.text(0.5, 0.5, 'No Info')

def plot_speed_stats(ax, df, min_max):
    ''' 
    Plots the avg, min, max speeds at each time point and plots error bars as confidence intervals.
    Confidence intervals are assumed to have the specific min and max values, speed is assumed to be mph
    '''
    # Sort values df by Time_bin
    df.sort_values('Time_bin')
    
    if min_max:
        cur_df = df.dropna(subset=['Avg_speed', 'Avg_speed_CI', 'Max_speed', 'Min_speed'])
        if cur_df.empty:
            no_info_plot(ax, min_max)
            return
        avg_speeds=cur_df['Avg_speed']
        confidence_intervals=cur_df['Avg_speed_CI']
        min_speeds=cur_df['Min_speed']
        max_speeds=cur_df['Max_speed']
    else:
        cur_df= df.dropna(subset=['Travel_time', 'Travel_time_CI'])
        if cur_df.empty:
            no_info_plot(ax, min_max)
            return
        avg_speeds=cur_df['Travel_time']
        confidence_intervals=cur_df['Travel_time_CI']
    
    # Get all columns from df
    time_points=cur_df['Time_bin'] 

    # Make confidence intervals var a list
    confidence_intervals = list(confidence_intervals)
    
    # Turn confidence intervals into tuple values
    if type(confidence_intervals[0]) == tuple:
        pass
    elif type(confidence_intervals[0]) == float:
        pass
    else:
        confidence_intervals = [tuple(map(float, s[1:-1].split(','))) for s in confidence_intervals]
    
    # Calculate error bars using confidence intervals
    lower_errors = [np.abs(conf[0] - avg) for avg, conf in zip(avg_speeds, confidence_intervals)]
    upper_errors = [np.abs(conf[1] - avg) for avg, conf in zip(avg_speeds, confidence_intervals)]

    # Plotting
    ax.errorbar(time_points, avg_speeds, yerr=[lower_errors, upper_errors], fmt='o', label='Average Speed', capsize=5)

    if min_max:
        ax.scatter(time_points, min_speeds, color= 'blue', marker= '^', s= 60, label='Minimum Speed')
        ax.scatter(time_points, max_speeds, color = 'green', marker= 'v', s= 60, label='Maximum Speed')

    # Adding labels and title
    ax.set_xlabel('Time Bins')
    ax.set_xticks([-1, 0, 1, 2, 3],['Weekend-Night', 'Weekday-Night', 'Weekend-Day', 'Weekday-Day', 'All'], rotation=20)
    ax.set_xlim([-1.5, 3.5])
    if min_max:
        ax.set_ylabel('Speed (miles per hour)')
        ax.set_title('Speed Variation Over Time Bins')
    else:
        ax.set_ylabel('Travel Time (minutes)')
        ax.set_title('Travel Time Variation Over Time Bins')

    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.grid(True)

def plot_lines(ax, time, counts_list, labels=None):
    """
    Plot multiple lines on a single plot.
    
    Parameters:
        time (array-like): Array containing time points.
        counts_list (list of array-like): List of arrays containing counts for each line.
        labels (list of str, optional): List of labels for each line. If None, labels will not be shown.
    """
    if labels is None:
        labels = ['Line {}'.format(i+1) for i in range(len(counts_list))]

    for counts, label in zip(counts_list, labels):
        ax.scatter(time, counts, marker='o', label=label)

    ax.set_xlabel('Time Bins')
    ax.set_ylabel('Number of Vehicles')
    ax.set_title('Intersection Flow')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    ax.set_xticks([-1, 0, 1, 2], ['Weekend-Night', 'Weekday-Night', 'Weekend-Day', 'Weekday-Day'], rotation=20)
    ax.set_xlim([-1.5, 3.5])

    ax.grid(True)

def process_node_flows(df):
    # Function to safely evaluate the string to a dictionary
    def safe_literal_eval(val):
        if type(val) == dict:
            return val
        else:
            try:
                return ast.literal_eval(val)
            except (ValueError, SyntaxError):
                return {}

    # Convert the 'Flow' column from string to dictionary safely
    df.loc[:, 'Flow'] = df['Flow'].apply(safe_literal_eval)

    # Expand the 'Flow' dictionary into separate columns
    flow_expanded = df['Flow'].apply(pd.Series)

    # Combine the expanded Flow columns with the original DataFrame
    df = pd.concat([df[['Time_bin']], flow_expanded], axis=1)

    # Fill NaN values with 0
    df = df.fillna(0)

    # Pivot the table to get the desired structure
    result = df.pivot_table(index='Time_bin', aggfunc='sum').sort_index()

    # Get the times and labels
    times = result.index.tolist()
    labels = result.columns.tolist()
    value_counts = [result[label].tolist() for label in labels]

    return times, labels, value_counts

def get_flow_plot(ax, cur_n_f):
    times_list, labels, values = process_node_flows(cur_n_f)
    # print('\n')
    # print(labels)
    # print('\n')
    # print(times_list)
    # print('\n')
    # print(values)
    plot_lines(ax, time=times_list, counts_list=values, labels=labels)

def generate_markdown(row, node):
    if node:
        return f"""
        **Intersection Structural Metadata:**

        **Intersection Index**: {row['Node']}
        
        **Street Count**:
            - **GPS**: {row['Edges_count']}
        
        **Number of GPS trajectories corresponding to this intersection**: {row['Count']}
        """
    else:
        return f"""
        **Road Structural Metadata:**

        **Road Index**: {row['Edge']}
        
        **Driving Directions**:
            - **GPS**: {row['Compass_dir']}

        **Oneway**:
            - **GPS**: {row['Directions']}
        
        **Number of GPS trajectories corresponding to this intersection**: {row['Count']}
        """
        # Final version
        return f"""
            **Intersection Structural Metadata:**

            **Intersection Index**: {row['Node']}
            
            **Street Count**:
                - **OSM**: {row['OSM_Street_count']}
                - **GPS**: {row['Edges_count']}
            
            **Road Type**:
                - **OSM**: {row['OSM_road_type']}
            
            **Number of GPS trajectories corresponding to this intersection**: {row['Count']}
            """

########################################## HELPER FUNCTIONS #################################
def get_unique_colors(num_colors):
    '''
    INPUT: num_colors (int) - the number of unique colors you want

    OUTPUT: colors (list) - list of hexidecimal color codes

    Code from: https://www.tutorialspoint.com/how-to-generate-random-colors-in-matplotlib
    '''
    hexadecimal_alphabets = '0123456789ABCDEF'
    colors = ["#" + ''.join([random.choice(hexadecimal_alphabets) for j in range(6)]) for i in range(num_colors)]
    
    return colors

def plot_graph_only(G, verbose=False):
    '''
    INPUT: G (osmnx MultiDiGraph) - graph that will be plotted
           verbose (boolean) - True if you want print statements, else False

    OUTPUT: fig, ax - matplotlib figure and axis with the graph
    '''

    # call osmnx function that plots graph
    fig, ax = ox.plot_graph(G=G,
                            figsize=FIG_SIZE,
                            bgcolor=GRAPH_BG_COLOR,
                            node_color=NODE_COLOR,
                            node_size=NODE_SIZE,
                            edge_color=EDGE_COLOR,
                            show=False              #TODO: make sure this is ok
                            )
    
    if verbose:
        print(f'Number of edges in graph: {len(G.edges)}')
        print(f'Number of nodes in graph: {len(G.nodes)}')

    return fig
    return fig, ax

def plot_graph_and_traj(G, lat_col, long_col, color, plot_type):
    '''
    INPUT: G (osmnx MultiDiGraph) - graph that will be plotted
           lat_col (pandas DataFrame column (series)) - latitude values of the trajectories
           long_col (pandas DataFrame column (series)) - longitude values of the trajectories
           color (str) - color of trajectory 
           plot_type (str) - how to plot trajectory: options:
                                                        'scatter' - plots each point as point
                                                        'line' - plots trajectory as a line

    OUTPUT: fig, ax - matplotlib figure and axis with the graph and trajectories given plotted together
    '''

    # plot graph G on matplotlib axis
    fig, ax = plot_graph_only(G)

    if plot_type == 'line':
        ax.plot(long_col, lat_col, marker=TRAJ_POINT_MARKER, c=color,  markersize=TRAJ_POINT_MARKER_SIZE)

    elif plot_type == 'scatter':
        ax.scatter(long_col, lat_col, marker=TRAJ_POINT_MARKER, c=color)
    else:
        print(f'plot_type parameter only takes in the following values: {PLOT_TYPES}\ncurrent value is {plot_type}, so trajectory was not plotted.')

    return fig
    return fig, ax

def plot_graph_and_multiple_traj(G, trajectory_df, traj_idx_col, plot_type):
    '''
    INPUT: G (osmnx MultiDiGraph) - graph that will be plotted
           trajectory_df (pandas DataFrame) with trajectories where latitude column name is 'lat' and longitude column is 'long'
           traj_idx_col (str) - name of column that has the trajectory indices
           plot_type (str) - how to plot trajectories: options:
                                                        'scatter' - plots each point as point
                                                        'line' - plots trajectory as a line

    OUTPUT: fig, ax - matplotlib figure and axis with the graph and trajectories given plotted together
    '''

    # plot graph G on matplotlib axis
    fig, ax = plot_graph_only(G)

    unique_traj = np.unique(trajectory_df[traj_idx_col])

    traj_colors = get_unique_colors(int(len(unique_traj)))

    for i in range(len(unique_traj)):

        cur_unique_traj = unique_traj[i]
        cur_df = trajectory_df[trajectory_df[traj_idx_col] == cur_unique_traj]

        if plot_type == 'line':
            ax.plot(cur_df.long, cur_df.lat, marker=TRAJ_POINT_MARKER, c=traj_colors[i],  markersize=TRAJ_POINT_MARKER_SIZE)

        elif plot_type == 'scatter':
            ax.scatter(cur_df.long, cur_df.lat, marker=TRAJ_POINT_MARKER, c=traj_colors[i])
        else:
            print(f'plot_type parameter only takes in the following values: {PLOT_TYPES}\ncurrent value is {plot_type}, so trajectory was not plotted.')

    return fig
    return fig, ax
