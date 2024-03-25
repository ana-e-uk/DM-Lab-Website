'''
File name: module-scripts/metadata/constants.py

Description: contains all the constants for the metadata module functions (in main.py) and visualization code (in visualization.py)

Author: Ana Uribe
'''

########################################## IMPORTS ##################################################
import os


########################################## START Main CONSTANTS #######################################
# OSMNx graph generation defaults
DIST = 8000
NETWORK_TYPE = 'drive'

# Metadata constants
HEADING_DICT = {'N': (337.5, 22,5),
                'NE': (22.5, 67.5),
                'E': (67.5, 112.5),
                'SE': (112.5, 157.5),
                'S': (157.5, 202.5),
                'SW': (202.5, 247.5),
                'W': (247.5, 292.5),
                'NW': (292.5, 337.5),
                }

DIRECT_OPPOSITE_HEADING = {
                            'N': 'S',
                            'NE': 'SW',
                            'E': 'W',
                            'SE': 'NW',
                            # repeat of above, switched
                            'S':'N',
                            'SW': 'NE',
                            'W': 'E',
                            'NW': 'SE'
                          }

OPPOSITE_HEADING = {
                    'N': ['SW', 'SE'],
                    'NE': ['W', 'S'],
                    'E': ['NW', 'SW'],
                    'SE': ['N', 'W'],
                    'S': ['NE', 'NW'],
                    'SW': ['E', 'N'],
                    'W': ['NE', 'SE'],
                    'NW': ['S', 'E']
                   }

TURN_RANGES = {
               'right': (67, 135),
               'left': (225, 292),
               'ahead': [(315, 360), (0, 45)],
               'u-turn': (157, 202)
              }

########################################## END Main CONSTANTS #######################################

########################################## START Visualization CONSTANTS #################################

# OSMNx graph, nodes and edges
FIG_SIZE = (8, 8)
GRAPH_BG_COLOR = '#111111'   #'#0a0a0a'
NODE_COLOR = 'w'
NODE_SIZE = 15
EDGE_COLOR = '#999999'  #'#ebe6e6'

# trajectories plotted on OSMNx graph
TRAJ_POINT_MARKER ='x'
TRAJ_POINT_MARKER_SIZE = 1
PLOT_TYPES = ['scatter', 'line']

########################################## END VISUALIZATION CONSTANTS ##################################

########################################## START metadata_pn CONSTANTS ##########################################

METADATA_DIR = os.path.join(os.pardir, os.pardir, 'data/output/metadata.csv')  ## TODO: save metadata file somewhere else (on a server)

# helps create range of lat/long from point
POINT_RANGE = 0.05