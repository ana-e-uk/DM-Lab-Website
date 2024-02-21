'''
File name: module-scripts/traj-split/visualization.py

Description: contains all the functions that generate the visualization for the
             traj-split module webpage/dashboard

             Imports constants from traj-split/constants.py

Authors: 
    Ana Uribe
'''

########################################## IMPORTS ##########################################
import panel as pn

from utils.visualization import (
                                 get_folium_map,
                                 get_polyline
                                )

from utils.constants import (
                             OUT_DATA_DIR
                            )

from constants import ( 
                       MAP_HEIGHT
                      )
########################################## HELPER FUNCTIONS #################################
def med_coordinates(lat, long):
    '''
    Returns the medium coordinates given the latitude and longitude
    columns of the data 
    '''
    m_lat = lat.median()
    m_long = long.median()

    return m_lat, m_long

########################################## FUNCTIONS ########################################

def visualize(dat, dat_file_name, temp, spatial, idle, cruise):
    '''
    Main function that visualizes the results
    '''
    # get latitude and longitude columns for trips, 
    # get trips list from dat
    lat = []
    long = []
    trips = []

    # call functions that create the map for the OG trips
    med_lat, med_long = med_coordinates(lat, long)

    m_og = get_folium_map(med_lat, med_long)
    for trip in trips:
        get_polyline(trip).add_to(m_og)

    m_og_folium_pane = pn.pane.plot.Folium(m_og, height=MAP_HEIGHT)

    # create the map for the Split Trips
    t = int(temp)
    s = int(spatial)
    i = int(idle)
    c = int(cruise)

    bool_str = f'_{t}{s}{i}{c}'

    ########### WORK IN PROGRESS  ########### 
    # cur_file_path = os.path.join(OUT_DATA_DIR, dat_file_name, bool_str)
    # split_trips_df = pd.read_csv(cur_file_path)

    # med_lat, med_long = med_coordinates(split_trips_df)

    # m = get_folium_map(med_lat, med_long)

    # # check for no boxes, this is not going to be necessary when I have the OG file, so will just need the else case
    # if bool_str == '_0000':
    #     df = save_lat_long(split_trips_df)
    #     get_polyline(df).add_to(m)
    # else:
    #     df = split_trips_df.groupby('trip_id')[['Latitude', 'Longitude']].agg(lambda x: list(x))

    #     for i in range(len(df)):
    #         p = get_polyline(zip(df['Latitude'][i], df['Longitude'][i]), num_trip=i)
    #         p.add_to(m)

    # folium_pane = pn.pane.plot.Folium(m, height = 500)

