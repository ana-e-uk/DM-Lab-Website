'''
File name: utils/data_processing.py

Description: contains all the functions that pre-process the data for use in various modules.

Authors:
    Ana Uribe
'''

########################################## IMPORTS ##########################################
import os
import json

import pandas as pd

from utils.constants import (
                             IN_DATA_DIR
                            )

########################################## HELPER FUNCTIONS #################################
# create a unique file name for a file upload
def get_in_file_path():
    file_name = '' #TODO: make the file name be unique for each uploaded file to save it
    file_path = os.path.join(IN_DATA_DIR, file_name)
    return file_path

# create a pandas df from the uploaded data
def get_in_data_df(f_input_widget):
    file_path = get_in_file_path()

    if f_input_widget is not None:
        f_input_widget.save(file_path)
        in_data_df = pd.read_csv(file_path)

        return in_data_df
    
# create a dictionary from the uploaded data info file
def get_in_data_info_dict(f_input_info_widget):
    file_path = get_in_file_path()

    if f_input_info_widget is not None:
        f_input_info_widget.save(file_path)
        in_data_info_dict = json.loads(file_path)

        return in_data_info_dict

# checks data input is valid, returns error message if not
def check_data_is_valid(df):
    pass

########################################## FUNCTIONS ########################################
'''
Create a class instance of InputData for each data upload.

This class gets and keeps the name of the necessary columns
    - this code assumes a file with the corresponding column names for the columns we want
      is provided along with the uploaded data. Later on, we can write a function that extracts
      this information from the raw file.
'''
class InputData:

    def __init__(self, f_input_widget, f_input_info_widget):

        self.df = get_in_data_df(f_input_widget=f_input_widget)
        self.columns = get_in_data_info_dict(f_input_info_widget=f_input_info_widget)

        # necessary column names
        self.lat = self.columns['latitude']
        self.long = self.columns['longitude']

        # additional column names
    
    # call the following functions to get the column names
    def lat_col_name(self):
        return self.lat
    
    def long_col_name(self):
        return self.long
    
    # call the following functions to get the columns
    def lat_column(self):
        return self.df[self.lat]
    
    def long_column(self):
        return self.df[self.long]
    

'''
This code declares an instance of the InputData defined above, 
and checks if the data is valid for the module choices
'''
# declare InputData

# given module_choice_widget choices, make sure the data is valid for the desired modules

# if it is, 
    # call the main.py functions for the coresponding modules
    # these modules will be passed the instance of the InputData defined above

    # when the main.py functions return their output here (and we knew it would take awhile), 
        # an email will be sent out to the user to say the data is ready
        # the data will be downloadable and ready for visualization

    # if the user decides to visualize the data, the visualization.py functions for the 
    # corresponding modules will be called
    # additionally, the panel-script for the module will be called to create the webpage/dashboard


# if the data is not valid/usable, this script will return errors regarding the data upload
    
    
    

        

