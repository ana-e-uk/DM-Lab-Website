

########################################## IMPORTS ##########################################

import pandas as pd
from tqdm import tqdm
import datetime
import math
import time
import requests
import pickle as pk
import os
import sys
import geopandas as gpd
from shapely.geometry import Point, LineString, shape
import folium
import matplotlib
import mapclassify
from ipyleaflet import Marker, Polyline, Circle, Map, basemaps, FullScreenControl, basemap_to_tiles, DrawControl, Popup, GeoData, LayersControl
from branca.colormap import linear

########################################## Functions ##########################################

def getDistanceFromLatLonInm(lat1,lon1,lat2,lon2): 
    R = 6378100 # radius in meters
    deg_cov = math.pi/180
    dLat = (deg_cov)*(lat2-lat1)  # deg2rad below
    dLon = deg_cov*(lon2-lon1) 
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(deg_cov*(lat1)) * math.cos(deg_cov*(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)); 
    d = R * c # Distance in km
    return d



def trajSplit(filename, map):
    trajsplit_gdf = gpd.read_feather("data\output\TrajSplit\TrajSplitdata_upload_2024_04_08-08_02_15_%-TS-cleaning.feather")
    trajsplit_gdf['prev_trip_id'] = trajsplit_gdf['trip_id'].apply(lambda x: float(x.split('-')[0]))
    trajsplit_gdf = trajsplit_gdf.sort_values(by="prev_trip_id")
    sta_gdf = gpd.read_feather("data\output\TrajSplit\TrajSplitdata_upload_2024_04_08-08_02_15_%-cleaning.feather")

    map.center = (trajsplit_gdf.centroid.y.mean(), trajsplit_gdf.centroid.x.mean())
    map.zoom = 14

    colors = ['blue', 'green', 'red', 'black', 'orange']
    count = 0
    for road in sta_gdf.itertuples():
        count+=1
        polyline = Polyline(
            locations=[(lat, lon) for lon, lat in road.geometry.coords],
            color=colors[count%5],
            tooltip=road.trip_id,
            fill=False,
            name="Basic Rules: " + str(road.trip_id),
            checked=False
        )
        map.add_layer(polyline)
        if count > 3:
            break

    prev_road = 0
    count = 0
    for idx, road in enumerate(trajsplit_gdf.itertuples()):
        if not (road.prev_trip_id == prev_road):
            prev_road = road.prev_trip_id
            count+=1
        if count > 4:
            break
        polyline = Polyline(
            locations=[(lat, lon) for lon, lat in road.geometry.coords],
            color=colors[idx%5],
            tooltip=road.trip_id,
            fill=False,
            name="TrajSplit: " + str(road.trip_id),
            checked=False
        )
        map.add_layer(polyline)
    map.save("map.html")
    return map

