'''
File name: module-scripts/metadata/visualization.py

Description: contains all the functions that generate the visualization for the
             metadata module webpage/dashboard

             Imports constants from metadata/constants.py

Author: Ana Uribe
'''

########################################## IMPORTS ##########################################
import osmnx as ox
import numpy as np
import random

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

########################################## FUNCTIONS ########################################

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


############################################################
from mappymatch.matchers.matcher_interface import MatchResult
from mappymatch.utils.crs import LATLON_CRS, XY_CRS
from shapely.geometry import Point
from typing import List
from mappymatch.constructs.match import Match
import pandas as pd
import geopandas as gpd
from ipyleaflet import Marker, Polyline, Circle, Map, basemaps, FullScreenControl, basemap_to_tiles, DrawControl, Polyline, Popup
from shapely.geometry import LineString

def plot_matches_on_pyleaflet(matches: List[Match], crs=XY_CRS, map=None):
    """
    Plots a trace and the relevant matches on a folium map.

    Args:
    matches: The matches.
    road_map: The road map.

    Returns:
        A folium map with trace and matches plotted.
    """

    def _match_to_road(m):
        """Private function."""
        d = {"road_id": m.road.road_id, "geom": m.road.geom}
        return d

    def _match_to_coord(m):
        """Private function."""
        d = {
            "road_id": m.road.road_id,
            "geom": Point(m.coordinate.x, m.coordinate.y),
            "distance": m.distance,
        }

        return d

    road_df = pd.DataFrame([_match_to_road(m) for m in matches if m.road])
    road_df = road_df.loc[road_df.road_id.shift() != road_df.road_id]
    road_gdf = gpd.GeoDataFrame(road_df, geometry=road_df.geom, crs=crs).drop(
        columns=["geom"]
    )
    road_gdf = road_gdf.to_crs(LATLON_CRS)

    coord_df = pd.DataFrame([_match_to_coord(m) for m in matches if m.road])

    coord_gdf = gpd.GeoDataFrame(
        coord_df, geometry=coord_df.geom, crs=crs
    ).drop(columns=["geom"])
    coord_gdf = coord_gdf.to_crs(LATLON_CRS)

    mid_i = int(len(coord_gdf) / 2)
    mid_coord = coord_gdf.iloc[mid_i].geometry

    map.center = (mid_coord.y, mid_coord.x)
    map.zoom = 14

    for coord in coord_gdf.itertuples():
        marker = Circle(
            location=(coord.geometry.y, coord.geometry.x),
            radius=5,
            tooltip=f"road_id: {coord.road_id}\ndistance: {coord.distance}",
            color = "red",  # Set the color of the point circle
            fill_color = "red"  
            )
        map.add_layer(marker)

    for road in road_gdf.itertuples():
        polyline = Polyline(
            locations=[(lat, lon) for lon, lat in road.geometry.coords],
            color="blue",
            tooltip=road.road_id
        )
        map.add_layer(polyline)

    return map

def plot_traj_from_file(traj_filepath, crs, map=None):
    #TODO: Remove the crs from here, to be determined by the user
    """
    Plots a trajectory on a ipyleaflet map.

    Args:
    traj_filepath: The filepath of the trajectory.
    road_map: The road map.

    Returns:
        A folium map with trace and matches plotted.
    """
    print("Traj Filename: ", traj_filepath)
    df = pd.read_csv(traj_filepath)  # Update 'your_data.csv' with your CSV file path
    # print("Selecting one Trajectory!")
    vechile_ids = df["Vehicle ID"].unique()
    # one_id = vechile_ids[0]
    if len(vechile_ids) > 1:
        raise Exception("Value Error: More than one trajectory is present!")
        one_id = random.choice(vechile_ids)
        sub_df = df[df["Vehicle ID"] == one_id]
    else:
        one_id = vechile_ids[0]
        sub_df = df
    sub_df.sort_values(by=['Position Date Time'], inplace=True)    

    geometry = gpd.points_from_xy(df.long, df.lat)

    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=geometry)

    # Set the coordinate reference system (CRS)
    gdf.crs = crs #'EPSG:4326'  # WGS84 coordinate system

    gdf = gdf.to_crs(LATLON_CRS)

    mid_i = int(len(gdf) / 2)
    mid_coord = gdf.iloc[mid_i].geometry

    map.center = (mid_coord.y, mid_coord.x)
    map.zoom = 14

    # Create a LineString from the points
    line = LineString(gdf['geometry'])

    # Create a Polyline object from the LineString
    print('Plotting the ployline')
    polyline = Polyline(
        locations=[(lat, lon) for lon, lat in line.coords],
        color="blue",
        fill=False
    )
    map.add_layer(polyline)

    print("Ploting the circles")
    for coord in gdf.itertuples():
        marker = Circle(
            location=(coord.geometry.y, coord.geometry.x),
            radius=5,
            # tooltip=f"road_id: {coord.road_id}\ndistance: {coord.distance}",
            color = "red",  # Set the color of the point circle
            fill_color = "red"  
            )
        map.add_layer(marker)

    return map