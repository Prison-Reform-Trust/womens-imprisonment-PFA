"""
This script provides useful funcs to all other scripts
"""

import yaml

def read_config():
    # Read in config file
    config = {k: v for d in yaml.load(
        open('config.yaml'),
            Loader=yaml.SafeLoader) for k, v in d.items()}
    return config

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