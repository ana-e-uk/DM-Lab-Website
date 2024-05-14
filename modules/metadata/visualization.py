'''
File name: modules/metadata/visualization.py

Description: contains all the functions that generate the visualization for the
             metadata module webpage/dashboard

             Imports constants from metadata/constants.py

Author: Ana Uribe
'''

########################################## IMPORTS ##########################################
import osmnx as ox
import numpy as np
import random
import pandas as pd

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
