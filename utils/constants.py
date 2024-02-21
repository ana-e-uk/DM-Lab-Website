'''
File name: utils/constants.py

Description: contains constants that are used in:
                - the panel-scripts including panel-scripts/main.py
                - utils/data_processing.py
                - utils/visualization.py
             
Author: Ana Uribe
'''

########################################## IMPORTS ##########################################
import random


########################################## DATA PROCESSING CONSTANTS ########################
# file paths
IN_DATA_DIR = '~/DM-Lab-Website/data/input'
OUT_DATA_DIR = '~/DM-Lab-Website/data/output'


########################################## VISUALIZATION CONSTANTS ##########################
# colors for the dashboard
BLACK_COLOR = "rgba(47, 79, 79, 1)"

# colors for multiple Polylines
# colors code copied from https://stackoverflow.com/questions/28999287/generate-random-colors-rgb,
n_colors = 200000
COLORS = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
             for i in range(n_colors)]