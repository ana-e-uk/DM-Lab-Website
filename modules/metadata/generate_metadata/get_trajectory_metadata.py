'''
File name: get_trajectory_metadata

DESCRIPTION: For each point of a trajectory with the following info:
                < trajectory_id, timestamp, latitude, longitude >
             
             Calculate:
                speed, compass direction, day, day type, time type, time bin

TODO: 
1. figure out how you would get the column names for a new trajectory file
2. code getting the heading and speed for each point accounting for trip ID(currently, we just use the columns already there)

Author: Ana Uribe
'''
########################################## IMPORTS ########################################## 
import json
import os
import pandas as pd
import numpy as np

import datetime
from geopy.distance import geodesic as GD

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
in_file_name = constants_dict['input file name']
out_file_name = constants_dict['trajectory metadata out']

# check if speed and heading need to be calculated
speed_bool = constants_dict['trajectory cols']['speed bool']
heading_bool = constants_dict['trajectory cols']['heading bool']

# get trajectory df column names
timestamp = constants_dict['trajectory cols']['timestamp col name']
speed = constants_dict['trajectory cols']['speed col name']
heading = constants_dict['trajectory cols']['heading col name']
latitude = constants_dict['trajectory cols']['latitude col name']
longitude = constants_dict['trajectory cols']['longitude col name']

# get metadata column names
compass_dir = constants_dict['metadata cols']['compass directions']
day = constants_dict['metadata cols']['day']
day_type = constants_dict['metadata cols']['day type']
time_type = constants_dict['metadata cols']['time type']
time_bin = constants_dict['metadata cols']['time bin']


# upload data as pandas dataframe
df = pd.read_csv(os.path.join(in_dir, in_file_name))

########################################## HELPER FUNCTIONS ########################################## 
def return_datetime_type(p):
   ''' 
   Returns point as datetime.datetime object
   '''
   if not isinstance(p, datetime.datetime) and not isinstance(p, str):
      raise TypeError('Input is not of type datetime.datetime or str')
   else:
      if type(p) == datetime.datetime:
         return p
      else:
         new_p = datetime.datetime.strptime(p, '%Y-%m-%d %H:%M:%S')
         return new_p

def time_difference(p_1, p_2, units='hours'): 
    ''' 
    IN: p_1, p_2 (datetime.datetime OR str) - timestamp of two points in  year-month-day hour-minute-seconds

    OUT: time difference (float OR None) - time difference between timestamps in hours if points of correct type, else None
    '''
    # make points be of datetime type
    dt_p1 = return_datetime_type(p_1)
    dt_p2 = return_datetime_type(p_2)

    # check points are correct type
    if type(dt_p1) == None or type(dt_p2) == None:
        return np.NAN
    # if they are, get time difference between them
    else:
        # get timedelta
        dif = dt_p2 - dt_p1

        d = dif.days
        s = dif.seconds
        ms = dif.microseconds

        if units == 'hours':
            hours = np.multiply(d, 24) + np.divide(s, 3600) + np.divide(ms, 3600000)
            return hours
        
        elif units == 'minutes':
            minutes = np.multiply(d, 1440) + np.divide(s, 60) + np.divide(ms, 60000)
            return minutes

        else: 
            raise ValueError('Units is not one of the following units: ("hours", "minutes").')

def distance_difference(lat_1, lat_2, long_1, long_2):
   '''
   IN: lat_1, lat_2, long_1, long_2 (float) - latitude and longitude coordinates for two points: (lat_1, long_1), (lat_2, long_2) 

   OUT: dif (float) - geodesic distance in miles between two points
   '''
   # create point tuples
   p_1 = (lat_1, long_1)
   p_2 = (lat_2, long_2)

   # use geodesic function from geopy to calculate distance
   dif = GD(p_1, p_2).miles

   return dif

def mph(r_1, r_2, cols=['Position Date Time', 'lat', 'long']):
    
   # get values
   t_1 = r_1[cols[0]]
   t_2 = r_2[cols[0]]
   
   lat_1 = r_1[cols[1]]
   lat_2 = r_2[cols[1]]

   long_1 = r_1[cols[2]]
   long_2 = r_2[cols[2]]

   # get time difference (hours)
   t_dif = time_difference(t_1, t_2)

   # get distance difference (miles)
   d_dif = distance_difference(lat_1=lat_1, lat_2=lat_2, long_1=long_1, long_2=long_2)

   # compute miles per hour
   dx_dt = np.divide(d_dif, t_dif)

   return dx_dt

# get all cardinal directions for the unique headings (binning headings into N,S,E,W,NE,NW, etc)
def get_compass_dir(x):
   if 337.5 <= x <= 360 or 0 <= x < 22.5:
      return 'N'
   elif 22.5 <= x < 67.5:
      return 'NE'
   elif 67.5 <= x < 112.5:
      return 'E'
   elif 112.5 <= x < 157.5:
      return 'SE'
   elif 157.5 <= x < 202.5:
      return 'S'
   elif 202.5 <= x < 247.5:
      return 'SW'
   elif 247.5 <= x < 292.5:
      return 'W'
   elif 292.5 <= x < 337.5:
      return 'NW'
   else:
      raise ValueError('Bearing not within bearing values (0-360).')
    
def get_day_type(t):

   dt_t = return_datetime_type(t)  # turn t into a datetime object
   weekday = dt_t.isoweekday()    # get weekday (0 - Monday, 6 - Sunday)

   if 1 <= weekday <= 5:
      return 1
   elif 6 <= weekday <= 7:
      return 0
   else:
      raise ValueError('Weekday value not within the datetime.isoweekday values (1-7).')
    
def get_day(t):

   dt_t = return_datetime_type(t)  # turn t into a datetime object
   weekday = dt_t.isoweekday()    # get weekday (0 - Monday, 6 - Sunday)
   
   if 1 <= weekday <= 7:
      return weekday
   
   ### Returns strings instead of int if needed
   # if weekday == 0:
   #     return 'M'
   # elif weekday == 1:
   #     return 'T'
   # elif weekday == 2:
   #     return 'W'
   # elif weekday == 3:
   #     return 'R'
   # elif weekday == 4:
   #     return 'F'
   # elif weekday == 5:
   #     return 'Sa'
   # elif weekday == 6:
   #     return 'Su'
   else:
      raise ValueError('Weekday value not within the datetime.isoweekday values (1-7).')
   
def get_time_type(t):
   dt_t = return_datetime_type(t)
   hour = dt_t.hour

   if 0 <= hour < 4:
      return -1
   elif 4 <= hour <= 18:
      return 1
   elif 18 < hour <= 23:
      return -1
   else:
      raise ValueError('Hour value not within regular hour times (0 - 23)')
   
def get_time_bin(d, t):
   if not isinstance(d, int) and not isinstance(t, int):
      raise TypeError('Day or time type is not an int.')
   else:
      bin = d + t
      return bin

########################################## MAIN ########################################## 
# if needed, generate speed and heading columns
if speed_bool == 0:
   print('Calculating speed')
   # osmnx.distance.euclidean might be useful

if heading_bool == 0:
   print('Calculating heading')

# generate compass directions, day type, time type columns
df[compass_dir] = df[heading].apply(get_compass_dir)
df[day] = df[timestamp].apply(get_day)
df[day_type] = df[timestamp].apply(get_day_type)
df[time_type] = df[timestamp].apply(get_time_type)

# generate time bin column
df[time_bin] = df[day_type] + df[time_type]

# save new df to the processed data
df.to_csv(os.path.join(processed_dir, out_file_name), index=False)