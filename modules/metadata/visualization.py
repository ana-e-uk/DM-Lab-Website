'''
File name: modules/metadata/visualization.py

Description: contains all the functions that generate the visualization for the
             metadata module webpage/dashboard

             Imports constants from metadata/constants.py

Author: Ana Uribe
'''

########################################## IMPORTS ##########################################
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import osmnx as ox
import numpy as np
import random
import pandas as pd
import ast

import geopandas as gpd
from mappymatch.utils.crs import LATLON_CRS
import folium
import networkx as nx

from ipyleaflet import (Marker, 
                        Polyline, 
                        Circle, 
                        Map, 
                        basemaps, 
                        FullScreenControl,
                        basemap_to_tiles, 
                        DrawControl, 
                        Popup, 
                        CircleMarker, 
                        LayerGroup)

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
    Function edited from a function by M.Hemdan

    Plot the roads and nodes on an NxMap.

    Args:
        tmap: The Nxmap to plot.
        m: the folium map to add to

    Returns:
        The folium map with the roads and nodes plotted.
    """
    tmap = nx.MultiDiGraph(ox_map)

    # Plot edges    # TODO make this generic to all map types, not just NxMap
    roads = list(tmap.edges(data=True))
    road_df = pd.DataFrame([r[2] for r in roads])

    print(f'\nRoad df head given to plot_map function in visualization.py {road_df.head(3)}\n')

    gdf = gpd.GeoDataFrame(
        road_df, geometry=road_df['geometry'], crs=LATLON_CRS
    )
    if gdf.crs != LATLON_CRS:
        gdf = gdf.to_crs(LATLON_CRS)

    for t in gdf.itertuples():
        if t.geometry is not None:
            l = [(lat, lon) for lon, lat in t.geometry.coords]
            polyline = Polyline(
                locations=l,
                color="red",
                fill=False,
            )
            popup_content = HTML()
            popup_content.value = f"Edge from {t[1]} to {t[2]}"
            popup = Popup(location=l[0], child=popup_content)
            # def on_polyline_click(event, polyline=polyline, popup=popup):
            #     # Remove existing popups
            #     for layer in m.layers:
            #         if isinstance(layer, Popup):
            #             m.remove_layer(layer)
            #     # Add new popup
            #     m.add_layer(popup)
            # polyline.on_click(on_polyline_click)

            polyline.popup = popup
            m.add_layer(polyline)
            m.add_layer(popup)

    # Plot nodes
    for node, data in tmap.nodes(data=True):
        if 'x' in data and 'y' in data:
            lat = data['y']
            long = data['x']
            circle_marker = CircleMarker(location=[lat, long],
                                         radius=5,
                                         color="blue",
                                         fill=True,
                                         fill_color="blue",
                                         fill_opacity=0.6,
                                         )
            popup_content = HTML()
            popup_content.value = f"Node {node}"
            popup = Popup(location=(lat, long), child=popup_content)
            circle_marker.popup = popup
            m.add_layer(circle_marker)
            m.add_layer(popup)
            
    return m

def no_info_plot(ax, p):
    '''
    p (int) - 1 for speed stats plot, 0 for travel time plot, 2 for flow plot
    '''
    # Adding labels and title
    if p==1:
        ax.set_ylabel('Speed (miles per hour)')
        ax.set_title('Speed Variation Over Time Bins')
    elif p==0:
        ax.set_ylabel('Travel Time (minutes)')
        ax.set_title('Travel Time Variation Over Time Bins')
    elif p==2:
        ax.set_ylabel('Number of Vehicles')
        ax.set_title('Intersection Flow')

    ax.text(0.5, 0.5, 'No Info')

def plot_boxplot(ax, edge_data, p):
    # get current column
    if p == 1:
        cur_col = 'Boxplot_speed'
    else:
        cur_col = 'Boxplot_time'

    # Define the time points and their corresponding labels
    time_points = [-1, 0, 1, 2, 3]
    time_labels = ['Weekend-Night', 'Weekday-Night', 'Weekend-Day', 'Weekday-Day', 'All']
    
    # Check if all 'Boxplot_speed' values are empty points or if there's no data for the edge
    if edge_data.empty or all(ast.literal_eval(row[cur_col]) == {'points': []} for _, row in edge_data.iterrows()):
        no_info_plot(ax, p)
        return
    
    for idx, time_point in enumerate(time_points):
        row = edge_data[edge_data['Time_bin'] == time_point]
        
        if row.empty:
            continue
        
        boxplot_speed = ast.literal_eval(row.iloc[0][cur_col])
        
        if 'q1' in boxplot_speed:
            ax.bxp([boxplot_speed], positions=[idx], showfliers=True)
        elif 'points' in boxplot_speed:
            if boxplot_speed['points']:
                x_coords = np.full(len(boxplot_speed['points']), idx)
                ax.scatter(x_coords, boxplot_speed['points'], color='black', marker='s', zorder=3)
    
    # Customize the plot
    ax.set_xticks(range(len(time_points)))
    ax.set_xticklabels(time_labels, rotation=45)
    ax.set_xlim(-1, 5)

    if p==1:
        ax.set_ylabel('Speed (miles per hour)')
        ax.set_title('Speed Variation Over Time Bins')
    else:
        ax.set_ylabel('Travel Time (minutes)')
        ax.set_title('Travel Time Variation Over Time Bins')

    ax.grid(True)

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
            no_info_plot(ax, p=1)
            return
        avg_speeds=cur_df['Avg_speed']
        confidence_intervals=cur_df['Avg_speed_CI']
        min_speeds=cur_df['Min_speed']
        max_speeds=cur_df['Max_speed']
    else:
        cur_df= df.dropna(subset=['Travel_time', 'Travel_time_CI'])
        if cur_df.empty:
            no_info_plot(ax, p=0)
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

def plot_flow(ax, edge_data):
    # Define the time points and their corresponding labels
    time_points = [-1, 0, 1, 2, 3]
    time_labels = ['Weekend-Night', 'Weekday-Night', 'Weekend-Day', 'Weekday-Day', 'All']

    # Check if there's no data for the edge
    if edge_data.empty:
        no_info_plot(ax, p=2)
        return
    
    # Initialize bar_width and position offset
    bar_width = 0.1
    
    # Collect all unique keys to assign colors
    unique_keys = set()
    for idx, time_point in enumerate(time_points):
        row = edge_data[edge_data['Time_bin'] == time_point]
        if row.empty:
            continue
        flow_data = ast.literal_eval(row.iloc[0]['Flow'])
        unique_keys.update(flow_data.keys())
    
    # Create a color map for the unique keys
    colors = plt.get_cmap('tab20', len(unique_keys))
    color_map = {key: colors(i) for i, key in enumerate(unique_keys)}
    
    # Collect bar heights and labels
    bar_heights = {time_point: [] for time_point in time_points}
    bar_labels = {time_point: [] for time_point in time_points}
    
    for idx, time_point in enumerate(time_points):
        row = edge_data[edge_data['Time_bin'] == time_point]
        
        if row.empty:
            continue
        
        flow_data = ast.literal_eval(row.iloc[0]['Flow'])
        
        for key, value in flow_data.items():
            bar_heights[time_point].append(value)
            bar_labels[time_point].append(key)
    
    # Plot the bars for each time point
    for idx, time_point in enumerate(time_points):
        heights = bar_heights[time_point]
        labels = bar_labels[time_point]
        
        if not heights:
            continue
        
        # Compute positions for the bars
        positions = np.arange(len(heights)) * bar_width + (idx - len(heights) / 2 * bar_width)
        
        # Plot each bar with the corresponding color
        for pos, height, label in zip(positions, heights, labels):
            ax.bar(pos, height, width=bar_width, color=color_map[label], label=label)
    
    # Customize the plot
    ax.set_xticks(range(len(time_points)))
    ax.set_xticklabels(time_labels, rotation=45)
    ax.set_xlim(-1, 5)
    ax.set_ylabel('Number of Vehicles')
    ax.set_title(f'Distribution of Trajectory Counts')
    
    # Create a legend with unique keys
    handles = [plt.Line2D([0], [0], color=color_map[key], lw=4) for key in unique_keys]
    ax.legend(handles, unique_keys, loc='upper right')

    # Set y-axis to increment by whole values
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

def generate_markdown(row, node):
    '''
    row (pandas dataframe) - one row corresp. to node or edge
    node (bool) - True if node, False if edge
    '''

    if node:
        # Node,OSM_street_count,OSM_highway,OSM_edges,Street_count,Count
        return f"""
                <h3>Intersection Structural Metadata:</h3>
                <table border="1" style="border-collapse: collapse; width: 50%;">
                    <tr>
                        <th>Metadata Value</th>
                        <th>GPS</th>
                        <th>OSM</th>
                    </tr>
                    <tr>
                        <td>Highway</td>
                        <td>TBD</td>
                        <td>{row['OSM_highway'].item()}</td>
                    </tr>
                    <tr>
                        <td>GPS Trajectory Counts</td>
                        <td>{int(row['Count'].item())}</td>
                        <td>X</td>
                    </tr>
                    <tr>
                        <td>Street Count</td>
                        <td>{row['Street_count'].item()}</td>
                        <td>{row['OSM_street_count'].item()}</td>
                    </tr>
                </table>
                """
    else:
        # Edge,OSM_oneway,OSM_lanes,OSM_name,OSM_highway,OSM_maxspeed,OSM_length,Oneway,Count
        return f"""
                <h3>Road Structural Metadata:</h3>
                <table border="1" style="border-collapse: collapse; width: 50%;">
                    <tr>
                        <th>Metadata Value</th>
                        <th>GPS</th>
                        <th>OSM</th>
                    </tr>
                    <tr>
                        <td>Highway</td>
                        <td>TBD</td>
                        <td>{row['OSM_highway'].item()}</td>
                    </tr>
                    <tr>
                        <td>GPS Trajectory Counts</td>
                        <td>{int(row['Count'].item())}</td>
                        <td>X</td>
                    </tr>
                    <tr>
                        <td>Oneway</td>
                        <td>{row['Oneway'].item()}</td>
                        <td>{row['OSM_oneway'].item()}</td>
                    </tr>
                    <tr>
                        <td>Maxspeed</td>
                        <td>Graphed</td>
                        <td>{row['OSM_maxspeed'].item()}</td>
                    </tr>
                    <tr>
                        <td>Lanes</td>
                        <td>TBD</td>
                        <td>{row['OSM_lanes'].item()}</td>
                    </tr>
                    <tr>
                        <td>Name</td>
                        <td>X</td>
                        <td>{row['OSM_name'].item()}</td>
                    </tr>
                    <tr>
                        <td>Length</td>
                        <td>TBD</td>
                        <td>{round(row['OSM_length'].item(), 2)}</td>
                    </tr>
                </table>
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
