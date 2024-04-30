'''
File name: module-scripts/traj-split/__init__.py

Description: contains all the functions that generate the output
             of the traj-split module

             This how you import it
             from modules.traj_split import [function]

Author:
'''

import panel as pn


def add_traj_split_widgets(column):
    column[:] = [
        pn.pane.Markdown('''
            This part is for TrajSplit
            ''')
    ]
    return