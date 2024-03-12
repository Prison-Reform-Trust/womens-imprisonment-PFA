"""
This script provides useful functions to all other scripts
"""

import yaml
import pandas as pd

def read_config():
    # Read in config file
    config = {k: v for d in yaml.load(
        open('config.yaml'),
            Loader=yaml.SafeLoader) for k, v in d.items()}
    return config

def load_data(status: str, filename: str) -> pd.DataFrame:
    """Load CSV file into Pandas DataFrame and convert object columns to categories when they meet criteria in `categoryColumns()`

    Parameters
    ----------
    status : {'raw', 'interim', 'processed'}
        Status of the data processing.
        * If 'raw' file is located in "rawFilePath" within config file
        * If 'interim', file is located in "intFilePath"
        * If 'processed', file is located in "clnFilePath"
    filename : str
        Name of CSV file to be loaded.

    Returns
    -------
    DataFrame
        CSV data is returned as Pandas DataFrame with any eligible object columns converted into category columns to limit memory requirements
    """
    paths = {
        "raw": 'rawFilePath',
        "interim": 'intFilePath',
        "processed": 'clnFilePath'
    }
    config = read_config()

    dfPath=f"{config['data'][paths[status]]}{filename}"
    df = pd.read_csv(dfPath)
    print('Data loaded')
    return categoryColumns(df)

def categoryColumns(df):
    """Convert columns to category data type if they meet ratio

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    DataFrame
        Processed DataFrame with object columns which meet criteria replaced with categories
    """
    cols = df.select_dtypes(include='object').columns
    for col in cols:
        ratio = len(df[col].value_counts()) / len(df)
        if ratio < 0.05:
            df[col] = df[col].astype('category')
    return df