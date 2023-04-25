"""
This script provides useful funcs to all other scripts
"""

import yaml
import os
import pandas as pd

def read_config():
    # Read in config file
    config = {k: v for d in yaml.load(
        open('config.yaml'),
            Loader=yaml.SafeLoader) for k, v in d.items()}
    return config

def loadData(path_to_data, cols):
    return pd.read_csv(path_to_data, usecols=cols, low_memory=False)

def lcColumns(data):
    '''
    Converting all `data` columns to lowercase and replacing spaces with underscores

    Parameters
    ----------
    data: Pandas dataframe
    '''
    data.columns = data.columns.str.lower().str.replace(' ', '_') 

def renameColumns(data, columns):
    '''
    Rename columns within a Pandas dataframe to standardised dictionary values
    
    Parameters
    ----------
    data: Pandas dataframe

    columns: dict of original and replacement column names
    '''
    data.rename(
        columns = columns,
        inplace = True
    )

def orderColumns(data, column_order):
    '''
    Set column order for dataframe

    Parameters
    ----------
    data: Pandas dataframe

    column_order: list, ordered in ascending order to be displayed
    '''
    data = data[column_order]


def remove_num_prefix(data):
    """
    Remove numbered prefixes from all elements in dataframe

    Parameters
    ----------
    data: Pandas dataframe

    Returns
    -------
    Dataframe
        Dataframe with regex parameters replaced
    """    
    regex = [r'^\S*: \S* - ',
             r'\d\d: ',
             ]
    return data.replace(regex=regex, value='', inplace=True)