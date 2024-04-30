''' 
File name modules/metadata/functions.py

Description: contains functions used by __init__.py

Author: Ana Uribe
'''


def get_metadata(m, bb):
    '''
    IN: m (ipyleaflet map)
        bb (boundig box)

    DESCRIPTION: get the OSMnx road network within the bounding box,
                 and return the road network and all the related metadata

    OUT: m_plus (ipyleaflet map) map with OSMnx road network 
         metadata_df (pandas df) 
    '''
    return