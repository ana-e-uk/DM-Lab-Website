'''
File name: draft_upload_data.py

Description: Generate (local) web dashboard to upload data for all modules. 
             The first 10 rows of the uploaded file are given.
             Uploaded data is saved at: '../data/input/uploads' but is NOT saved on github (by design)
             
             To generate the dashboard, type the following command in the command line:
                
                    panel serve draft_upload_data.py

Author: Ana Uribe
'''
########################################## START IMPORTS ##########################################
import panel as pn
import numpy as np
import pandas as pd
import io
import os
import json
from datetime import datetime

import bokeh
from bokeh.plotting import figure

########################################## END IMPORTS ##########################################

pn.extension()


########################################## START CONSTANTS ##########################################

data_dir = os.path.join(os.pardir, 'data/input/uploads')

########################################## END CONSTANTS ##########################################


########################################## START HELPER FUNCTIONS ##########################################
# Function to save uploaded data with unique name 
def save_uploaded_file(df):

    unique_file_name = datetime.now().strftime("%Y_%m_%d-%H_%M_%S_%")
    file_name = 'data_upload_' + unique_file_name
    df.to_csv(os.path.join(data_dir, file_name))
########################################## END HELPER FUNCTIONS ##########################################


########################################## START PANEL ELEMENTS ##########################################
gen_description = pn.pane.Markdown('''
                                   # Data Upload:
                                   Upload your CSV file with trajectories which will be used to inform the modules.
                                   ''')

file_input_widget = pn.widgets.FileInput()

@pn.depends(file_input_widget)
def f(file_input_widget):
    if file_input_widget is None:
        data = pd.DataFrame({'TimeStamp': [], 
                             'Latitude': [], 
                             'Longitude': [],
                             'ID': []})
    
    else:
        data = pd.read_csv(io.BytesIO(file_input_widget))

        save_uploaded_file(data)
    
    return pn.Column(f'## Uploaded File: first 10 rows', data.head(10))

elements = pn.Column(gen_description,
                     file_input_widget,
                     f
                     ).servable()
########################################## END PANEL ELEMENTS ##########################################