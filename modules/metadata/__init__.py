'''
File name: module-scripts/metadata/__init__.py

Description: contains the important functions that can generate the output
             of the metadata module

             Imports constants from metadata/constants.py
             import it like this 
             from modules.metadata import [function]

Author: Ana Uribe
'''


import panel as pn

def add_metadata_widgets(column):
    column[:] = [
        pn.pane.Markdown('''
            This part is for MetaData
            ''')
    ]